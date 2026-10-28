from typing import Optional, Dict, Any
from datetime import datetime
import json

class ActionLogger:
    """Format agent actions for chat display with reasoning"""
    
    def __init__(self):
        self.actions = []
    
    def log_action(
        self,
        action_type: str,
        target: str,
        reasoning: str,
        thought_process: str,
        screenshot_b64: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an agent action with reasoning
        
        Args:
            action_type: Type of action (click, type, scroll, navigate)
            target: Description of target element
            reasoning: 3-4 line explanation of why this action
            thought_process: Agent's internal reasoning
            screenshot_b64: Optional annotated screenshot
            metadata: Additional metadata (coordinates, etc.)
            
        Returns:
            Formatted action log dict
        """
        action_log = {
            "type": "agent_action",
            "action": action_type,
            "target": target,
            "reasoning": self._format_reasoning(reasoning),
            "thought_process": self._format_thought_process(thought_process),
            "screenshot": screenshot_b64,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.actions.append(action_log)
        return action_log
    
    def _format_reasoning(self, reasoning: str) -> str:
        """Format reasoning to be 3-4 lines max"""
        lines = reasoning.strip().split('\n')
        # Take first 4 lines, ensure each is not too long
        formatted_lines = []
        for line in lines[:4]:
            if len(line) > 80:
                line = line[:77] + "..."
            formatted_lines.append(line)
        return '\n'.join(formatted_lines)
    
    def _format_thought_process(self, thought: str) -> str:
        """Format thought process to be concise"""
        if len(thought) > 200:
            return thought[:197] + "..."
        return thought
    
    def get_timeline(self) -> list:
        """Get all actions as a timeline"""
        return [
            {
                "index": i,
                "action": action["action"],
                "target": action["target"],
                "timestamp": action["timestamp"]
            }
            for i, action in enumerate(self.actions)
        ]
    
    def get_action(self, index: int) -> Optional[Dict[str, Any]]:
        """Get specific action by index"""
        if 0 <= index < len(self.actions):
            return self.actions[index]
        return None
    
    def format_for_chat(self, action_log: Dict[str, Any]) -> str:
        """Format action log for chat display"""
        return f"""🤖 Agent: {action_log['action'].upper()} - {action_log['target']}

Reasoning: {action_log['reasoning']}

Thought Process: {action_log['thought_process']}
"""
    
    def to_json(self, action_log: Dict[str, Any]) -> str:
        """Convert action log to JSON string"""
        # Remove screenshot from JSON to reduce size
        log_copy = action_log.copy()
        if 'screenshot' in log_copy:
            log_copy['screenshot'] = '<base64_data>' if log_copy['screenshot'] else None
        return json.dumps(log_copy, indent=2)
    
    def clear(self):
        """Clear all logged actions"""
        self.actions = []
