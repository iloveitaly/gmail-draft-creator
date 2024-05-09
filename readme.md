# Gmail Drafter: Create Mail Merge Drafts

Simple tool to take a CSV and a template and create drafts in your Gmail. Useful for sending emails to large-ish numbers
of people where you want to slightly customize the emails for each user. You can quickly run through drafts, customize it, and send.

## Installation

```shell
pip install -U gmail-draft-creator
```

## Usage

```shell
Usage: gmail-draft-creator [OPTIONS]

Options:
  --csv PATH       Path to the CSV file.  [required]
  --template PATH  Path to the template file.  [required]
  --subject TEXT   Subject for the email drafts.
  --dry-run        Run script without creating drafts.
  --help           Show this message and exit.
```

You can also import the `create_draft` function and use it in your own scripts.

### CSV Files

Must contain an `email` column (case insensitive).

Each column in the CSV is passed as a parameter to the provided template. The column name is stripped of whitespace, lowercased, and stripped all non-alpha characters. For example, a column named `First Name` would be passed as `$firstname` in the template.

### Template Files

You can include subject line and variables in the template file:

```text
Subject: Hello $NAME

Hi, here's another ${REASON} why I'm emailing you.
```

### CSV Files

A CSV file that would work with this template might be something like this:

```
Email,Name,Reason,OtherColumn,...
joe@test.com,Joe,reminder,...
jeff@email.com,Jeff,sales pitch,...
```

## Setup

You need to create a "OAuth 2.0 Client IDs" which has to be done with a Google Workspace (gsuite). This will not work on a personal gmail account (unless you create a app on a workspace and add your personal account as a test account).

### Generating a Gmail API Token

1. Navigate to the Google Cloud Console. https://console.developers.google.com/
2. Create a new project or select an existing one.
3. Go to "APIs & Services" -> "Library" and enable the Gmail API.
4. Navigate to "APIs & Services" -> "Credentials".
5. Click "Create Credentials" -> "OAuth client ID".
6. Select "Desktop app" as the application type, then click "Create".
7. Download the JSON file, rename it to `credentials.json`, and place it in the root of this project.
8. Run the script and oauth into your account

If you want to edit scopes on an existing application, you can:

1. OAuth Consent Screen
2. Edit
3. Continue to step 2
4. Add or remove scopes
5. Add scopes and save

#### Credential Scopes Needed

Two main scopes are required for this:

* `https://www.googleapis.com/auth/gmail.compose`
* `https://www.googleapis.com/auth/gmail.readonly`

Some other scopes I'd add so you can reuse the credentials in other projects, [like gmailctl](https://github.com/mbrt/gmailctl) or calendar scripts:

* `https://www.googleapis.com/auth/calendar.readonly`
* `https://www.googleapis.com/auth/calendar.event`
* `https://www.googleapis.com/auth/gmail.labels`
* `https://www.googleapis.com/auth/gmail.settings.basic`

## TODO

- [ ] add credentials as a command line argument
- [ ] add serialized token as a CLI argument
