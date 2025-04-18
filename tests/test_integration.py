"""
Gmail MCP Server Integration Tests
===============================

This test suite contains integration tests that verify the Gmail MCP Server's
ability to interact with the actual Gmail API. These tests:
- Make real API calls to Gmail
- Verify email retrieval functionality
- Test draft creation and management
- Check sent email access
- Validate search functionality

Usage:
------
1. Ensure you have activated your virtual environment:
   .\venv\Scripts\activate

2. Ensure you have valid Gmail credentials:
   - client_secret.json in project root or config directory
   - token.json (will be created on first run)

3. Run the tests:
   python -m pytest tests/test_integration.py -v

Note: These tests require valid Gmail OAuth credentials and will make actual
API calls to your Gmail account. They may create and delete test data
(like draft emails) during execution.
"""

import os
import pytest
from dotenv import load_dotenv
from src.server import GmailMCPServer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json
import base64
from email.mime.text import MIMEText

# Load environment variables
load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_credentials_file():
    """Get the path to the credentials file."""
    return os.getenv('GMAIL_CREDENTIALS_FILE', 'client_secret.json')

def get_token_file():
    """Get the path to the token file."""
    return os.getenv('GMAIL_TOKEN_FILE', 'token.json')

@pytest.fixture(scope="session")
def gmail_credentials():
    """Set up Gmail credentials for testing."""
    creds = None
    token_file = get_token_file()
    credentials_file = get_credentials_file()

    if not os.path.exists(credentials_file):
        pytest.skip(f"Credentials file {credentials_file} not found. Please set up Google Cloud Project first.")

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    return creds

@pytest.fixture(scope="session")
def server(gmail_credentials):
    """Create a GmailMCPServer instance with authentication."""
    server = GmailMCPServer()
    return server

def test_email_retrieval_integration(server):
    """Test real email retrieval from Gmail."""
    # Get emails from inbox
    result = server._get_gmail_service().users().messages().list(
        userId='me',
        maxResults=5
    ).execute()
    assert isinstance(result, dict)
    assert 'messages' in result

def test_draft_retrieval_integration(server):
    """Test real draft retrieval from Gmail."""
    # Get drafts
    result = server._get_gmail_service().users().drafts().list(
        userId='me',
        maxResults=5
    ).execute()
    assert isinstance(result, dict)
    assert 'drafts' in result

def test_sent_email_retrieval_integration(server):
    """Test real sent email retrieval from Gmail."""
    # Get sent emails
    result = server._get_gmail_service().users().messages().list(
        userId='me',
        labelIds=['SENT'],
        maxResults=5
    ).execute()
    assert isinstance(result, dict)
    assert 'messages' in result

def test_email_search_integration(server):
    """Test real email search functionality."""
    # Search for emails with query
    result = server._get_gmail_service().users().messages().list(
        userId='me',
        q='test',
        maxResults=5
    ).execute()
    assert isinstance(result, dict)
    assert 'messages' in result

def test_email_composition_integration(server):
    """Test real email composition and draft creation."""
    # Create a test draft
    message = MIMEText('This is a test draft.')
    message['to'] = 'test@example.com'
    message['subject'] = 'Test Draft'
    
    # Encode the message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    # Create the draft
    result = server._get_gmail_service().users().drafts().create(
        userId='me',
        body={'message': {'raw': encoded_message}}
    ).execute()
    assert isinstance(result, dict)
    assert 'id' in result
    
    # Clean up - delete the test draft
    server._get_gmail_service().users().drafts().delete(
        userId='me',
        id=result['id']
    ).execute() 