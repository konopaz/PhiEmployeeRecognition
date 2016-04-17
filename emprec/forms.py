from wtforms import Form, TextField, PasswordField, DateTimeField, validators

class LoginForm(Form):
  username = TextField('Username', [validators.Required(message="Please enter your username.")])
  password = PasswordField('Password', [validators.Required(message="Please enter your password.")])

class CreateCertificateForm(Form):
    awardType = TextField('Type')
    awardRecipientName = TextField('Recipient Name')
    awardRecipientEmail = TextField('Recipient Email')
    awardCreatorEmail = TextField('Your Email')
    awardDateTime = DateTimeField('Date/Time')
