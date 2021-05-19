import os
import shutil
import zipfile

import PyInstaller.__main__

# Can be replaced with any lib
import flask

packages_path = flask.__file__
while not packages_path.endswith('site-packages'):
    packages_path = os.path.dirname(packages_path)


PyInstaller.__main__.run([
    'main.py', '--name=SSHManager', '--icon=logo.ico', '--onedir', '--noconfirm', '--clean',
    '--add-data=templates;templates',
    '--add-binary=controllers/*.exe;controllers', '--add-binary=logo.ico;.',
    f'--paths={packages_path}',
    '--hidden-import=engineio.async_drivers.threading'
])

print("Removing build folder...")
shutil.rmtree('build')
print("Zipping files...")
built_file = zipfile.ZipFile('SSHManager.zip', 'w')

for folder, subfolders, filenames in os.walk(r'dist\SSHManager'):
    for filename in filenames:
        filepath = os.path.join(folder, filename)
        print(f"Zipping {filepath}")
        built_file.write(filepath, os.path.basename(filepath))

built_file.close()
print("Removing dist folder...")
shutil.rmtree('dist')
print("Done! Happy distributing!")
