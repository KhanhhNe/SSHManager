import os

import PyInstaller.__main__

# Can be replaced with any lib
import flask

packages_path = flask.__file__
while not packages_path.endswith('site-packages'):
    packages_path = os.path.dirname(packages_path)


PyInstaller.__main__.run([
    'main.py', '--name=SSHManager', '--onedir', '--noconfirm', '--clean',
    '--add-data=templates;templates', '--add-binary=controllers/*.exe;controllers',
    f'--paths={packages_path}',
    '--hidden-import=engineio.async_drivers.threading'
])
