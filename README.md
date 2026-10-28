# 🤖 WebPilot Agent – AI-Powered Browser Assistant

**An intelligent browser automation agent powered by Google's Gemini 2.5 Pro that controls your Chrome browser through natural language commands.**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.40+-orange.svg)

## 🎯 Overview

WebPilot Agent – AI-Powered Browser Assistant is a browser automation system that lets you control Chrome using natural language. Simply describe what you want to do, and the AI agent will navigate websites, click buttons, fill forms, and extract information for you. The system uses a Chrome extension to communicate with the browser in real-time, providing visual feedback through an elegant web interface.

**Key Innovation**: Unlike traditional browser automation tools, WebPilot Agent – AI-Powered Browser Assistant uses LangGraph and Gemini 2.5 Pro to intelligently plan and execute multi-step tasks, adapting to dynamic web pages and handling errors gracefully.

## ✨ Features

- 🧠 **AI-Powered Navigation**: Uses Gemini 2.5 Pro to understand tasks and plan browser actions
- 🔌 **Chrome Extension Integration**: Real-time browser control through WebSocket communication
- 📸 **Visual Feedback**: Annotated screenshots showing agent actions (clicks, scrolls, typing)
- 💬 **Real-time Updates**: WebSocket-based streaming of agent actions to the frontend
- ⏸️ **Pause/Resume Control**: Control agent execution from the web interface
- 📊 **Action Timeline**: View the complete sequence of agent actions
- 🎨 **Minimal UI**: Clean, terminal-style black & white interface

## 🏗️ Architecture

```
┌─────────────────┐         WebSocket          ┌──────────────────┐
│  Web Frontend   │ ◄─────────────────────────► │   FastAPI Server │
│  (HTML/CSS/JS)  │                              │   (api_server.py)│
└─────────────────┘                              └────────┬─────────┘
                                                          │
                                                          │ Controls
                                                          ▼
┌─────────────────┐         WebSocket          ┌──────────────────┐
│ Chrome Extension│ ◄─────────────────────────► │ Extension Agent  │
│  (background.js)│                              │(agent_extension) │
└────────┬────────┘                              └────────┬─────────┘
         │                                                │
         │ Controls                                       │ Uses
         ▼                                                ▼
┌─────────────────┐                              ┌──────────────────┐
│  Chrome Browser │                              │  Browser Tools   │
│   (User's Tab)  │                              │  Action Logger   │
└─────────────────┘                              │  Screenshot      │
                                                  └──────────────────┘
```

**Flow**:
1. User sends task via web frontend
2. FastAPI server receives task and initializes Extension Agent
3. Agent uses Gemini 2.5 Pro to plan actions
4. Agent sends commands to Chrome extension via WebSocket
5. Extension executes actions in the browser
6. Screenshots and action logs stream back to frontend in real-time

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- Google API key for Gemini 2.5 Pro ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd WebPilot-Agent
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

5. **Install Chrome Extension**
   
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right)
   - Click "Load unpacked"
   - Select the `extension/` directory from this project
   - The extension icon should appear in your toolbar

### Running the Application

1. **Start the API server**
   ```bash
   python api_server.py
   ```
   
   The server will start at `http://localhost:8000`

2. **Open the web interface**
   
   Navigate to `http://localhost:8000` in Chrome

3. **Connect the extension**
   
   - Click the WebPilot Agent – AI-Powered Browser Assistant extension icon in Chrome
   - Click "Connect to Server"
   - Status should change to "Connected"

4. **Give the agent a task!**
   
   Type a task in the chat interface, for example:
   - "Navigate to google.com and search for artificial intelligence"
   - "Go to Wikipedia and find information about Python programming"
   - "Open GitHub and show me trending repositories"

## � Usage Examples

### Example 1: Web Search
```
Task: "Search for the latest news about AI on Google"
```
The agent will:
1. Navigate to google.com
2. Find the search box
3. Type "latest news about AI"
4. Click the search button
5. Return results

### Example 2: Information Extraction
```
Task: "Go to Wikipedia and tell me about the Python programming language"
```
The agent will:
1. Navigate to wikipedia.org
2. Search for "Python programming language"
3. Extract and summarize key information

