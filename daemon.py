#!/usr/bin/env python2.7.x
# Created by Adam Melton (.dok) referenceing https://bitmessage.org/wiki/API_Reference for API documentation
# Distributed under the MIT/X11 software license. See http://www.opensource.org/licenses/mit-license.php.

# This is an example of a daemon client for PyBitmessage 0.3.5, by .dok (Version 0.2.2)


import ConfigParser
import xmlrpclib
import datetime
import hashlib
import getopt
import json
import time
import sys
import os

api = ''
keysPath = 'keys.dat'
usrPrompt = 0 #0 = First Start, 1 = prompt, 2 = no prompt if the program is starting up

def restartBmNotify(): #Prompts the user to restart Bitmessage. 
    print ' '
    print '***********************************************************'
    print 'WARNING: If Bitmessage is running, you must restart it now.'
    print '***********************************************************'
    print ' '

def safeConfigGetBoolean(section,field):
    global keysPath
    config = ConfigParser.SafeConfigParser()
    config.read(keysPath)
    
    try:
        return config.getboolean(section,field)
    except:
        return False

#Begin keys.dat interactions
def lookupAppdataFolder(): #gets the appropriate folders for the .dat files depending on the OS. Taken from bitmessagemain.py
    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            print 'Could not find home folder, please report this message and your OS X version to the Daemon Github.'
            os.exit()

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = path.join(environ['APPDATA'], APPNAME) + '\\'
    else:
        dataFolder = path.expanduser(path.join("~", ".config/" + APPNAME + "/"))
    return dataFolder

def apiInit(apiEnabled):
    global keysPath
    config = ConfigParser.SafeConfigParser()
    config.read(keysPath)

    
    if (apiEnabled == False): #API information there but the api is disabled.
        uInput = raw_input("The API is not enabled. Would you like to do that now?(y/n):")

        if uInput == "y": #
            config.set('bitmessagesettings','apienabled','true') #Sets apienabled to true in keys.dat
            with open(keysPath, 'wb') as configfile:
                config.write(configfile)
                
            print 'Done'
            restartBmNotify()
            return True
            
        elif uInput == "n":
            print ' '
            print '************************************************************'
            print 'daemon will not work when the API is disabled.'
            print 'Please refer to the Bitmessage Wiki on how to setup the API.'
            print '************************************************************'
            print ' '
            usrPrompt = 1
            main()
            
        else:
            print 'Invalid entry'
            usrPrompt = 1
            main()
    elif (apiEnabled == True): #API correctly setup
        #Everything is as it should be
        return True
    
    else: #API information was not present.
        print 'keys.dat not properly configured!'
        uInput = raw_input("Would you like to do this now?(y/n):")

        if uInput == "y": #User said yes, initalize the api by writing these values to the keys.dat file
            print '-----------------------------------'
            apiUsr = raw_input("API Username:")
            apiPwd = raw_input("API Password:")
            apiPort = raw_input("API Port:")
            print '-----------------------------------'
                
            config.set('bitmessagesettings','apienabled','true')
            config.set('bitmessagesettings', 'apiport', apiPort)
            config.set('bitmessagesettings', 'apiinterface', '127.0.0.1')
            config.set('bitmessagesettings', 'apiusername', apiUsr)
            config.set('bitmessagesettings', 'apipassword', apiPwd)
            with open(keysPath, 'wb') as configfile:
                config.write(configfile)
            
            print 'Finished configuring the keys.dat file with API information.'
            restartBmNotify()
            return True
        
        elif uInput == "n":
            print ' '
            print '***********************************************************'
            print 'Please refer to the Bitmessage Wiki on how to setup the API.'
            print '***********************************************************'
            print ' '
            usrPrompt = 1
            main()
        elif uInput == "exit":
            usrPrompt = 1
            main()
        else:
            print 'Invalid entry'
            usrPrompt = 1
            main()


