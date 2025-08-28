#!/usr/bin/env python3
"""
Advanced Automation Example

This example demonstrates sophisticated automation patterns using MKD v2.0:
1. Multi-step workflows with conditional logic
2. Template-based action generation
3. Error recovery and retry mechanisms
4. Integration with external systems
5. Real-world application automation
"""

import asyncio
import logging
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from mkd_v2.integration import SystemController, EventBus, EventType
from mkd_v2.playback import InputAction, ActionType, ExecutionConfig
from mkd_v2.performance import get_profiler, get_cache
from mkd_v2.exceptions import RecordingError, PlaybackError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AutomationStep:
    """Represents a single step in an automation workflow"""
    name: str
    actions: List[InputAction]
    conditions: Dict[str, Any] = None
    retry_attempts: int = 3
    timeout_seconds: float = 30.0
    success_criteria: str = None


class WorkflowTemplate:
    """Template system for creating reusable automation workflows"""
    
    def __init__(self, name: str):
        self.name = name
        self.steps: List[AutomationStep] = []
        self.variables: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
    
    def add_step(self, step: AutomationStep) -> 'WorkflowTemplate':
        """Add a step to the workflow"""
        self.steps.append(step)
        return self
    
    def set_variable(self, name: str, value: Any) -> 'WorkflowTemplate':
        """Set a workflow variable"""
        self.variables[name] = value
        return self
    
    def add_click_step(self, name: str, x: int, y: int, button: str = "left") -> 'WorkflowTemplate':
        """Add a click step to the workflow"""
        action = InputAction(
            action_type=ActionType.CLICK if button == "left" else ActionType.RIGHT_CLICK,
            timestamp=time.time(),
            coordinates=(x, y),
            metadata={"template_generated": True}
        )
        step = AutomationStep(name=name, actions=[action])
        return self.add_step(step)
    
    def add_type_step(self, name: str, text: str, delay: float = 0.1) -> 'WorkflowTemplate':
        """Add a typing step to the workflow"""
        actions = []
        
        # Add optional delay before typing
        if delay > 0:
            actions.append(InputAction(
                action_type=ActionType.WAIT,
                timestamp=time.time(),
                duration=delay
            ))
        
        # Add the text typing action
        actions.append(InputAction(
            action_type=ActionType.TYPE_TEXT,
            timestamp=time.time(),
            text=text,
            metadata={"template_generated": True}
        ))
        
        step = AutomationStep(name=name, actions=actions)
        return self.add_step(step)
    
    def add_wait_step(self, name: str, duration: float) -> 'WorkflowTemplate':
        """Add a wait step to the workflow"""
        action = InputAction(
            action_type=ActionType.WAIT,
            timestamp=time.time(),
            duration=duration
        )
        step = AutomationStep(name=name, actions=[action])
        return self.add_step(step)
    
    def process_variables(self, text: str) -> str:
        """Process variables in text using {variable_name} syntax"""
        for var_name, var_value in self.variables.items():
            text = text.replace(f"{{{var_name}}}", str(var_value))
        return text


