"""
Gmail MCP Client Test Script
===========================

This script is a client application that demonstrates and tests real Gmail MCP server functionality.
It connects to your Gmail account and performs actual operations like:
- Reading inbox messages
- Viewing drafts
- Checking sent emails
- Searching emails
- Creating draft emails

Usage:
------
1. Ensure you have activated your virtual environment:
   .\venv\Scripts\activate

2. Run the script:
   python tests/test_client.py
   
Note: This script requires valid Gmail OAuth credentials (client_secret.json) and 
an authenticated session (token.json) to be present in the project root.
"""

import asyncio
import sys

# Imports based on mcp v1.6.0 SDK examples
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

async def main():
    # Parameters to launch the server script via stdio
    server_params = StdioServerParameters(
        command=sys.executable, # Use the same python interpreter
        args=["-m", "src.server"], # Run the server module
        cwd=None, # Let it run in the current directory
        env=None,
    )
    print(f"Launching server via stdio: {server_params.command} {' '.join(server_params.args)}")

    try:
        # stdio_client manages starting the server and providing streams
        async with stdio_client(server_params) as (read_stream, write_stream):
            print("Server process likely started by stdio_client.")
            # ClientSession uses the streams
            async with ClientSession(read_stream, write_stream) as session:
                print("stdio client session created. Initializing...")
                # Initialize manually is needed for ClientSession
                init_result = await session.initialize()
                print(f"Initialization successful.") # Simplified init log

                # --- Test 1: Read Minimal Resource --- 
                try:
                    resource_uri = "test://hello"
                    print(f"\n>>> Reading resource: {resource_uri}")
                    content, mime_type = await session.read_resource(resource_uri)
                    print("--- Result ---")
                    print(f"MimeType: {mime_type}\nContent: {content}")
                    print("--------------")
                except Exception as e:
                    print(f"*** Error reading resource '{resource_uri}': {e} ***")

                # --- Test 2: Read Inbox Resource --- 
                try:
                    resource_uri = "gmail://inbox" # Using the simplified URI
                    print(f"\n>>> Reading resource: {resource_uri}")
                    content, mime_type = await session.read_resource(resource_uri)
                    print("--- Result ---")
                    print(f"MimeType: {mime_type}\nContent:\n{content}")
                    print("--------------")
                except Exception as e:
                    print(f"*** Error reading resource '{resource_uri}': {e} ***")

                # --- Test 3: Read Drafts Resource --- 
                try:
                    resource_uri = "gmail://drafts/5" # Get up to 5 drafts
                    print(f"\n>>> Reading resource: {resource_uri}")
                    content, mime_type = await session.read_resource(resource_uri)
                    print("--- Result ---")
                    print(f"MimeType: {mime_type}\nContent:\n{content}")
                    print("--------------")
                except Exception as e:
                    print(f"*** Error reading resource '{resource_uri}': {e} ***")
                    
                # --- Test 4: Read Sent Resource --- 
                try:
                    resource_uri = "gmail://sent/3" # Get up to 3 sent items
                    print(f"\n>>> Reading resource: {resource_uri}")
                    content, mime_type = await session.read_resource(resource_uri)
                    print("--- Result ---")
                    print(f"MimeType: {mime_type}\nContent:\n{content}")
                    print("--------------")
                except Exception as e:
                    print(f"*** Error reading resource '{resource_uri}': {e} ***")

                # --- Test 5: Search Emails Tool --- 
                try:
                    tool_name = "search_emails"
                    tool_params = {"query": "from:me subject:test", "max_results": 2}
                    print(f"\n>>> Calling tool: {tool_name} with params: {tool_params}")
                    # Note: session.call_tool might return a specific result object or just the content
                    result = await session.call_tool(tool_name, arguments=tool_params)
                    print("--- Result ---")
                    print(result)
                    print("--------------")
                except Exception as e:
                    print(f"*** Error calling tool '{tool_name}': {e} ***")

                # --- Test 6: Compose Draft Tool --- 
                try:
                    tool_name = "compose_email"
                    tool_params = {
                        "to": "test.recipient@example.com", # CHANGE THIS if you want to test sending
                        "subject": "MCP Test Draft Subject", 
                        "body": "This is a test email body composed via MCP.", 
                        "save_as_draft": True # Set to True to save as draft
                    }
                    print(f"\n>>> Calling tool: {tool_name} with params: {tool_params}")
                    result = await session.call_tool(tool_name, arguments=tool_params)
                    print("--- Result ---")
                    print(result)
                    print("--------------")
                except Exception as e:
                    print(f"*** Error calling tool '{tool_name}': {e} ***")

    except Exception as e:
        print(f"*** Error during stdio client execution: {e} ***")

if __name__ == "__main__":
    asyncio.run(main()) 