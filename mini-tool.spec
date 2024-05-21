# -*- mode: python ; coding: utf-8 -*-
from PyInstaller import HOMEPATH

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[(f'{HOMEPATH}/wx/WebView2Loader.dll', '.')],
    datas=[('./static/datasets', 'pyecharts/datasets/'), ('./static/templates', 'pyecharts/render/templates/'), ('./static/js', 'static/js/')],
    hiddenimports=[],
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
    name='mini-tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['static\\icon.png','static\\icon.png'],
)
