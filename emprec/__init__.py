import functools
import logging
import sqlite3
import StringIO, csv
import json
from sets import Set
from flask import Flask, request, session, g, redirect, url_for, \
  abort, render_template, flash, get_flashed_messages, jsonify, send_file, make_response, \
  Response
from forms import LoginForm, CreateCertificateForm, CreateAccountForm
from datetime import datetime
from emprec.pdfcert import pdfcert
from emprec.mailcert import mailcert

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

@app.route('/testviewpdf')
def testviewpdf():
  cursor = g.db.execute("select * from awards where id = 8")
  award = cursor.fetchone()
  award['date'] = datetime.utcnow().strftime("%B %-d, %Y")
  cert = pdfcert("./blank-certificate.jpg")
  cert.writeAward(award)
  return send_file(cert.save(), as_attachment=False, attachment_filename="certificate.pdf", mimetype="application/pdf")

@app.route('/testemailpdf')
def testemailpdf():
  cursor = g.db.execute("select * from awards where id = 8")
  award = cursor.fetchone()
  cert = pdfcert("./blank-certificate.jpg")
  cert.writeAward(award)
  mailcert(award["recipientEmail"],
    'Interesting subject line goes here.', 'Some message body goes here.', cert.save())
  return "sent email to %s" % award["recipientEmail"]

@app.route('/')
@login_required()
def home():
  return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  form = LoginForm(request.form)
  if request.method == 'POST' and form.validate():
    cursor = g.db.execute('select * from users where username = ? and password = ?',\
      [form.username.data, form.password.data])
    row = cursor.fetchone()
    session['admin'] = False
    app.logger.debug(row)
    if row is not None:
      session['username'] = form.username.data
      if row['usertype'] == 'admin':
          session['admin'] = True
      return redirect(url_for('home'))
  return render_template('login.html', form=form)

@app.route('/addUser', methods=['GET', 'POST'])
@login_required()
def addUser():
    form = CreateAccountForm(request.form)
    if request.method == 'POST' and form.validate():
        # save user in the database
        if session.get('username') is not None:
            app.logger.debug("User is logged in so it must be an admin editing users")
            usertype = form.usertype.data
            app.logger.debug(form.usertype.data)
            cursor = g.db.execute('insert into users(name, username, password, usertype) values(?, ?, ?, ?)',\
            [form.newname.data, form.newusername.data, form.newpassword.data, usertype])
            # log the user in
            g.db.commit()
            app.logger.debug('New user created')
            allUsersQuery = g.db.execute('select * from users')
            allUsers = allUsersQuery.fetchall()
            # session['data'] = {'allUsers': allUsers, 'form': form, 'message': 'User has been addedd'}
            session['message'] = { 'message': 'User has been added'}
            return redirect(url_for('userOptions'))
            # return render_template('useroptions.html', form=form, message="User has been added", allUsers=allUsers)
        else:
            app.logger.debug("User is not logged in- a new user is being created")
            app.logger.debug("Form field has data")
            usertype = form.usertype.data
            app.logger.debug(form.usertype.data)
            cursor = g.db.execute('insert into users(name, username, password, usertype) values(?, ?, ?, ?)',\
            [form.newname.data, form.newusername.data, form.newpassword.data, usertype])
            # log the user in
            g.db.commit()
            app.logger.debug('New user created')
            session['username'] = form.newusername.data
            return redirect(url_for('userOptions'))
    title = "Add a New User"
    return render_template('adduser.html', form=form, title=title)

@app.route('/createAccount', methods=['GET', 'POST'])
def createAccount():
    app.logger.debug('In create account!')
    form = CreateAccountForm(request.form)
    if request.method == 'POST' and form.validate():
        usertype = form.usertype.data
        app.logger.debug(form.usertype.data)
        cursor = g.db.execute('insert into users(name, username, password, usertype) values(?, ?, ?, ?)',\
        [form.newname.data, form.newusername.data, form.newpassword.data, usertype])
        # log the user in
        g.db.commit()
        app.logger.debug('New user created')
        session['username'] = form.newusername.data
        return redirect(url_for('home'))
    title = "Create An Account"
    return render_template('createaccount.html', url="base.html", form=form, title=title)

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

        # send the email of the award
        award = {
          'recipientName': form.awardRecipientName.data,
          'date': form.awardDateTime.data.strftime("%B %-d, %Y"),
          'type': form.awardType.data
        }
        cert = pdfcert("./blank-certificate.jpg")
        cert.writeAward(award)
        mailcert(form.awardRecipientEmail.data,
          'Your %s certificate is here.' % award['type'],
          'Please find the certificate attached.',
          cert.save())

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

