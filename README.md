PyBitmessage-Daemon
===================

PyBitmessage Daemon Client allows users to interact with Bitmessage through the command line. Bitmessage can be found here: https://github.com/Bitmessage/PyBitmessage

It allows you to interact with Bitmessage via the api which unforatunately (as of Bitmessage version 0.3.5) is limited.

Bitmessage API Reference: https://bitmessage.org/wiki/API_Reference

Please make sure that you are using Python 2.7.5+ or if you would like to download Daemon.exe you can do that on my site here: http://addictronics.com/bitmessage.php Just scroll down to the Daemon section.

Setup
=====
1. Install PyBitmessage and run it once. Close Bitmessage.
2. Download daemon.py into the same directory as Bitmessage.
3. Run Bitmessage.
4. Run daemon.py and it will either: automatically pull your API information from the keys.dat file or ask if you want to automatically add the API information to the keys.dat file.
5. Test the API connection with the command "apiTest".


Features
=====
1. Change bitmessage settings (keys.dat) including setting api information, connection information, and daemon mode
2. Send and receive messages or broadcasts with or without attachments
3. Reply to or forward messages
2. View the inbox/outbox
3. Save inbox/outbox messages to txt file
4. Create new identites
5. Subscribe to/unsubscribe from broadcast addresses
6. Get addresss from a passphrase without adding to identities
7. Delete individual or all messages from the inbox or outbox
