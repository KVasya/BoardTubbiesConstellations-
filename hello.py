# coding: utf-8
from flask import Flask, render_template, request, redirect
app = Flask(__name__)
email_addss = []
count = 0

@app.route('/')
def hello_world():
    u = u'Найди нашего Ботана!!'
    author = "Rashik"
    name = "Botan"    
    return render_template('index.html', author=author, name=name)

@app.route('/signup', methods = ['POST'])
def signup():
    email = request.form['email']
    email_addss.append(email)
    count = len(email_addss)
    #ext_people = request.form.get('extra_people', None)
    print email_addss, count
    #if (ext_people is not None) and int(ext_people) == 1 : print u"И кандидатов тоже!" 
    #print ext_people
    return redirect('/')
    
@app.route('/emails.html')
def emails():
    return render_template('emails.html', email_addresses=email_addss)

if __name__ == '__main__':
	app.run()
