'''This function updates the model and shows the snapshot of it's input'''import numpy as npimport picklefrom sklearn import preprocessingimport tensorflow as Timport timeimport randomimport pca_visualize as pca_visimport covertreefrom scipy.sparse import dok_matrix##   Model parameters:# -     D:  peop2vec dimensionalityD = 100# - C_neg:  number of negative samples accompanying each personC_neg   = 10##  Learning parameters:#       initial  learning rate,  definitely larger than necessarylearning_rate_0 = 100.0regularizer = 1E-16# - N_of_epochs: optimization steps are repeated for  N_epochs timesN_of_epochs = 1## - MsgInterval:MsgInterval = 100# - Nopt: optimization for each stage is repeated for Nopt times:N_opt=1## CoverTree params:NNsNumber = 10  # number of NNs around each user-user pair vector                # used in interpost distance calculationdef initModelAttr(Object, AttrName):    try:        LoadedItem = pickle.load(open(AttrName +'.p','r'))  # in case the model already exists        if AttrName!='Users_dict':            D = LoadedItem.shape[1]    except:        if AttrName!='Users_dict':            LoadedItem = np.array([])        else:            LoadedItem = {}    setattr(Object, AttrName, LoadedItem)def optimizeNewContext(Model, ListOfListsOfUserNames):     # updates vecs present in newly added context                                                           # returns the sum of optimized functional values                                                           # over all optimization steps accepted    TotalScore = 0                                         # model quality measure    Vc_sampled          = np.zeros([1, D])    U_sampled           = np.zeros([1, D])    U_neg_mtx_sampled   = np.zeros([C_neg, D])    # workflow graph setup    # internal vector of a person sampled    Vc          = T.Variable(T.zeros([1, D]))    # external vector of single context person    U           = T.Variable(T.zeros([1, D]))    # matrix of negative context external vectors    U_neg_mtx           = T.Variable(T.zeros([C_neg, D]))    Vc_plchldr              = T.placeholder(T.float32)    U_plchldr               = T.placeholder(T.float32)    U_neg_mtx_plchldr       = T.placeholder(T.float32)    learning_rate_plchldr   = T.placeholder(T.float32)    Score   =   -T.log(T.sigmoid(T.matmul(Vc, T.transpose(U))) + T.constant(regularizer, shape= [1, 1] ))+ \            T.reduce_sum(            -T.log(T.sigmoid(-T.matmul(Vc, T.transpose(U_neg_mtx))) + T.constant(regularizer,  shape= [1, C_neg]))            )    assign_step_Vc          = Vc.assign(Vc_plchldr)    assign_step_U           = U.assign(U_plchldr)    assign_step_U_neg_mtx   = U_neg_mtx.assign(U_neg_mtx_plchldr)    opt_step = T.train.GradientDescentOptimizer(learning_rate_plchldr).minimize(Score)    S = T.Session()    S.run(T.initialize_all_variables())    Nexecutions = 0    #calculate the number of optimization executions    for ListOfUserNames in ListOfListsOfUserNames:        for epochCnt in range(N_of_epochs):                Slen= len(ListOfUserNames)                if Slen>1 and len(Model.Users_dict)-len(ListOfUserNames)>C_neg:                    for CentralWordID in range(Slen):                        for contextWordID in range(1, CentralWordID)+ range(CentralWordID+1, Slen):                            if ListOfUserNames[CentralWordID]!=ListOfUserNames[contextWordID]:                                Nexecutions+=1    if __debug__:        print 'We shall execute optimization procedure for ', Nexecutions, ' times'    for ListOfUserNames in ListOfListsOfUserNames:        ExecutionsCnt = 0        learning_rate = learning_rate_0        t0 = time.time()        epochScore_functional = []  #epochScore calculated as sum of functional values        for epochCnt in range(N_of_epochs):            epochScore_functional.extend([0])            Slen= len(ListOfUserNames)            if Slen>1 and len(Model.Users_dict)-len(ListOfUserNames)>C_neg:                #t2 = t0                for centralWordID in range(Slen):                    #each pair of words is treated twice, with context and central words interchanged                    for contextWordID in range(1, centralWordID)+ range(centralWordID+1, Slen):                        if ListOfUserNames[centralWordID]!=ListOfUserNames[contextWordID]: # if 2 instances of the same word happen, no optimization for the pair                            Vc_sampled_ind = Model.Users_dict[ListOfUserNames[centralWordID]]                            U_sampled_ind  = Model.Users_dict[ListOfUserNames[contextWordID]]                            Vc_sampled     = np.array([Model.Vmtx[Vc_sampled_ind, :]])                            U_sampled      = np.array([Model.Umtx[U_sampled_ind, :]])                            U_neg_mtx_sampled_inds  = []                            cnt=0                            while cnt<C_neg:                                rand_ind = random.randint(0, len(Model.Users_dict) - 1)                                RandUserName =  Model.Users_dict.keys()[rand_ind]                                if not RandUserName in ListOfUserNames:                                    U_neg_mtx_sampled_inds.extend([Model.Users_dict[RandUserName]])                                    cnt+=1                            U_neg_mtx_sampled = np.empty([C_neg, D])                            cnt=0                            for ind in U_neg_mtx_sampled_inds:                                U_neg_mtx_sampled[cnt,:]       = Model.Umtx[ind,:]                                cnt += 1                            S.run(assign_step_Vc, feed_dict={Vc_plchldr: Vc_sampled})                            S.run(assign_step_U_neg_mtx, feed_dict={U_neg_mtx_plchldr: U_neg_mtx_sampled})                            S.run(assign_step_U, feed_dict={U_plchldr: U_sampled})                            OldScore= S.run(Score)                            epochScore_functional[epochCnt]+= float(OldScore)                            NewScore = np.inf                            learning_rate *= 2                            while NewScore>OldScore:                                S.run(assign_step_Vc, feed_dict={Vc_plchldr: Vc_sampled})                                S.run(assign_step_U, feed_dict={U_plchldr: U_sampled})                                S.run(assign_step_U_neg_mtx, feed_dict={U_neg_mtx_plchldr: U_neg_mtx_sampled})                                for j in range(N_opt):                                    S.run(opt_step, feed_dict= {learning_rate_plchldr: learning_rate})                                NewScore= S.run(Score)                                learning_rate /= 2                            TotalScore += NewScore                            if __debug__ and ExecutionsCnt%MsgInterval==0:                                print 'Epoch ', (epochCnt+1), 'of ', N_of_epochs, '. The scores of completed epochs =', epochScore_functional[:epochCnt]                                print 'learning rate =', learning_rate                                #print 'Score after optimization = ', S.run(Score)                                #print 'Score difference = ', S.run(Score) - OldScore                            #print 'Optimization step is done for ', time.time()-t0,' secs.'                            #t0 = time.time()                            # print 'After Learning', 30*'='                            # print 'Vc=', preprocessing.normalize(S.run(Vc))                            # print 'U=',  preprocessing.normalize(S.run(U))                            # print 'Vc*U=', np.dot(preprocessing.normalize(S.run(Vc)), np.transpose(preprocessing.normalize(S.run(U))))                            # saving the results back into vec matrices                            Model.Vmtx[Vc_sampled_ind, :] = preprocessing.normalize(S.run(Vc))                            Model.Umtx[U_sampled_ind, :]  = preprocessing.normalize(S.run(U))                            #print(U_neg_mtx_sampled_inds)                            Model.Umtx[U_neg_mtx_sampled_inds, :] = preprocessing.normalize(S.run(U_neg_mtx))                            #print 'Optimized results are saved, for ', time.time()-t0,' secs.'                            #t0 = time.time()                            ExecutionsCnt+=1                            # if ExecutionsCnt%MsgInterval==0:                            #     t1= time.time()                            #     print ExecutionsCnt,' optimization steps of total ', Nexecutions,' were taken'                            #     print 'Time elapsed: ', (t1-t0)/3600 ,'hrs'                            #     print (Nexecutions - ExecutionsCnt)*(t1-t0)/(3600*ExecutionsCnt), ' hrs left'                            #                            #     print 100*'_'    S.close()    return TotalScoredef distance(Wind0, Wind1):  # distance (square value) btwn 2 user-user vectors || (Va-Vb) - (Vc-Vd) ||^2    global Vmtx    Vdiff = Vmtx[Wind0[0], :] - Vmtx[Wind0[1], :] - Vmtx[Wind1[0], :] + Vmtx[Wind1[1], :]    return Vdiff.dot(Vdiff.T)class Model:    def __init__(self):        for Attr in ['Vmtx', 'Umtx', 'Users_dict']: # attributes which may be loaded from files            initModelAttr(self, Attr)        self.CoverTree = covertree.CoverTree(distance)    def modelUpdate(self, ListOfListsOfUserNames):        global Vmtx                                 # used for distance function determined outside the class        for ListOfUserNames in ListOfListsOfUserNames:            for User in ListOfUserNames:                if not self.Users_dict.has_key(User):                    self.Users_dict[User]    = len(self.Users_dict)                    InitRandomVec       = np.random.rand(1, D) - np.random.rand(1, D)                    if len(self.Vmtx)==0:                        self.Vmtx = np.array(InitRandomVec)                    else:                        self.Vmtx = np.append(self.Vmtx, np.array(InitRandomVec), axis=0)                    InitRandomVec       = np.random.rand(1, D) - np.random.rand(1, D)                    if len(self.Umtx)==0:                        self.Umtx = InitRandomVec                    else:                        self.Umtx = np.append(self.Umtx, InitRandomVec, axis=0)        OptScore = optimizeNewContext(self, ListOfListsOfUserNames)             # the summary value of optimization func                                                                            # over all optimization steps is returned        Vmtx = self.Vmtx    # global value (to be used in distance) is updated        # tree update        for ListOfUserNames in ListOfListsOfUserNames:            Nusers = len(ListOfUserNames)            for User1 in ListOfUserNames:                for User2 in ListOfUserNames:                    col1 = self.Users_dict[User1]                    col2 = self.Users_dict[User2]                    if col2>col1:                        self.CoverTree.insert((col1, col2))        return OptScore    # for user-user pairs from post ListOfUserNames finds closest user-user pairs,    # then finds number of those pairs present in the post ListOfUserNamesX    def Post2PostDistance(self, ListOfUserNamesX, ListOfUserNames):        Nwords = self.Vmtx.shape[0]        Word2WordMtx_Post0 = dok_matrix((Nwords, Nwords), dtype=np.int) # mtx with 1's at NNs places of ListOfUserNames        Word2WordMtx_Postn = dok_matrix((Nwords, Nwords), dtype=np.int) # mtx with 1's at U-U pairs of ListOfUserNamesX        # matrix for given post ListOfUserNames representation        for User1 in ListOfUserNames:            col1 = self.Users_dict[User1]            for User2 in ListOfUserNames:                col2 = self.Users_dict[User2]                if col2>col1:                    NNsList = self.CoverTree.knn(NNsNumber, (col1, col2), True)                    for NN in NNsList:                        Word2WordMtx_Post0[NN[0], NN[1]] = 1        # removal of initial word pairs from post matrix        for User1 in ListOfUserNames:            col1 = self.Users_dict[User1]            for User2 in ListOfUserNames:                col2 = self.Users_dict[User2]                if col2 > col1:                    Word2WordMtx_Post0[col1, col2] = 0        # w2w matrix init for mtx 2 compare with        for User1 in ListOfUserNamesX:            col1 = self.Users_dict[User1]            for User2 in ListOfUserNamesX:                col2 = self.Users_dict[User2]                if col2 > col1:                    Word2WordMtx_Postn[col1, col2] = 0        MultResult = Word2WordMtx_Post0 * Word2WordMtx_Postn        Score = int(MultResult.sum(0).sum(1))        return Score    # returns the list of names for NN-post    # INPUT:    # ListOfUserNames -- post whose NN is required    #    # ListOfListsOfUserNames -- list with posts, potential NNs    def findNNPost(self, ListOfUserNames, ListOfListsOfUserNames):        Scores = np.empty([len(ListOfListsOfUserNames), 1])        cnt=0        for ListOfUserNamesX in ListOfListsOfUserNames:                     # loop over potential candidates to NNs            Scores[cnt, 0] = self.Post2PostDistance(ListOfUserNamesX, ListOfUserNames)            cnt+= 1        return ListOfListsOfUserNames[int(np.argsort(Scores, axis=0)[-1:])]    # Given a list of users from new post, 'ListOfUserNames',    # uses the list as a context and finds users closest to the context.    # At least one user from ListOfUserNames has to be incorporated into the    # model already, otherwise a random set of users is depicted.    # Args:    # NNQty - the quantity of users to picture (users with highest probability    # to take part in the post)    # ImageFName - file name to save the resulting image    to    def showNNs(self, ListOfUserNames, ImageFName='ImageOfPost.jpg', NNQty = 10):        Nwords = len(self.Users_dict)        User2User_ScoreMtx = self.Vmtx.dot(self.Umtx.T)  # matrix with all-2-all scalar products in the dictionary        ListOfUserNamesUnique = list(set(ListOfUserNames))        Context_Indices = []        for Name in ListOfUserNamesUnique:            try:                                                               # in case the Name is new for the model                Context_Indices.extend([self.Users_dict[Name]])            except:                ListOfUserNamesUnique.remove(Name)                pass        ImageTitle = 'Users of the post (in red) and not more \n than ' + str(NNQty) + \                     ' most probable contributors (green)'        if Context_Indices == []:                                              # average context with all words is taken            ImageTitle = 'No users known to the model, \n  showing  just 10 most probable users'            Context_Indices = range(Nwords)        VecOfScores = np.sum(User2User_ScoreMtx[:, Context_Indices], axis=1)  # vector elements, indexed by all words                                                                              # in vocabulary,                                                                              # show the probability of being in the                                                                              # context        MostProbable_Indices = np.argsort(VecOfScores)[-NNQty:]        ListOfUserNames2Show = []        for j in xrange(Nwords):            if self.Users_dict.items()[j][1] in MostProbable_Indices:                ListOfUserNames2Show.extend([self.Users_dict.items()[j][0]])        ListOfUserNames2Show += ListOfUserNamesUnique        ListOfUserNames2Show = list(set(ListOfUserNames2Show))  # for prognosed users amidst users already present in                                                                # the post        # ListOfUserNamesUnique (names currently present in the post) is provided in order to mark it in red        pca_vis.pca_plot( pca_vis.getMtxFromUserNames(ListOfUserNames2Show),                          ListOfUserNames = ListOfUserNames2Show,                          SublistOfUserNames = ListOfUserNamesUnique,                          ImageTitle = ImageTitle                          )    def showPost(self, ListOfUserNames, ImageFName='ImageOfPost.jpg'):        Nwords = len(self.Users_dict)        ListOfUserNamesUnique = list(set(ListOfUserNames))        # users unknown to the model are removed        for Name in ListOfUserNamesUnique:            try:  # in case the Name is new for the model                self.Users_dict[Name]            except:                ListOfUserNamesUnique.remove(Name)                pass        if len(ListOfUserNamesUnique)>0:            pca_vis.pca_plot(pca_vis.getMtxFromUserNames(ListOfUserNamesUnique),                             ListOfUserNames = ListOfUserNamesUnique,                             ImageFName = ImageFName                             )        else:            print "Model's unaware of the users of the post, no output picture"