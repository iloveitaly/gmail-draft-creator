import base64
import csv
import logging
import os
import pickle
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

import click
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


@click.command()
@click.option("--csv", "csv_file_path", type=click.Path(exists=True), help="Path to the CSV file.", required=True)
@click.option(
    "--template", "template_file_path", type=click.Path(exists=True), help="Path to the template file.", required=True
)
@click.option("--subject", "subject", type=str, help="Subject for the email drafts.", required=False)
@click.option("--dry-run", is_flag=True, default=False, help="Run script without creating drafts.")
def send_drafts_from_csv_cli(csv_file_path, template_file_path, subject, dry_run):
    send_drafts_from_csv(csv_file_path, template_file_path, subject, dry_run)


def _process_template_string(raw_template_string):
    # if the first line in the file starts with "Subject: " pull that into a separate variable
    # and remove it from the template string
    first_line = raw_template_string.split("\n")[0]

    if first_line.startswith("Subject: "):
        subject = first_line.replace("Subject: ", "").strip()
        # remove first line from template string
        template_string = "\n".join(raw_template_string.split("\n")[1:])
    else:
        subject = None
        template_string = raw_template_string

    template_string = markdown.markdown(template_string.strip())

    return subject, template_string


def send_drafts_from_csv(csv_file_path, template_file_path, subject, dry_run):
    with open(template_file_path, "r") as template_file:
        template_string = template_file.read()

    with open(csv_file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            email = None

            for key in row.keys():
                if key.lower() == 'email':
                    email = row[key]
                    break

            if email:
                email = email.strip()

            if email is None:
                print("No email found for row, skipping")
                continue

            def normalize_key(key):
                cleaned_key = key.lower().strip()
                cleaned_key = re.sub(r'\W+', '', cleaned_key)
                return cleaned_key

            # each column in the CSV is passed as a parameter to the template
            template_params = {normalize_key(k): v.strip() for k, v in row.items()}

            if email is not None:
                create_draft(email, template_string, template_params, subject, dry_run)


# TODO this should really be much smarter
def _extract_credentials():
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

    return creds


def create_draft(email, template_string, template_params, subject=None, dry_run=False):
    creds = _extract_credentials()
    service = build("gmail", "v1", credentials=creds)

    template_subject, template_string = _process_template_string(template_string)

    if template_subject and subject:
        raise ValueError("Subject defined in both template and arguments, pick one")

    subject_template = template_subject or subject
    subject = Template(subject_template).substitute(template_params)

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
