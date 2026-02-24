# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for building a single .exe.

Project layout:
  client/  - Angular app (build output: client/dist/my-first-angular-app/browser)
  server/  - Flask backend (server.py, manifest.json, build files)

Build: Run from project root: python server/build.py
Output: dist/AppStore.exe
"""

import os

# Run from project root; cwd = project root
SPEC_DIR = os.getcwd()

def _resolve_datas():
    datas = [
        (os.path.join(SPEC_DIR, 'server', 'manifest.json'), '.'),
    ]
    angular_candidates = [
        (os.path.join(SPEC_DIR, 'client', 'dist', 'my-first-angular-app', 'browser'), 'ui/dist'),
        (os.path.join(SPEC_DIR, 'client', 'dist', 'browser'), 'ui/dist'),
        (os.path.join(SPEC_DIR, 'client', 'dist'), 'ui/dist'),
    ]
    for src, dest in angular_candidates:
        index_path = os.path.join(src, 'index.html')
        if os.path.isdir(src) and os.path.exists(index_path):
            datas.append((src, dest))
            break
    downloads_src = os.path.join(SPEC_DIR, 'server', 'downloads')
    if os.path.isdir(downloads_src):
        datas.append((downloads_src, 'downloads'))
    return datas

a = Analysis(
    [os.path.join(SPEC_DIR, 'server', 'server.py')],
    pathex=[SPEC_DIR, os.path.join(SPEC_DIR, 'server')],
    binaries=[],
    datas=_resolve_datas(),
    hiddenimports=[
        'flask', 'flask_cors', 'werkzeug', 'werkzeug.routing',
        'werkzeug.serving', 'werkzeug.wrappers', 'jinja2', 'markupsafe',
        'click', 'itsdangerous',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AppStore',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
