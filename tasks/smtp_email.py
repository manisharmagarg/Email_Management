import boto.ses
from conf.config import AWS_ACCESS_KEY, AWS_REGION, AWS_SECRET_KEY, \
    AWS_FROM_ADDRESS, LOGIN_EMAIL, LOGIN_PASSWORD
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SmtpEmail(object):

    AWS_ACCESS_KEY = AWS_ACCESS_KEY
    AWS_REGION = AWS_REGION
    FROM_ADDRESS = AWS_FROM_ADDRESS
    AWS_SECRET_KEY = AWS_SECRET_KEY
    FORMAT = 'html'

    def __init__(self, email_address, subject, html):
        self.email_address = email_address
        self.subject = subject
        self._html = html

    def send(self):
        s = smtplib.SMTP_SSL(host='smtp.gmail.com', port=465)
        # s.starttls()
        s.login(LOGIN_EMAIL, LOGIN_PASSWORD)

        # For each contact, send the email:
        msg = MIMEMultipart()  # create a message

        # setup the parameters of the message
        msg['From'] = LOGIN_EMAIL
        msg['To'] = self.email_address
        msg['Subject'] = self.subject

        # add in the message body
        msg.attach(MIMEText(self._html, 'html'))

        # send the message via the server set up earlier.
        s.send_message(msg)
        del msg