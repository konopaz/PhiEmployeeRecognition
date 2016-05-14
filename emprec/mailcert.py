import smtplib, socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

socket.setdefaulttimeout(None)
HOST = 'smtp.gmail.com'
PORT = '587'
SENDER = 'osucs491phiemprec@gmail.com'
PASSWORD = 'Crazy!Talking&Horse'

def mailcert(to, subject, body, attachment):
  msg = MIMEMultipart()
  msg['From'] = SENDER
  msg['To'] = to
  msg['Subject'] = subject

  textPart = MIMEText(body)
  msg.attach(textPart)

  pdfPart = MIMEApplication(attachment.read())
  pdfPart.add_header('Content-Disposition', 'attachment', filename='certificate.pdf')
  msg.attach(pdfPart)

  smtp = smtplib.SMTP()
  smtp.connect(HOST, PORT)
  smtp.starttls()
  smtp.login(SENDER, PASSWORD)
  smtp.sendmail(SENDER, to, msg.as_string())
  smtp.close()
