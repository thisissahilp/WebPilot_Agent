"""
Extension handler - manages WebSocket connection with Chrome extension
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Optional, Dict, Any
import json
import asyncio

class ExtensionHandler:
    def __init__(self):
        self.extension_ws: Optional[WebSocket] = None
        self.is_connected = False
        self.command_queue = asyncio.Queue()
        self.screenshot_queue = asyncio.Queue()
        self.page_state = None
    
    async def connect(self, websocket: WebSocket):
        """Connect extension WebSocket"""
        await websocket.accept()
        self.extension_ws = websocket
        self.is_connected = True
        print("✅ Chrome extension connected")
    
    def disconnect(self):
        """Disconnect extension"""
        self.extension_ws = None
        self.is_connected = False
        print("❌ Chrome extension disconnected")
    
    async def send_command(self, command: Dict[str, Any]) -> bool:
        """Send command to extension"""
        if not self.is_connected or not self.extension_ws:
            return False
        
        try:
            await self.extension_ws.send_json({
                "type": "execute_command",
                "command": command
            })
            return True
        except Exception as e:
            print(f"Error sending command to extension: {e}")
            return False
    
    async def handle_message(self, data: dict):
        """Handle message from extension"""
        msg_type = data.get("type")
        
        if msg_type == "extension_connected":
            print(f"Extension connected: {data.get('userAgent', 'Unknown')}")
        
        elif msg_type == "command_result":
            # Command execution result
            await self.command_queue.put(data)
        
        elif msg_type == "screenshot":
            # Screenshot from extension
            await self.screenshot_queue.put(data.get("data"))
        
        elif msg_type == "page_state":
            # Page state update
            self.page_state = data.get("data")
        
        elif msg_type == "pong":
            # Ping response
            pass
    
    async def wait_for_result(self, timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """Wait for command result"""
        try:
            result = await asyncio.wait_for(
                self.command_queue.get(),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            return None
    
    async def wait_for_screenshot(self, timeout: float = 5.0) -> Optional[str]:
        """Wait for screenshot"""
        try:
            screenshot = await asyncio.wait_for(
                self.screenshot_queue.get(),
                timeout=timeout
            )
            return screenshot
        except asyncio.TimeoutError:
            return None
    
    async def get_page_state(self) -> Optional[Dict[str, Any]]:
        """Request current page state"""
        if not self.is_connected:
            return None
        
        try:
            await self.extension_ws.send_json({
                "type": "get_page_state"
            })
            
            # Wait a bit for response
            await asyncio.sleep(0.5)
            return self.page_state
        except Exception as e:
            print(f"Error getting page state: {e}")
            return None
    
    async def ping(self):
        """Ping extension to check connection"""
        if not self.is_connected:
            return False
        
        try:
            await self.extension_ws.send_json({"type": "ping"})
            return True
        except:
            return False
