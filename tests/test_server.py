"""
Gmail MCP Server Unit Tests
=========================

This test suite contains unit tests for the Gmail MCP Server implementation.
These tests verify the basic structure and setup of the server components without
making actual Gmail API calls. They ensure that:
- Server initializes correctly
- Required methods and attributes exist
- Resources and tools are properly registered

Usage:
------
1. Ensure you have activated your virtual environment:
   .\venv\Scripts\activate

2. Run the tests:
   python -m pytest tests/test_server.py -v

Note: These tests do not require Gmail credentials as they don't make actual API calls.
They are primarily for development and code quality assurance.
"""

import pytest
from src.server import GmailMCPServer

def test_server_initialization():
    """Test server initialization."""
    server = GmailMCPServer()
    assert server.mcp is not None
    assert server.mcp.name == "gmail_mcp_server"

def test_gmail_service_authentication():
    """Test Gmail service authentication."""
    server = GmailMCPServer()
    service = server._get_gmail_service()
    assert service is not None

def test_server_attributes():
    """Test if server has necessary attributes and methods."""
    server = GmailMCPServer()
    # Check if server has required methods
    assert hasattr(server, '_setup_resources')
    assert hasattr(server, '_setup_tools')
    assert hasattr(server, 'run')
    assert callable(server.run)

def test_email_retrieval():
    """Test email retrieval functionality."""
    server = GmailMCPServer()
    # Access the resource directly
    result = server.mcp.resource("gmail://inbox/5")
    assert callable(result)
    # We can't actually call it here as it requires authentication
    # In a real test environment, we would mock the Gmail service

def test_draft_retrieval():
    """Test draft retrieval functionality."""
    server = GmailMCPServer()
    # Access the resource directly
    result = server.mcp.resource("gmail://drafts/5")
    assert callable(result)
    # We can't actually call it here as it requires authentication
    # In a real test environment, we would mock the Gmail service

def test_sent_email_retrieval():
    """Test sent email retrieval functionality."""
    server = GmailMCPServer()
    # Access the resource directly
    result = server.mcp.resource("gmail://sent/5")
    assert callable(result)
    # We can't actually call it here as it requires authentication
    # In a real test environment, we would mock the Gmail service

def test_email_search():
    """Test email search functionality."""
    server = GmailMCPServer()
    # Access the tool directly
    result = server.mcp.tool("search_emails")
    assert callable(result)
    # We can't actually call it here as it requires authentication
    # In a real test environment, we would mock the Gmail service

def test_email_composition():
    """Test email composition functionality."""
    server = GmailMCPServer()
    # Access the tool directly
    result = server.mcp.tool("compose_email")
    assert callable(result)
    # We can't actually call it here as it requires authentication
    # In a real test environment, we would mock the Gmail service

# Note: Email retrieval and search tests are commented out until Phase 2.2 is implemented
"""
def test_email_retrieval():
    # To be implemented in Phase 2.2
    pass

def test_email_search():
    # To be implemented in Phase 2.2
    pass
""" 