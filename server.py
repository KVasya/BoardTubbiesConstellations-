# coding: utf-8

import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
from shutil import copyfile

path_to_flask_workshop = '/home/Vasya/mysite/'

UPLOAD_FOLDER = path_to_flask_workshop + 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp'])

# local paths to files (images, texts)
p_img = 'static/_images/map.jpg'
p_txt = 'static/sub.txt'

SHOWED_IMAGE = path_to_flask_workshop + p_img
SHOWED_TEXT = path_to_flask_workshop + p_txt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        for f_idx in request.files:
            file = request.files[f_idx]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                path_to_uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path_to_uploaded_file)
                if f_idx == 'pic':
                    copyfile(path_to_uploaded_file, SHOWED_IMAGE)
                elif f_idx == 'text':
                    copyfile(path_to_uploaded_file, SHOWED_TEXT)
        return redirect(url_for('upload_file'))
        
    with open(SHOWED_TEXT, 'rb') as tf :
        plain_text = tf.read()
        
    return render_template('index.html', img_ref = p_img, txt_data = plain_text)

if __name__ == '__main__':
    #app.debug = True
    app.run()