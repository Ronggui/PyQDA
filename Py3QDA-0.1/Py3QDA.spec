# -*- mode: python -*-

block_cipher = None


a = Analysis(['Py3QDA/Py3QDA.py'],
             pathex=['/Users/rghuang/Documents/Works/教学资料/localGit/PyQDA/Py3QDA-0.1'],
             binaries=[],
             datas=[('/Users/rghuang/Documents/Works/教学资料/localGit/PyQDA/Py3QDA-0.1/Py3QDA/*.py', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Py3QDA',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Py3QDA')
