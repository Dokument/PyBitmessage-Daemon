PyBitmessage-Daemon
===================

PyBitmessage Daemon Client allows users to interact with PyBitmessage through the command line. PyBitmessage can be found here: https://github.com/Bitmessage/PyBitmessage

It allows you to interact with PyBitmessage via the api which unforatunately (as of PyBitmessage version 0.3.0) is limited.


Setup
=====
1. Install PyBitmessage and run it once. Close PyBitmessage.
2. Note:If you are running bitmessage in portable mode, please move Daemon.py into the same directory as PyBitmessage
3. Run PyBitmessage.
4. Run daemon.py and it will either: automatically pull your API information from the keys.dat file or ask if you want to automatically add the API information to the keys.dat file.
5. Test the API connection with the command "apiTest".
