import pickleimport numpy as npimport matplotlib.pyplot as pltfrom unidecode import unidecodeFolderName = './'#_CnegEquals1'# plots row-vectors from matrix M and marks the points with names from ListOfUserNames# if SublistOfUserNames provided, part of ListOfUserNames is marked in red ( in contrast to green)def pca_plot(M, ListOfUserNames=[], SublistOfUserNames=[], ImageFName  = 'PostImage.jpg', ImageTitle=''):    N = M - np.mean(M, axis= 0)    covariance = N.T.dot(N)    U, S, V = np.linalg.svd(covariance)    #print 'U= ', U    #print 'U-V.T=', (U-V.T)    Xvec = U.T[:,0]    Xvec = Xvec/((Xvec.dot(Xvec.T))**.5)    pca_x_vals = N.dot(Xvec)    print 'np.shape(pca_x_vals)= ', np.shape(pca_x_vals)    Yvec = U.T[:,1]    Yvec = Yvec / ((Yvec.dot(Yvec.T)) ** .5)    pca_y_vals = N.dot(Yvec)    if ListOfUserNames!= []:        for i in xrange(len(ListOfUserNames)):            if ListOfUserNames[i] in SublistOfUserNames:                color = 'red'            else:                color = 'green'            plt.text(pca_x_vals[i], pca_y_vals[i], unidecode(ListOfUserNames[i]),            bbox=dict(facecolor= color, alpha=0.5))    plt.title(ImageTitle)    plt.xlim((np.min(pca_x_vals), np.max(pca_x_vals)))    plt.ylim((np.min(pca_y_vals), np.max(pca_y_vals)))    plt.plot(pca_x_vals, pca_y_vals, '.')    plt.savefig(ImageFName)    plt.show(block=False)    #print(U[0:2,:])    #print 'np.shape(U)= ', np.shape(U)def getMtxFromUserNames(ListOfUserNames):    Umtx = pickle.load(open(FolderName + 'Umtx.p', 'r'))    Vmtx = pickle.load(open(FolderName + 'Vmtx.p', 'r'))    User_dict = pickle.load(open(FolderName + 'Users_dict.p', 'r'))    subsetListOfIndices = [User_dict[User] for User in ListOfUserNames]    Umtx_subset = Umtx[subsetListOfIndices, :]    #pca_plot(Umtx_subset)    Vmtx_subset = Vmtx[subsetListOfIndices, :]    return Umtx_subset+Vmtx_subset    #pca_plot(Umtx_subset)