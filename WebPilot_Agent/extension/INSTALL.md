# Chrome Extension Installation Guide

## 📦 Installing the WebPilot Agent – AI-Powered Browser Assistant Extension

### Step 1: Open Chrome Extensions Page

1. Open Google Chrome or Microsoft Edge
2. Navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in top-right corner)

### Step 2: Load the Extension

1. Click "Load unpacked"
2. Navigate to: `d:\AI\AIML\SUNRISE COUNTDOWN\ai-craftsman-portfolio\projects\WebPilot Agent – AI-Powered Browser Assistant\extension`
3. Select the `extension` folder
4. Click "Select Folder"

### Step 3: Verify Installation

You should see:
- ✅ Extension card with "WebPilot Agent – AI-Powered Browser Assistant Agent Controller"
- ✅ Robot icon in your extensions toolbar
- ✅ Green badge showing "●" (connected)

### Step 4: Pin the Extension (Optional)

1. Click the puzzle piece icon in Chrome toolbar
2. Find "WebPilot Agent – AI-Powered Browser Assistant Agent Controller"
3. Click the pin icon to keep it visible

---

## 🚀 Using the Extension

### 1. Start the Backend Server

```bash
cd "d:\AI\AIML\SUNRISE COUNTDOWN\ai-craftsman-portfolio\projects\WebPilot Agent – AI-Powered Browser Assistant"
python api_server.py
```

Wait for:
```
🚀 Starting WebPilot Agent – AI-Powered Browser Assistant Visual Frontend Server...
📱 Open http://localhost:8000 in your browser
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Open the Frontend

1. Open a new tab
2. Navigate to `http://localhost:8000`
3. You should see the black & white chat interface

### 3. Verify Extension Connection

1. Click the extension icon in your toolbar
2. Popup should show: "Connected" with green dot
3. If not connected, click "Connect to Backend"

### 4. Give the Agent a Task

1. In the frontend chat, type a task:
   - "Search for AI agents on Google"
   - "Go to Wikipedia and search for Python"
   - "Navigate to GitHub and find trending repositories"

2. Press Enter or click Send

### 5. Watch the Magic! ✨

You will see:
- **In your browser**: 
  - Green pulsing border appears
  - "🤖 Agent Controlling Browser" banner at top
  - Elements highlighted yellow before clicks
  - Actions happening live!

- **In the frontend chat**:
  - Agent's reasoning for each action
  - Annotated screenshots showing what was clicked
  - Timeline of all actions
  - Pause/Resume controls

---

## 🎨 Visual Indicators

### In Your Browser (Live)

| Indicator | Meaning |
|-----------|---------|
| Green pulsing border | Agent is active |
| Yellow element glow | About to click this element |
| Banner at top | Shows current action |

### In Frontend Chat

| Element | Purpose |
|---------|---------|
| Red circles | Shows where agent clicked |
| Yellow boxes | Shows what was typed |
| Blue arrows | Shows scroll direction |
| Green highlights | Shows navigation |

---

## 🔧 Troubleshooting

### Extension Not Connecting

1. **Check backend is running**:
   - Look for "Uvicorn running" message
   - Visit http://localhost:8000 - should load

2. **Reload extension**:
   - Go to `chrome://extensions/`
   - Click refresh icon on extension card
   - Click extension icon, then "Connect to Backend"

3. **Check console**:
   - Right-click extension icon → "Inspect popup"
   - Look for WebSocket connection errors

### Agent Not Controlling Browser

1. **Verify extension connected**:
   - Extension popup shows "Connected" with green dot

2. **Check active tab**:
   - Extension controls the currently active tab
   - Make sure you're on the tab you want controlled

3. **Refresh page**:
   - Sometimes content script needs page refresh
   - Press F5 on the tab you want controlled

### No Visual Indicators

1. **Content script not loaded**:
   - Refresh the page (F5)
   - Check if URL is allowed (some sites block extensions)

2. **CSS not injected**:
   - Check `chrome://extensions/` for errors
   - Reload extension

---

## 🎯 Example Tasks to Try

### Easy
- "Search for Python tutorials on Google"
- "Go to Wikipedia"
- "Navigate to GitHub"

### Medium
- "Search for AI agents on Google and click the first result"
- "Go to Wikipedia and search for Machine Learning"

### Advanced
- "Go to Google, search for 'best laptops 2024', and scroll down"
- "Navigate to GitHub and find trending repositories"

---

## 🛑 Stopping the Agent

### Pause Agent
- Click "Pause" button in frontend
- Agent will stop after current action
- Click "Resume" to continue

### Disconnect Extension
- Click extension icon
- Click "Disconnect" button
- Green border will disappear

### Stop Backend
- Press `Ctrl+C` in terminal where server is running

---

## 📝 Notes

- **Privacy**: Extension only connects to localhost:8000
- **Permissions**: Extension needs access to all URLs to control any page
- **Security**: Only use on trusted sites
- **Performance**: Extension is lightweight, minimal impact

---

## 🎉 You're Ready!

The extension is now installed and ready to use. Open the frontend, give the agent a task, and watch it control your browser live!

For more information, see the main [README.md](../README.md).
