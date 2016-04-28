import functools
import logging
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash
from forms import LoginForm, CreateCertificateForm, CreateAccountForm
from datetime import datetime

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
        message = "Thanks! Your award has been submitted."
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
    # for award in row:
    #     app.logger.debug(award)

    return render_template('view.html', received=awardsReceived, given=awardsGiven)

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
