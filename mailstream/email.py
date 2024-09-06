from fastapi import FastAPI, HTTPException, Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
import os
import base64
from email.mime.text import MIMEText

app = FastAPI()

# Scopes needed for sending and retrieving emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

# Path to the credentials file downloaded from Google Cloud Console
CREDENTIALS_FILE = 'path/to/credentials.json'

# In-memory storage for credentials
credentials = None

def get_gmail_service():
    global credentials
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=credentials)

@app.post("/send_email")
async def send_email(to: str, subject: str, body: str):
    try:
        service = get_gmail_service()
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        message = {'raw': raw}
        
        service.users().messages().send(userId='me', body=message).execute()
        return {"status": "Email sent successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_emails")
async def get_emails():
    try:
        service = get_gmail_service()
        results = service.users().messages().list(userId='me', maxResults=10).execute()
        messages = results.get('messages', [])
        
        emails = []
        for msg in messages:
            msg = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = msg['snippet']
            emails.append(snippet)
        
        return {"emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
