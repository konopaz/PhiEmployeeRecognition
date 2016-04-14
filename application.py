from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash
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

@application.route('/')
def home():
  if 'username' in session:
    return render_template('home.html')
  return redirect(url_for('login'))

@application.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    application.logger.debug('handling login post')
    session['username'] = request.form['username']
    return redirect(url_for('home'))

  return render_template('login.html')

@application.route('/create')
def create():
  if 'username' in session:
    return render_template('create.html')
  return redirect(url_for('login'))

@application.route('/view')
def view():
  if 'username' in session:
    return render_template('view.html')
  return redirect(url_for('login'))

@application.route('/logout')
def logout():
  # log the user out and redirect to log in page
  return redirect(url_for('login'))

if __name__ == '__main__':
  application.run()
