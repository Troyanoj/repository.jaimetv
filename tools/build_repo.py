#!/usr/bin/env python3
"""Build a Kodi repository (addons.xml + md5 + zips) from ./src.

Usage:
    python3 tools/build_repo.py --base-url https://USER.github.io/REPO
    python3 tools/build_repo.py --base-url http://127.0.0.1:8000   # local test

The script is intentionally dependency-free (stdlib only).
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BUILD = ROOT / "build"
DOCS = ROOT / "docs"

PLUGIN_ID = "plugin.video.palantir3"
REPO_ID = "repository.jaimetv"

IGNORE = shutil.ignore_patterns(
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    ".audit",
    ".DS_Store",
    "*.dis.txt",
    ".stage2.bin",
    ".stage3.marshal",
)


def addon_version(addon_dir: Path) -> str:
    text = (addon_dir / "addon.xml").read_text(encoding="utf-8")
    m = re.search(r'<addon\b[^>]*\bversion="([^"]+)"', text)
    if not m:
        raise SystemExit(f"No version found in {addon_dir / 'addon.xml'}")
    return m.group(1)


def validate_xml(path: Path) -> None:
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        raise SystemExit(f"Invalid XML in {path}: {exc}") from exc


def stage(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=IGNORE)


def substitute(path: Path, base_url: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace("{{BASE_URL}}", base_url)
    path.write_text(text, encoding="utf-8")


def zip_addon(stage_dir: Path, addon_id: str, out_zip: Path) -> None:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in sorted(stage_dir.rglob("*")):
            if p.is_file():
                zf.write(p, f"{addon_id}/{p.relative_to(stage_dir).as_posix()}")


def addon_xml_block(addon_xml: Path, addon_id: str) -> str:
    text = addon_xml.read_text(encoding="utf-8")
    text = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", text, count=1).strip()
    if f'id="{addon_id}"' not in text:
        raise SystemExit(f"{addon_xml} does not declare id={addon_id}")
    return text


def build(base_url: str, output: Path) -> None:
    base_url = base_url.rstrip("/")
    plugin_src = SRC / PLUGIN_ID
    repo_src = SRC / REPO_ID
    if not plugin_src.is_dir() or not repo_src.is_dir():
        raise SystemExit("Missing src/plugin.video.palantir3 or src/repository.jaimetv")

    plugin_version = addon_version(plugin_src)
    repo_version = addon_version(repo_src)

    validate_xml(plugin_src / "addon.xml")
    validate_xml(repo_src / "addon.xml")

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)
    zips_root = output / "zips"
    if zips_root.exists():
        shutil.rmtree(zips_root)

    plugin_stage = BUILD / PLUGIN_ID
    stage(plugin_src, plugin_stage)
    validate_xml(plugin_stage / "addon.xml")
    plugin_zip = zips_root / PLUGIN_ID / f"{PLUGIN_ID}-{plugin_version}.zip"
    zip_addon(plugin_stage, PLUGIN_ID, plugin_zip)

    repo_stage = BUILD / REPO_ID
    stage(repo_src, repo_stage)
    substitute(repo_stage / "addon.xml", base_url)
    validate_xml(repo_stage / "addon.xml")
    repo_zip = zips_root / REPO_ID / f"{REPO_ID}-{repo_version}.zip"
    zip_addon(repo_stage, REPO_ID, repo_zip)

    addons = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        "<addons>\n"
        + addon_xml_block(plugin_stage / "addon.xml", PLUGIN_ID)
        + "\n"
        + addon_xml_block(repo_stage / "addon.xml", REPO_ID)
        + "\n</addons>\n"
    )
    output.mkdir(parents=True, exist_ok=True)
    addons_path = output / "addons.xml"
    addons_path.write_text(addons, encoding="utf-8")
    validate_xml(addons_path)
    digest = hashlib.md5(addons.encode("utf-8")).hexdigest()
    (output / "addons.xml.md5").write_text(digest + "\n", encoding="ascii")

    print(f"base URL      : {base_url}")
    print(f"plugin        : {plugin_version} -> {plugin_zip}")
    print(f"repository    : {repo_version} -> {repo_zip}")
    print(f"addons.xml    : {addons_path} ({len(addons)} bytes)")
    print(f"addons.xml.md5: {digest}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-url", required=True, help="Public base URL (no trailing slash)")
    ap.add_argument("--output", default=str(DOCS), help="Output directory (default: docs)")
    args = ap.parse_args()
    build(args.base_url, Path(args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
