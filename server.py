# coding: utf-8

import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
from shutil import copyfile

path_to_flask_workshop = 'D:/flask-workshop/'

UPLOAD_FOLDER = path_to_flask_workshop + 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp'])

local_path_to_img = 'static/_images/map.jpg'
SHOWED_FILE = path_to_flask_workshop + local_path_to_img

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path_to_uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_to_uploaded_file)
            copyfile(path_to_uploaded_file, SHOWED_FILE)
            return redirect(url_for('upload_file'))
            
    return render_template('index.html', img_ref = local_path_to_img)

if __name__ == '__main__':
    #app.debug = True
    app.run()