class AdvancedAutomationEngine:
    """Advanced automation engine with sophisticated workflow capabilities"""
    
    def __init__(self):
        self.controller = SystemController()
        self.event_bus = None
        self.profiler = get_profiler()
        self.cache = get_cache()
        self.workflows: Dict[str, WorkflowTemplate] = {}
        
        # Execution state
        self.current_workflow: Optional[WorkflowTemplate] = None
        self.execution_context: Dict[str, Any] = {}
        
        # Statistics
        self.stats = {
            "workflows_executed": 0,
            "successful_workflows": 0,
            "failed_workflows": 0,
            "total_steps_executed": 0,
            "total_execution_time": 0.0
        }
    
    async def initialize(self):
        """Initialize the automation engine"""
        logger.info("🚀 Initializing Advanced Automation Engine...")
        
        await self.controller.initialize()
        
        # Get event bus for monitoring
        self.event_bus = self.controller.get_component("event_bus")
        
        # Subscribe to events
        if self.event_bus:
            self.event_bus.subscribe(EventType.ACTION_EXECUTED, self._on_action_executed)
            self.event_bus.subscribe(EventType.ERROR_OCCURRED, self._on_error_occurred)
        
        logger.info("✅ Advanced Automation Engine initialized")
    
    async def shutdown(self):
        """Shut down the automation engine"""
        logger.info("🧹 Shutting down Advanced Automation Engine...")
        await self.controller.shutdown()
        logger.info("✅ Shutdown complete")
    
    def register_workflow(self, workflow: WorkflowTemplate):
        """Register a workflow template"""
        self.workflows[workflow.name] = workflow
        logger.info(f"📝 Registered workflow: {workflow.name}")
    
    @get_profiler().profile("execute_workflow")
    async def execute_workflow(self, workflow_name: str, variables: Dict[str, Any] = None) -> bool:
        """Execute a registered workflow"""
        if workflow_name not in self.workflows:
            logger.error(f"❌ Workflow not found: {workflow_name}")
            return False
        
        workflow = self.workflows[workflow_name]
        self.current_workflow = workflow
        
        # Set variables
        if variables:
            for var_name, var_value in variables.items():
                workflow.set_variable(var_name, var_value)
        
        logger.info(f"🎬 Executing workflow: {workflow_name}")
        start_time = time.time()
        
        try:
            success = await self._execute_workflow_steps(workflow)
            
            execution_time = time.time() - start_time
            self.stats["workflows_executed"] += 1
            self.stats["total_execution_time"] += execution_time
            
            if success:
                self.stats["successful_workflows"] += 1
                logger.info(f"✅ Workflow completed successfully: {workflow_name} ({execution_time:.2f}s)")
            else:
                self.stats["failed_workflows"] += 1
                logger.warning(f"⚠️  Workflow completed with errors: {workflow_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Workflow execution failed: {workflow_name} - {e}")
            self.stats["failed_workflows"] += 1
            return False
        finally:
            self.current_workflow = None
    
    async def _execute_workflow_steps(self, workflow: WorkflowTemplate) -> bool:
        """Execute the steps of a workflow"""
        overall_success = True
        
        for i, step in enumerate(workflow.steps, 1):
            logger.info(f"📍 Step {i}/{len(workflow.steps)}: {step.name}")
            
            # Check step conditions if any
            if step.conditions and not self._evaluate_conditions(step.conditions):
                logger.info(f"⏭️  Skipping step due to conditions: {step.name}")
                continue
            
            # Execute step with retries
            step_success = await self._execute_step_with_retries(step)
            
            if step_success:
                logger.info(f"✅ Step completed: {step.name}")
            else:
                logger.warning(f"❌ Step failed: {step.name}")
                overall_success = False
                
                # Check if we should continue or abort
                if step.conditions and step.conditions.get("abort_on_failure", False):
                    logger.error(f"🛑 Aborting workflow due to critical step failure: {step.name}")
                    break
            
            self.stats["total_steps_executed"] += 1
            
            # Brief pause between steps
            await asyncio.sleep(0.1)
        
        return overall_success
    
    async def _execute_step_with_retries(self, step: AutomationStep) -> bool:
        """Execute a step with retry logic"""
        for attempt in range(step.retry_attempts):
            try:
                # Process variables in actions
                processed_actions = self._process_step_variables(step)
                
                # Configure execution
                config = ExecutionConfig(
                    fail_on_error=False,
                    screenshot_on_error=True,
                    timeout=step.timeout_seconds
                )
                
                # Execute actions
                result = await self.controller.execute_actions(processed_actions, config=config)
                
                if result.success:
                    return True
                
                if attempt < step.retry_attempts - 1:
                    retry_delay = min(2 ** attempt, 10)  # Exponential backoff, max 10s
                    logger.info(f"🔄 Retrying step in {retry_delay}s (attempt {attempt + 2}/{step.retry_attempts})")
                    await asyncio.sleep(retry_delay)
                
            except Exception as e:
                logger.error(f"❌ Step execution error (attempt {attempt + 1}): {e}")
                
                if attempt < step.retry_attempts - 1:
                    await asyncio.sleep(1)
        
        return False
    
    def _process_step_variables(self, step: AutomationStep) -> List[InputAction]:
        """Process variables in step actions"""
        processed_actions = []
        
        for action in step.actions:
            # Create a copy of the action
            new_action = InputAction(
                action_type=action.action_type,
                timestamp=action.timestamp,
                coordinates=action.coordinates,
                key=action.key,
                modifiers=action.modifiers.copy() if action.modifiers else [],
                text=action.text,
                metadata=action.metadata.copy() if action.metadata else {}
            )
            
            # Process variables in text
            if new_action.text and self.current_workflow:
                new_action.text = self.current_workflow.process_variables(new_action.text)
            
            processed_actions.append(new_action)
        
        return processed_actions
    
    def _evaluate_conditions(self, conditions: Dict[str, Any]) -> bool:
        """Evaluate step conditions"""
        # Simple condition evaluation - can be extended
        for condition, expected in conditions.items():
            if condition == "workflow_variable":
                var_name = expected.get("name")
                var_value = expected.get("value")
                if self.current_workflow and var_name in self.current_workflow.variables:
                    if self.current_workflow.variables[var_name] != var_value:
                        return False
            # Add more condition types as needed
        
        return True
    
    async def _on_action_executed(self, event_data: Dict[str, Any]):
        """Handle action executed events"""
        if self.current_workflow:
            logger.debug(f"📊 Action executed: {event_data.get('action_type')}")
    
    async def _on_error_occurred(self, event_data: Dict[str, Any]):
        """Handle error events"""
        logger.warning(f"⚠️  Error occurred during workflow: {event_data}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "registered_workflows": len(self.workflows),
            "execution_stats": self.stats.copy(),
            "average_execution_time": (
                self.stats["total_execution_time"] / max(self.stats["workflows_executed"], 1)
            ),
            "success_rate": (
                (self.stats["successful_workflows"] / max(self.stats["workflows_executed"], 1)) * 100
            ) if self.stats["workflows_executed"] > 0 else 0
        }


