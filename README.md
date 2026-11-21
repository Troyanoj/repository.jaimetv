# Repositorio Kodi de Palantir 3 (auto-hospedado)

Este directorio contiene `plugin.video.palantir3` **3.3.13** y el repositorio
Kodi `repository.jaimetv`. La 3.3.13 usa un `default.py` **en fuente** (Plan B),
compatible con Python 3.12, 3.13 y 3.14; los `libs/*.md` son los del addon
original y no se han tocado.

## Estado actual

- GitHub: <https://github.com/Troyanoj/repository.jaimetv>
- GitHub Pages: <https://troyanoj.github.io/repository.jaimetv/>
- Publicado: `plugin.video.palantir3` **3.3.13** y `repository.jaimetv` **1.0.0**.
- Validado en **Kodi nativo Ubuntu 26.04 / Kodi 21.3 / Python 3.14**. El mismo
  fuente carga en Python 3.12 y 3.13; el Flatpak 21.3 (3.12) queda pendiente de
  la prueba real en el equipo de trabajo.
- `minversion="21.3.0"`: el repositorio solo se ofrece a Kodi 21.3, que es la
  versión probada. No se ofrece a versiones anteriores sin probar.
- **Contenido**: la BD Moria es una foto fija; las series y episodios nuevos no
  se actualizan solos. Ver “Actualización de contenido”.

## Qué se ha cambiado

- `default.py` está reescrito **en fuente** (cargador de `libs`, router de
  acciones, renderizado de listas e inicialización). Sustituye al bytecode 3.12
  que hacía crash a Kodi 3.14 y funciona en 3.12, 3.13 y 3.14.
- `libs/ioiiIII11.md` (actualizador de la base Moria) ya **no consulta**
  `https://api.github.com/repos/Maniac2017/Mipal2025`. La URL se ha dejado vacía
  y `getDateUpdate()` devuelve una lista de actualizaciones vacía. El addon sigue
  usando la BD Moria existente.
- `addon.xml` pasa de `3.3.11` a `3.3.13` (versión numérica, compatible con Kodi).
- Se ha añadido `repository.jaimetv` (1.0.0) y el generador de repositorio.

**No se ha tocado** la búsqueda, los listados, Alldebrid, Real-Debrid, Trakt, TMDb
ni la reproducción: toda esa lógica sigue en los `libs/*.md` originales.

## Estructura

```text
kodi-repo/
├── src/
│   ├── plugin.video.palantir3/       # fuente del addon (se empaqueta)
│   └── repository.jaimetv/             # addon repositorio (plantilla con {{BASE_URL}})
├── docs/                             # raíz que se publica (GitHub Pages)
│   ├── addons.xml
│   ├── addons.xml.md5
│   └── zips/
│       ├── plugin.video.palantir3/plugin.video.palantir3-3.3.13.zip
│       └── repository.jaimetv/repository.jaimetv-1.0.0.zip
├── tools/
│   ├── build_repo.py                 # genera addons.xml, md5 y zips
│   ├── release.py                    # sube versión + build + git
│   └── p3_codec.py                   # decodifica/codifica libs/*.md
└── README.md
```

## Requisitos

- Python 3.8+ (solo stdlib).
- Kodi 21.3, probado en **Kodi nativo Ubuntu 26.04 (Python 3.14)**. El mismo
  `default.py` fuente carga en Python 3.12/3.13; el Flatpak 21.3 (Python 3.12)
  está pendiente de la prueba real en el equipo de trabajo.
- El repo declara `minversion="21.3.0"` porque es la versión probada; no se
  ofrece a versiones anteriores de Kodi sin probar.
- Para publicar: una cuenta de GitHub (GitHub Pages gratuito) o cualquier hosting
  HTTPS que sirva archivos estáticos.

## Prueba local (antes de publicar)

```bash
cd kodi-repo
python3 tools/build_repo.py --base-url http://127.0.0.1:8000 --output docs-local

# En otra terminal, servir docs-local/
python3 -m http.server 8000 --directory docs-local
```

En Kodi de **este mismo equipo**:
1. Ajustes → Sistema → Add-ons → activar “Fuentes desconocidas”.
2. Add-ons → Instalar desde archivo zip →
   `kodi-repo/docs-local/zips/repository.jaimetv/repository.jaimetv-1.0.0.zip`.
3. Add-ons → Instalar desde repositorio → “Repositorio Jaimetv” →
   Add-ons de vídeo → Palantir 3 → Instalar.
4. Comprobar que instala **3.3.13**.

> `127.0.0.1` solo funciona en este equipo. Para otro dispositivo usa la IP LAN
> del equipo que sirve (`http://192.168.x.x:8000`) o publica en GitHub Pages.

## Actualizar el repositorio publicado

El repositorio ya está creado y GitHub Pages está activo. Para publicar una
versión nueva:

```bash
python3 tools/release.py \
  --base-url https://troyanoj.github.io/repository.jaimetv \
  --bump patch \
  --publish
```

`release.py` sube la versión del plugin, regenera `docs/`, hace commit y push.
GitHub Pages republica en 1-2 minutos. Verifica:

```bash
curl -sS https://troyanoj.github.io/repository.jaimetv/addons.xml.md5
```

Si cambias el `addon.xml` del **repositorio** (por ejemplo `minversion`), sube
también su versión (`1.0.0` → `1.0.1`) para que Kodi lo actualice.

Si alguna vez hay que recrear el repo desde cero:

