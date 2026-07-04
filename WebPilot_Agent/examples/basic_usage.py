"""
Basic example of using the WebPilot Agent – AI-Powered Browser Assistant Extension Agent.

This example demonstrates how to programmatically use the agent
with the Chrome extension for browser automation tasks.

Prerequisites:
1. Chrome extension must be installed and running
2. API server must be running (python api_server.py)
3. Extension must be connected to the WebSocket server
"""

import asyncio
from sitback.agent_extension import ExtensionAgent
from sitback.extension_handler import ExtensionHandler

async def main():
    """Run a simple browser automation task."""
    
    # Create extension handler
    extension_handler = ExtensionHandler()
    
    # Note: In production, the extension connects via WebSocket
    # This example shows the agent structure
    
    print("🤖 WebPilot Agent – AI-Powered Browser Assistant - Extension Agent Example")
    print("=" * 50)
    print("\nTo use this agent:")
    print("1. Start the API server: python api_server.py")
    print("2. Install the Chrome extension from extension/")
    print("3. Open the frontend at http://localhost:8000")
    print("4. Give the agent a task through the web interface")
    print("\nExample tasks:")
    print("- 'Navigate to google.com and search for AI'")
    print("- 'Go to wikipedia.org and search for Python'")
    print("- 'Open github.com and find trending repositories'")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
