# -*- coding: utf-8 -*-

import requests
from time import sleep


# url to our upload service, that is @app.route('/upload', ...)
url = "http://127.0.0.1:5000/upload"

''' Testing part '''
# from glob import glob

# global_path = 'D:/BOARD_PROJECT/test_images/'
# fpostfix = '.bmp'

# fyles = glob(global_path + '*' + fpostfix)

# for f in fyles :
    # file = {'file': open(f, 'rb')}
    # r = requests.post(url, files=file)
    # sleep(10)
''' Testing part ENDs'''

img_to_sent = 'D:/BOARD_PROJECT/test_images/1.bmp' # write your own path + filename

while True:
    # opens img_to_sent file, constructs a dict from data (img_to_sent)
    file = {'file': open(img_to_sent, 'rb')}
    
    # sends the image to the server via post request
    r = requests.post(url, files=file)
    
    # waits 10 sec. before sending again.
    sleep(10) # One SHOULD have a condition when it's to send POST request but now it's just wait 10s. 