def apiData():
    global keysPath
    
    config = ConfigParser.SafeConfigParser()
    keysPath = 'keys.dat'
    
    config.read(keysPath) #First try to load the config file (the keys.dat file) from the program directory

    try:
        config.get('bitmessagesettings','settingsversion')
        appDataFolder = ''
    except:
        #Could not load the keys.dat file in the program directory. Perhaps it is in the appdata directory.
        appDataFolder = lookupAppdataFolder()
        keysPath = appDataFolder + 'keys.dat'
        config = ConfigParser.SafeConfigParser()
        config.read(keysPath)

        try:
            config.get('bitmessagesettings','settingsversion')
        except:
            #keys.dat was not there either, something is wrong.
            print ' '
            print '******************************************************************'
            print 'There was a problem trying to access the Bitmessage keys.dat file.'
            print 'Make sure that daemon is in the same directory as Bitmessage.'
            print '******************************************************************'
            print ' '
            usrPrompt = 1
            main()

    try: #checks to make sure that everyting is configured correctly. Excluding apiEnabled, it is checked after
        config.get('bitmessagesettings', 'apiport')
        config.get('bitmessagesettings', 'apiinterface')
        config.get('bitmessagesettings', 'apiusername')
        config.get('bitmessagesettings', 'apipassword')
    except:
        apiInit("") #Initalize the keys.dat file with API information

    #keys.dat file was found or appropriately configured, allow information retrieval
    apiEnabled = apiInit(safeConfigGetBoolean('bitmessagesettings','apienabled')) #if false it will prompt the user, if true it will return true

    config.read(keysPath)#read again since changes have been made
    apiPort = int(config.get('bitmessagesettings', 'apiport'))
    apiInterface = config.get('bitmessagesettings', 'apiinterface')
    apiUsername = config.get('bitmessagesettings', 'apiusername')
    apiPassword = config.get('bitmessagesettings', 'apipassword')
    
    print 'API data successfully imported.'
    print ' '
    return "http://" + apiUsername + ":" + apiPassword + "@" + apiInterface+ ":" + str(apiPort) + "/" #Build the api credentials
#End keys.dat interactions

def apiTest(): #Tests the API connection to bitmessage. Returns true if it is connected.
    if (api.add(2,3) == 5):
        return True
    else:
        return False

