from decouple import config
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def create_draft(email, name, subject, template):
    creds = config('GMAIL_API_TOKEN')

    service = build('gmail', 'v1', developerKey=creds)

    message = MIMEText(template)
    message['to'] = email
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    raw_message = raw_message.decode()
    body = {'raw': raw_message}

    draft = service.users().drafts().create(userId='me', body=body).execute()
