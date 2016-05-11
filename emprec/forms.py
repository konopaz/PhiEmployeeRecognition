from wtforms import Form, TextField, PasswordField, DateTimeField, SelectField, validators

class LoginForm(Form):
  username = TextField('Username', [validators.Required(message="Please enter your username.")])
  password = PasswordField('Password', [validators.Required(message="Please enter your password.")])

class CreateCertificateForm(Form):
    awardTypeChoices = [('Employee of the Week', 'Employee of the Week'), ('Employee of the Month', 'Employee of the Month')]
    awardType = SelectField('Type', choices=awardTypeChoices)
    # awardType = TextField('Type', [validators.Required(message="Please enter the award type.")])
    awardRecipientName = TextField('Recipient Name', [validators.Required(message="Please enter the award recipient's name.")])
    awardRecipientEmail = TextField('Recipient Email', [validators.Required(message="Please enter the award recipient's email.")])
    awardCreatorEmail = TextField('Your Email', [validators.Required(message="Please enter your email.")])
    awardDateTime = DateTimeField('Date/Time', [validators.Required(message="Please enter the date/time.")])

class CreateAccountForm(Form):
    newname = TextField('Name', [validators.Required(message="Please enter your name.")])
    newusername = TextField('Username', [validators.Required(message="Please enter your username."), validators.Email(message="Username should be your email address")])
    newpassword = PasswordField('Password', [validators.Required(message="Please enter your password."), validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
