from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash
import functools
import logging

DEBUG = True
LOGGING_LOCATION = 'application.log'
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

application = Flask(__name__)
application.config.from_object(__name__)
#used for session cookie encryption
application.secret_key = 'somesecretkeyhere'
handler = logging.FileHandler(application.config['LOGGING_LOCATION'])
handler.setLevel(application.config['LOGGING_LEVEL'])
formatter = logging.Formatter(application.config['LOGGING_FORMAT'])
handler.setFormatter(formatter)
application.logger.addHandler(handler)

def login_required(f):
  @functools.wraps(f)
  def decorator_function(*args, **kwargs):
    if 'username' not in session:
      application.logger.debug('auth redirect')
      return redirect(url_for('login'))
    return f(*args, **kwargs)
  return decorator_function

@login_required
@application.route('/')
def home():
  return render_template('home.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    application.logger.debug('handling login post')
    session['username'] = request.form['username']
    return redirect(url_for('home'))

  return render_template('login.html')

@login_required
@application.route('/create')
def create():
  return render_template('create.html')

@login_required
@application.route('/view')
def view():
  return render_template('view.html')

@application.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('login'))

if __name__ == '__main__':
  application.run()
