# This is an example of a daemon client for PyBitmessage 0.3.0, by .dok (Version 0.1.0)
# See https://bitmessage.org/wiki/API_Reference for API documentation

import xmlrpclib
import json
import sys
import getopt
import time
import datetime
import os
import ConfigParser

api = ''

firstRun = True

#Begin API lookup data
def lookupAppdataFolder():
    APPNAME = "PyBitmessage"
    from os import path, environ
    if sys.platform == 'darwin':
        if "HOME" in environ:
            dataFolder = path.join(os.environ["HOME"], "Library/Application support/", APPNAME) + '/'
        else:
            print 'Could not find home folder, please report this message and your OS X version to the BitMessage Github.'
            sys.exit()

    elif 'win32' in sys.platform or 'win64' in sys.platform:
        dataFolder = path.join(environ['APPDATA'], APPNAME) + '\\'
    else:
        dataFolder = path.expanduser(path.join("~", "." + APPNAME + "/"))
    return dataFolder

def apiData():
    config = ConfigParser.SafeConfigParser()
    config.read(lookupAppdataFolder() + 'keys.dat')

    try:
        apiConfigured = config.get('bitmessagesettings','apienabled')
    except:
        apiConfigured = ''
    if apiConfigured == '' or apiConfigured == False :
        print 'keys.dat not properly configured!'
    else:
        apiEnabled = config.getboolean('bitmessagesettings','apienabled')
        apiInterface = config.get('bitmessagesettings', 'apiinterface')
        apiPort = config.getint('bitmessagesettings', 'apiport')
        apiUsername = config.get('bitmessagesettings', 'apiusername')
        apiPassword = config.get('bitmessagesettings', 'apipassword')

        return "http://" + apiUsername + ":" + apiPassword + "@" + apiInterface+ ":" + str(apiPort) + "/" #Build the api credentials

#End API lookup data

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
    if (toAddress == ''):
        toAddress = raw_input("To Address:")
        
    if (fromAddress == ''):
        jsonAddresses = json.loads(api.listAddresses())
        numAddresses = len(jsonAddresses['addresses']) #Number of addresses
        
        if (numAddresses > 1): #Ask what address to send from if multiple addresses
            fromAddress = raw_input("Enter an Address to send from:") # todo: add ability to type in label instead of full address
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
    print 'The ackData is: ', ackData
    print ' '


def sendBrd(fromAddress, subject, message): #sends a broadcast
    if (fromAddress == ''):
        jsonAddresses = json.loads(api.listAddresses())
        numAddresses = len(jsonAddresses['addresses']) #Number of addresses
        
        if (numAddresses > 1): #Ask what address to send from if multiple addresses
            fromAddress = raw_input("Enter an Address to send from:") # todo: add ability to type in label instead of full address
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
    print 'The ackData is: ', ackData
    print ' '

