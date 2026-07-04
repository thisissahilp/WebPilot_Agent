from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """State of the browser automation agent"""
    messages: Annotated[list, add_messages]
    task: str
    current_url: str
    screenshot_b64: str
    page_content: str
    plan: List[dict]
    current_step: int
    completed: bool
    error: Optional[str]
