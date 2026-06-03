# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

# Collect everything from the nice package
datas, binaries, hiddenimports = collect_all("nice")

hiddenimports += collect_submodules("nice") + [
    "importlib.util",
    "importlib.metadata",
    "pydantic",
    "pydantic_settings",
    "typer",
    "rich",
    "httpx",
    "difflib",
    "subprocess",
    "threading",
]

a = Analysis(
    ["_entry.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter", "turtle", "curses",
        "unittest", "test", "tests",
        "email", "html.parser", "http.server",
        "xmlrpc", "xml.etree",
        "multiprocessing",
        "numpy", "pandas", "scipy", "matplotlib", "PIL",
        "setuptools", "pkg_resources",
        "IPython", "jupyter",
        "sqlite3",
        "ssl",  # httpx bundles its own
    ],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="nice",
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
    icon=None,
)
