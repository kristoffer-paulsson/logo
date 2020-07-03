#! python

import os
import sys
from kivy.tools.packaging.pyinstaller_hooks import (
    get_deps_all, hookspath, runtime_hooks)
import kivymd

block_cipher = None
path = os.path.abspath(".")
bin_path = os.path.join(path, 'bin', 'prod')
lib_path = os.path.join(path, 'lib', 'logo')
sys.path.insert(0, lib_path)
kivymd_path = os.path.dirname(kivymd.__file__)
sys.path.insert(0, kivymd_path)

from kivy_deps.sdl2 import dep_bins as sdl2_dep_bins
from kivy_deps.glew import dep_bins as glew_dep_bins
from kivymd import hooks_path as kivymd_hooks_path

kivydeps = get_deps_all()

a = Analysis([bin_path],
             pathex=[kivymd_path],
             binaries=kivydeps["binaries"] + [],
             datas=[("assets/", "assets/")],
             hiddenimports=kivydeps["hiddenimports"] + ["kivymd.toast", "logo", "logo.main"],
             hookspath=hookspath() + [kivymd_hooks_path],
             runtime_hooks=runtime_hooks() + [],
             excludes=kivydeps["excludes"] + ["_tkinter", "Tkinter", "enchant", "twisted"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=True)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name="logo",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False )
app = BUNDLE(exe,
             name="LogoMessenger.app",
             icon="assets/icons/dove.icns",
             bundle_identifier=None,
             info_plist={
                'NSHighResolutionCapable': 'True'
                })