### Example 3: Multi-step Navigation
```
Task: "Go to GitHub, search for 'langchain', and open the first repository"
```
The agent will:
1. Navigate to github.com
2. Find and use the search functionality
3. Locate the first result
4. Click to open the repository

## 🛠️ Tech Stack

- **AI/ML**: 
  - [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration framework
  - [Google Gemini 2.5 Pro](https://deepmind.google/technologies/gemini/) - Large language model
  - [LangChain](https://github.com/langchain-ai/langchain) - LLM application framework

- **Backend**:
  - [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
  - [Uvicorn](https://www.uvicorn.org/) - ASGI server
  - [WebSockets](https://websockets.readthedocs.io/) - Real-time communication

- **Browser Automation**:
  - [Playwright](https://playwright.dev/) - Browser automation library
  - Chrome Extension API - Browser control
  - [Pillow](https://python-pillow.org/) - Image processing for screenshots

- **Frontend**:
  - Vanilla HTML/CSS/JavaScript
  - WebSocket client for real-time updates

## 📁 Project Structure

```
WebPilot Agent – AI-Powered Browser Assistant/
├── api_server.py              # FastAPI server with WebSocket endpoints
├── sitback/                   # Core agent package
│   ├── agent_extension.py     # Extension-based agent implementation
│   ├── extension_handler.py   # WebSocket handler for Chrome extension
│   ├── state.py              # Agent state definition
│   └── tools/                # Agent tools
│       ├── browser.py        # Core browser automation tools
│       ├── action_logger.py  # Action logging with reasoning
│       └── screenshot_annotator.py  # Screenshot annotation engine
├── frontend/                  # Web interface
│   ├── index.html            # Main HTML page
│   ├── styles.css            # Minimal black & white styling
│   └── app.js                # WebSocket client & UI logic
├── extension/                 # Chrome extension
│   ├── manifest.json         # Extension configuration
│   ├── background.js         # Background service worker
│   ├── content.js            # Content script for page interaction
│   ├── popup.html            # Extension popup UI
│   └── popup.js              # Popup logic
├── examples/                  # Usage examples
│   └── basic_usage.py        # Basic programmatic usage
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (create this)
└── .gitignore                # Git ignore rules
```

## 🎨 How It Works

### Screenshot Annotations

The agent provides visual feedback through annotated screenshots:

- **🔴 Red circles with crosshairs**: Click locations
- **🟡 Yellow boxes**: Text that was typed
- **🔵 Blue arrows**: Scroll direction and distance
- **🟢 Green highlights**: Navigation actions
- **Banner overlay**: "🤖 AGENT CONTROLLED" status

### WebSocket Communication

#### Client → Server Messages
```json
{
  "type": "user_message",
  "message": "Search for AI on Google"
}
```

#### Server → Client Messages
```json
{
  "type": "agent_action",
  "data": {
    "action": "click",
    "target": "Search button",
    "reasoning": "Clicking search to submit query...",
    "screenshot": "base64_encoded_image",
    "timestamp": "2026-01-15T09:30:00Z"
  }
}
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google API key for Gemini 2.5 Pro (required)

### Extension Configuration

The extension connects to `ws://localhost:8000/ws/extension` by default. To change this, edit `extension/background.js`:

```javascript
const WS_URL = 'ws://your-server:port/ws/extension';
```

## 🚧 Limitations & Future Enhancements

### Current Limitations
- Single user session (one task at a time)
- Requires Chrome extension to be manually installed
- Limited to Chrome browser

### Planned Features
- [ ] Multi-session support (multiple concurrent tasks)
- [ ] Session recording and replay
- [ ] Export session as video
- [ ] Support for Firefox and Edge
- [ ] Cloud deployment with remote browser control
- [ ] Task templates and saved workflows
- [ ] Advanced error recovery and retry logic

## 🤝 Contributing

Contributions are welcome! This project was built as a portfolio piece to demonstrate:
- AI agent development with LangGraph
- Real-time WebSocket communication
- Chrome extension development
- Browser automation with Playwright
- Modern web application architecture

## � License

MIT License - feel free to use this project for learning and portfolio purposes.

