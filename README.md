﻿# SSHManager

(This version is deprecated, use https://github.com/KhanhhNe/sshmanager-2.0.0)

An open source tool to manage & use SSH.

Features
----
- **Multi-threaded SSH checking**, real-time status update, quick CSV export
- **Multi-port SSH port forwarding**, control panel with port SSH resetting functionality, real-time status update, per-port forwarded IP for better managing
- **Multi-device support** - control and manage easier with Web interface, allowing both Desktop and Mobile access in the same network
- **Programming API interface included**, ranging from HTTP requests to Python programming interface, simple and powerful

Give me a star if you find this project useful and open an issue if you find any bugs. I'll be happy to help you out!

Usage
----
Download the latest release, run SSHManager.exe and a new browser tab will open with the web server URL. You can navigate to that URL on other devices from the same network to access the web interface, too!

Creating your own SSHManager
----
Main SSH operations are in `bitvise.py`. To create your own, see the examples of usage in `examples` folder. To use it in your application, copy `bitvise.py`, `stnlc.exe` and all DLL files in `examples` folder to your project, import them and use as described in example codes.

Building your own
----
Doing this requires `Windows 8.1+`, `Python 3.9.5` so make sure to install them first to proceed to next steps.
Clone the repository
```bash
https://github.com/KhanhhNe/SSHManager.git
cd SSHManager
```
Install needed libraries
```bash
pip install -r requirements.txt
```
Run the build script
```bash
python build.py
```
A new file named `SSHManager.zip` will be generated. It is ready to be distributed!



> Written with [StackEdit](https://stackedit.io/).
