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
    '--add-binary=logo.ico;.', '--add-binary=bitvise_ssh/*;bitvise_ssh',
    f'--paths={packages_path}',
    '--hidden-import=engineio.async_drivers.threading'
])

print("Removing build folder...")
shutil.rmtree('build')
print("Zipping files...")
built_file = zipfile.ZipFile('SSHManager.zip', 'w')

os.chdir('dist')
for folder, _, filenames in os.walk(r'SSHManager'):
    for filename in filenames:
        filepath = os.path.join(folder, filename)
        print(f"Zipping {filepath}")
        built_file.write(filepath)
os.chdir('..')

built_file.close()
print("Removing dist folder...")
shutil.rmtree('dist')
os.remove('SSHManager.spec')
print("Done! Happy distributing!")
