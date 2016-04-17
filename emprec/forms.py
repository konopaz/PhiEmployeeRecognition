from wtforms import Form, TextField, PasswordField, DateTimeField, validators

class LoginForm(Form):
  username = TextField('Username', [validators.Length(min=4, max=25)])
  password = PasswordField('Password', [validators.Required()])

class CreateCertificateForm(Form):
    awardType = TextField('Type')
    awardRecipientName = TextField('Recipient Name')
    awardRecipientEmail = TextField('Recipient Email')
    awardCreatorEmail = TextField('Your Email')
    awardDateTime = DateTimeField('Date/Time')
