# Repositorio Kodi de Palantir 3 (auto-hospedado)

Este directorio contiene el addon `plugin.video.palantir3` **3.3.12** (partiendo del
3.3.11 real instalado en el equipo) y un repositorio Kodi propio
(`repository.jaimetv`) para distribuirlo y actualizarlo en todos tus dispositivos.

> **Aviso importante (Python 3.12 vs 3.13).** El `default.py` real es bytecode
> específico de la versión de Python. Este paquete 3.3.12 se ha extraído de un
> Kodi Flatpak 21.3 con **Python 3.12**. El Kodi 21.2 de Debian enlaza
> `libpython3.13` y necesita el `default.py` de Python 3.13. Antes de publicar
> el repo para esos equipos hay que añadir `default_3.13.py` y el selector
> multi-versión (3.3.13). **No publiques 3.3.12 en un repo visible a equipos
> Debian nativos hasta tener esa versión**: Kodi los actualizaría a un paquete
> que no puede ejecutar.

## Qué se ha cambiado

- `default.py` es el **código real** del addon (47.987 bytes), no el launcher que
  descargaba código desde `palantir.5g.in`. Ya no hay bootstrap remoto.
- `libs/ioiiIII11.md` (actualizador de la base Moria) ya **no consulta**
  `https://api.github.com/repos/Maniac2017/Mipal2025`. La URL se ha dejado vacía
  y `getDateUpdate()` devuelve una lista de actualizaciones vacía. El addon sigue
  usando la BD Moria existente.
- `addon.xml` pasa de `3.3.11` a `3.3.12` (versión numérica, compatible con Kodi).
- Se ha añadido `repository.jaimetv` (1.0.0) y el generador de repositorio.

**No se ha tocado** la búsqueda, los listados, Alldebrid, Real-Debrid, Trakt, TMDb
ni la reproducción. Los únicos cambios funcionales son los dos anteriores.

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
│       ├── plugin.video.palantir3/plugin.video.palantir3-3.3.12.zip
│       └── repository.jaimetv/repository.jaimetv-1.0.0.zip
├── tools/
│   ├── build_repo.py                 # genera addons.xml, md5 y zips
│   ├── release.py                    # sube versión + build + git
│   └── p3_codec.py                   # decodifica/codifica libs/*.md
└── README.md
```

## Requisitos

- Python 3.8+ (solo stdlib).
- Kodi 21+ en este paquete. El `default.py` real es bytecode de **Python 3.12**
  (Kodi Flatpak 21.3). El **Kodi 21.2 nativo de Debian usa Python 3.13** porque
  enlaza `libpython3.13`; para esos equipos hace falta su `default.py` y un
  selector multi-versión (3.3.13). Para Kodi 19/20/22 ocurre lo mismo: el
  bytecode no es portable entre versiones. Mientras el repo solo tenga el
  entrypoint 3.12, declara `minversion="21.3.0"` para que el Kodi 21.2 de
  Debian (Python 3.13) **no** vea/instale esta versión. Cuando se añada
  `default_3.13.py` en 3.3.13 se bajará a `21.0.0`.
- Para publicar: una cuenta de GitHub (GitHub Pages gratuito) o cualquier hosting
  HTTPS que sirva archivos estáticos.

## Prueba local (antes de publicar)

```bash
cd kodi-repo
python3 tools/build_repo.py --base-url http://127.0.0.1:8000

# En otra terminal, servir docs/
python3 -m http.server 8000 --directory docs
```

En Kodi de **este mismo equipo**:
1. Ajustes → Sistema → Add-ons → activar “Fuentes desconocidas”.
2. Add-ons → Instalar desde archivo zip →
   `kodi-repo/docs/zips/repository.jaimetv/repository.jaimetv-1.0.0.zip`.
3. Add-ons → Instalar desde repositorio → “Repositorio Jaimetv” →
   Add-ons de vídeo → Palantir 3 → Instalar.
4. Comprobar que instala **3.3.12**.

> `127.0.0.1` solo funciona en este equipo. Para otro dispositivo usa la IP LAN
> del equipo que sirve (`http://192.168.x.x:8000`) o publica en GitHub Pages.

