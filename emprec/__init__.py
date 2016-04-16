from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash
import functools
import logging

DEBUG = True
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

@app.route('/')
@login_required()
def home():
  app.logger.debug('hello!')
  return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    app.logger.debug('handling login post')
    session['username'] = request.form['username']
    return redirect(url_for('home'))

  return render_template('login.html')

@app.route('/create')
@login_required()
def create():
  return render_template('create.html')

@app.route('/view')
@login_required()
def view():
  return render_template('view.html')

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('login'))
