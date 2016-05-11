import functools
import logging
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash, jsonify, send_file
from forms import LoginForm, CreateCertificateForm, CreateAccountForm
from datetime import datetime

import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw

from tempfile import NamedTemporaryFile
from shutil import copyfileobj
import os

DEBUG = True
DATABASE = './emprec.db'
LOGGING_LOCATION = 'application.log'
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

app = Flask(__name__)
app.config.from_object(__name__)
#used for session cookie encryption
app.secret_key = 'somesecretkeyhere'
handler = logging.FileHandler(app.config['LOGGING_LOCATION'])
handler.setLevel(app.config['LOGGING_LEVEL'])
formatter = logging.Formatter(app.config['LOGGING_FORMAT'])
handler.setFormatter(formatter)
app.logger.addHandler(handler)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def login_required():
  def wrapper(f):
    app.logger.debug('wrapping %s' % f)
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
      app.logger.debug('running login_required decorator')
      if 'username' not in session:
        app.logger.debug('auth redirect')
        return redirect(url_for('login'))
      return f(*args, **kwargs)
    return wrapped
  return wrapper

@app.before_request
def before_request():
    g.db = sqlite3.connect(app.config['DATABASE'])
    g.db.row_factory = dict_factory

@app.route('/testpdf')
def testpdf():
  #font = ImageFont.truetype("./emprec/fonts/DroidSansMono.ttf", 50)
  font = ImageFont.truetype("DroidSansMono.ttf", 50)
  img = Image.open("./blank-certificate.jpg")
  draw = ImageDraw.Draw(img)
  draw.text((500, 500), "Zac Konopa", (0, 0, 0), font=font)
  draw =ImageDraw.Draw(img)
  img.save("/tmp/testpdf.pdf", "PDF", Quality = 100)

  tmp = NamedTemporaryFile(mode="w+b", suffix="pdf")
  pdf = open("/tmp/testpdf.pdf", "rb")
  copyfileobj(pdf, tmp)
  pdf.close()
  os.remove("/tmp/testpdf.pdf")
  tmp.seek(0, 0)

  return send_file(tmp, as_attachment=True, attachment_filename="testpdf.pdf")

@app.route('/')
@login_required()
def home():
  app.logger.debug('hello!')
  return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate():
    cursor = g.db.execute('select username and password from users where username = ? and password = ?',\
      [form.username.data, form.password.data])
    row = cursor.fetchone()
    session['admin'] = False
    if row is not None:
      session['username'] = form.username.data
      if form.username.data == 'admin' and form.password.data == 'admin':
          session['admin'] = True
      return redirect(url_for('home'))
  return render_template('login.html', form=form)

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    app.logger.debug('In create account!')
    form = CreateAccountForm(request.form)
    if request.method == 'POST' and form.validate():
        # save user in the database
        cursor = g.db.execute('insert into users(name, username, password) values(?, ?, ?)',\
        [form.newname.data, form.newusername.data, form.newpassword.data])
        # log the user in
        g.db.commit()
        app.logger.debug('New user created')
        session['username'] = form.newusername.data
        return redirect(url_for('home'))
    return render_template('createaccount.html', form=form)

@app.route('/create', methods=['GET', 'POST'])
@login_required()
def create():
    form = CreateCertificateForm(request.form)
    #prefill form with user's username (should be their email)
    form.awardCreatorEmail.data = session['username']
    form.awardDateTime.data = datetime.utcnow()
    if request.method == 'POST' and form.validate():
        # save award in the database
        cursor = g.db.execute('insert into awards(type, recipientName, recipientEmail, creatorEmail, date) values(?, ?, ?, ?, ?)',\
        [form.awardType.data, form.awardRecipientName.data, form.awardRecipientEmail.data, form.awardCreatorEmail.data, form.awardDateTime.data])
        g.db.commit()
        flash('Thanks! Your award has been submitted.')
        return redirect(url_for('create'))
    return render_template('create.html', form=form)

@app.route('/view')
@login_required()
def view():
    awardsReceivedQuery = g.db.execute('select * from awards where recipientEmail = ?',\
      [session['username']])
    awardsReceived = awardsReceivedQuery.fetchall()
    awardsGivenQuery = g.db.execute('select * from awards where creatorEmail = ?',\
      [session['username']])
    awardsGiven = awardsGivenQuery.fetchall()

    return render_template('view.html', received=awardsReceived, given=awardsGiven)

@app.route('/adminQuery')
@login_required()
def adminQuery():
    return render_template('adminQuery.html')

@app.route('/userOptions')
@login_required()
def userOptions():
    form = CreateAccountForm(request.form)
    allUsersQuery = g.db.execute('select * from users')
    allUsers = allUsersQuery.fetchall()
    return render_template('userOptions.html', allUsers=allUsers, form=form)

@app.route('/deleteUsers')
@login_required()
def deleteUsers():
    app.logger.debug("In deleteUsers function")
    allUsersQuery = g.db.execute('select * from users')
    allUsers = allUsersQuery.fetchall()

    # get users that are checked
    # delete each user

    return render_template('userOptions.html', allUsers=allUsers, message="Delete was successful!")

@app.route('/handleQuery')
def handleQuery():
    awardType = request.args.get('type')
    recipientName = request.args.get('recipientName')
    recipientEmail = request.args.get('recipientEmail')
    creator = request.args.get('creator')
    date = request.args.get('date')
    sortField = request.args.get('sortField')
    chartType = request.args.get('chartType')

    # change this query to reflect what the admin entered
    query = g.db.execute('select * from awards')
    results = query.fetchall()
    usersQuery = g.db.execute('select username from users')
    usersResults = usersQuery.fetchall()
    final = {
        'users': usersResults,
        'query': results,
        'chartType': chartType
    };

    # pass query back to js to create chart
    return jsonify(final=final)

# @app.route('/confirmcert', methods=['GET', 'POST'])
# @login_required()
# def confirmcert():
#     form = CreateCertificateForm(request.form)
#     if request.method == 'POST' and form.validate():
#         certData = form.awardType.data, form.awardRecipientName.data, form.awardRecipientEmail.data, form.awardCreatorEmail.data, form.awardDateTime.data
#         app.logger.info("Certificate Data = ", certData)
#         return render_template('confirmcert.html', certData=certData)
#     return redirect(url_for('create'))

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('login'))
