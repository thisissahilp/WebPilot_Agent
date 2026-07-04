// Background service worker - manages WebSocket connection to backend
let ws = null;
let isConnected = false;
let currentTabId = null;

// WebSocket connection
function connectToBackend() {
    const wsUrl = 'ws://localhost:8000/ws/extension';

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ Connected to WebPilot Agent – AI-Powered Browser Assistant backend');
        isConnected = true;
        updateBadge('connected');

        // Notify backend of connection
        sendToBackend({
            type: 'extension_connected',
            userAgent: navigator.userAgent
        });
    };

    ws.onmessage = async (event) => {
        const data = JSON.parse(event.data);
        await handleCommand(data);
    };

    ws.onclose = () => {
        console.log('❌ Disconnected from backend');
        isConnected = false;
        updateBadge('disconnected');

        // Attempt to reconnect after 3 seconds
        setTimeout(connectToBackend, 3000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Handle commands from backend
async function handleCommand(data) {
    const { type, command } = data;

    if (type === 'execute_command') {
        // Get active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        currentTabId = tab.id;

        // Handle navigation specially to avoid port closure
        if (command.action === 'navigate') {
            try {
                // Create new tab for navigation (keeps frontend tab open)
                const newTab = await chrome.tabs.create({
                    url: command.params.url,
                    active: true
                });
                currentTabId = newTab.id;

                // Wait for page to load
                await new Promise(resolve => {
                    chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
                        if (tabId === currentTabId && info.status === 'complete') {
                            chrome.tabs.onUpdated.removeListener(listener);
                            resolve();
                        }
                    });
                });

                // Send success response
                sendToBackend({
                    type: 'command_result',
                    success: true,
                    data: { url: command.params.url, tabId: currentTabId }
                });

                // Capture screenshot
                await captureAndSendScreenshot();
            } catch (error) {
                sendToBackend({
                    type: 'command_result',
                    success: false,
                    error: error.message
                });
            }
            return;
        }

        // For other commands, send to content script
        try {
            const response = await chrome.tabs.sendMessage(currentTabId, {
                type: 'execute',
                command: command
            });

            // Send response back to backend
            sendToBackend({
                type: 'command_result',
                success: response.success,
                data: response.data,
                error: response.error
            });

            // Capture screenshot after action
            if (response.success) {
                await captureAndSendScreenshot();
            }
        } catch (error) {
            sendToBackend({
                type: 'command_result',
                success: false,
                error: error.message
            });
        }
    }
    else if (type === 'get_page_state') {
        await getPageState();
    }
    else if (type === 'ping') {
        sendToBackend({ type: 'pong' });
    }
}

// Capture screenshot and send to backend
async function captureAndSendScreenshot() {
    try {
        const screenshot = await chrome.tabs.captureVisibleTab(null, {
            format: 'jpeg',
            quality: 70
        });

        // Remove data URL prefix to get base64
        const base64 = screenshot.split(',')[1];

        sendToBackend({
            type: 'screenshot',
            data: base64
        });
    } catch (error) {
        console.error('Screenshot capture failed:', error);
    }
}

// Get current page state
async function getPageState() {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    currentTabId = tab.id;

    try {
        const response = await chrome.tabs.sendMessage(currentTabId, {
            type: 'get_state'
        });

        sendToBackend({
            type: 'page_state',
            data: response
        });
    } catch (error) {
        sendToBackend({
            type: 'page_state',
            error: error.message
        });
    }
}

// Send message to backend
function sendToBackend(message) {
    if (ws && isConnected) {
        ws.send(JSON.stringify(message));
    }
}

// Update extension badge
function updateBadge(status) {
    if (status === 'connected') {
        chrome.action.setBadgeText({ text: '●' });
        chrome.action.setBadgeBackgroundColor({ color: '#00ff00' });
    } else if (status === 'active') {
        chrome.action.setBadgeText({ text: '▶' });
        chrome.action.setBadgeBackgroundColor({ color: '#00aaff' });
    } else {
        chrome.action.setBadgeText({ text: '○' });
        chrome.action.setBadgeBackgroundColor({ color: '#666666' });
    }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'connect') {
        connectToBackend();
        sendResponse({ success: true });
    }
    else if (request.type === 'disconnect') {
        if (ws) {
            ws.close();
        }
        sendResponse({ success: true });
    }
    else if (request.type === 'get_status') {
        sendResponse({ connected: isConnected });
    }

    return true;
});

// Auto-connect on extension load
connectToBackend();
