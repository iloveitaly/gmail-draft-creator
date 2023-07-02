
## Generating a Gmail API Token

1. Navigate to the Google Cloud Console. https://console.developers.google.com/
2. Create a new project or select an existing one.
3. Go to "APIs & Services" -> "Library" and enable the Gmail API.
4. Navigate to "APIs & Services" -> "Credentials".
5. Click "Create Credentials" -> "OAuth client ID".
6. Select "Desktop app" as the application type, then click "Create".
7. Download the JSON file, rename it to `credentials.json`, and place it in the root of your project.
8. Run the script and oauth into your account

### Scopes Needed

* https://www.googleapis.com/auth/gmail.compose
* https://www.googleapis.com/auth/gmail.readonly
* https://www.googleapis.com/auth/calendar.readonly
* https://www.googleapis.com/auth/calendar.event