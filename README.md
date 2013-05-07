PyBitmessage-Daemon
===================

PyBitmessage Daemon Client allows users to interact with PyBitmessage while daemon = true

It allows you to interact with PyBitmessage via the api which unforatunately (as of PyBitmessage version 0.3.0) is limited.


Setup
=====
1. Install PyBitmessage and run it once. Close PyBitmessage.
2. Navigate to the keys.dat file and fill in the appropriate API information (https://bitmessage.org/wiki/API_Reference)
3. Run Pybitmessage.
4. Run Daemon.py and it will automatically pull your API information from the keys.dat file.
5. Test the API connection with the command "apiTest"