def inbox(): #Lists the messages by: Message Number, To Address Label, From Address Label, Subject, Received Time)
    inboxMessages = json.loads(api.getAllInboxMessages())
    numMessages = len(inboxMessages['inboxMessages'])
    print 'There are ',numMessages,' messages in the inbox.'
    print ' '

    for msgNum in range (0, numMessages): #processes all of the messages in the inbox
        print '-----------------------------------'
        print ' '
        print 'Message Number:',msgNum #Message Number
        print 'To:', inboxMessages['inboxMessages'][msgNum]['toAddress'] #Get the to address
        print 'From:', inboxMessages['inboxMessages'][msgNum]['fromAddress'] #Get the from address
        print 'Subject:', inboxMessages['inboxMessages'][msgNum]['subject'].decode('base64') #Get the subject
        print datetime.datetime.fromtimestamp(float(inboxMessages['inboxMessages'][msgNum]['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')
        print ' '

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
    
    subject = inboxMessages['inboxMessages'][msgNum]['subject']
    subject = subject.decode('base64')
    subject = "Re: " + subject
    subject = subject.encode('base64')
    
    message = raw_input("Message:")
    message = message.encode('base64')

    sendMsg(toAdd, fromAdd, subject, message) 
    
    main()

def delMsg(msgNum): #Deletes a specified message from the inbox
    inboxMessages = json.loads(api.getAllInboxMessages())
    msgId = inboxMessages['inboxMessages'][int(msgNum)]['msgid'] #gets the message ID via the message index number
    return api.trashMessage(msgId)

def UI(usrInput): #Main user menu
    if usrInput == "help" or usrInput == "h":
        print ' '
  print 'Possible Commands:'
	print '-----------------------------------'
	print 'help or h - This help file.'
	print 'apiTest - Tests the API'
	print 'exit - Exits the program'
	print '-----------------------------------'
	print 'listAddresses - Lists all of the users addresses'
	print 'generateAddress - Generates a new address'
	print '-----------------------------------'
	print 'sendMessage - Sends a message'
	print 'sendBroadcast - Sends a broadcast'
	print 'inbox - Lists the message information in the inbox'
	print 'open - Opens a message'
	print 'delete - Deletes a message'
	print '-----------------------------------'
	print ' '
	main()
        
    elif usrInput == "apiTest": #tests the api. should return '5'
	print 'What is 2 + 3: ',api.add(2,3)
	print ' '
        main()

    elif usrInput == "exit": #Exits the application
        print 'Bye'
        sys.exit()
    elif usrInput == "listAddresses": #Lists all of the identities in the addressbook
        listAdd()
        main()
        
    elif usrInput == "generateAddress": #Generates a new address
        print ' '
        uInput = raw_input('Would you like to create a deterministic address?(y/n):')

        if uInput == "y": #Creates a deterministic address
            deterministic = True

            #lbl = raw_input('Label the new address:') #currently not possible via the api
            passphrase = raw_input('Passphrase:').encode('base64')
            numOfAdd = int(raw_input('Number of addresses to generate:'))
            addVNum = int(raw_input('Address version number (default "0"):'))
            streamNum = int(raw_input('Stream number (default "0"):'))
            isRipe = raw_input('Shorten the address?(y/n):')

            if isRipe == "y":
                ripe = True
                print genAdd(lbl,deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)
                main()
            elif isRipe == "n":
                ripe = False
                print genAdd(lbl,deterministic, passphrase, numOfAdd, addVNum, streamNum, ripe)
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
        
    elif usrInput == "sendMessage": #Send Message
        null = ''
        sendMsg(null,null,null,null)
        
	main()
        
    elif usrInput == "sendBroadcast": #Send Broadcast from address
        null = ''
        sendBrd(null,null,null)
	main()
        
    elif usrInput == "inbox":
        inbox()
        main()
        
    elif usrInput == "open": #Opens a message from the inbox for viewing. 

        msgNum = int(raw_input("message number to open:"))

        readMsg(msgNum)

        print ' '
        print 'Would you like to reply to this message(y/n)?' #Gives the user the option to reply to the message
        uInput = raw_input(">")

        if uInput == "y":
            replyMsg(msgNum)
            main()
                
        elif uInput == "n":
            print 'Would you like to delete this message(y/n)?' #Gives the user the option to delete the message
            uInput = raw_input(">")

            if uInput == "y":
                print 'Are you sure(y/n)?' #Prevent accidental deletion
                uInput = raw_input(">")

                if uInput == "y":
                    delMsg(msgNum)
                    print 'Done'
                    print ' '
                    main()
                else:
                    main()
            
            elif uInput == "n":
                main()
            else:
                print 'invalid entry'
        else:
            print 'invalid entry'
        
    elif usrInput == "delete": #will delete a message from the system, not reflected on the UI.
        msgNum = int(raw_input("Message number to delete:"))
        print 'Are you sure(y/n)?' #Prevent accidental deletion
        uInput = raw_input(">")

        if uInput == "y":
            delMsg(msgNum)
            print 'Notice: Message numbers may have changed'
            print ' '
            main()
        else:
            main()

	main()
        
    else:
	print 'unknown command'
	global firstrun
	firstrun = True
	main()
    
def main():
    global firstRun
    global api
    
    if (firstRun == True):
        api = xmlrpclib.ServerProxy(apiData()) #Connect to BitMessage using these api credentials
        print 'bitmessage daemon by .dok, "help" or "h" for a list of commands' #Startup message
        firstRun = False
        
    UI(raw_input('>'))
      
main()
