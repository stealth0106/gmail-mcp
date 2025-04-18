"""Script to run the Gmail MCP server."""

import logging
import sys
from server import GmailMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Run the Gmail MCP server."""
    try:
        logger.info("Starting Gmail MCP server...")
        server = GmailMCPServer()
        
        # Run the server
        logger.info("Server initialized, starting on port 8000...")
        server.run(host="0.0.0.0", port=8000)
        
    except Exception as e:
        logger.error(f"Error running server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 