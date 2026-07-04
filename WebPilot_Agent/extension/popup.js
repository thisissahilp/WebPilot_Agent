// Popup script
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');

// Check connection status on popup open
chrome.runtime.sendMessage({ type: 'get_status' }, (response) => {
    updateStatus(response.connected);
});

// Connect button
connectBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'connect' }, (response) => {
        if (response.success) {
            setTimeout(() => {
                chrome.runtime.sendMessage({ type: 'get_status' }, (response) => {
                    updateStatus(response.connected);
                });
            }, 1000);
        }
    });
});

// Disconnect button
disconnectBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: 'disconnect' }, (response) => {
        if (response.success) {
            updateStatus(false);
        }
    });
});

// Update status display
function updateStatus(connected) {
    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
        connectBtn.style.display = 'none';
        disconnectBtn.style.display = 'block';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
        connectBtn.style.display = 'block';
        disconnectBtn.style.display = 'none';
    }
}

// Auto-refresh status every 2 seconds
setInterval(() => {
    chrome.runtime.sendMessage({ type: 'get_status' }, (response) => {
        if (response) {
            updateStatus(response.connected);
        }
    });
}, 2000);