@app.route('/download/<int:awardid>')
@login_required()
def download(awardid):
  cursor = g.db.execute("select * from awards where id = %d" % awardid)
  award = cursor.fetchone()
  award['date'] = datetime.utcnow().strftime("%B %-d, %Y")
  cert = pdfcert("./blank-certificate.jpg")
  cert.writeAward(award)
  return send_file(cert.save(), as_attachment=False, attachment_filename="certificate.pdf", mimetype="application/pdf")

@app.route('/_sendCert', methods=['POST'])
@login_required()
def sendCert():

  certId = (int)(request.form['id'])

  cursor = g.db.execute("select * from awards where id = %d" % certId)
  award = cursor.fetchone()
  cert = pdfcert("./blank-certificate.jpg")
  cert.writeAward(award)
  mailcert(award["recipientEmail"],
    'Your %s certificate is here.' % award['type'],
    'Please find the certificate attached.',
    cert.save())

  data = {
    'success': True
  }
  js = json.dumps(data)
  resp = Response(js, status=200, mimetype="application/json")
  return resp

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
    sessionMessage = session.pop('message', [])
    app.logger.debug(sessionMessage)
    if sessionMessage:
        message = sessionMessage['message']
    else:
        message = ''
    return render_template('userOptions.html', allUsers=allUsers, form=form , message=message)

@app.route('/editUser/<username>/', methods=['GET', 'POST'])
@login_required()
def editUser(username):
    form = CreateAccountForm(request.form)
    app.logger.debug("Username", username)
    if request.method == 'POST' and username == 'None':
        updateQuery = g.db.execute('update users set name=?, usertype=?, username=? where username=?', \
        [form.newname.data, form.usertype.data, form.newusername.data, session['oldusername']])
        g.db.commit()
        allUsersQuery = g.db.execute('select * from users')
        allUsers = allUsersQuery.fetchall()
        session['oldusername'] = ''
        session['message'] = {'message': 'User has been edited'}
        return redirect(url_for('userOptions'))
    else:
        allUsersQuery = g.db.execute('select * from users')
        allUsers = allUsersQuery.fetchall()
        editUserQuery = g.db.execute('select * from users where username=?', \
        [username])
        editUser = editUserQuery.fetchall()
        form.newname.data = editUser[0]['name']
        form.newusername.data = editUser[0]['username']
        form.usertype.data = editUser[0]['usertype']
        app.logger.debug(editUser[0])
        session['oldusername'] = editUser[0]['username']
    return render_template('edituser.html', editUser=editUser, form=form)

@app.route('/deleteUser/<username>')
@login_required()
def deleteUser(username):
    form = CreateAccountForm(request.form)
    app.logger.debug(username)
    if username == session['username']:
        session['message'] = {'message': 'Logged in user cannot be deleted'}
    else:
        query = g.db.execute('delete from users where username = ?',\
        [username])
        g.db.commit()
        session['message'] = {'message': 'User has been deleted'}
    return redirect(url_for('userOptions'))

