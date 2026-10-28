from langchain_core.tools import tool
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
import base64
import json
import time

class BrowserManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
            cls._instance._init_browser()
        return cls._instance
    
    def _init_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = self.context.new_page()

    def get_page(self):
        return self.page
    
    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

# Tool Definitions
browser_manager = BrowserManager()

@tool
def wait(seconds: int = 2) -> str:
    """Wait for a specified number of seconds. Useful for letting dynamic content load."""
    time.sleep(seconds)
    return f"Waited {seconds} seconds"

@tool
def navigate(url: str) -> str:
    """Navigate to a URL"""
    try:
        page = browser_manager.get_page()
        page.goto(url, timeout=15000) # Reduced timeout
        return f"Navigated to {url}"
    except Exception as e:
        return f"Navigation failed: {str(e)}"

@tool
def click_element(selector: str) -> str:
    """Click an element. Smartly tries selectors, text, and roles."""
    page = browser_manager.get_page()
    try:
        # 1. Try exact selector
        if selector.startswith('#') or selector.startswith('.'):
            try:
                page.click(selector, timeout=1000)
                return f"Clicked element with selector: {selector}"
            except:
                pass 

        # 2. Try by text (submit buttons often have text "Guess", "Search", etc.)
        try:
            page.get_by_text(selector, exact=True).click(timeout=1000)
            return f"Clicked element with exact text: {selector}"
        except:
            pass
        
        # 3. Try by role (button)
        try:
            page.get_by_role("button", name=selector).click(timeout=1000)
            return f"Clicked button with name: {selector}"
        except:
            pass

        # 4. Fallback
        try:
            page.click(selector, timeout=2000)
            return f"Clicked: {selector}"
        except:
            pass

        return f"Could not find clickable element matching '{selector}'"

    except Exception as e:
        return f"Click failed: {str(e)}"

@tool
def type_text(selector: str, text: str) -> str:
    """Type text into an input field AND PRESS ENTER."""
    page = browser_manager.get_page()
    try:
        # Try finding by selector, placeholder, or label
        try:
            page.fill(selector, text, timeout=2000)
            # CRITICAL: Always press Enter after typing to ensure submission
            page.keyboard.press("Enter")
        except:
            try:
                page.get_by_placeholder(selector).fill(text, timeout=2000)
                page.keyboard.press("Enter")
            except:
                page.get_by_label(selector).fill(text, timeout=2000)
                page.keyboard.press("Enter")
        
        return f"Typed '{text}' into {selector} and pressed Enter"
    except Exception as e:
        return f"Type failed: {str(e)}"

@tool
def press_key(key: str) -> str:
    """Press a keyboard key (Enter, Tab, Escape, etc.)"""
    try:
        browser_manager.get_page().keyboard.press(key)
        return f"Pressed {key}"
    except Exception as e:
        return f"Press key failed: {str(e)}"

@tool
def scroll(direction: str = "down", amount: int = 500) -> str:
    """Scroll the page 'up' or 'down'."""
    try:
        page = browser_manager.get_page()
        if direction == "down":
            page.evaluate(f"window.scrollBy(0, {amount})")
        else:
            page.evaluate(f"window.scrollBy(0, -{amount})")
        return f"Scrolled {direction} by {amount}px"
    except Exception as e:
        return f"Scroll failed: {e}"

def get_page_analysis():
    """Helper to get page state (NOT A TOOL, internal use)"""
    page = browser_manager.get_page()
    try:
        # Optimization: Take smaller screenshots (JPEG, lower quality)
        screenshot = page.screenshot(type='jpeg', quality=50)
        screenshot_b64 = base64.b64encode(screenshot).decode()
        
        # Dense JS analysis - Optimized to be faster and focus on actionable elements
        page_info = page.evaluate("""() => {
            const actionable = Array.from(document.querySelectorAll('button, a, input, textarea, [role="button"]'));
            const elements = actionable.map(el => {
                     let text = el.innerText || el.placeholder || el.value || el.getAttribute('aria-label') || "";
                     text = text.trim().substring(0, 50);
                     if (!text && el.tagName === 'INPUT') text = "Input: " + el.type;
                     return {
                        tag: el.tagName.toLowerCase(),
                        text: text,
                        id: el.id,
                        class: el.className,
                        type: el.type
                     }
                })
                .filter(i => i.text.length > 0)
                .slice(0, 60); // slightly increased limit
            
            return {
                url: window.location.href,
                title: document.title,
                text: document.body.innerText.substring(0, 5000), 
                interactive: elements
            }
        }""")
        
        return {
            "screenshot_b64": screenshot_b64,
            "url": page_info["url"],
            "title": page_info["title"],
            "text": page_info["text"],
            "interactive": page_info["interactive"]
        }
    except Exception as e:
        return {"error": str(e), "url": "error", "screenshot_b64": None, "text": "", "interactive": []}
