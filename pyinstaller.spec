# -*- mode: python ; coding: utf-8 -*-


import os
import sys
from kivy.tools.packaging.pyinstaller_hooks import (
    get_deps_all, hookspath, runtime_hooks)
import kivymd

block_cipher = None
kivymd_path = os.path.dirname(kivymd.__file__)
sys.path.insert(0, kivymd_path)

# from kivy_deps import sdl2, glew
# from kivymd.tools.packaging.pyinstaller import hooks_path as kivymd_hooks_path, datas as kivymd_datas
from kivymd import hooks_path as kivymd_hooks_path

kivydeps = get_deps_all()
print('Hookspath:',hookspath())
print('Runtime hooks:', runtime_hooks())
print('KivyMD hooks:', kivymd_hooks_path)

a = Analysis(["bin/logo"],
             pathex=[os.path.abspath("."), kivymd_path],
             binaries=kivydeps["binaries"] + [],
             datas=[("assets/", "assets/")],
             hiddenimports=kivydeps["hiddenimports"] + [],
             hookspath=hookspath() + [kivymd_hooks_path],
             runtime_hooks=runtime_hooks() + [],
             excludes=kivydeps["excludes"] + ["_tkinter", "Tkinter", "enchant", "twisted"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [], # *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
          name="logo",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name="Logo.app",
             icon=None,
             bundle_identifier=None)
