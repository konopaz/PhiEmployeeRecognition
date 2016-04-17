import functools
import logging
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash
from forms import LoginForm, CreateCertificateForm
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
    if row is not None:
      session['username'] = form.username.data
      return redirect(url_for('home'))
  return render_template('login.html', form=form)

@app.route('/create')
@login_required()
def create():
    form = CreateCertificateForm()
    #prefill form with user's username (should be their email)
    form.awardCreatorEmail.data = session['username']
    form.awardDateTime.data = datetime.utcnow()
    return render_template('create.html', form=form)

@app.route('/view')
@login_required()
def view():
  return render_template('view.html')

@app.route('/confirmcert', methods=['GET', 'POST'])
@login_required()
def confirmcert():
    form = CreateCertificateForm(request.form)
    if request.method == 'POST':
        certData = form.awardType.data, form.awardRecipientName.data, form.awardRecipientEmail.data, form.awardCreatorEmail.data, form.awardDateTime.data
        app.logger.info("Certificate Data = ", certData)
        # return redirect(url_for('confirmcert'), info="green")
        return render_template('confirmcert.html', certData=certData)
    return redirect(url_for('create'))

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('login'))
