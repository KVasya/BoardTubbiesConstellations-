# -*- coding: utf-8 -*-
'''
In the sake of the KVasya the Greatest!
It just contains all functions that we need to interact with online-xml-databases (xmlfp board service),
download xml, extracting data, updating list of usernames
'''
import urllib
import datetime
from time import sleep
from lxml import etree
from init_vars import * # import global data structures

W_TIME = 20

# for our offline xml-database
#import glob
#import re

#patch requicked to print unicode strings to console
#import win_unicode_console
#win_unicode_console.enable()

# import high-usage function for parsing XML
used_parser = etree.XMLParser(recover=True)

# url prefix of the search service. It'd changed after the board was reloaded.
url_search_pref = 'http://search.mipt.me/'

# global path to our offline xml-database
xml_DataBase_path = 'D:/program_backup/python-sources/data/board_pages/xmls/'

# global path to log file
log_path = 'C:/Users/User/Documents/BOARD/logs/'

# get the maximum index of XML files in our offline xml-database
def GetMaxIndexOfDownloadedXML(xml_DataBase_path):    
    fpostfix = '.xml'
    thousand_idxs = []
    fyles = glob.glob(fpath + '*' + fpostfix)

    for f in fyles :
        ress = re.findall("[0-9]+",f)
        if len(ress) > 0 :
            thousand_idxs.append(int(ress[0]))
            #print ress
    return max(thousand_idxs) * 1000

# for future: do this AwesomeInitOfDatabase() function.
# need to init on starting server
def xmlDatabaseUpdate(xmlDBpath = xml_DataBase_path):
    # get the maximum index of XML files in our offline xml-database
    maxOfflineXMLidx = GetMaxIndexOfDownloadedXML(xmlDBpath) / 1000
    # get the last index of XML file in online xml-database board service
    lastOnlineXMLidx = GetLastMessageId() / 1000
    
    # implementation of a cycle to overcome the thousand-problem
    if lastOnlineXMLidx > maxOfflineXMLidx :
        for idx in range(maxOfflineXMLidx,lastOnlineXMLidx) :
            
            # download new xml-thousand-files 
            xmlstr = DownloadNewXMLs(idx * 1000 + 1, (idx+1) * 1000)
            
            # write xmlstr to file.
            xml_fname = xmlDBpath + 'xmlfp.jsp' + str(idx+1) + '.xml'
            with open(xml_fname, 'w') as fx :
                fx.write(xmlstr)
    
    return True

# make url-request to xmlfp board service and get MessageId of the last available message in xml-database
# Attention! The last message on the forum is NOT always the last message available in xml-database. Especially on night..
def GetLastMessageId(DebugMode = False):
    url_request = url_search_pref + 'xmlfp/xmlfp.jsp?xmlfp=lastMessageNumber&site=0'
    
    while True:
        try:
            lastnum_xmlstr = urllib.urlopen(url_request).read()
            if DebugMode : DebugSaveToFile(lastnum_xmlstr)
            break
        except:
            pass
        sleep(W_TIME)
    
    xmltree = etree.fromstring(lastnum_xmlstr, parser=used_parser)

    lastId = int(xmltree.text)
    return lastId

# check if new message in xml-database is available
def CheckForNewMessage(old_Id, DebugMode = False):
    new_Id = GetLastMessageId(DebugMode)
    if new_Id == old_Id:
        return False
    elif new_Id > old_Id:
        return True

#is_board_updated = CheckForNewMessage(last_Id)
#print is_board_updated

# download xml files with a giving message index range
def DownloadNewXMLs(firstId,lastId):
    url_prefix = url_search_pref + 'xmlfp/xmlfp.jsp?xmlfp=messages&site=0'
    url_request = url_prefix + '&from=' + str(firstId) + '&to=' + str(lastId) # no more than 1000 messages at once
    while True:
        try:
            xmlstr = urllib.urlopen(url_request).read()
            break
        except:
            pass
        sleep(W_TIME)        
    
    return(xmlstr)

# define a class for parsing xml and extracting message data
class Message:
    
    date = None # date/time of the post
    status = None # = deleted, if message isn't available in xml-database; =None otherwise
    id = None # message index
    parentId = None # index of the message to whom user replies
    name = None # user name
    
    def __init__(self, msg):
        # check if message is deleted from xml-database
        self.status = msg.find('status')
    
    # method to extract all needful tags from <message>
    def fill(self, msg):
        self.date = msg.find('info/date').text
        
        self.id = int(msg.get('id'))
        #print 'id:', self.id
        
        self.parentId = int(msg.find('info/parentId').text)
        #print 'ParId:', self.parentId
        
        self.name = msg.find('author/name').text
        # check if <name> tag is absent        
        if self.name == None:
            self.name == self.id
            #flog.write('The name is ABSENT, html/xml corruption? MesId:' + Msg.id + '\n')