def create_web_form_automation() -> WorkflowTemplate:
    """Create a web form automation workflow template"""
    return (WorkflowTemplate("web_form_automation")
        .set_variable("username", "demo_user")
        .set_variable("email", "demo@example.com")
        .set_variable("message", "This is an automated test message")
        
        # Step 1: Navigate to form
        .add_click_step("click_username_field", 200, 150)
        .add_wait_step("wait_for_focus", 0.5)
        
        # Step 2: Fill username
        .add_type_step("enter_username", "{username}")
        .add_wait_step("wait_after_username", 0.3)
        
        # Step 3: Navigate to email field
        .add_click_step("click_email_field", 200, 200)
        .add_wait_step("wait_for_email_focus", 0.5)
        
        # Step 4: Fill email
        .add_type_step("enter_email", "{email}")
        .add_wait_step("wait_after_email", 0.3)
        
        # Step 5: Navigate to message field
        .add_click_step("click_message_field", 200, 250)
        .add_wait_step("wait_for_message_focus", 0.5)
        
        # Step 6: Fill message
        .add_type_step("enter_message", "{message}")
        .add_wait_step("wait_after_message", 0.5)
        
        # Step 7: Submit form
        .add_click_step("click_submit", 200, 320)
        .add_wait_step("wait_for_submission", 2.0)
    )


def create_file_management_automation() -> WorkflowTemplate:
    """Create a file management automation workflow"""
    return (WorkflowTemplate("file_management")
        .set_variable("source_folder", "/path/to/source")
        .set_variable("dest_folder", "/path/to/destination")
        .set_variable("file_pattern", "*.txt")
        
        # This would integrate with actual file operations
        .add_click_step("open_file_manager", 100, 50)
        .add_wait_step("wait_for_file_manager", 2.0)
        
        # Navigate to source folder
        .add_click_step("click_address_bar", 400, 100)
        .add_type_step("type_source_path", "{source_folder}")
        
        # Add more steps as needed for file operations
    )


async def main():
    """Main demonstration function"""
    print("MKD Automation Platform v2.0 - Advanced Automation Example")
    print("=" * 70)
    
    engine = AdvancedAutomationEngine()
    
    try:
        # Initialize the engine
        await engine.initialize()
        
        # Register workflow templates
        web_form_workflow = create_web_form_automation()
        engine.register_workflow(web_form_workflow)
        
        file_mgmt_workflow = create_file_management_automation()
        engine.register_workflow(file_mgmt_workflow)
        
        print("\n📋 Registered Workflows:")
        for name, workflow in engine.workflows.items():
            print(f"  • {name}: {len(workflow.steps)} steps")
        
        # Demonstrate workflow execution (dry run without actual GUI interaction)
        print(f"\n🎭 Demonstrating workflow execution...")
        print("Note: This is a demonstration - no actual GUI interactions will occur")
        
        # Execute web form workflow with custom variables
        success = await engine.execute_workflow(
            "web_form_automation",
            variables={
                "username": "advanced_user",
                "email": "advanced@example.com", 
                "message": "Advanced automation demonstration"
            }
        )
        
        print(f"Web form workflow result: {'✅ Success' if success else '❌ Failed'}")
        
        # Show statistics
        stats = engine.get_statistics()
        print(f"\n📊 Execution Statistics:")
        print(f"  • Workflows executed: {stats['execution_stats']['workflows_executed']}")
        print(f"  • Success rate: {stats['success_rate']:.1f}%")
        print(f"  • Average execution time: {stats['average_execution_time']:.2f}s")
        print(f"  • Total steps executed: {stats['execution_stats']['total_steps_executed']}")
        
        # Demonstrate saving/loading workflows
        workflow_file = Path("demo_workflow.json")
        print(f"\n💾 Saving workflow to: {workflow_file}")
        
        # Save workflow (simplified serialization)
        workflow_data = {
            "name": web_form_workflow.name,
            "variables": web_form_workflow.variables,
            "steps": [
                {
                    "name": step.name,
                    "actions": [
                        {
                            "action_type": action.action_type.value,
                            "coordinates": action.coordinates,
                            "text": action.text,
                            "duration": getattr(action, 'duration', None)
                        }
                        for action in step.actions
                    ]
                }
                for step in web_form_workflow.steps
            ]
        }
        
        with open(workflow_file, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        print(f"✅ Workflow saved successfully")
        
        print(f"\n🎉 Advanced automation demonstration completed!")
        print("Key features demonstrated:")
        print("  • Template-based workflow creation")
        print("  • Variable substitution in actions") 
        print("  • Multi-step execution with retry logic")
        print("  • Conditional step execution")
        print("  • Comprehensive error handling")
        print("  • Performance profiling integration")
        print("  • Workflow serialization/deserialization")
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        await engine.shutdown()


if __name__ == "__main__":
    asyncio.run(main())