from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from sitback.state import AgentState
from sitback.tools.action_logger import ActionLogger
from sitback.tools.screenshot_annotator import ScreenshotAnnotator
import json
import os
import asyncio

class ExtensionAgent:
    """Agent that controls user's browser via Chrome extension"""
    
    def __init__(self, api_key: str = None, extension_handler=None, websocket_manager=None):
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=api_key,
            temperature=0,
            max_output_tokens=4096
        )
        self.extension = extension_handler
        self.ws_manager = websocket_manager
        self.action_logger = ActionLogger()
        self.annotator = ScreenshotAnnotator()
        self.graph = self._create_graph()
        # For compatibility with api_server timeline requests
        self.browser = self
    
    def _create_graph(self):
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("analyze", self.analyze_task)
        workflow.add_node("plan", self.create_plan)
        workflow.add_node("execute", self.execute_step)
        workflow.add_node("verify", self.verify_result)
        
        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "plan")
        workflow.add_edge("plan", "execute")
        workflow.add_edge("execute", "verify")
        
        workflow.add_conditional_edges(
            "verify",
            self.should_continue,
            {
                "continue": "execute",
                "replan": "plan",
                "end": END
            }
        )
        
        return workflow.compile()
    
    async def _send_action(self, action_log: dict):
        """Send action to frontend via WebSocket"""
        if self.ws_manager:
            await self.ws_manager.send_action(action_log)
    
    def analyze_task(self, state: AgentState) -> AgentState:
        """Analyze the user's task"""
        print("🔍 Analyzing task...")
        
        # Check if extension is connected
        if not self.extension or not self.extension.is_connected:
            print("⚠️ Extension not connected, skipping page state retrieval")
            state["error"] = "Extension not connected. Please ensure the Chrome extension is installed and connected."
            return state
        
        # Get page state from extension
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        page_state = loop.run_until_complete(self.extension.get_page_state())
        
        if page_state:
            state["current_url"] = page_state.get("url", "")
            state["page_content"] = json.dumps(page_state)
        
        return state
    
    def create_plan(self, state: AgentState) -> AgentState:
        """Create action plan with reasoning"""
        print("📋 Creating plan...")
        
        messages = [
            SystemMessage(content="""You are a browser automation expert.
Create a step-by-step plan with detailed reasoning for each action.

Return ONLY valid JSON:
{
  "steps": [
    {
      "action": "navigate|click|type|press_key|scroll",
      "params": {"selector": "...", "text": "...", "url": "..."},
      "reasoning": "Detailed 3-4 line explanation of WHY this step is needed.",
      "thought_process": "Your internal reasoning about how to execute this."
    }
  ]
}
"""),
            HumanMessage(content=f"""
Task: {state['task']}

Current page state:
{state.get('page_content', '{}')}

Create a detailed plan.
""")
        ]
        
        try:
            response = self.llm.invoke(messages)
            plan_text = response.content
            
            if "```json" in plan_text:
                json_part = plan_text.split("```json")[1].split("```")[0]
            elif "```" in plan_text:
                json_part = plan_text.split("```")[1].split("```")[0]
            else:
                json_part = plan_text
            
            plan = json.loads(json_part.strip())
            state["plan"] = plan["steps"]
            state["current_step"] = 0
            state["error"] = None
            
            print(f"\n🤔 Agent's Plan ({len(plan['steps'])} steps):")
            for i, step in enumerate(plan["steps"]):
                print(f"  {i+1}. {step['action'].upper()}")
            
        except Exception as e:
            print(f"⚠️ Plan creation failed: {e}")
            state["plan"] = []
            state["error"] = str(e)
        
        return state
    
    def execute_step(self, state: AgentState) -> AgentState:
        """Execute current step via extension"""
        if not state.get("plan") or state["current_step"] >= len(state["plan"]):
            state["completed"] = True
            return state
        
        step = state["plan"][state["current_step"]]
        print(f"\n⚡ Executing step {state['current_step'] + 1}: {step['action']}")
        
        try:
            # Send command to extension
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            success = loop.run_until_complete(
                self.extension.send_command(step)
            )
            
            if not success:
                raise Exception("Extension not connected")
            
            # Wait for result
            result = loop.run_until_complete(
                self.extension.wait_for_result(timeout=10.0)
            )
            
            if not result or not result.get("success"):
                error = result.get("error", "Unknown error") if result else "Timeout"
                raise Exception(error)
            
            # Wait for screenshot
            screenshot_b64 = loop.run_until_complete(
                self.extension.wait_for_screenshot(timeout=5.0)
            )
            
            # Annotate screenshot
            if screenshot_b64:
                coords = result.get("data", {}).get("coords")
                
                if coords and step["action"] == "click":
                    screenshot_b64 = self.annotator.annotate_click(
                        screenshot_b64,
                        x=coords["x"],
                        y=coords["y"],
                        label="CLICK"
                    )
                elif coords and step["action"] == "type":
                    screenshot_b64 = self.annotator.annotate_type(
                        screenshot_b64,
                        x=coords["x"],
                        y=coords["y"],
                        text=step["params"].get("text", "")
                    )
                elif step["action"] == "scroll":
                    screenshot_b64 = self.annotator.annotate_scroll(
                        screenshot_b64,
                        direction=step["params"].get("direction", "down"),
                        amount=step["params"].get("amount", 500)
                    )
                elif step["action"] == "navigate":
                    screenshot_b64 = self.annotator.annotate_navigate(
                        screenshot_b64,
                        url=step["params"].get("url", "")
                    )
                
                # Add control banner
                screenshot_b64 = self.annotator.add_control_banner(
                    screenshot_b64,
                    action_type=step["action"],
                    timestamp=self._get_timestamp()
                )
            
            # Log action
            action_log = self.action_logger.log_action(
                action_type=step["action"],
                target=str(step["params"]),
                reasoning=step.get("reasoning", ""),
                thought_process=step.get("thought_process", ""),
                screenshot_b64=screenshot_b64,
                metadata=result.get("data", {})
            )
            
            # Send to frontend
            if self.ws_manager:
                loop.run_until_complete(self._send_action(action_log))
            
            # Wait for page to update
            import time
            time.sleep(2)
            
        except Exception as e:
            state["error"] = f"Step {state['current_step']} failed: {str(e)}"
            print(f"❌ Error: {state['error']}")
        
        return state
    
    def verify_result(self, state: AgentState) -> AgentState:
        """Verify if step was successful"""
        print("✅ Verifying result...")
        
        if not state.get("error"):
            state["current_step"] += 1
        
        return state
    
    def should_continue(self, state: AgentState) -> str:
        """Decide whether to continue"""
        # If error and already tried replanning, stop
        if state.get("error"):
            replan_count = state.get("replan_count", 0)
            if replan_count >= 2:
                print("⚠️ Too many replanning attempts, stopping")
                return "end"
            state["replan_count"] = replan_count + 1
            return "replan"
        if state["current_step"] >= len(state["plan"]):
            return "end"
        return "continue"
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def run(self, task: str):
        """Run the agent on a task"""
        initial_state = {
            "messages": [],
            "task": task,
            "current_url": "",
            "screenshot_b64": "",
            "page_content": "",
            "plan": [],
            "current_step": 0,
            "completed": False,
            "error": None,
            "replan_count": 0
        }
        
        # Increase recursion limit
        config = {"recursion_limit": 50}
        final_state = self.graph.invoke(initial_state, config=config)
        
        print(f"\n✨ Task completed!")
        return final_state
    
    def get_timeline(self):
        """Get action timeline"""
        return self.action_logger.get_timeline()
    
    def get_action(self, index: int):
        """Get specific action"""
        return self.action_logger.get_action(index)
