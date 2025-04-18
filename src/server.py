"""
Gmail MCP Server implementation.
This module provides the core server functionality for Gmail integration using MCP.
"""

import base64
import os
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional, List, Dict, Any

import anyio

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from mcp.server.fastmcp import FastMCP
import logging

# Load environment variables
load_dotenv()

# Constants
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',  # Read/write access (no delete)
    'https://www.googleapis.com/auth/gmail.compose',  # Create/send emails
    'https://www.googleapis.com/auth/gmail.readonly'  # Read-only access
]
TOKEN_PATH = Path('token.json')
CREDENTIALS_PATH = Path('config/client_secret.json')

logger = logging.getLogger(__name__)

class GmailMCPServer:
    """Gmail MCP Server implementation."""
    
    def __init__(self, name: str = "gmail_mcp_server"):
        """Initialize the Gmail MCP server.
        
        Args:
            name: Name of the MCP server instance
        """
        self.mcp = FastMCP(name)
        self._setup_resources()
        self._setup_tools()
    
    def _get_gmail_service(self) -> Optional[object]:
        """Get authenticated Gmail service.
        
        Returns:
            Gmail API service object or None if authentication fails
        """
        creds = None
        
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                    logger.info("Credentials refreshed successfully.")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}", exc_info=True)
                    creds = None 
            
            if not creds or not creds.valid:
                logger.info("No valid credentials, starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_PATH), SCOPES)
                creds = flow.run_local_server(port=0) 
                logger.info("OAuth flow complete, credentials obtained.")
            
            logger.info("Saving credentials to token.json")
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        else:
            logger.info("Using existing valid credentials.")

        try:
            service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail service object built successfully.")
            return service
        except Exception as e:
            logger.error(f"Error building Gmail service: {e}", exc_info=True)
            return None
    
    def _format_messages(self, service, messages: List[Dict[str, Any]]) -> str:
        """Format messages for display.
        
        Args:
            service: Gmail API service object
            messages: List of message dictionaries
            
        Returns:
            Formatted message string
        """
        formatted_msgs = []
        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From', 'To', 'Date']
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            to = next((h['value'] for h in headers if h['name'] == 'To'), 'No Recipient')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            formatted_msgs.append(
                f"Message ID: {msg['id']}\n"
                f"From: {sender}\n"
                f"To: {to}\n"
                f"Date: {date}\n"
                f"Subject: {subject}\n"
                f"{'-'*50}\n"
            )
        
        return "\n".join(formatted_msgs)
    
    def _setup_resources(self):
        """Set up MCP resources."""

        @self.mcp.resource("test://hello")
        async def get_hello() -> str:
            logger.info("Executing get_hello")
            return "Hello from Minimal Resource!"

        @self.mcp.resource("gmail://inbox")
        async def get_emails() -> str:
            """Get emails from inbox."""
            max_results = 10
            logger.info(f"Executing get_emails with fixed max_results={max_results}")
            try:
                logger.info("Attempting to get Gmail service...")
                service = await anyio.to_thread.run_sync(self._get_gmail_service)
                if not service:
                    logger.warning("Failed to get Gmail service in get_emails")
                    return "Failed to authenticate Gmail service"
                logger.info("Gmail service obtained successfully.")

                logger.info("Attempting to list messages...")
                def _list_messages():
                    return service.users().messages().list(
                        userId='me',
                        maxResults=max_results
                    ).execute()
                results = await anyio.to_thread.run_sync(_list_messages)
                logger.info(f"List messages API call returned: {results}")

                messages = results.get('messages', [])
                if not messages:
                    logger.info("No messages found.")
                    return "No messages found."
                logger.info(f"Found {len(messages)} messages.")

                logger.info("Attempting to format messages...")
                formatted_response = await anyio.to_thread.run_sync(self._format_messages, service, messages)
                logger.info("Messages formatted successfully.")
                return formatted_response
            except Exception as e:
                logger.error(f"Error inside get_emails: {e}", exc_info=True)
                return f"Error retrieving messages: {str(e)}"

        @self.mcp.resource("gmail://drafts/{max_results}")
        async def get_drafts(max_results: int = 10) -> str:
            """Get email drafts."""
            logger.info(f"Executing get_drafts with max_results={max_results}")
            try:
                logger.info("Attempting to get Gmail service (get_drafts)...")
                service = await anyio.to_thread.run_sync(self._get_gmail_service)
                if not service:
                    logger.warning("Failed to get Gmail service in get_drafts")
                    return "Failed to authenticate Gmail service"
                logger.info("Gmail service obtained successfully (get_drafts).")

                logger.info("Attempting to list drafts...")
                def _list_drafts():
                    return service.users().drafts().list(
                        userId='me',
                        maxResults=max_results
                    ).execute()
                results = await anyio.to_thread.run_sync(_list_drafts)
                logger.info(f"List drafts API call returned: {results}")

                drafts = results.get('drafts', [])
                if not drafts:
                    logger.info("No drafts found.")
                    return "No drafts found."
                logger.info(f"Found {len(drafts)} drafts.")

                formatted_drafts = []
                logger.info("Formatting drafts...")
                for draft in drafts:
                    def _get_single_draft(draft_id):
                        return service.users().drafts().get(
                            userId='me',
                            id=draft_id,
                            format='metadata'
                        ).execute()
                    draft_data = await anyio.to_thread.run_sync(_get_single_draft, draft['id'])

                    message = draft_data['message']
                    headers = message['payload']['headers']
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    to = next((h['value'] for h in headers if h['name'] == 'To'), 'No Recipient')

                    formatted_drafts.append(
                        f"Draft ID: {draft['id']}\n"
                        f"To: {to}\n"
                        f"Subject: {subject}\n"
                        f"{'-'*50}\n"
                    )
                logger.info("Drafts formatted.")
                return "\n".join(formatted_drafts)
            except Exception as e:
                logger.error(f"Error inside get_drafts: {e}", exc_info=True)
                return f"Error retrieving drafts: {str(e)}"

        @self.mcp.resource("gmail://sent/{max_results}")
        async def get_sent_emails(max_results: int = 10) -> str:
            """Get sent emails."""
            logger.info(f"Executing get_sent_emails with max_results={max_results}")
            try:
                logger.info("Attempting to get Gmail service (get_sent_emails)...")
                service = await anyio.to_thread.run_sync(self._get_gmail_service)
                if not service:
                    logger.warning("Failed to get Gmail service in get_sent_emails")
                    return "Failed to authenticate Gmail service"
                logger.info("Gmail service obtained successfully (get_sent_emails).")

                logger.info("Attempting to list sent messages...")
                def _list_sent():
                    return service.users().messages().list(
                        userId='me',
                        labelIds=['SENT'],
                        maxResults=max_results
                    ).execute()
                results = await anyio.to_thread.run_sync(_list_sent)
                logger.info(f"List sent messages API call returned: {results}")

                messages = results.get('messages', [])
                if not messages:
                    logger.info("No sent messages found.")
                    return "No sent messages found."
                logger.info(f"Found {len(messages)} sent messages.")

                logger.info("Attempting to format sent messages...")
                formatted_response = await anyio.to_thread.run_sync(self._format_messages, service, messages)
                logger.info("Sent messages formatted successfully.")
                return formatted_response
            except Exception as e:
                logger.error(f"Error inside get_sent_emails: {e}", exc_info=True)
                return f"Error retrieving sent messages: {str(e)}"
    
    def _setup_tools(self):
        """Set up MCP tools."""
        @self.mcp.tool("search_emails")
        async def search_emails(query: str, max_results: int = 10) -> str:
            """Search emails using Gmail query."""
            logger.info(f"Executing search_emails with query='{query}', max_results={max_results}")
            try:
                logger.info("Attempting to get Gmail service (search_emails)...")
                service = await anyio.to_thread.run_sync(self._get_gmail_service)
                if not service:
                    logger.warning("Failed to get Gmail service in search_emails")
                    return "Failed to authenticate Gmail service"
                logger.info("Gmail service obtained successfully (search_emails).")

                logger.info("Attempting to search messages...")
                def _search():
                    return service.users().messages().list(
                        userId='me',
                        q=query,
                        maxResults=max_results
                    ).execute()
                results = await anyio.to_thread.run_sync(_search)
                logger.info(f"Search messages API call returned: {results}")

                messages = results.get('messages', [])
                if not messages:
                    logger.info("No messages found matching the query.")
                    return "No messages found matching the query."
                logger.info(f"Found {len(messages)} matching messages.")

                logger.info("Attempting to format search results...")
                formatted_response = await anyio.to_thread.run_sync(self._format_messages, service, messages)
                logger.info("Search results formatted successfully.")
                return formatted_response
            except Exception as e:
                logger.error(f"Error inside search_emails: {e}", exc_info=True)
                return f"Error searching messages: {str(e)}"

        @self.mcp.tool("compose_email")
        async def compose_email(to: str, subject: str, body: str, save_as_draft: bool = False) -> str:
            """Compose and send/save an email."""
            logger.info(f"Executing compose_email (To: {to}, Subject: {subject}, SaveAsDraft: {save_as_draft})")
            try:
                logger.info("Attempting to get Gmail service (compose_email)...")
                service = await anyio.to_thread.run_sync(self._get_gmail_service)
                if not service:
                    logger.warning("Failed to get Gmail service in compose_email")
                    return "Failed to authenticate Gmail service"
                logger.info("Gmail service obtained successfully (compose_email).")

                message = MIMEText(body)
                message['to'] = to
                message['subject'] = subject
                encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
                email = {'raw': encoded_message}
                logger.info("Email message created and encoded.")

                if save_as_draft:
                    logger.info("Attempting to save draft...")
                    def _save_draft():
                        return service.users().drafts().create(
                            userId='me',
                            body={'message': email}
                        ).execute()
                    draft = await anyio.to_thread.run_sync(_save_draft)
                    logger.info(f"Draft saved successfully. Draft ID: {draft['id']}")
                    return f"Draft saved successfully. Draft ID: {draft['id']}"
                else:
                    logger.info("Attempting to send email...")
                    def _send_email():
                        return service.users().messages().send(
                            userId='me',
                            body=email
                        ).execute()
                    sent_message = await anyio.to_thread.run_sync(_send_email)
                    logger.info(f"Email sent successfully. Message ID: {sent_message['id']}")
                    return f"Email sent successfully. Message ID: {sent_message['id']}"
            except Exception as e:
                logger.error(f"Error inside compose_email: {e}", exc_info=True)
                return f"Error composing email: {str(e)}"
    
    def run(self, port: int = 8000):
        """Run the MCP server.
        
        Args:
            port: Port to run the server on
        """
        try:
            logger.info(f"Starting server on port {port}...")
            self.mcp.run(transport='stdio')  # Use stdio transport by default
            logger.info("Server finished running.")
        except Exception as e:
            logger.error(f"Error running server: {e}", exc_info=True)
            raise

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Initializing GmailMCPServer (for direct run)...")
    server = GmailMCPServer()
    logger.info("Initialization complete.")

    # Use stdio transport as documented for mcp library
    try:
        logger.info("Attempting server.mcp.run(transport='stdio')...")
        server.mcp.run(transport='stdio') # Specify stdio transport
        logger.info("server.mcp.run() finished.") 
    except Exception as e:
        logger.error(f"Error during server.mcp.run(): {e}", exc_info=True)

    # NOTE: We are removing the .run() call here because 
    # 'fastmcp dev' or 'fastmcp install' will handle running the server.
    # If you wanted to run directly via 'python -m src.server', you would need:
    # server.mcp.run() # Might default to SSE/HTTP
    # or
    # server.mcp.run(transport='stdio') # For stdio 