@app.route('/handleQuery')
@login_required()
def handleQuery():
    awardType = request.args.get('type')
    recipientName = request.args.get('recipientName')
    recipientEmail = request.args.get('recipientEmail')
    creator = request.args.get('creator')
    # date = request.args.get('date')
    sortField = request.args.get('sortField')
    queryType = request.args.get('queryType')
    chartType = request.args.get('chartType')
    app.logger.debug(queryType)
    awardResults = ''
    title = ''

    # change this query to reflect what the admin entered
    # query = g.db.execute('select * from awards')
    # results = query.fetchall()
    # app.logger.debug(results)
    if queryType:
        app.logger.debug("QUERY TYPE IS SET")
        if queryType == 'numRcvdPU':
            # Number of awards received per person
            queryNumAwardsRcvdPU = g.db.execute('select recipientName, recipientEmail, count(recipientEmail) as numAwards from awards group by recipientEmail')
            awardResults = queryNumAwardsRcvdPU.fetchall()
            app.logger.debug(awardResults)
            title = "Number of Awards Received Per User"
        elif queryType == 'numGivenPU':
            # Number of awards given per person
            queryNumAwardsGivenPU = g.db.execute('select creatorEmail, count(creatorEmail)as numAwards from awards group by creatorEmail')
            awardResults = queryNumAwardsGivenPU.fetchall()
            app.logger.debug(awardResults)
            title = "Number of Awards Given Per User"
        elif queryType == 'numEachType':
            # Number of awards of each type
            queryNumAwardsEachType = g.db.execute('select type as awardType, count(type) as numAwards from awards group by type')
            awardResults = queryNumAwardsEachType.fetchall()
            app.logger.debug(awardResults)
            title = "Number of Each Type of Award"
        else:
            queryAllAwards = g.db.execute('select * from awards')
            awardResults = queryAllAwards.fetchall()
            app.logger.debug(awardResults)
            title = "All Awards"
    else:
        app.logger.debug("QUERY TYPE IS NOT SET")
        # Query for all awards then filter by what the user entered
        # queryAllAwards = g.db.execute('select * from awards')
        # awardResults = queryAllAwards.fetchall()
        # app.logger.debug(awardResults)

        # Handle user input boxes
        if awardType:
            app.logger.debug(awardType)
            queryForAwardType = g.db.execute('select * from awards where type = ?',\
            [awardType])
            awardResults = queryForAwardType.fetchall()
            title = 'All Awards of Type: ' + awardType
            app.logger.debug(awardResults)
        elif recipientName:
            app.logger.debug(recipientName)
            queryForRecipientName = g.db.execute('select * from awards where recipientName = ?',\
            [recipientName])
            awardResults = queryForRecipientName.fetchall()
            title = 'Number of each type for ' + recipientName
            app.logger.debug(awardResults)
        elif recipientEmail:
            app.logger.debug(recipientEmail)
            queryForRecipientEmail = g.db.execute('select * from awards where recipientEmail = ?',\
            [recipientEmail])
            awardResults = queryForRecipientEmail.fetchall()
            title = 'Number of each type for ' + recipientEmail
            app.logger.debug(awardResults)
        elif creator:
            app.logger.debug(creator)
            queryForCreator = g.db.execute('select * from awards where creatorEmail = ?',\
            [creator])
            awardResults = queryForCreator.fetchall()
            app.logger.debug(awardResults)
        else:
            queryAllAwards = g.db.execute('select * from awards')
            awardResults = queryAllAwards.fetchall()
            app.logger.debug(awardResults)
            title = "All Awards"

    final = {
        'queryType': queryType,
        'chartType': chartType,
        'queryResults': awardResults,
        'title': title
    };

    # pass query back to js to create chart
    session['queryResults'] = awardResults
    session['final'] = final
    return jsonify(final=final)

@app.route('/exportToCSV', methods=['GET', 'POST'])
@login_required()
def exportToCSV():
    si = StringIO.StringIO()
    cw = csv.writer(si)
    cw.writerow([session['final']['title']])

    if session['final']['queryType']:
        if session['final']['queryType'] == 'numRcvdPU':
            cw.writerow(['Email', 'Number of Awards'])
            for row in session['queryResults']:
                cw.writerow([row["recipientEmail"], row["numAwards"]])
        elif session['final']['queryType'] == 'numGivenPU':
            cw.writerow(['Email', 'Number of Awards'])
            for row in session['queryResults']:
                cw.writerow([row["creatorEmail"], row["numAwards"]])
        elif session['final']['queryType'] == 'numEachType':
            cw.writerow(['Type', 'Number of Awards'])
            for row in session['queryResults']:
                cw.writerow([row["awardType"], row["numAwards"]])
    else:
        cw.writerow(['Date', 'Recipient Name', 'Recipient Email', 'Creator Email', 'Type'])
        for row in session['queryResults']:
            cw.writerow([row["date"], row["recipientName"], row["recipientEmail"], row["creatorEmail"], row["type"]])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=query.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('login'))
