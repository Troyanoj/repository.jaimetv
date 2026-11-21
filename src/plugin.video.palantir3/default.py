# -*- coding: utf-8 -*-
"""Palantir 3 - entrypoint compatiblee con Python 3.8+ (Kodi 19-22).

Reconstruido a partir del entrypoint 3.3.11 (Python 3.12) para poder ejecutarlo
tambien en Kodi nativo de Debian/Ubuntu con Python 3.13/3.14. La logica del
addon sigue en libs/*.md; aqui solo estan el cargador, el router y el render.
"""
import base64
import builtins
import os
import sys
import threading
import traceback
from types import ModuleType

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

_ADDON = xbmcaddon.Addon()
_ADDON_PATH = xbmcvfs.translatePath(_ADDON.getAddonInfo('Path'))
_ORIG_IMPORT = builtins.__import__
_LOAD_LOCK = threading.RLock()


def _load_lib(name):
    path = os.path.join(_ADDON_PATH, name.replace('.', os.sep) + '.md')
    if not os.path.isfile(path):
        raise ImportError('No existe %s' % path)
    data = open(path, 'rb').read()
    n = len(data)
    k = n // 3
    encoded = data[n - k:] + data[:k] + data[k:n - k][::-1]
    source = base64.b85decode(encoded).decode('utf-8')
    module = ModuleType(name)
    module.__file__ = path
    module.__package__ = 'libs'
    sys.modules[name] = module
    exec(compile(source, path, 'exec'), module.__dict__)
    return module


def _p3_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name not in sys.modules and name.startswith('libs.'):
        with _LOAD_LOCK:
            if name not in sys.modules:
                _load_lib(name)
    return _ORIG_IMPORT(name, globals, locals, fromlist, level)


builtins.__import__ = _p3_import
xbmc.log('Palantir 3 PlanB: loader instalado', xbmc.LOGINFO)

from libs.ioo000O00Oo import (  # noqa: E402
    CACHE,
    ISESTUARYPALANTIR,
    KODI_VERSION,
    WINDOW,
    get_setting,
    localize,
    logger,
    set_setting,
)
from libs.ioI1iIiIii1 import P3Item, setInfoTag  # noqa: E402
from libs.ioOOo000OOO import menu  # noqa: E402
from libs.iooOO0OO import Trakt, Watched  # noqa: E402
xbmc.log('Palantir 3 PlanB: imports OK', xbmc.LOGINFO)

_ADDON_ID = 'plugin.video.palantir3'
_DB_ADDON = 'special://home/addons/plugin.video.palantir3/moria.cm3'
_DB_USER = 'special://profile/addon_data/script.module/settings.xml'


def _notify(message, error=False):
    try:
        icon = xbmcgui.NOTIFICATION_ERROR if error else xbmcgui.NOTIFICATION_INFO
        xbmcgui.Dialog().notification('Palantir 3', message, icon, 5000)
    except Exception:
        pass


def _db_exists():
    try:
        return os.path.isfile(xbmcvfs.translatePath(_DB_ADDON)) or os.path.isfile(
            xbmcvfs.translatePath(_DB_USER)
        )
    except Exception:
        return False


def _init():
    """Inicializacion minima: no toca la actualizacion Moria (URL muerta)."""
    xbmc.log('Palantir 3 PlanB: init DB_exists=%s' % _db_exists(), xbmc.LOGINFO)
    if _db_exists():
        return True
    _notify(localize(30053), True)
    xbmc.log('Palantir 3: no se encontro la BD Moria', xbmc.LOGERROR)
    return False


def _view_for(content):
    try:
        with Watched() as watched:
            view = watched.getView(content)
        if isinstance(view, int):
            return view
    except Exception:
        pass
    return 50


def _render(p3item, items):
    xbmc.log('Palantir 3 PlanB: render items=%s action=%s' % (len(items) if items else 0, p3item.action), xbmc.LOGINFO)
    if not items:
        return
    try:
        content = items[0].content or p3item.content or 'files'
    except Exception:
        content = p3item.content or 'files'
    view = _view_for(content)
    handle = int(sys.argv[1])
    directory = []
    breadcrumb = ''
    for item in items:
        try:
            if item.is_label() and view not in (50, 51, 55):
                breadcrumb = item.label or ''
                continue
            if item.is_label():
                continue
            label = item.label or item.title or ''
            li = xbmcgui.ListItem(label=label)
            if item.isPlayable:
                is_folder = False
            elif isinstance(item.isFolder, bool):
                is_folder = item.isFolder
            elif not item.action:
                is_folder = False
            else:
                is_folder = True
            setInfoTag(li, item)
            url = sys.argv[0] + '?' + item.tourl()
            directory.append((url, li, is_folder))
        except Exception:
            xbmc.log('Palantir 3: error renderizando item: %s' % traceback.format_exc(),
                     xbmc.LOGERROR)
    if directory:
        xbmcplugin.addDirectoryItems(handle, directory, len(directory))
        if breadcrumb:
            try:
                xbmcplugin.setProperty(handle, 'breadcrumbs_label', breadcrumb)
            except Exception:
                pass
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_NONE)
    xbmcplugin.setContent(handle, content)
    xbmcplugin.endOfDirectory(handle, True, cacheToDisc=False)
    if not ISESTUARYPALANTIR:
        try:
            xbmc.sleep(100)
            xbmc.executebuiltin('Container.SetViewMode(%s)' % view)
        except Exception:
            pass