## Publicar en GitHub Pages

1. Crea un repositorio **público** en GitHub, por ejemplo `kodi-repo`.
2. Sube el contenido de este directorio:
   ```bash
   git init
   git add -A
   git commit -m "Repositorio Palantir 3"
   git branch -M main
   git remote add origin https://github.com/Troyanoj/repository.jaimetv.git
   git push -u origin main
   ```
3. En GitHub: Settings → Pages → “Deploy from a branch” → `main` / `/docs`.
4. Espera a que publique y comprueba:
   ```bash
   curl -I https://troyanoj.github.io/repository.jaimetv/addons.xml
   curl -I https://troyanoj.github.io/repository.jaimetv/addons.xml.md5
   ```
5. Reconstruye con la URL real (importante: cambia las URLs del repo addon):
   ```bash
   python3 tools/release.py --base-url https://troyanoj.github.io/repository.jaimetv
   git add -A && git commit -m "URL de Pages" && git push
   ```
6. Instala en cada dispositivo el **nuevo** zip
   `docs/zips/repository.jaimetv/repository.jaimetv-1.0.0.zip`.

### Desinstalar el repositorio antiguo

Para que Kodi deje de consultar `palantir.5g.in/Repo/addons.xml.md5`:

1. Ajustes → Add-ons → Mis add-ons → Repositorios de add-ons.
2. `Repositorio Palantir` / `repository.estupalant` → Desinstalar.
3. Si Kodi ofrece desinstalar addons instalados desde ese repo, **no** desinstales
   Palantir 3; solo el repositorio.

Después instala `repository.jaimetv`. El addon 3.3.12 y su BD Moria se conservan.

## Publicar futuras actualizaciones

Edita lo que quieras en `src/plugin.video.palantir3/` y después:

```bash
# sube la parte patch: 3.3.12 -> 3.3.13
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
tamaño y porque no debe publicarse en un repo público. En tus dispositivos ya
existe y las actualizaciones del addon no la tocan.

Para un dispositivo nuevo, copia ese archivo desde uno que funcione a la misma
ruta (`.../userdata/addon_data/script.module/settings.xml`) con Kodi cerrado.
Si no existe, el addon no tendrá contenido que listar: el actualizador original
está desactivado porque su origen en GitHub ya no existe.

Si en el futuro quieres actualizar contenidos, habrá que decidir una fuente
propia para los archivos `moria_*.up` / `*.zm3` (por ejemplo un servidor privado)
y volver a poner esa URL en `libs/ioiiIII11.md`.

## Rollback

- Código original 3.3.11: `../.audit/live/plugin.video.palantir3/` (copia exacta
  del addon instalado antes de tocar nada).
- BD original: `../.audit/backup/moria_settings.xml` (144 MB).
- Repo original: `../.audit/live/repository.estupalant/`.
- Para volver atrás en Kodi: desinstala 3.3.12 e instala el zip 3.3.11 original;
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
- `default.py` es código ofuscado (marshal) del addon original; no se ha tocado.
- `addons.xml.md5` se calcula sobre los bytes exactos de `addons.xml`.
- El repo addon usa `<dir minversion="19.0.0">` con `info`, `checksum` y
  `datadir zip="true"`.

## Comprobaciones tras instalar

En `kodi.log` no deben aparecer ya:

```text
api.github.com/repos/Maniac2017/Mipal2025
palantir.5g.in/Repo/addons.xml.md5
```

Y sí debe aparecer la versión nueva:

```text
plugin.video.palantir3 v3.3.12 installed
```

Prueba después: abrir el addon, buscar una película, abrir una serie, reproducir
un enlace y comprobar Alldebrid.
