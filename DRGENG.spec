# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['server.py'],
    pathex=[],
    binaries=[],
    datas=[('static', 'static'), ('templates', 'templates'), ('prompts.py', '.'), ('lessons.py', '.'), ('placement.py', '.'), ('database.py', '.'), ('ai.py', '.'), ('tts.py', '.'), ('config.py', '.'), ('app.py', '.')],
    hiddenimports=['flask', 'jinja2', 'openai', 'edge_tts', 'pywebview', 'sqlite3', 'aiohttp'],
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
    name='DRGENG',
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
    icon=r'C:\Users\Vladimir Kamashev\Desktop\Mod\app.ico',
)
