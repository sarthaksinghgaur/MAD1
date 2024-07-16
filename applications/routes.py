from flask import render_template, request, redirect, url_for, flash, session
from flask import current_app as app
from applications.database import db
from applications.models import *



# admin = Admin(username='adminniitm', password='123@adminniitm')
# db.session.add(admin)
# db.session.commit()


@app.route('/')
def home():
    return "hallow"

@app.route('/signup', methods=['GET', 'POST'])
def sigup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']

        new_user = User(username=username, password=password, name=name, email=email)
        db.session.add(new_user)
        db.session.commit()
        return "helllo "
    else:
        return "error"
    

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db.session.add(new_user)
        db.session.commit()
        return "helllo "
    else:
        return "error"
    
# @app.route('/admin_signin', methods=['GET', 'POST'])
# def signin():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         db.session.add(new_user)
#         db.session.commit()
#         return "helllo "
#     else:
#         return "error"

# @app.route('/', methods=['GET', 'POST'])
# def Admin_Dashboard():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         db.session.add(new_user)
#         db.session.commit()
#         return "helllo "
#     else:
#         return "error"

# def Influencer_Dashboard():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         db.session.add(new_user)
#         db.session.commit()
#         return "helllo "
#     else:
#         return "error"
    
# def Sponsor_Dashboard():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         db.session.add(new_user)
#         db.session.commit()
#         return "helllo "
#     else:
#         return "error"