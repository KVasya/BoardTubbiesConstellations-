# -*- coding: utf-8 -*-
'''
The program uses these functions in the order of appareance:
1. xu.BadInit() - download last N=1000 posted messages, extract data,
                  updates Model with it and return last processed message
                  
Then in the while cycle real-time part starts to operate -->
2. time.sleep(T) - waiting T seconds between checks of the forum for new messages

3. xu.CheckForNewMessage(lastProcId) - in the if-else clause we check
                                      for new messages available on forum
                
4. xu.GetLastMessageId() - get last message index available on forum (not processed yet)

5. xu.DownloadNewXMLs(lastProcId,lastId) - get new forum messages in range (lastProcId,lastId),
                                            (those ones that are not processed yet)
                                            
6. xu.XMLstrProcessing(new_xmlstr) - process the xml string: get message data, etc.
                                    See xu module for details.
7. xu.UpdateListOfUserNames(X = default) - get new list of users, which commented in the TS post X days ago.

8. M.modelUpdate(new_list) - updates model with new list of users
'''
import time
# this module contains all functions and classes to download posts
import xml_utility as xu

import model    # contains class 'Model' storing data from posts and updating model with it
from pca_visualize import pca_plot, getMtxFromUserNames
import pickle


# download and processing the last NumOfMess=10000 messages, updating Model with them
# wait for about 40 seconds to BadInit is completed
lastProcId, Model_Init_List = xu.BadInit(NumOfMess=10000) # get last _processed_ message index

# model is initialized
M = model.Model()

# #DebugPart, to be removed!!!!! BEEGIN
#
# Model_Init_List = Model_Init_List[:3]
# #DeburPart, to be remoded!!!!!!END


# first bunch of users fed to model
M.modelUpdate(Model_Init_List)




# real-time Model update
while True:
    # waiting 10 seconds between checks of the forum for new messages
    time.sleep(10)

    # check forum for new message and process it if it's available
    if xu.CheckForNewMessage(lastProcId):
        lastId = xu.GetLastMessageId() # get the last message index available on the forum (not processed yet)

        # download new xmls appeared in the wait-time and convert it to a string
        new_xmlstr = xu.DownloadNewXMLs(lastProcId+1, lastId)

        # gets message data from xml_string and process it
        xu.XMLstrProcessing(new_xmlstr)
        lastProcId = lastId # new messages processed. By now the last processed message is the last on the forum.
        print "Last message accepted: ", lastProcId

    else: print "..... waiting messages ..... Last processed MesId:", lastProcId

    # get new list of usernames
    new_list = xu.UpdateListOfUserNames()

    # ################# DEBUG PART ################# BEGIN
    # import numpy as np
    # new_list = Model_Init_List[-1:][0]
    #
    # for User in new_list:
    #     User_mod = User + '_mod'
    #     cnt = M.Vmtx.shape[0]
    #     if not M.Users_dict.has_key(User_mod):
    #         M.Vmtx = np.append(M.Vmtx, np.empty([1, M.Vmtx.shape[1]]), axis=0)
    #         M.Vmtx[cnt, :] = M.Vmtx[M.Users_dict[User], :]
    #         M.Umtx = np.append(M.Umtx, np.empty([1, M.Umtx.shape[1]]), axis=0)
    #         M.Umtx[cnt, :] = M.Umtx[M.Users_dict[User], :]
    #         M.Users_dict[User_mod] = cnt
    #
    # List2Add = []
    # for User in new_list:
    #     List2Add.append(User + '_mod')
    # model.Vmtx = M.Vmtx
    # model.Umtx = M.Umtx
    # print  'M.Post2PostSimilarities(Model_Init_List, List2Add) =', M.Post2PostSimilarities(Model_Init_List, List2Add)
    #
    #
    #
    # ################# DEBUG PART ################# END


    # print 'Post closest to the new one is', new_list, ':\n', M.findNNPost(new_list, Model_Init_List)

    if new_list:
        print "Updating Model with:", new_list, '\n'
        M.modelUpdate([new_list])

        # ################ DEBUG PART ############################## BEGIN
        # pickle.dump(M, open('./testFles/M.p', 'w'))
        # pickle.dump(new_list, open('./testFles/new_list.p', 'w'))
        # pickle.dump(Model_Init_List, open('./testFles/Model_Init_List.p', 'w'))
        # ################ DEBUG PART ################################ END

        NN_list = M.findNNPost(new_list, Model_Init_List)
        ListOfUserNames = new_list + NN_list
        ListOfDistinguishedUsers = M.PostsIntersection(NN_list, new_list)   # users which take part in depicted posts
                                                                            # intersection
        pca_plot(getMtxFromUserNames(M.Umtx, M.Vmtx, M.Users_dict, ListOfUserNames), ListOfUserNames=ListOfUserNames,
                 SublistOfUserNames=NN_list, TurnNondistinguishedUsersOff = True,
                 ListOfDistinguishedUsers = ListOfDistinguishedUsers)
        print 'Post closest to the new one is :\n',  NN_list
        print 'Scores of posts: ', M.Post2PostSimilarities(Model_Init_List, new_list)
        Model_Init_List.extend([new_list])
    # saving new_list to a file
    #xu.DebugSaveToFile(new_list)

