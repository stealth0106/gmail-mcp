# Gmail MCP Server

A Model Context Protocol (MCP) server implementation for Gmail that enables natural language interactions with Gmail services. This server acts as a bridge between MCP-compatible clients and Gmail's API, providing intuitive email management capabilities.

## Features

- **Gmail API Integration**: Secure OAuth2 authentication and comprehensive Gmail API access
- **MCP Resources**:
  - Email inbox access and management
  - Draft creation and management
  - Sent email retrieval
  - Email search functionality
  - Email composition with attachment support
- **Secure Authentication**: OAuth 2.0 flow with token management and refresh capabilities
- **Extensible Architecture**: Built on FastMCP for easy expansion and customization

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with Gmail API enabled
- OAuth 2.0 credentials (client_secret.json)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GmailMCP.git
cd GmailMCP
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure OAuth credentials:
   - Place your `client_secret.json` in the project root directory
   - First run will initiate OAuth flow and store credentials

## Usage

1. Start the server:
```bash
python src/server.py
```

2. The server will start on the default port (8000) and handle MCP requests for:
   - Email retrieval: `gmail://inbox`
   - Draft management: `gmail://drafts`
   - Sent mail access: `gmail://sent`
   - Email search: `gmail://search`
   - Email composition: `gmail://compose`

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Project Status

- ✓ Phase 1: Project Setup and Dependencies
- ✓ Phase 2.1: Basic Server Setup
- ✓ Phase 2.2: Core Gmail Resources
- ⚡ Phase 2.3: Natural Language Interface (In Progress)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 