```bash
git init
git add -A
git commit -m "Repositorio Palantir 3"
git branch -M main
git remote add origin https://github.com/Troyanoj/repository.jaimetv.git
git push -u origin main
# Settings → Pages → Deploy from a branch → main / docs
```

### Instalar en un dispositivo

Instala el zip del repositorio:

`docs/zips/repository.jaimetv/repository.jaimetv-1.0.0.zip`

o descárgalo de:

`https://troyanoj.github.io/repository.jaimetv/zips/repository.jaimetv/repository.jaimetv-1.0.0.zip`

### Desinstalar el repositorio antiguo

Para que Kodi deje de consultar `palantir.5g.in/Repo/addons.xml.md5`:

1. Ajustes → Add-ons → Mis add-ons → Repositorios de add-ons.
2. `Repositorio Palantir` / `repository.estupalant` → Desinstalar.
3. Si Kodi ofrece desinstalar addons instalados desde ese repo, **no** desinstales
   Palantir 3; solo el repositorio.

Después instala `repository.jaimetv`. El addon 3.3.13 y su BD Moria se conservan.

## Publicar futuras actualizaciones

Edita lo que quieras en `src/plugin.video.palantir3/` y después:

```bash
# sube la parte patch: 3.3.13 -> 3.3.14
python3 tools/release.py \
  --base-url https://troyanoj.github.io/repository.jaimetv \
  --bump patch \
  --publish
```

`release.py` hace: bump de `addon.xml`, build de `docs/`, commit y push. GitHub
Pages publica solo. Kodi lo detecta al comprobar actualizaciones (o al reiniciar).

Reglas de versión:
- Usa siempre números: `3.3.13`, `3.3.14`, `3.4.0`.
- **No uses** `3.3.13-local.1`: Kodi separa el nombre del zip por el último `-`
  y una versión con guion puede confundir la instalación.
- La versión del addon repositorio (`repository.jaimetv`) solo hay que subirla si
  cambias su `addon.xml`.

## Base de datos Moria (contenidos)

La BD real está en el dispositivo de trabajo:

```text
special://profile/addon_data/script.module/settings.xml   (~144 MB)
```

Es la que contiene películas, series y enlaces. **No se incluye en el zip** por
tamaño y porque no debe publicarse en un repo público. En los equipos ya
instalados suele existir; si falta, cópiala desde uno que funcione a la misma
ruta (`.../userdata/addon_data/script.module/settings.xml`) con Kodi cerrado.
Si no existe, el addon no tendrá contenido que listar: el actualizador original
está desactivado porque su origen en GitHub ya no existe.

## Actualización de contenido

- **Código** (scrapers, resolvers, arreglos): se actualiza automáticamente desde
  este repositorio.
- **Contenido** (series nuevas, temporadas/episodios nuevos, enlaces nuevos):
  **no** se actualiza solo. La BD Moria es una foto fija (contenido hasta
  finales de octubre de 2026, versión 556.1). El actualizador original
  (`getDateUpdate`/`get_moria`) descargaba `moria_*.up`/`.zm3` de
  `Maniac2017/Mipal2025`, que ya no existe.
- `listado_episodioS` construye la lista con
  `SELECT DISTINCT episodio FROM enlaces_series`; si un episodio nuevo no está
  en la BD, no aparece aunque TMDb lo conozca.
- Para tener contenido nuevo automático haría falta una **fuente propia** de
  actualizaciones (generar y alojar `moria_*.up`/`.zm3` o una BD completa) y
  volver a activar el actualizador con esa URL. Es un proyecto de contenido
  aparte; no basta con actualizar el código.
- Interino: si aparece una BD Moria actualizada de confianza, se copia y las
  series/episodios nuevos aparecen sin tocar el código. No uses BDs/`.up` de
  origen desconocido: el actualizador ejecuta SQL sobre la BD del addon.

## Rollback

- Código original 3.3.11: `../.audit/live/plugin.video.palantir3/` (copia exacta
  del addon instalado antes de tocar nada).
- BD original: `../.audit/backup/moria_settings.xml` (144 MB).
- Repo original: `../.audit/live/repository.estupalant/`.
- Para volver atrás en Kodi: desinstala 3.3.13 e instala el zip 3.3.11 original;
  la BD Moria no se modifica.

## Notas técnicas

- `libs/*.md` **no son Markdown**: son módulos Python en Base85 con una rotación
  de bytes. Para editar uno:
  ```bash
  python3 - <<'EOF'
  import sys; sys.path.insert(0, 'tools')
  from p3_codec import decode, encode
  src = decode(open('src/plugin.video.palantir3/libs/ioiiIII11.md','rb').read())
  open('/tmp/ioiiIII11.py','wb').write(src)
  EOF
  # editar /tmp/ioiiIII11.py y volver a codificar con encode(...)
  ```
- `default.py` es ahora código fuente (Plan B); los `libs/*.md` siguen siendo los módulos originales codificados.
- `addons.xml.md5` se calcula sobre los bytes exactos de `addons.xml`.
- El repo addon usa `<dir minversion="21.3.0">` (versión de Kodi probada) con
  `info`, `checksum` y `datadir zip="true"`.

## Comprobaciones tras instalar

En `kodi.log` no deben aparecer ya:

```text
api.github.com/repos/Maniac2017/Mipal2025
palantir.5g.in/Repo/addons.xml.md5
```

Y sí debe aparecer la versión nueva:

```text
plugin.video.palantir3 v3.3.13 installed
```

Prueba después: abrir el addon, buscar una película, abrir una serie, reproducir
un enlace y comprobar Alldebrid.
