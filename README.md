PyBitmessage-Daemon
===================

PyBitmessage Daemon Client allows users to interact with Bitmessage through the command line. Bitmessage can be found here: https://github.com/Bitmessage/PyBitmessage

It allows you to interact with Bitmessage via the api which unforatunately (as of Bitmessage version 0.3.0) is limited.

Please make sure that you are using Python 2.7.x

Setup
=====
1. Install PyBitmessage and run it once. Close Bitmessage.
2. Download daemon.py into the same directory as Bitmessage.
3. Run Bitmessage.
4. Run daemon.py and it will either: automatically pull your API information from the keys.dat file or ask if you want to automatically add the API information to the keys.dat file.
5. Test the API connection with the command "apiTest".
