# Gmail Drafter: Create Mail Merge Drafts

Simple tool to take a CSV and a template and create drafts in your Gmail. Useful for sending emails to large-ish numbers
of people where you want to slightly customize the emails for each user. You can quickly run through drafts, customize it, and send.

## Installation

```shell
pip install gmail-draft-creator
```

## Usage

```shell
Usage: gmail-draft-creator [OPTIONS]

Options:
  --csv PATH       Path to the CSV file.  [required]
  --template PATH  Path to the template file.  [required]
  --subject TEXT   Subject for the email drafts.  [required]
  --dry-run        Run script without creating drafts.
  --help           Show this message and exit.

```

You can also import the `create_draft` function and use it in your own scripts.

### Template Files

You can include subject line and variables in the template file:

```text
Subject: Hello $NAME

Hi, here's another ${REASON} why I'm emailing you.
```

## Setup

### Generating a Gmail API Token

1. Navigate to the Google Cloud Console. https://console.developers.google.com/
2. Create a new project or select an existing one.
3. Go to "APIs & Services" -> "Library" and enable the Gmail API.
4. Navigate to "APIs & Services" -> "Credentials".
5. Click "Create Credentials" -> "OAuth client ID".
6. Select "Desktop app" as the application type, then click "Create".
7. Download the JSON file, rename it to `credentials.json`, and place it in the root of your project.
8. Run the script and oauth into your account

#### Credential Scopes Needed

* https://www.googleapis.com/auth/gmail.compose
* https://www.googleapis.com/auth/gmail.readonly
* https://www.googleapis.com/auth/calendar.readonly
* https://www.googleapis.com/auth/calendar.event

Some of these are in place for possible future improvements.

## TODO

- [ ] add credentials as a command line argument
- [ ] add serialized token as a CLI argument