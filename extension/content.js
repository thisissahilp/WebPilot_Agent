// Content script - injected into web pages, executes agent commands
let agentActive = false;
let highlightedElement = null;

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'execute') {
        executeCommand(request.command)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Keep channel open for async response
    }
    else if (request.type === 'get_state') {
        const state = getPageState();
        sendResponse(state);
    }
    else if (request.type === 'set_active') {
        setAgentActive(request.active);
        sendResponse({ success: true });
    }
});

// Execute agent command
async function executeCommand(command) {
    const { action, params } = command;

    try {
        // Show agent is active
        setAgentActive(true);

        let result = {};

        switch (action) {
            case 'click':
                result = await clickElement(params.selector);
                break;

            case 'type':
                result = await typeText(params.selector, params.text);
                break;

            case 'press_key':
                result = await pressKey(params.key);
                break;

            case 'scroll':
                result = await scrollPage(params.direction, params.amount);
                break;

            case 'execute_js':
                result = { value: eval(params.code) };
                break;

            default:
                throw new Error(`Unknown action: ${action}`);
        }

        // Wait a bit for page to update
        await sleep(500);

        return {
            success: true,
            data: result,
            coords: result.coords
        };

    } catch (error) {
        return {
            success: false,
            error: error.message
        };
    }
}

// Click element
async function clickElement(selector) {
    const element = findElement(selector);
    if (!element) {
        throw new Error(`Element not found: ${selector}`);
    }

    // Highlight element before clicking
    await highlightElement(element);
    await sleep(300);

    // Get coordinates
    const rect = element.getBoundingClientRect();
    const coords = {
        x: Math.round(rect.left + rect.width / 2),
        y: Math.round(rect.top + rect.height / 2)
    };

    // Click
    element.click();

    // Remove highlight
    removeHighlight();

    return { coords, selector };
}

// Type text into element
async function typeText(selector, text) {
    const element = findElement(selector);
    if (!element) {
        throw new Error(`Element not found: ${selector}`);
    }

    // Highlight element
    await highlightElement(element);

    // Get coordinates
    const rect = element.getBoundingClientRect();
    const coords = {
        x: Math.round(rect.left + rect.width / 2),
        y: Math.round(rect.top + rect.height / 2)
    };

    // Focus and type
    element.focus();
    element.value = text;

    // Trigger input event
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));

    await sleep(300);
    removeHighlight();

    return { coords, text, selector };
}

// Press keyboard key
async function pressKey(key) {
    const activeElement = document.activeElement;

    // Create keyboard events
    const keydownEvent = new KeyboardEvent('keydown', {
        key: key,
        code: key === 'Enter' ? 'Enter' : key,
        keyCode: key === 'Enter' ? 13 : undefined,
        which: key === 'Enter' ? 13 : undefined,
        bubbles: true,
        cancelable: true
    });

    const keypressEvent = new KeyboardEvent('keypress', {
        key: key,
        code: key === 'Enter' ? 'Enter' : key,
        keyCode: key === 'Enter' ? 13 : undefined,
        which: key === 'Enter' ? 13 : undefined,
        bubbles: true,
        cancelable: true
    });

    const keyupEvent = new KeyboardEvent('keyup', {
        key: key,
        code: key === 'Enter' ? 'Enter' : key,
        keyCode: key === 'Enter' ? 13 : undefined,
        which: key === 'Enter' ? 13 : undefined,
        bubbles: true,
        cancelable: true
    });

    activeElement.dispatchEvent(keydownEvent);
    activeElement.dispatchEvent(keypressEvent);
    activeElement.dispatchEvent(keyupEvent);

    // For Enter key, also trigger form submission
    if (key === 'Enter') {
        if (activeElement.form) {
            activeElement.form.submit();
        } else {
            // Try to find and click search button
            const searchButton = document.querySelector('button[type="submit"], input[type="submit"], button[aria-label*="Search"], button[name="btnK"]');
            if (searchButton) {
                searchButton.click();
            }
        }
    }

    return { key };
}

// Scroll page
async function scrollPage(direction, amount = 500) {
    const scrollAmount = direction === 'down' ? amount : -amount;
    window.scrollBy(0, scrollAmount);

    return { direction, amount };
}

// Find element using various strategies
function findElement(selector) {
    // Try CSS selector
    let element = document.querySelector(selector);
    if (element) return element;

    // Try by text content
    const allElements = document.querySelectorAll('button, a, input, textarea, [role="button"]');
    for (const el of allElements) {
        if (el.textContent.trim() === selector || el.placeholder === selector) {
            return el;
        }
    }

    // Try by aria-label
    element = document.querySelector(`[aria-label="${selector}"]`);
    if (element) return element;

    return null;
}

// Highlight element with yellow glow
async function highlightElement(element) {
    removeHighlight(); // Remove any existing highlight

    highlightedElement = element;
    element.style.outline = '3px solid #ffff00';
    element.style.outlineOffset = '2px';
    element.style.boxShadow = '0 0 20px rgba(255, 255, 0, 0.8)';
    element.style.transition = 'all 0.3s ease';
}

// Remove highlight
function removeHighlight() {
    if (highlightedElement) {
        highlightedElement.style.outline = '';
        highlightedElement.style.outlineOffset = '';
        highlightedElement.style.boxShadow = '';
        highlightedElement = null;
    }
}

// Set agent active state
function setAgentActive(active) {
    agentActive = active;

    const banner = document.getElementById('sitback-ai-banner');
    const border = document.getElementById('sitback-ai-border');

    if (active) {
        if (!banner) createBanner();
        if (!border) createBorder();
    } else {
        if (banner) banner.remove();
        if (border) border.remove();
    }
}

// Create "Agent Active" banner
function createBanner() {
    const banner = document.createElement('div');
    banner.id = 'sitback-ai-banner';
    banner.className = 'sitback-banner';
    banner.innerHTML = '🤖 Agent Controlling Browser';
    document.body.appendChild(banner);
}

// Create pulsing border
function createBorder() {
    const border = document.createElement('div');
    border.id = 'sitback-ai-border';
    border.className = 'sitback-border';
    document.body.appendChild(border);
}

// Get current page state
function getPageState() {
    const actionable = Array.from(document.querySelectorAll('button, a, input, textarea, [role="button"]'));
    const elements = actionable.map(el => {
        let text = el.innerText || el.placeholder || el.value || el.getAttribute('aria-label') || '';
        text = text.trim().substring(0, 50);
        if (!text && el.tagName === 'INPUT') text = 'Input: ' + el.type;

        return {
            tag: el.tagName.toLowerCase(),
            text: text,
            id: el.id,
            class: el.className,
            type: el.type
        };
    })
        .filter(i => i.text.length > 0)
        .slice(0, 60);

    return {
        url: window.location.href,
        title: document.title,
        text: document.body.innerText.substring(0, 5000),
        interactive: elements
    };
}

// Utility: sleep
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Auto-deactivate after 30 seconds of inactivity
let inactivityTimer = null;
function resetInactivityTimer() {
    if (inactivityTimer) clearTimeout(inactivityTimer);
    inactivityTimer = setTimeout(() => {
        setAgentActive(false);
    }, 30000);
}

// Initialize
console.log('WebPilot Agent – AI-Powered Browser Assistant content script loaded');
