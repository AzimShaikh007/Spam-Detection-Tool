import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Warning: credentials.json not found. Cannot connect to Gmail API.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def setup_watch():
    pubsub_topic = os.environ.get('PUBSUB_TOPIC')
    if not pubsub_topic:
        print("Warning: PUBSUB_TOPIC not found in .env")
        return
        
    service = get_gmail_service()
    if not service:
        return
    try:
        request = {
            'labelIds': ['INBOX'],
            'topicName': pubsub_topic
        }
        response = service.users().watch(userId='me', body=request).execute()
        print(f"Gmail watch setup successful. History ID: {response.get('historyId')}")
    except HttpError as error:
        print(f'An error occurred setting up watch: {error}')

def get_message(message_id: str) -> dict:
    service = get_gmail_service()
    if not service:
        return {}
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload = message.get('payload', {})
        headers = payload.get('headers', [])
        
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        
        body = ''
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data')
                    if data:
                        body += base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = payload['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                
        return {
            'id': message_id,
            'sender': sender,
            'subject': subject,
            'body': body,
            'timestamp': message.get('internalDate')
        }
    except HttpError as error:
        print(f'An error occurred fetching message: {error}')
        return {}

def get_or_create_spam_label(service):
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        for label in labels:
            if label['name'] == '⚠ Spam-Detected':
                return label['id']
                
        label_object = {
            'messageListVisibility': 'show',
            'name': '⚠ Spam-Detected',
            'labelListVisibility': 'labelShow',
            'color': {
                'backgroundColor': '#cc3a21',
                'textColor': '#ffffff'
            }
        }
        created_label = service.users().labels().create(userId='me', body=label_object).execute()
        return created_label['id']
    except HttpError as error:
        print(f'An error occurred handling label: {error}')
        return None

def apply_spam_label(message_id: str):
    service = get_gmail_service()
    if not service:
        return
    label_id = get_or_create_spam_label(service)
    if not label_id:
        return
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'addLabelIds': [label_id]}
        ).execute()
        print(f"Applied spam label to {message_id}")
    except HttpError as error:
        print(f'An error occurred applying label: {error}')

def remove_spam_label(message_id: str):
    service = get_gmail_service()
    if not service:
        return
    label_id = get_or_create_spam_label(service)
    if not label_id:
        return
    try:
        service.users().messages().modify(
            userId='me',
            id=message_id,
            body={'removeLabelIds': [label_id]}
        ).execute()
        print(f"Removed spam label from {message_id}")
    except HttpError as error:
        print(f'An error occurred removing label: {error}')
