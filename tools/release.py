#!/usr/bin/env python3
"""Bump the plugin version, rebuild the repo and optionally publish it.

Examples:
    python3 tools/release.py --base-url https://USER.github.io/kodi-repo --bump patch
    python3 tools/release.py --base-url https://USER.github.io/kodi-repo --version 3.3.13 --publish
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_XML = ROOT / "src" / "plugin.video.palantir3" / "addon.xml"

sys.path.insert(0, str(ROOT / "tools"))
import build_repo  # noqa: E402


def read_version() -> str:
    text = PLUGIN_XML.read_text(encoding="utf-8")
    m = re.search(r'(<addon\b[^>]*\bversion=")([^"]+)(")', text)
    if not m:
        raise SystemExit(f"No version in {PLUGIN_XML}")
    return m.group(2)


def bump(version: str, part: str) -> str:
    nums = [int(x) for x in version.split(".")]
    while len(nums) < 3:
        nums.append(0)
    if part == "major":
        nums = [nums[0] + 1, 0, 0]
    elif part == "minor":
        nums = [nums[0], nums[1] + 1, 0]
    else:
        nums[2] += 1
    return ".".join(str(x) for x in nums[:3])


def set_version(new: str) -> None:
    if not re.fullmatch(r"\d+(\.\d+){1,3}", new):
        raise SystemExit(
            "Kodi version must be numeric (e.g. 3.3.12). Avoid '-local.1' suffixes."
        )
    text = PLUGIN_XML.read_text(encoding="utf-8")
    text, n = re.subn(
        r'(<addon\b[^>]*\bversion=")([^"]+)(")', rf"\g<1>{new}\g<3>", text, count=1
    )
    if n != 1:
        raise SystemExit("Could not update version in addon.xml")
    PLUGIN_XML.write_text(text, encoding="utf-8")


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--bump", choices=["patch", "minor", "major"])
    ap.add_argument("--version")
    ap.add_argument("--publish", action="store_true", help="git add/commit/push")
    args = ap.parse_args()

    current = read_version()
    if args.version and args.bump:
        raise SystemExit("Use either --version or --bump, not both")

    if args.version:
        new = args.version
    elif args.bump:
        new = bump(current, args.bump)
    else:
        new = current

    if new != current:
        set_version(new)
        print(f"version: {current} -> {new}")
    else:
        print(f"version: {new} (unchanged)")

    build_repo.build(args.base_url, build_repo.DOCS)

    if args.publish:
        run(["git", "add", "-A"])
        run(["git", "commit", "-m", f"Palantir 3 {new}"])
        run(["git", "push"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
