import random
import matplotlib.pyplot as plt
import numpy as np
from unidecode import unidecode
import PIL.Image


def combine2Images(ImageFName0, ImageFName1):

    def img2mtx(ImageFName):
        i = PIL.Image.open(ImageFName)
        return np.asarray(i)

    i_mtx_combined = np.hstack((img2mtx(ImageFName0), img2mtx(ImageFName1)))
    i = PIL.Image.fromarray(i_mtx_combined)
    i.save('PostImage.jpg')



class PlateLine:
    ''' Plate with names of users at image's outskirts'''
    def __init__(self):
        self.plate_arr = []


    def addPlate(self, x_min, x_max, UserName, color):
        level = 0
        PlaceFound = False

        while not PlaceFound:
            PlaceFound = True
            for plate in self.plate_arr:
                if (not ((x_min>=plate[1]) or (x_max<=plate[0]))) and level==plate[2]:
                    PlaceFound = False
                    level+=1

        self.plate_arr.append((x_min, x_max, level, UserName, color))
        return level





class Point:
    ''' Points depicting users '''
    def __init__(self, x,y, sym, color):
        self.x = x
        self.y = y
        self.sym = sym
        self.color = color


class Line:
    ''' Line between user pairs and connections to user name plates '''
    def __init__(self, (x0,y0), (x1, PlateLineMark, level)):

        self.p_User  = (x0, y0)
        self.p_Plate = (x1, PlateLineMark, level)


class Connection:
    ''' Line connecting 2 points '''
    def __init__(self, (x0,y0), (x1,y1), color, mark):

        self.User0 = (x0,y0)
        self.User1 = (x1,y1)
        self.color = color
        self.mark = mark




class Plot:

    def __init__(self, NofPlateLevels = 5, text_sym_w = 0.03, ImageFName  = 'PostImage.jpg' ):

        self.PlateLine_Top = PlateLine()
        self.PlateLine_Bot = PlateLine()
        self.Lines = []
        self.Points = []
        self.Connections = []
        self.NofPlateLevels = NofPlateLevels
        self.text_sym_w = text_sym_w
        self.xlim = (0,0)
        self.ylim = (0,1)
        self.ImageFName = ImageFName



    def addPoint(self, x, y, UserName, color):
        self.Points.append(Point(x,y,'o', color))

        x_right = x + self.text_sym_w*len(UserName)# right boundary of user name plate
        if random.random() >=0.5:
            level = self.PlateLine_Bot.addPlate(x, x_right, UserName, color)
            self.Lines.append( Line((x,y), (x, 'bottom', level)) )
        else:
            level = self.PlateLine_Top.addPlate(x, x_right, UserName, color)
            self.Lines.append( Line((x,y), (x, 'top', level)) )


    def addConnection(self, p0, p1, color = 'black', mark = ''):
        self.Connections.append(Connection(p0, p1, color, mark))



    def draw(self):


        plt.close()

        x_arr = []
        y_arr = []
        for Point in self.Points:
            x_arr.append(Point.x)
            y_arr.append(Point.y)
            plt.plot(Point.x, Point.y, Point.sym, color = Point.color)

        Dx = (np.max(x_arr) - np.min(x_arr)) / 1
        Dy = (np.max(y_arr) - np.min(y_arr)) / 1
        self.xlim = [np.min(x_arr)-Dx, np.max(x_arr)+Dx]
        self.ylim = [np.min(y_arr)-Dy/2, np.max(y_arr)+Dy/2]
        self.text_sym_h = Dy/self.NofPlateLevels



        self.yPlate_min =  self.ylim[0]
        self.yPlate_max =  self.ylim[1]
        for PlateLine in [self.PlateLine_Bot, self.PlateLine_Top]:
            for Plate in PlateLine.plate_arr:
                level = Plate[2]
                if PlateLine == self.PlateLine_Bot:
                    yPlate = self.ylim[0] - level*self.text_sym_h
                else:
                    yPlate = self.ylim[1] + level*self.text_sym_h

                if yPlate<self.yPlate_min:
                    self.yPlate_min = yPlate
                if yPlate>self.yPlate_max:
                    self.yPlate_max = yPlate

                color = Plate[4]
                alpha = 0.5
                plt.text(Plate[0], yPlate, unidecode(unicode(Plate[3])),
                          bbox=dict(facecolor=color, alpha=alpha))

        for Line in self.Lines:
            level = Line.p_Plate[2]
            if Line.p_Plate[1] =='bottom':
                yPlate = self.ylim[0] - level*self.text_sym_h
            else:
                yPlate = self.ylim[1] + level*self.text_sym_h
            plt.plot([Line.p_User[0], Line.p_Plate[0]], [Line.p_User[1], yPlate], '--', color = 'gray')


        for Connection in self.Connections:
            plt.plot([Connection.User0[0], Connection.User1[0]], [Connection.User0[1], Connection.User1[1]],
                     color = Connection.color)

            x_mark = (Connection.User0[0] + Connection.User1[0])/2
            y_mark = (Connection.User0[1] + Connection.User1[1])/2
            plt.text(x_mark, y_mark, Connection.mark)

        plt.xlim(self.xlim)
        plt.ylim((self.yPlate_min, self.yPlate_max))
        plt.show(block = False)
        plt.savefig(self.ImageFName)