def bmSettings(): #Allows the viewing and modification of keys.dat settings. 
    global keysPath
    global usrPrompt
    config = ConfigParser.SafeConfigParser()
    keysPath = 'keys.dat'
    
    config.read(keysPath)#Read the keys.dat

    port = config.get('bitmessagesettings', 'port')
    startonlogon = config.get('bitmessagesettings', 'startonlogon')
    minimizetotray = config.get('bitmessagesettings', 'minimizetotray')
    showtraynotifications = config.get('bitmessagesettings', 'showtraynotifications')
    startintray = config.get('bitmessagesettings', 'startintray')
    defaultnoncetrialsperbyte = config.get('bitmessagesettings', 'defaultnoncetrialsperbyte')
    defaultpayloadlengthextrabytes = config.get('bitmessagesettings', 'defaultpayloadlengthextrabytes')

    socksproxytype = config.get('bitmessagesettings', 'socksproxytype')
    sockshostname = config.get('bitmessagesettings', 'sockshostname')
    socksport = config.get('bitmessagesettings', 'socksport')
    socksauthentication = config.get('bitmessagesettings', 'socksauthentication')
    socksusername = config.get('bitmessagesettings', 'socksusername')
    sockspassword = config.get('bitmessagesettings', 'sockspassword')


    print ' '
    print '-----------------------------------'
    print 'Current Bitmessage Settings:'
    print 'port = ' + port
    print 'startonlogon = ' + startonlogon
    print 'minimizetotray = ' + minimizetotray
    print 'showtraynotifications = ' + showtraynotifications
    print 'startintray = ' + startintray
    print 'defaultnoncetrialsperbyte = ' + defaultnoncetrialsperbyte
    print 'defaultpayloadlengthextrabytes = ' + defaultpayloadlengthextrabytes
    print ' '
    print 'Current Connection Settings:'
    print 'socksproxytype = ' + socksproxytype
    print 'sockshostname = ' + sockshostname
    print 'socksport = ' + socksport
    print 'socksauthentication = ' + socksauthentication
    print 'socksusername = ' + socksusername
    print 'sockspassword = ' + sockspassword
    print '-----------------------------------'
    print ' '

    uInput = raw_input("Would you like to modify any of these settings?(y/n):")
    
    if uInput == "y":
        while True: #loops if they mistype the setting name, they can exit the loop with 'exit'
            invalidInput = False
            uInput = raw_input("What setting would you like to modify? :")
            print ' '

            if uInput == "port":
                print 'Current port number: ' + port
                uInput = raw_input("New port:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'port', str(uInput))
            elif uInput == "startonlogon":
                print 'Current status: ' + startonlogon
                uInput = raw_input("New status:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'startonlogon', str(uInput))
            elif uInput == "minimizetotray":
                print 'Current status: ' + minimizetotray
                uInput = raw_input("New status:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'minimizetotray', str(uInput))
            elif uInput == "showtraynotifications":
                print 'Current status: ' + showtraynotifications
                uInput = raw_input("New status:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'showtraynotifications', str(uInput))
            elif uInput == "startintray":
                print 'Current status: ' + startintray
                uInput = raw_input("New status:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'startintray', str(uInput))
            elif uInput == "defaultnoncetrialsperbyte":
                print 'Current default nonce trials per byte: ' + defaultnoncetrialsperbyte
                uInput = raw_input("New defaultnoncetrialsperbyte:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'defaultnoncetrialsperbyte', str(uInput))
            elif uInput == "defaultpayloadlengthextrabytes":
                print 'Current default payload length extra bytes: ' + defaultpayloadlengthextrabytes
                uInput = raw_input("New defaultpayloadlengthextrabytes:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'defaultpayloadlengthextrabytes', str(uInput))
            elif uInput == "socksproxytype":
                print 'Current socks proxy type: ' + socksproxytype
                print "Possibilities: 'none', 'SOCKS4a', 'SOCKS5'."
                uInput = raw_input("New socksproxytype:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'socksproxytype', str(uInput))
            elif uInput == "sockshostname":
                print 'Current socks host name: ' + sockshostname
                uInput = raw_input("New sockshostname:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'sockshostname', str(uInput))
            elif uInput == "socksport":
                print 'Current socks port number: ' + socksport
                uInput = raw_input("New socksport:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'socksport', str(uInput))
            elif uInput == "socksauthentication":
                print 'Current status: ' + socksauthentication
                uInput = raw_input("New status:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'socksauthentication', str(uInput))
            elif uInput == "socksusername":
                print 'Current socks username: ' + socksusername
                uInput = raw_input("New socksusername:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'socksusername', str(uInput))
            elif uInput == "sockspassword":
                print 'Current socks password: ' + sockspassword
                uInput = raw_input("New password:")
                if uInput == 'exit':
                    usrPrompt = 1
                    main()
                else:
                    config.set('bitmessagesettings', 'sockspassword', str(uInput))
            elif uInput == "exit":
                usrPrompt = 1
                break
            else:
                print "Invalid input. Please try again."
                invalidInput = True
                
            if invalidInput != True: #don't prompt if they made a mistake. 
                uInput = raw_input("Would you like to change another setting?(y/n):")

                if uInput != "y":
                    print 'Changes Made.'
                    with open(keysPath, 'wb') as configfile:
                        config.write(configfile)
                    restartBmNotify()
                    break
                
            
    elif uInput == "n":
        usrPrompt = 1
        main()
    elif uInput == "exit":
        usrPrompt = 1
        main()
    else:
        print "Invalid input."
        usrPrompt = 1
        main()
    
#Begin BM address verifiication

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def decodeBase58(string, alphabet=ALPHABET): #Taken from addresses.py
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0

    try:
        power = strlen - 1
        for char in string:
            num += alphabet.index(char) * (base ** power)
            power -= 1
    except:
        #character not found (like a space character or a 0)
        return 0
    return num

def decodeAddress(address):
    #returns true if valid, false if not a valid address. - taken from addresses.py

    address = str(address).strip()

    if address[:3] == 'BM-':
        integer = decodeBase58(address[3:])
    else:
        integer = decodeBase58(address)
        
    if integer == 0:
        #print 'invalidcharacters' Removed because it appears in regular sendMessage
        return False
    #after converting to hex, the string will be prepended with a 0x and appended with a L
    hexdata = hex(integer)[2:-1]

    if len(hexdata) % 2 != 0:
        hexdata = '0' + hexdata

    #print 'hexdata', hexdata

    data = hexdata.decode('hex')
    checksum = data[-4:]

    sha = hashlib.new('sha512')
    sha.update(data[:-4])
    currentHash = sha.digest()
    #print 'sha after first hashing: ', sha.hexdigest()
    sha = hashlib.new('sha512')
    sha.update(currentHash)
    #print 'sha after second hashing: ', sha.hexdigest()

    if checksum != sha.digest()[0:4]:
        print 'checksumfailed'
        return False

    return True
#End BM address verifiication

def getAddress(passphrase,vNumber,sNumber):
    passphrase = passphrase.encode('base64')#passphrase must be encoded

    return api.getDeterministicAddress(passphrase,vNumber,sNumber)

def subscribe():
    global usrPrompt

    while True:
        address = raw_input("Address to subscribe to:")

        if (address == "c"):
                usrPrompt = 1
                print ' '
                main()
        elif (decodeAddress(address)== False):
            print 'Invalid. "c" to cancel. Please try again.'
        else:
            break
    
    label = raw_input("Label for this address:")
    label = label.encode('base64')
    
    api.addSubscription(address,label)
    print ' '
    print ('You are now subscribed to: ' + address)
    print ' '

def unsubscribe():
    global usrPrompt
    
    while True:
        address = raw_input("Address to unsubscribe from:")

        if (address == "c"):
                usrPrompt = 1
                print ' '
                main()
        elif (decodeAddress(address)== False):
            print 'Invalid. "c" to cancel. Please try again.'
        else:
            break
    
    
    uInput = raw_input("Are you sure?(y/n):")
    
    api.deleteSubscription(address)
    print ' '
    print ('You are now unsubscribed from: ' + address)
    print ' '

def listSubscriptions():
    #jsonAddresses = json.loads(api.listSubscriptions())
    #numAddresses = len(jsonAddresses['addresses']) #Number of addresses
    print ' '
    print 'Label, Address, Enabled'
    print ' '
    print api.listSubscriptions()
    '''for addNum in range (0, numAddresses): #processes all of the addresses and lists them out
        label = jsonAddresses['addresses'][addNum]['label']
        address = jsonAddresses['addresses'][addNum]['address']
        enabled = jsonAddresses['addresses'][addNum]['enabled']

        print label, address, enabled
    '''
    print ' '


def listAdd(): #Lists all of the addresses and their info
    jsonAddresses = json.loads(api.listAddresses())
    numAddresses = len(jsonAddresses['addresses']) #Number of addresses
    print ' '
    print 'Address Number,Label,Address,Stream,Enabled'
    print ' '

    for addNum in range (0, numAddresses): #processes all of the addresses and lists them out
        label = jsonAddresses['addresses'][addNum]['label']
        address = jsonAddresses['addresses'][addNum]['address']
        stream = jsonAddresses['addresses'][addNum]['stream']
        enabled = jsonAddresses['addresses'][addNum]['enabled']

        print addNum, label, address, stream, enabled

    print ' '

def genAdd(lbl,deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe): #Generate address
    if deterministic == False: #Generates a new address with the user defined label. non-deterministic
        addressLabel = lbl.encode('base64')
        return api.createRandomAddress(addressLabel)
    
    elif deterministic == True: #Generates a new deterministic address with the user inputs.
        passphrase = passphrase.encode('base64')
        return api.createDeterministicAddresses(passphrase, numOfAdd, addVNum, streamNum, ripe)
    else:
        return 'Entry Error'

def sendMsg(toAddress, fromAddress, subject, message): #With no arguments sent, sendMsg fills in the blanks. subject and message must be encoded before they are passed.
    if (decodeAddress(toAddress)== False):
        while True:
            toAddress = raw_input("To Address:")

            if (toAddress == "c"):
                usrPrompt = 1
                print ' '
                main()
            elif (decodeAddress(toAddress)== False):
                print 'Invalid. "c" to cancel. Please try again.'
            else:
                break
        
        
    if (decodeAddress(fromAddress)== False):
        jsonAddresses = json.loads(api.listAddresses())
        numAddresses = len(jsonAddresses['addresses']) #Number of addresses
        
        if (numAddresses > 1): #Ask what address to send from if multiple addresses
            found = False
            while True:
                print ' '
                fromAddress = raw_input("Enter an Address or Address Label to send from:")

                if fromAddress == "exit":
                    usrPrompt = 1
                    main()

                for addNum in range (0, numAddresses): #processes all of the addresses
                    label = jsonAddresses['addresses'][addNum]['label']
                    address = jsonAddresses['addresses'][addNum]['address']
                    #stream = jsonAddresses['addresses'][addNum]['stream']
                    #enabled = jsonAddresses['addresses'][addNum]['enabled']
                    if (fromAddress == label): #address entered was a label and is found
                        fromAddress = address
                        found = True
                        break
                
                if (found == False):
                    if(decodeAddress(fromAddress)== False):
                        print 'Invalid Address. Please try again.'
                    
                    else:
                        for addNum in range (0, numAddresses): #processes all of the addresses
                            #label = jsonAddresses['addresses'][addNum]['label']
                            address = jsonAddresses['addresses'][addNum]['address']
                            #stream = jsonAddresses['addresses'][addNum]['stream']
                            #enabled = jsonAddresses['addresses'][addNum]['enabled']
                            if (fromAddress == address): #address entered was a found in our addressbook.
                                found = True
                                break
                            
                        if (found == False):
                            print 'The address entered is not one of yours. Please try again.'
                
                if (found == True):
                    break #Address was found
        
        else: #Only one address in address book
            print 'Using the only address in the addressbook to send from.'
            fromAddress = jsonAddresses['addresses'][0]['address']

    if (subject == ''):
            subject = raw_input("Subject:")
            subject = subject.encode('base64')
    if (message == ''):
            message = raw_input("Message:")
            message = message.encode('base64')

    ackData = api.sendMessage(toAddress, fromAddress, subject, message)
    print 'The ackData is: ', ackData #.decode("hex")
    print ' '


def sendBrd(fromAddress, subject, message): #sends a broadcast
    if (fromAddress == ''):
        jsonAddresses = json.loads(api.listAddresses())
        numAddresses = len(jsonAddresses['addresses']) #Number of addresses
        
        if (numAddresses > 1): #Ask what address to send from if multiple addresses
            found = False
            while True:
                print ' '
                fromAddress = raw_input("Enter an Address or Address Label to send from:")

                if fromAddress == "exit":
                    usrPrompt = 1
                    main()

                for addNum in range (0, numAddresses): #processes all of the addresses
                    label = jsonAddresses['addresses'][addNum]['label']
                    address = jsonAddresses['addresses'][addNum]['address']
                    #stream = jsonAddresses['addresses'][addNum]['stream']
                    #enabled = jsonAddresses['addresses'][addNum]['enabled']
                    if (fromAddress == label): #address entered was a label and is found
                        fromAddress = address
                        found = True
                        break
                
                if (found == False):
                    if(decodeAddress(fromAddress)== False):
                        print 'Invalid Address. Please try again.'
                    
                    else:
                        for addNum in range (0, numAddresses): #processes all of the addresses
                            #label = jsonAddresses['addresses'][addNum]['label']
                            address = jsonAddresses['addresses'][addNum]['address']
                            #stream = jsonAddresses['addresses'][addNum]['stream']
                            #enabled = jsonAddresses['addresses'][addNum]['enabled']
                            if (fromAddress == address): #address entered was a found in our addressbook.
                                found = True
                                break
                            
                        if (found == False):
                            print 'The address entered is not one of yours. Please try again.'
                
                if (found == True):
                    break #Address was found
        
        else: #Only one address in address book
            print 'Using the only address in the addressbook to send from.'
            fromAddress = jsonAddresses['addresses'][0]['address']

    if (subject == ''):
            subject = raw_input("Subject:")
            subject = subject.encode('base64')
    if (message == ''):
            message = raw_input("Message:")
            message = message.encode('base64')

    ackData = api.sendBroadcast(fromAddress, subject, message)
    print 'The ackData is: ', ackData #.decode("hex")
    print ' '

def inbox(): #Lists the messages by: Message Number, To Address Label, From Address Label, Subject, Received Time)
    inboxMessages = json.loads(api.getAllInboxMessages())
    numMessages = len(inboxMessages['inboxMessages'])
    print ' '

    for msgNum in range (0, numMessages): #processes all of the messages in the inbox
        print '-----------------------------------'
        print ' '
        print 'Message Number:',msgNum #Message Number
        print 'To:', inboxMessages['inboxMessages'][msgNum]['toAddress'] #Get the to address
        print 'From:', inboxMessages['inboxMessages'][msgNum]['fromAddress'] #Get the from address
        print 'Subject:', inboxMessages['inboxMessages'][msgNum]['subject'].decode('base64') #Get the subject
        print 'Received:', datetime.datetime.fromtimestamp(float(inboxMessages['inboxMessages'][msgNum]['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
        print ' '
        
        '''if (inboxMessages['inboxMessages'][msgNum]['read'] == 0):
            print 'Unread'
        else:
            print 'Read'
        print ' '
        '''
    print 'There are ',numMessages,' messages in the inbox.'
    print '-----------------------------------'
    print ' '

def outbox():
    outboxMessages = json.loads(api.getAllSentMessages())
    numMessages = len(outboxMessages['sentMessages'])
    print numMessages
    print ' '

    for msgNum in range (0, numMessages): #processes all of the messages in the outbox
        print '-----------------------------------'
        print ' '
        print 'Message Number:',msgNum #Message Number
        #print 'Message ID:', outboxMessages['sentMessages'][msgNum]['msgid']
        print 'To:', outboxMessages['sentMessages'][msgNum]['toAddress'] #Get the to address
        print 'From:', outboxMessages['sentMessages'][msgNum]['fromAddress'] #Get the from address
        print 'Subject:', outboxMessages['sentMessages'][msgNum]['subject'].decode('base64') #Get the subject
        print 'Status:', outboxMessages['sentMessages'][msgNum]['status'] #Get the subject
        
        print 'Last Action Time:', datetime.datetime.fromtimestamp(float(outboxMessages['sentMessages'][msgNum]['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')
        print ' '
    print 'There are ',numMessages,' messages in the outbox.'
    print '-----------------------------------'
    print ' '

def readMsg(msgNum): #Opens a message for reading
    
    inboxMessages = json.loads(api.getAllInboxMessages())
    print ' '
    print 'To:', inboxMessages['inboxMessages'][msgNum]['toAddress'] #Get the to address
    print 'From:', inboxMessages['inboxMessages'][msgNum]['fromAddress'] #Get the from address
    print 'Subject:', inboxMessages['inboxMessages'][msgNum]['subject'].decode('base64') #Get the subject
    print datetime.datetime.fromtimestamp(float(inboxMessages['inboxMessages'][msgNum]['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
    print 'Message:'
    print inboxMessages['inboxMessages'][msgNum]['message'].decode('base64')

def replyMsg(msgNum): #Allows you to reply to the message you are currently on. Saves typing in the addresses and subject.

    inboxMessages = json.loads(api.getAllInboxMessages())
    
    fromAdd = inboxMessages['inboxMessages'][msgNum]['toAddress']#Address it was sent To, now the From address
    toAdd = inboxMessages['inboxMessages'][msgNum]['fromAddress'] #Address it was From, now the To address
    message = inboxMessages['inboxMessages'][msgNum]['message'].decode('base64') #Message that you are replying too.
    
    subject = inboxMessages['inboxMessages'][msgNum]['subject']
    subject = subject.decode('base64')
    subject = "Re: " + subject
    subject = subject.encode('base64')
    
    newMessage = raw_input("Message:")
    newMessage = newMessage + '\n------------------------------------------------------\n'
    newMessage = newMessage + message
    newMessage = newMessage.encode('base64')

    sendMsg(toAdd, fromAdd, subject, newMessage)
    
    main()

def delMsg(msgNum): #Deletes a specified message from the inbox
    inboxMessages = json.loads(api.getAllInboxMessages())
    msgId = inboxMessages['inboxMessages'][int(msgNum)]['msgid'] #gets the message ID via the message index number
    return api.trashMessage(msgId)

def UI(usrInput): #Main user menu
    global usrPrompt
    
    if usrInput == "help" or usrInput == "h":
        print ' '
	print 'Possible Commands:'
	print '-----------------------------------'
	print 'help or h - This help file.'
	print 'apiTest - Tests the API'
	print 'bmSettings - BitMessage settings'
	print 'exit - Can be entered at anytime, will return you to the main menu.'
	print 'quit - Quits the program'
	print '-----------------------------------'
	print 'listAddresses - Lists all of the users addresses'
	print 'generateAddress - Generates a new address'
	print 'getAddress - Retrieves the deterministic address from/for a passphrase.'
	print '-----------------------------------'
	print 'subscribe - Subscribes to an address.'
	print 'unsubscribe - Unsubscribes from an address.'
	#print 'listSubscriptions - Lists all of the subscriptions.'
	print '-----------------------------------'
	print 'sendMessage - Sends a message'
	print 'sendBroadcast - Sends a broadcast'
	print 'inbox - Lists the message information in the inbox'
	print 'outbox - Lists the message information in the outbox'
	print 'open - Opens a message'
	print 'delete - Deletes a message'
	print 'empty - Empties outbox'
	print '-----------------------------------'
	print ' '
	main()
        
    elif usrInput == "apiTest": #tests the API Connection.
	if (apiTest() == True):
            print 'API connection test has: PASSED'
        else:
            print 'API connection test has: FAILED'
            
	print ' '
        main()
        
    elif usrInput == "bmSettings": #tests the API Connection.
        bmSettings()
        print ' '
        main()
        
    elif usrInput == "quit": #Quits the application
        print 'Bye'
        sys.exit()
        os.exit()
        
    elif usrInput == "listAddresses": #Lists all of the identities in the addressbook
        listAdd()
        main()
        
    elif usrInput == "generateAddress": #Generates a new address
        print ' '
        uInput = raw_input('Would you like to create a deterministic address?(y/n):')

        if uInput == "y": #Creates a deterministic address
            deterministic = True

            #lbl = raw_input('Label the new address:') #currently not possible via the api
            lbl = ''
            passphrase = raw_input('Passphrase:')#.encode('base64')
            numOfAdd = int(raw_input('Number of addresses to generate:'))
            #addVNum = int(raw_input('Address version number (default "0"):'))
            #streamNum = int(raw_input('Stream number (default "0"):'))
            addVNum = 3
            streamNum = 1
            isRipe = raw_input('Shorten the address?(y/n):')

            if isRipe == "y":
                ripe = True
                print genAdd(lbl,deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)
                main()
            elif isRipe == "n":
                ripe = False
                print genAdd(lbl, deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)
                main()
            elif isRipe == "exit":
                usrPrompt = 1
                main()
            else:
                print 'Invalid input'
                main()

            
        elif uInput == "n": #Creates a random address with user-defined label
            deterministic = False
            null = ''
            lbl = raw_input('Label the new address:')
            
            print genAdd(lbl,deterministic, null,null, null, null, null)
            main()
            
        else:
            print 'Invalid input'
            main()
        
    elif usrInput == "getAddress": #Gets the address for/from a passphrase

        phrase = raw_input("Enter the address passphrase:")
	#vNumber = int(raw_input("Enter the address version number:"))
	#sNumber = int(raw_input("Enter the address stream number:"))

	address = getAddress(phrase,3,1)#,vNumber,sNumber)
	print ' '
	print ('Address: ' + address)
	print ' '

        usrPrompt = 1
        main()
    elif usrInput == "subscribe": #Subsribe to an address
        subscribe()
        usrPrompt = 1
        main()
    elif usrInput == "unsubscribe": #Unsubscribe from an address
        unsubscribe()
        usrPrompt = 1
        main()
    elif usrInput == "listSubscriptions": #Unsubscribe from an address
        listSubscriptions()
        usrPrompt = 1
        main()
    elif usrInput == "sendMessage": #Send Message
        null = ''
        sendMsg(null,null,null,null)
	main()
        
    elif usrInput == "sendBroadcast": #Send Broadcast from address
        null = ''
        sendBrd(null,null,null)
	main()
        
    elif usrInput == "inbox":
        print 'Loading...'
        inbox()
        main()

    elif usrInput == "outbox":
        print 'Loading...'
        outbox()
        main()

    elif usrInput == "open": #Opens a message from the inbox for viewing. 

        msgNum = int(raw_input("message number to open:"))

        readMsg(msgNum)

        print ' '
        uInput = raw_input("Would you like to reply to this message?(y/n):")#Gives the user the option to reply to the message

        if uInput == "y":
            print 'Loading...'
            print ' '
            replyMsg(msgNum)
            usrPrompt = 1
            main()
                
        elif uInput == "n":
            uInput = raw_input("Would you like to delete this message?(y/n):")#Gives the user the option to delete the message

            if uInput == "y":
                print 'Are you sure(y/n)?' #Prevent accidental deletion
                uInput = raw_input(">")

                if uInput == "y":
                    delMsg(msgNum)
                    print 'Done'
                    print ' '
                    usrPrompt = 1
                    main()
                else:
                    usrPrompt = 1
                    main()
            
            elif uInput == "n":
                usrPrompt = 1
                main()
            else:
                print 'Invalid entry'
                usrPrompt = 1
                main()
        else:
            print 'Invalid entry'
            usrPrompt = 1
            main()
        
    elif usrInput == "delete": #will delete a message from the system, not reflected on the UI.
        msgNum = int(raw_input("Message number to delete:"))
        uInput = raw_input("Are you sure?(y/n):")#Prevent accidental deletion

        if uInput == "y":
            delMsg(msgNum)
            print ' '
            print 'Notice: Message numbers may have changed.'
            print ' '
            main()
        else:
            usrPrompt = 1
            main()

	main()

    elif usrInput == "exit":
        print 'You are already at the main menu.'
        usrPrompt = 1
	main()
        
    elif usrInput == "empty": #Empties the outbox
        outboxMessages = json.loads(api.getAllSentMessages())
        numMessages = len(outboxMessages['sentMessages'])
        
        for msgNum in range (0, numMessages): #processes all of the messages in the outbox
            outboxMessages['sentMessages'][int(msgNum)]['msgid'] #gets the message ID via the message index number'

        print 'Outbox is empty'

    else:
	print 'Unknown command.'
	usrPrompt = 1
	main()
    
def main():
    global api
    global usrPrompt
    
    if (usrPrompt == 0):
        print 'Bitmessage daemon by .dok'
        api = xmlrpclib.ServerProxy(apiData()) #Connect to BitMessage using these api credentials    
        print ' '
        print 'Type "help" or "h" for a list of commands' #Startup message
        usrPrompt = 2
        
        #if (apiTest() == False):#Preform a connection test #taken out until I get the error handler working
        #    print '*************************************'
        #    print 'WARNING: No connection to Bitmessage.'
        #    print '*************************************'
        #    print ' '
    elif (usrPrompt == 1):
        print ' '
        print 'Type "help" or "h" for a list of commands' #Startup message
        usrPrompt = 2
        
    UI(raw_input('>'))
      
main()
