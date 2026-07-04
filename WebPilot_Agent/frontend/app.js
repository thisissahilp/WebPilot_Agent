// WebSocket connection
let ws = null;
let isConnected = false;

// DOM elements
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const controls = document.getElementById('controls');
const pauseBtn = document.getElementById('pauseBtn');
const resumeBtn = document.getElementById('resumeBtn');
const timelineBtn = document.getElementById('timelineBtn');
const timelineContainer = document.getElementById('timelineContainer');
const timeline = document.getElementById('timeline');
const closeTimelineBtn = document.getElementById('closeTimelineBtn');

// Connect to WebSocket
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ Connected to server');
        isConnected = true;
        updateStatus('idle');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    ws.onclose = () => {
        console.log('❌ Disconnected from server');
        isConnected = false;
        updateStatus('disconnected');

        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Handle incoming messages
function handleMessage(data) {
    const type = data.type;

    if (type === 'connection_established') {
        console.log('Connection established');
    }
    else if (type === 'agent_action') {
        displayAgentAction(data.data);
    }
    else if (type === 'status_update') {
        updateStatus(data.status);
    }
    else if (type === 'timeline_update') {
        updateTimeline(data.timeline);
    }
    else if (type === 'action_detail') {
        displayActionDetail(data.action);
    }
    else if (type === 'system_message') {
        displaySystemMessage(data.message);
    }
    else if (type === 'error') {
        displayError(data.message);
    }
}

// Display user message
function displayUserMessage(message) {
    // Remove welcome message if it exists
    const welcomeMsg = chatContainer.querySelector('.welcome-message');
    if (welcomeMsg) {
        welcomeMsg.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-header">▶ You:</div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Display agent action
function displayAgentAction(action) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent-message';

    let html = `
        <div class="message-header">🤖 Agent: ${action.action.toUpperCase()} - ${escapeHtml(action.target)}</div>
    `;

    // Add reasoning
    if (action.reasoning) {
        html += `
            <div class="reasoning">
                <div class="reasoning-label">Reasoning</div>
                <div>${escapeHtml(action.reasoning)}</div>
            </div>
        `;
    }

    // Add thought process
    if (action.thought_process) {
        html += `
            <div class="reasoning">
                <div class="reasoning-label">Thought Process</div>
                <div>${escapeHtml(action.thought_process)}</div>
            </div>
        `;
    }

    // Add screenshot
    if (action.screenshot) {
        html += `
            <div class="screenshot" onclick="toggleZoom(this)">
                <img src="data:image/jpeg;base64,${action.screenshot}" alt="Action screenshot">
            </div>
        `;
    }

    messageDiv.innerHTML = html;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Display system message
function displaySystemMessage(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system-message';
    messageDiv.innerHTML = `
        <div class="message-header">⚙ System:</div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Display error message
function displayError(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message error-message';
    messageDiv.innerHTML = `
        <div class="message-header">❌ Error:</div>
        <div class="message-content">${escapeHtml(message)}</div>
    `;
    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Display action detail (when clicking timeline item)
function displayActionDetail(action) {
    // Similar to displayAgentAction but maybe with different styling
    displayAgentAction(action);
}

// Update status indicator
function updateStatus(status) {
    statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    statusDot.className = 'status-dot';

    if (status === 'active') {
        statusDot.classList.add('active');
        controls.style.display = 'flex';
        pauseBtn.style.display = 'inline-block';
        resumeBtn.style.display = 'none';
    } else if (status === 'paused') {
        statusDot.classList.add('paused');
        pauseBtn.style.display = 'none';
        resumeBtn.style.display = 'inline-block';
    } else {
        controls.style.display = 'none';
    }
}

// Update timeline
function updateTimeline(timelineData) {
    timeline.innerHTML = '';

    timelineData.forEach((item, index) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'timeline-item';
        if (index === timelineData.length - 1) {
            itemDiv.classList.add('current');
        }

        const icon = getActionIcon(item.action);

        itemDiv.innerHTML = `
            <div class="timeline-icon">${icon}</div>
            <div class="timeline-label">${item.action}<br>${item.timestamp.split('T')[1].split('.')[0]}</div>
        `;

        itemDiv.onclick = () => requestAction(item.index);
        timeline.appendChild(itemDiv);
    });
}

// Get icon for action type
function getActionIcon(action) {
    const icons = {
        'navigate': '🌐',
        'click': '👆',
        'type': '⌨️',
        'scroll': '📜',
        'press_key': '⏎',
        'execute_js': '⚡'
    };
    return icons[action] || '•';
}

// Request specific action details
function requestAction(index) {
    if (ws && isConnected) {
        ws.send(JSON.stringify({
            type: 'get_action',
            index: index
        }));
    }
}

// Send message
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || !isConnected) return;

    // Display user message
    displayUserMessage(message);

    // Send to server
    ws.send(JSON.stringify({
        type: 'user_message',
        message: message
    }));

    // Clear input
    messageInput.value = '';
    sendBtn.disabled = true;
}

// Pause agent
function pauseAgent() {
    if (ws && isConnected) {
        ws.send(JSON.stringify({ type: 'pause_agent' }));
    }
}

// Resume agent
function resumeAgent() {
    if (ws && isConnected) {
        ws.send(JSON.stringify({ type: 'resume_agent' }));
    }
}

// Toggle timeline view
function toggleTimeline() {
    if (timelineContainer.style.display === 'none') {
        timelineContainer.style.display = 'block';
        // Request timeline data
        if (ws && isConnected) {
            ws.send(JSON.stringify({ type: 'get_timeline' }));
        }
    } else {
        timelineContainer.style.display = 'none';
    }
}

// Toggle screenshot zoom
function toggleZoom(element) {
    element.classList.toggle('zoomed');
}

// Scroll to bottom of chat
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});
messageInput.addEventListener('input', () => {
    sendBtn.disabled = !messageInput.value.trim() || !isConnected;
});
pauseBtn.addEventListener('click', pauseAgent);
resumeBtn.addEventListener('click', resumeAgent);
timelineBtn.addEventListener('click', toggleTimeline);
closeTimelineBtn.addEventListener('click', () => {
    timelineContainer.style.display = 'none';
});

// Initialize
connectWebSocket();
