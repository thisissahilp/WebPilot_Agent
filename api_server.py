from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import json
import asyncio
from pathlib import Path
import os
from dotenv import load_dotenv
from sitback.extension_handler import ExtensionHandler

# Load environment variables
load_dotenv()

app = FastAPI(title="WebPilot Agent – AI-Powered Browser Assistant Visual Frontend")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.agent_status = "idle"  # idle, active, paused
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass
    
    async def send_action(self, action_log: dict):
        """Send agent action to all connected clients"""
        await self.broadcast({
            "type": "agent_action",
            "data": action_log
        })
    
    async def send_status(self, status: str):
        """Send agent status update"""
        self.agent_status = status
        await self.broadcast({
            "type": "status_update",
            "status": status
        })
    
    async def send_timeline(self, timeline: list):
        """Send action timeline"""
        await self.broadcast({
            "type": "timeline_update",
            "timeline": timeline
        })

manager = ConnectionManager()
extension_handler = ExtensionHandler()

# Store agent instance globally (will be set when agent starts)
current_agent = None
agent_task = None
agent_paused = False

@app.get("/")
async def get_frontend():
    """Serve the frontend HTML"""
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    if frontend_path.exists():
        return FileResponse(frontend_path)
    return HTMLResponse("<h1>Frontend not found. Please create frontend/index.html</h1>")

@app.websocket("/ws/extension")
async def extension_websocket(websocket: WebSocket):
    """WebSocket endpoint for Chrome extension"""
    await extension_handler.connect(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            await extension_handler.handle_message(data)
    
    except WebSocketDisconnect:
        extension_handler.disconnect()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket)
    
    try:
        # Send initial status
        await manager.send_message({
            "type": "connection_established",
            "status": manager.agent_status
        }, websocket)
        
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "user_message":
                # User sent a task
                user_task = data.get("message")
                await handle_user_task(user_task)
            
            elif message_type == "pause_agent":
                # Pause agent execution
                global agent_paused
                agent_paused = True
                await manager.send_status("paused")
            
            elif message_type == "resume_agent":
                # Resume agent execution
                agent_paused = False
                await manager.send_status("active")
            
            elif message_type == "get_timeline":
                # Send current timeline
                if current_agent:
                    timeline = current_agent.browser.get_timeline()
                    await manager.send_timeline(timeline)
            
            elif message_type == "get_action":
                # Get specific action by index
                index = data.get("index")
                if current_agent:
                    action = current_agent.browser.get_action(index)
                    if action:
                        await manager.send_message({
                            "type": "action_detail",
                            "action": action
                        }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

async def handle_user_task(task: str):
    """Handle user task by running the agent"""
    global current_agent, agent_task, agent_paused
    
    # Check if extension is connected
    if not extension_handler.is_connected:
        await manager.broadcast({
            "type": "error",
            "message": "Chrome extension not connected. Please install and connect the extension first."
        })
        return
    
    # Send acknowledgment
    await manager.broadcast({
        "type": "system_message",
        "message": f"Starting task: {task}"
    })
    
    await manager.send_status("active")
    
    # Import and run agent in background
    try:
        from sitback.agent_extension import ExtensionAgent
        
        # Create agent instance with extension handler
        agent = ExtensionAgent(
            extension_handler=extension_handler,
            websocket_manager=manager
        )
        current_agent = agent
        
        # Run agent task in background
        agent_task = asyncio.create_task(
            run_agent_async(agent, task)
        )
    
    except Exception as e:
        await manager.broadcast({
            "type": "error",
            "message": f"Error starting agent: {str(e)}"
        })
        await manager.send_status("idle")

async def run_agent_async(agent, task: str):
    """Run agent asynchronously"""
    try:
        # Run agent in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, agent.run, task)
        
        await manager.send_status("idle")
        await manager.broadcast({
            "type": "system_message",
            "message": "Task completed!"
        })
    
    except Exception as e:
        await manager.broadcast({
            "type": "error",
            "message": f"Agent error: {str(e)}"
        })
        await manager.send_status("idle")

# Mount static files (CSS, JS)
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting WebPilot Agent – AI-Powered Browser Assistant Visual Frontend Server...")
    print("📱 Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
