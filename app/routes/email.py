# Class that will be used to send emails from an SMTP server for password reset
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import imaplib
import time


class EmailClient:
    def __init__(self, smtp_username, smtp_password, smtp_server='smtp.titan.email', smtp_port=587, imap_server='imap.titan.email', imap_port=993):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.imap_server = imap_server
        self.imap_port = imap_port

    def send_email(self, to, subject, body):
        message = MIMEText(body, 'plain', 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = self.smtp_username
        message['To'] = to

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.smtp_username, to, message.as_string())
                return message
        except Exception as e:
            print(e)
            raise Exception('Unable to send email')

    def move_mail_to_sent_items(self, to, subject, body):
        # Append the sent email to the IMAP server's "Sent" folder
        message = MIMEText(body, 'plain', 'utf-8')
        message['Subject'] = Header(subject, 'utf-8')
        message['From'] = self.smtp_username
        message['To'] = to

        try:
            with imaplib.IMAP4_SSL(self.imap_server, self.imap_port) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.append('Sent', '', imaplib.Time2Internaldate(
                    imaplib.Time2Internaldate(imaplib.Time2Internaldate(time.time()))), message.as_bytes())
        except imaplib.IMAP4.error as e:
            print('Error appending email to "Sent" folder:', str(e))
            raise Exception('Unable to move email to "Sent" folder')
