import boto.ses
from conf.config import AWS_ACCESS_KEY, AWS_REGION, AWS_SECRET_KEY, AWS_FROM_ADDRESS


class Email(object):

    AWS_ACCESS_KEY = AWS_ACCESS_KEY
    AWS_REGION = AWS_REGION
    AWS_FROM_ADDRESS = AWS_FROM_ADDRESS
    AWS_SECRET_KEY = AWS_SECRET_KEY
    FORMAT = 'html'

    def __init__(self, email_address, subject, html):
        self.email_address = email_address
        self.subject = subject
        self._html = html

    def send(self):

        aws_from_address = self.AWS_FROM_ADDRESS

        connection = boto.ses.connect_to_region(
            self.AWS_REGION,
            aws_access_key_id=self.AWS_ACCESS_KEY,
            aws_secret_access_key=self.AWS_SECRET_KEY)

        return connection.send_email(
            aws_from_address,
            self.subject,
            None,
            self.email_address,
            format=self.FORMAT,
            # text_body=self._text,
            html_body=self._html
        )

