import base64
import csv
import logging
import os
import pickle
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

import markdown
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

import click


@click.command()
@click.option("--csv", "csv_file_path", type=click.Path(exists=True), help="Path to the CSV file.", required=True)
@click.option(
    "--template", "template_file_path", type=click.Path(exists=True), help="Path to the template file.", required=True
)
@click.option("--subject", "subject", type=str, help="Subject for the email drafts.", required=True)
@click.option("--dry-run", is_flag=True, default=False, help="Run script without creating drafts.")
def send_drafts_from_csv_cli(csv_file_path, template_file_path, subject, dry_run):
    send_drafts_from_csv(csv_file_path, template_file_path, subject, dry_run)


def send_drafts_from_csv(csv_file_path, template_file_path, subject, dry_run=False):
    with open(template_file_path, "r") as template_file:
        template_string = markdown.markdown(template_file.read())

    with open(csv_file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = row.pop("email", None) or row.pop("Email", None)
            template_params = {k.lower(): v for k, v in row.items()}

            if email is not None:
                create_draft(email, subject, template_string, template_params, dry_run)


def create_draft(email, subject, template_string, template_params, dry_run=False):
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    service = build("gmail", "v1", credentials=creds)

    message_template = Template(template_string)
    message_text = message_template.substitute(template_params)

    # remove <p> and </p> tags if they are on the first line
    # this causes weird formatting in gmail
    first_line, remaining_text = message_text.split("\n", 1)
    first_line = re.sub(r"^<p>(.*)</p>$", r"\1", first_line)
    message_text = first_line + "\n" + remaining_text

    message = MIMEMultipart("alternative")
    message["to"] = email
    message["subject"] = subject
    message.attach(MIMEText(message_text, "html"))

    raw_message = base64.urlsafe_b64encode(message.as_bytes())
    raw_message = raw_message.decode()
    body = {"message": {"raw": raw_message}}

    if not dry_run:
        draft = service.users().drafts().create(userId="me", body=body).execute()

    logging.info(f"draft created for email: {email}")


def main():
    logging.basicConfig(level=logging.INFO)
    send_drafts_from_csv_cli()