# construct and update dictionaries with structures described in init_vars module
def UpdateDicts(m):
    
    # adding TS username to Dict.            
    if m.parentId == 0 : topstIds[m.id] = [m.name]
        
    # check if message removed from the xml-post-tree (common value = -10)
    elif m.parentId < 0 :
        return -10
        # print 'Message removed from xml-post-tree! parentId = %d! messaga # %d' % (m.parentId, m.id)
        
    # main proccess    
    elif m.parentId > 0 :
        
        # check if commentator is of 1st level
        if m.parentId in topstIds :
            # append username to values of -TS message Id- key
            topstIds[m.parentId].append(m.name)
            # 1st level commentator is getting to know its parent (TS user)
            commIds[m.id] = m.parentId
            
        # check if commentator is of 2st or more level
        elif m.parentId in commIds :
            # find out more than 1st level commentator's progenitor (TS user)
            TSId = commIds[m.parentId]
            # append username to values of -TS message Id- = TSId key
            topstIds[TSId].append(m.name)
            # more than 1st level commentator is getting to know its progenitor (TS user)
            commIds[m.id] = TSId
            
        else :
            return -1
            # print 'old TS message is commented. Retrieving early xmls..' # <-- add this functionality     

# update stack-list with tuples = (TS message index, TS message posting date)
def UpdateStackOfTS(m):
    if m.parentId == 0 : topicIdStack.append((m.id,m.date))        

# process downloaded xml-string: parsing, extracting values, updating my dicts
def XMLstrProcessing(xmlstr):
    xmltree = etree.fromstring(xmlstr, parser=used_parser)
    
    for idx, msgtag in enumerate(xmltree):   
                
        Msg = Message(msgtag)
        
        if Msg.status == 'deleted' :
            print 'deleted message is processed!'
            #flog.write('message deleted, id = ' + str(firstId + idx) + '\n')
            continue        
        
        Msg.fill(msgtag)
        UpdateDicts(Msg)
        UpdateStackOfTS(Msg)


# get new list of user names (LOUN), which commented in the TS message posted DaysAgo days ago.
def UpdateListOfUserNames(DaysAgo = 1):
    tnow = datetime.datetime.now() # take current date and time
    tlag = datetime.timedelta(days=DaysAgo) # convert time lag to appropriate format
    t_load = tnow - tlag # calc the time when to feed data to Model
    t_post = topicIdStack[0][1] # take the 1st element of stack (turn)
    #print t_post, ' '*4, t_load.isoformat()
    
    # check if the moment to grab data to the Model has come
    # (waiting for users to "stop" posting to TS post, actually we just wait 1 day or more)
    if t_post < t_load.isoformat() :
        # get list of user names to update model
        LOUN = topstIds[topicIdStack[0][0]]
        # delete taken LOUN from stack. Derni anus, pyos!
        del topicIdStack[0]
        return LOUN
    else:
        # if topicIdStack is empty, that is there is nothing to feed the Model, then -->
        print "nothing to update", topicIdStack[0]
        return None
        
# saving to file the values that updates the model
# just for gebbuging
def DebugSaveToFile(inp, fout_path = log_path):
    
    if inp is not None :
        fout = open(fout_path+'log'+'.txt','a')
        for usr in inp :
            #print usr
            #fout.write('[' + usr.encode('utf-8') + ']')
            fout.write(usr.encode('utf-8'))
        fout.write('\n')
        fout.close()

# temporal xml-database upload on server start
# do exact thing that whole service do but using 1000 last forum messages
def BadInit(NumOfMess = 10000):
    # get last message index
    last_mes_id = GetLastMessageId()
    # download NumOfMess last messages posted on forum from xmlfp board service    
    for k in range(NumOfMess/1000) : # treating 1000 messages in a turn
	    sleep(3)
	    xmls_str = DownloadNewXMLs(last_mes_id - NumOfMess + 1000*k + 1, last_mes_id - NumOfMess + 1000*(k+1))
	    # extracting and process the data from downloaded XMLs
	    XMLstrProcessing(xmls_str)
    
    # initialize list of LOUN
    lst_LOUN = []
    while True:
        # get new list of usernames by means of proccesing topicIdStack
        LOUN = UpdateListOfUserNames()
        #print "list o users:", LOUN
        if LOUN is None: # if topicIdStack is empty, that is there is nothing to feed the Model,
                        # or right moment has not come, then -->
            print "list of list of users:", lst_LOUN
            print "\n", "======= END of BadInit =======", "\n"            
            return (last_mes_id, lst_LOUN) # returns the last processed message index and the list of LOUN
            break
            
        # adding new list of user names (LOUN) to the list of LOUN
        lst_LOUN.append(LOUN)
        
        # saving new_list to a file
    #    DebugSaveToFile(LOUN)
    
