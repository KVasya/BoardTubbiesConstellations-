# -*- coding: utf-8 -*-
'''
I hate you, KVasya! This is fucking bullshit!!!!
The program operates as follows:
1. xu.BadInit() - download last N=1000 posted messages,
                extract data, updates Model with it and
                return last processed message
2. ...
Realization of board-xml-database loading, real-time updating;
topicstarter's/commentator's messages's attributies processing;
obtaining list of all users who posted in the topicstarter's message with specific id
'''
import time
# this module contains all functions and classes requied to achieve the purpose
import xml_update_2_0 as xu

# download and processing last 1000 messages, updating Model with them
lastProcId = xu.BadInit() # get last _processed_ message index

# real-time Model update
while True:
    # waiting 10 seconds between checks of the forum for new messages
    time.sleep(10)
    
    # check forum for new message and process it if it's available
    if xu.CheckForNewMessage(lastProcId):
        lastId = xu.GetLastMessageId() # get last message index available on forum (not processed yet)
        
        # download new xmls appeared in the wait time and convert it to a string
        new_xmlstr = xu.DownloadNewXMLs(lastProcId,lastId) # may be bug here. Should be (lastProcId+1,lastId)
        
        # gets message data from xml_string and process it
        # Wanna know what does "process" mean? That is - br-bla-blm-grr-uhm (my guts moving around).
        # or may look in xu module. I hate you, KVasya!!!
        xu.XMLstrProcessing(new_xmlstr)
        lastProcId = lastId # new messages processed. By now last processed message is the last on forum.
        print "Last message accepted: ", lastProcId
    
    else: print "....... waiting messages ....... last processed MesId:", lastProcId
    
    # get new list of usernames
    new_list = xu.UpdateListOfUserNames(1)
    print "Updating Model with:", new_list, '\n'
    
    # Updating Model with new_list
    M.modelUpdate(new_list)
    
    #xu.DebugSaveToFile(new_list)
