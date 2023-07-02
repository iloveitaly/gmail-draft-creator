from string import Template
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import os
import base64
import pickle
import csv

SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

import click

@click.command()
@click.argument('csv_file_path', type=click.Path(exists=True))
@click.argument('template_file_path', type=click.Path(exists=True))
@click.argument('subject', type=str)
@click.option('--dry-run', is_flag=True, default=False, help='Run script without creating drafts.')
def send_drafts_from_csv_cli(csv_file_path, template_file_path, subject, dry_run):
    send_drafts_from_csv(csv_file_path, template_file_path, subject, dry_run)

def send_drafts_from_csv(csv_file_path, template_file_path, subject, dry_run=False):
    with open(template_file_path, 'r') as template_file:
        template_string = template_file.read()

    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row.pop('email', None) or row.pop('Email', None)
            template_params = {k.lower(): v for k, v in row.items()}
            if email is not None:
                create_draft(email, subject, template_string, template_params, dry_run)

def create_draft(email, subject, template_string, template_params, dry_run=False):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message_template = Template(template_string)
    message_text = message_template.substitute(template_params)

    message = MIMEText(message_text)
    message['to'] = email
    message['subject'] = subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    raw_message = raw_message.decode()
    body = {'message': {'raw': raw_message}}

    if not dry_run:
        draft = service.users().drafts().create(userId='me', body=body).execute()


if __name__ == '__main__':
    send_drafts_from_csv_cli()