def _dispatch(p3item):
    action = p3item.action
    xbmc.log('Palantir 3 PlanB: dispatch action=%s' % action, xbmc.LOGINFO)
    if not action:
        if p3item.is_label():
            return
        p3item.action = 'menu'
        action = 'menu'
    module = __import__('libs.ioOOo000OOO', fromlist=[action])
    func = getattr(module, action)
    result = func(p3item)
    if isinstance(result, list) and result:
        _render(p3item, result)


def _reload(arg, state):
    """Procesa ?reload=... Devuelve False si hay que salir."""
    parts = arg[1:].split('&')
    for part in parts[1:]:
        key, _, value = part.partition('=')
        if key == 'debrid_pin':
            xbmc.executebuiltin('SendClick(10140,28)')
            if value == 'alldebrid':
                keys = ['Alldebrid_apikey']
            elif value == 'realdebrid':
                keys = ['Realdebrid_token', 'Realdebrid_refresh_token',
                        'Realdebrid_client_id', 'Realdebrid_client_secret']
            elif value == 'debridlink':
                keys = ['DebridLink_access_token', 'DebridLink_refresh_token']
            else:
                keys = []
            for k in keys:
                set_setting(k, '')
            return False
        if key == 'trakt_pin':
            xbmc.executebuiltin('SendClick(10140,28)')
            xbmc.sleep(500)
            Trakt().authenticationDevices()
            return False
        if key == 'reset_cache':
            CACHE.clear('all')
            _notify('Cache reiniciada')
            return False
        if key == 'reset_watched':
            Watched().clear()
            _notify('Reiniciando la sincronizacion con trakt.tv')
            t = threading.Thread(target=Trakt().syncToTrakt)
            t.daemon = True
            t.start()
            return False
        if key == 'resumable':
            state['resumable'] = (value == 'true')
            continue
        if key == 'limit':
            try:
                state['limit'] = int(value)
            except Exception:
                pass
            continue
        if key == 'update':
            _init()
            return False
        if key == 'searchYou':
            from libs.ioiiiiiiI import searchYou
            searchYou()
            return False
        if key == 'contextMenu' and value:
            from urllib.parse import unquote
            from libs.ioI11Ii1i import ContextMenu
            ContextMenu(unquote(value).replace('plugin://plugin.video.palantir3/?', '')).show()
            return False
        if key == 'addRating' and len(value.split('_')) == 3:
            content, label, rating = value.split('_')
            Trakt().addRatings(content, label, rating, forzado=True)
            return False
        if key == 'findByActor' and len(value.split('_')) == 2:
            actor_id, content = value.split('_')
            xbmc.executebuiltin('Dialog.Close(movieinformation,force)')
            sys.argv[2] = P3Item(
                action='listado_content_actor', content=content, actorID=actor_id
            ).tourl()
            return True
    return True


def _main_menu_item():
    content = 'files' if not xbmc.getSkinDir().startswith('skin.estuary') else 'albums'
    return P3Item(
        icon='special://home/addons/plugin.video.palantir3/icon.png',
        fanart='special://home/addons/plugin.video.palantir3/fanart.gif',
        content=content,
        sql='select label,action,icon,sql,fanart from menus where menu_id = 10 ORDER by item_id asc',
    )


def main():
    xbmc.log('Palantir 3 PlanB: main argv=%s' % (sys.argv,), xbmc.LOGINFO)
    if KODI_VERSION < 19:
        xbmcgui.Dialog().ok('Palantir 3', localize(30057))
        return
    if len(sys.argv) <= 2 or not sys.argv[2] or sys.argv[2] == '?':
        p3item = _main_menu_item()
        _init()
        _dispatch(p3item)
        return
    arg = sys.argv[2]
    state = {'resumable': False, 'limit': None}
    if arg.startswith('?reload='):
        if not _reload(arg, state):
            return
        arg = sys.argv[2]
        if arg.startswith('?reload=') or arg == '?':
            return
    p3item = P3Item().fromurl(arg)
    if state['limit'] is not None:
        p3item.limitItemList = state['limit']
    elif not p3item.limitItemList:
        p3item.limitItemList = get_setting('limitItemList')
    if not _init():
        return
    _dispatch(p3item)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        xbmc.log('Palantir 3: error fatal:\n%s' % traceback.format_exc(), xbmc.LOGERROR)
        _notify('Error en Palantir 3. Revisa kodi.log', True)
