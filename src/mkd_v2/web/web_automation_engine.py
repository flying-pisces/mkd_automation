"""
Web Automation Engine

Unified web automation system integrating all web enhancement components:
- DOM inspection and manipulation
- Multi-tab browser coordination
- JavaScript injection and execution
- Cross-browser compatibility
- Advanced web interaction patterns
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import time
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .dom_inspector import DOMInspector, DOMQuery, DetectionStrategy, ElementInfo, InspectionResult
from .browser_controller import BrowserController, BrowserType, BrowserCommand, TabInfo, CommandResult
from .javascript_injector import JavaScriptInjector, ScriptType, ExecutionContext, ScriptContext, ScriptSecurity, ScriptResult

logger = logging.getLogger(__name__)


class WebActionType(Enum):
    """Types of web actions"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    HOVER = "hover"
    SELECT = "select"
    DRAG_DROP = "drag_drop"
    UPLOAD_FILE = "upload_file"
    EXTRACT_DATA = "extract_data"
    EXECUTE_SCRIPT = "execute_script"
    WAIT_FOR_ELEMENT = "wait_for_element"
    WAIT_FOR_CONDITION = "wait_for_condition"


class InteractionMode(Enum):
    """Modes for web interaction"""
    STANDARD = "standard"        # Standard automation approach
    STEALTH = "stealth"         # Stealthy automation to avoid detection
    PERFORMANCE = "performance" # Optimized for speed
    RELIABLE = "reliable"       # Maximum reliability with retries
    HYBRID = "hybrid"           # Combination of methods


@dataclass
class WebAction:
    """Web automation action definition"""
    action_type: WebActionType
    target: Dict[str, Any]  # Element targeting information
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 10.0
    retry_count: int = 3
    retry_delay: float = 1.0
    validation: Optional[Dict[str, Any]] = None
    fallback_actions: List['WebAction'] = field(default_factory=list)


@dataclass
class WebWorkflow:
    """Complete web automation workflow"""
    workflow_id: str
    name: str
    actions: List[WebAction]
    initial_url: Optional[str] = None
    browser_config: Dict[str, Any] = field(default_factory=dict)
    global_timeout: float = 300.0  # 5 minutes
    parallel_execution: bool = False
    error_recovery: bool = True


@dataclass
class ExecutionResult:
    """Result of web action execution"""
    success: bool
    action: WebAction
    execution_time: float
    result_data: Any = None
    element_info: Optional[ElementInfo] = None
    screenshots: List[str] = field(default_factory=list)
    console_logs: List[str] = field(default_factory=list)
    network_logs: List[Dict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    retry_attempts: int = 0


@dataclass
class WorkflowResult:
    """Result of complete workflow execution"""
    success: bool
    workflow: WebWorkflow
    execution_results: List[ExecutionResult]
    total_execution_time: float
    success_rate: float
    failed_actions: List[int] = field(default_factory=list)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    final_state: Dict[str, Any] = field(default_factory=dict)


class WebAutomationEngine:
    """Unified web automation engine with advanced capabilities"""
    
    def __init__(self, interaction_mode: InteractionMode = InteractionMode.HYBRID):
        self.interaction_mode = interaction_mode
        
        # Initialize component systems
        self.dom_inspector = DOMInspector()
        self.browser_controller = BrowserController()
        self.javascript_injector = JavaScriptInjector()
        
        # Execution state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.session_contexts: Dict[str, ScriptContext] = {}
        self.execution_history: List[WorkflowResult] = []
        
        # Performance and reliability settings
        self.performance_config = self._get_performance_config()
        self.reliability_config = self._get_reliability_config()
        
        # Thread pool for parallel execution
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def _get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration based on interaction mode"""
        configs = {
            InteractionMode.PERFORMANCE: {
                "page_load_timeout": 15.0,
                "element_timeout": 3.0,
                "implicit_wait": 0.5,
                "script_timeout": 5.0,
                "parallel_actions": True,
                "cache_elements": True,
                "preload_scripts": True
            },
            InteractionMode.RELIABLE: {
                "page_load_timeout": 60.0,
                "element_timeout": 15.0,
                "implicit_wait": 2.0,
                "script_timeout": 30.0,
                "parallel_actions": False,
                "cache_elements": False,
                "preload_scripts": False
            },
            InteractionMode.STANDARD: {
                "page_load_timeout": 30.0,
                "element_timeout": 10.0,
                "implicit_wait": 1.0,
                "script_timeout": 15.0,
                "parallel_actions": False,
                "cache_elements": True,
                "preload_scripts": True
            }
        }
        
        return configs.get(self.interaction_mode, configs[InteractionMode.STANDARD])
    
    def _get_reliability_config(self) -> Dict[str, Any]:
        """Get reliability configuration based on interaction mode"""
        configs = {
            InteractionMode.RELIABLE: {
                "max_retries": 5,
                "retry_delay_multiplier": 1.5,
                "element_stability_wait": 2.0,
                "verify_actions": True,
                "screenshot_on_error": True,
                "fallback_strategies": True
            },
            InteractionMode.PERFORMANCE: {
                "max_retries": 1,
                "retry_delay_multiplier": 1.0,
                "element_stability_wait": 0.1,
                "verify_actions": False,
                "screenshot_on_error": False,
                "fallback_strategies": False
            },
            InteractionMode.STEALTH: {
                "max_retries": 3,
                "retry_delay_multiplier": 2.0,
                "element_stability_wait": 1.5,
                "verify_actions": True,
                "screenshot_on_error": False,
                "fallback_strategies": True,
                "human_like_delays": True,
                "randomize_timing": True
            }
        }
        
        return configs.get(self.interaction_mode, configs[InteractionMode.STANDARD])
    
    def execute_workflow(self, workflow: WebWorkflow) -> WorkflowResult:
        """Execute complete web automation workflow"""
        start_time = time.time()
        
        logger.info(f"Starting workflow execution: {workflow.name} ({len(workflow.actions)} actions)")
        
        # Initialize workflow result
        result = WorkflowResult(
            success=False,
            workflow=workflow,
            execution_results=[],
            total_execution_time=0.0,
            success_rate=0.0
        )
        
        try:
            # Create browser session
            session_id = self._setup_browser_session(workflow)
            
            # Navigate to initial URL if specified
            if workflow.initial_url:
                self._navigate_to_url(session_id, workflow.initial_url)
            
            # Setup script context
            context = self._create_script_context(session_id)
            self.session_contexts[session_id] = context
            
            # Preload libraries if enabled
            if self.performance_config.get("preload_scripts", False):
                self._preload_automation_libraries(context)
            
            # Execute actions
            if workflow.parallel_execution and self.performance_config.get("parallel_actions", False):
                execution_results = self._execute_actions_parallel(workflow.actions, context)
            else:
                execution_results = self._execute_actions_sequential(workflow.actions, context)
            
            result.execution_results = execution_results
            
            # Calculate success metrics
            successful_actions = [r for r in execution_results if r.success]
            result.success_rate = len(successful_actions) / len(execution_results) if execution_results else 0.0
            result.success = result.success_rate >= 0.8  # 80% success threshold
            result.failed_actions = [i for i, r in enumerate(execution_results) if not r.success]
            
            # Extract final state
            result.final_state = self._capture_final_state(context)
            
            # Collect extracted data
            result.extracted_data = self._collect_extracted_data(execution_results)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            result.success = False
            
        finally:
            result.total_execution_time = time.time() - start_time
            
            # Store in history
            self.execution_history.append(result)
            if len(self.execution_history) > 100:  # Keep last 100 workflows
                self.execution_history.pop(0)
        
        logger.info(f"Workflow completed: {result.success} (success rate: {result.success_rate:.2%})")
        return result
    
    def _setup_browser_session(self, workflow: WebWorkflow) -> str:
        """Setup browser session for workflow"""
        browser_type = BrowserType(workflow.browser_config.get('type', 'chrome'))
        headless = workflow.browser_config.get('headless', False)
        extensions = workflow.browser_config.get('extensions', [])
        
        session_id = self.browser_controller.create_session(
            browser_type=browser_type,
            headless=headless,
            extensions=extensions
        )
        
        self.active_workflows[workflow.workflow_id] = {
            'session_id': session_id,
            'start_time': time.time(),
            'workflow': workflow
        }
        
        return session_id
    
    def _navigate_to_url(self, session_id: str, url: str) -> None:
        """Navigate to initial URL"""
        result = self.browser_controller.execute_command(
            BrowserCommand.NAVIGATE,
            params={'url': url}
        )
        
        if not result.success:
            raise Exception(f"Failed to navigate to {url}: {result.error_message}")
        
        # Wait for page load
        time.sleep(self.performance_config.get("implicit_wait", 1.0))
    
    def _create_script_context(self, session_id: str) -> ScriptContext:
        """Create script execution context for session"""
        return ScriptContext(
            context_id=f"ctx_{session_id}",
            execution_context=ExecutionContext.PAGE,
            security_level=ScriptSecurity.SANDBOXED,
            isolated_world=True,
            tab_id=session_id  # Simplified - in real implementation would get actual tab ID
        )
    
    def _preload_automation_libraries(self, context: ScriptContext) -> None:
        """Preload automation utility libraries"""
        libraries_to_load = ['dom_utils', 'automation_utils']
        
        if logger.isEnabledFor(logging.DEBUG):
            libraries_to_load.append('debug_utils')
        
        for lib_id in libraries_to_load:
            try:
                result = self.javascript_injector.inject_library(lib_id, context)
                if result.success:
                    logger.debug(f"Preloaded library: {lib_id}")
                else:
                    logger.warning(f"Failed to preload library {lib_id}: {result.errors}")
            except Exception as e:
                logger.warning(f"Error preloading library {lib_id}: {e}")
    
    def _execute_actions_sequential(self, actions: List[WebAction], context: ScriptContext) -> List[ExecutionResult]:
        """Execute actions sequentially"""
        results = []
        
        for i, action in enumerate(actions):
            logger.debug(f"Executing action {i+1}/{len(actions)}: {action.action_type.value}")
            
            result = self._execute_single_action(action, context)
            results.append(result)
            
            # Stop on critical failure if error recovery is disabled
            if not result.success and not context.tab_id:  # Simplified error recovery check
                logger.error(f"Critical failure on action {i+1}, stopping workflow")
                break
            
            # Add delay between actions for reliability/stealth
            if self.reliability_config.get("human_like_delays", False):
                delay = self._calculate_human_delay()
                time.sleep(delay)
        
        return results
    
    def _execute_actions_parallel(self, actions: List[WebAction], context: ScriptContext) -> List[ExecutionResult]:
        """Execute actions in parallel where possible"""
        # Group actions by dependency - for now, execute sequentially
        # In real implementation, would analyze action dependencies and parallelize independent actions
        return self._execute_actions_sequential(actions, context)
    
    def _execute_single_action(self, action: WebAction, context: ScriptContext) -> ExecutionResult:
        """Execute a single web action with retries"""
        start_time = time.time()
        
        result = ExecutionResult(
            success=False,
            action=action,
            execution_time=0.0
        )
        
        max_retries = min(action.retry_count, self.reliability_config.get("max_retries", 3))
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    delay = action.retry_delay * (self.reliability_config.get("retry_delay_multiplier", 1.5) ** (attempt - 1))
                    logger.debug(f"Retrying action after {delay:.2f}s delay (attempt {attempt + 1}/{max_retries + 1})")
                    time.sleep(delay)
                
                result.retry_attempts = attempt
                
                # Execute action based on type
                execution_success = self._execute_action_by_type(action, context, result)
                
                if execution_success:
                    result.success = True
                    break
                    
            except Exception as e:
                logger.error(f"Action execution attempt {attempt + 1} failed: {e}")
                result.errors.append(f"Attempt {attempt + 1}: {str(e)}")
        
        # Try fallback actions if primary action failed
        if not result.success and action.fallback_actions:
            logger.info(f"Trying {len(action.fallback_actions)} fallback actions")
            
            for fallback_action in action.fallback_actions:
                fallback_result = self._execute_single_action(fallback_action, context)
                if fallback_result.success:
                    result.success = True
                    result.result_data = fallback_result.result_data
                    result.element_info = fallback_result.element_info
                    break
        
        result.execution_time = time.time() - start_time
        return result
    
    def _execute_action_by_type(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute action based on its type"""
        
        if action.action_type == WebActionType.NAVIGATE:
            return self._execute_navigate_action(action, context, result)
        
        elif action.action_type == WebActionType.CLICK:
            return self._execute_click_action(action, context, result)
        
        elif action.action_type == WebActionType.TYPE:
            return self._execute_type_action(action, context, result)
        
        elif action.action_type == WebActionType.SCROLL:
            return self._execute_scroll_action(action, context, result)
        
        elif action.action_type == WebActionType.WAIT_FOR_ELEMENT:
            return self._execute_wait_for_element_action(action, context, result)
        
        elif action.action_type == WebActionType.EXECUTE_SCRIPT:
            return self._execute_script_action(action, context, result)
        
        elif action.action_type == WebActionType.EXTRACT_DATA:
            return self._execute_extract_data_action(action, context, result)
        
        else:
            result.errors.append(f"Unsupported action type: {action.action_type.value}")
            return False
    
    def _execute_navigate_action(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute navigation action"""
        url = action.parameters.get('url')
        if not url:
            result.errors.append("Navigation action missing 'url' parameter")
            return False
        
        cmd_result = self.browser_controller.execute_command(
            BrowserCommand.NAVIGATE,
            target=context.tab_id,
            params={'url': url}
        )
        
        result.result_data = cmd_result.result_data
        return cmd_result.success
    
    def _execute_click_action(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute click action"""
        # Find element using DOM inspector
        element_info = self._find_element(action.target, context)
        if not element_info:
            result.errors.append("Element not found for click action")
            return False
        
        result.element_info = element_info
        
        # Execute click using JavaScript injection
        click_script = f"""
        const element = document.querySelector('{element_info.selectors.get("css", "")}');
        if (!element) throw new Error('Element not found');
        
        // Use automation utils for safe click
        return AutomationUtils.safeClick(element, {action.parameters});
        """
        
        script_result = self.javascript_injector.inject_script(
            click_script,
            context,
            libraries=['automation_utils'],
            async_execution=True
        )
        
        result.console_logs.extend(script_result.console_output)
        result.errors.extend(script_result.errors)
        
        return script_result.success
    
    def _execute_type_action(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute type action"""
        text = action.parameters.get('text', '')
        if not text:
            result.errors.append("Type action missing 'text' parameter")
            return False
        
        # Find element
        element_info = self._find_element(action.target, context)
        if not element_info:
            result.errors.append("Element not found for type action")
            return False
        
        result.element_info = element_info
        
        # Execute typing with automation utils
        type_script = f"""
        const element = document.querySelector('{element_info.selectors.get("css", "")}');
        if (!element) throw new Error('Element not found');
        
        return AutomationUtils.typeText(element, {json.dumps(text)}, {action.parameters});
        """
        
        script_result = self.javascript_injector.inject_script(
            type_script,
            context,
            libraries=['automation_utils'],
            async_execution=True
        )
        
        result.console_logs.extend(script_result.console_output)
        result.errors.extend(script_result.errors)
        
        return script_result.success
    
    def _execute_scroll_action(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute scroll action"""
        scroll_params = action.parameters
        
        scroll_script = f"""
        const scrollOptions = {json.dumps(scroll_params)};
        
        if (scrollOptions.element) {{
            const element = document.querySelector(scrollOptions.element);
            if (element) {{
                element.scrollIntoView(scrollOptions);
                return true;
            }}
        }} else {{
            window.scrollBy(scrollOptions.x || 0, scrollOptions.y || 0);
            return true;
        }}
        
        return false;
        """
        
        script_result = self.javascript_injector.inject_script(scroll_script, context)
        
        result.console_logs.extend(script_result.console_output)
        result.errors.extend(script_result.errors)
        
        return script_result.success
    
    def _execute_wait_for_element_action(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute wait for element action"""
        timeout = action.parameters.get('timeout', action.timeout) * 1000  # Convert to ms
        
        wait_script = f"""
        const selector = '{action.target.get("css_selector", "")}';
        const timeout = {timeout};
        
        return DOMUtils.waitForElement(selector, timeout);
        """
        
        script_result = self.javascript_injector.inject_script(
            wait_script,
            context,
            libraries=['dom_utils'],
            async_execution=True
        )
        
        result.console_logs.extend(script_result.console_output)
        result.errors.extend(script_result.errors)
        
        return script_result.success
    
    def _execute_script_action(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute custom script action"""
        script = action.parameters.get('script', '')
        if not script:
            result.errors.append("Script action missing 'script' parameter")
            return False
        
        libraries = action.parameters.get('libraries', [])
        async_execution = action.parameters.get('async', False)
        
        script_result = self.javascript_injector.inject_script(
            script,
            context,
            libraries=libraries,
            async_execution=async_execution
        )
        
        result.result_data = script_result.result_value
        result.console_logs.extend(script_result.console_output)
        result.errors.extend(script_result.errors)
        
        return script_result.success
    
    def _execute_extract_data_action(self, action: WebAction, context: ScriptContext, result: ExecutionResult) -> bool:
        """Execute data extraction action"""
        extractors = action.parameters.get('extractors', {})
        if not extractors:
            result.errors.append("Extract data action missing 'extractors' parameter")
            return False
        
        extract_script = f"""
        const extractors = {json.dumps(extractors)};
        return AutomationUtils.extractData(extractors);
        """
        
        script_result = self.javascript_injector.inject_script(
            extract_script,
            context,
            libraries=['automation_utils']
        )
        
        if script_result.success:
            result.result_data = script_result.result_value
        
        result.console_logs.extend(script_result.console_output)
        result.errors.extend(script_result.errors)
        
        return script_result.success
    
    def _find_element(self, target: Dict[str, Any], context: ScriptContext) -> Optional[ElementInfo]:
        """Find element using DOM inspector"""
        
        # Build DOM query from target specification
        strategies = []
        
        if 'css_selector' in target:
            strategies.append(DetectionStrategy.CSS_SELECTOR)
        if 'xpath' in target:
            strategies.append(DetectionStrategy.XPATH)
        if 'text' in target:
            strategies.append(DetectionStrategy.TEXT_CONTENT)
        if 'attributes' in target:
            strategies.append(DetectionStrategy.ATTRIBUTES)
        
        if not strategies:
            strategies = [DetectionStrategy.CSS_SELECTOR, DetectionStrategy.ATTRIBUTES]
        
        query = DOMQuery(
            strategies=strategies,
            target_attributes=target.get('attributes', {}),
            text_patterns=[target.get('text')] if target.get('text') else [],
            timeout=10.0
        )
        
        inspection_result = self.dom_inspector.inspect_element(query)
        
        if inspection_result.success and inspection_result.elements:
            return inspection_result.elements[0]  # Return best match
        
        return None
    
    def _calculate_human_delay(self) -> float:
        """Calculate human-like delay between actions"""
        import random
        
        base_delay = 0.5
        variation = random.uniform(0.2, 1.8)
        return base_delay * variation
    
    def _capture_final_state(self, context: ScriptContext) -> Dict[str, Any]:
        """Capture final page state"""
        state_script = """
        return DebugUtils.captureState();
        """
        
        script_result = self.javascript_injector.inject_script(
            state_script,
            context,
            libraries=['debug_utils']
        )
        
        return script_result.result_value if script_result.success else {}
    
    def _collect_extracted_data(self, execution_results: List[ExecutionResult]) -> Dict[str, Any]:
        """Collect all extracted data from execution results"""
        extracted_data = {}
        
        for i, result in enumerate(execution_results):
            if result.action.action_type == WebActionType.EXTRACT_DATA and result.result_data:
                extracted_data[f"extraction_{i}"] = result.result_data
        
        return extracted_data
    
    def create_simple_workflow(self, actions: List[Dict[str, Any]], 
                              initial_url: str = None,
                              workflow_name: str = "Simple Workflow") -> WebWorkflow:
        """Create a simple workflow from action dictionaries"""
        
        web_actions = []
        
        for action_dict in actions:
            action_type = WebActionType(action_dict.get('type', 'click'))
            target = action_dict.get('target', {})
            parameters = action_dict.get('parameters', {})
            
            web_action = WebAction(
                action_type=action_type,
                target=target,
                parameters=parameters,
                timeout=action_dict.get('timeout', 10.0)
            )
            
            web_actions.append(web_action)
        
        workflow_id = f"workflow_{int(time.time())}"
        
        return WebWorkflow(
            workflow_id=workflow_id,
            name=workflow_name,
            actions=web_actions,
            initial_url=initial_url,
            browser_config={'type': 'chrome', 'headless': False}
        )
    
    def get_execution_statistics(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        if not self.execution_history:
            return {"status": "No execution history available"}
        
        recent_workflows = self.execution_history[-10:]
        
        total_actions = sum(len(w.execution_results) for w in recent_workflows)
        successful_actions = sum(len([r for r in w.execution_results if r.success]) for w in recent_workflows)
        
        return {
            "total_workflows": len(self.execution_history),
            "recent_workflows": len(recent_workflows),
            "average_success_rate": sum(w.success_rate for w in recent_workflows) / len(recent_workflows),
            "average_execution_time": sum(w.total_execution_time for w in recent_workflows) / len(recent_workflows),
            "total_actions_executed": total_actions,
            "action_success_rate": successful_actions / total_actions if total_actions > 0 else 0,
            "active_workflows": len(self.active_workflows),
            "interaction_mode": self.interaction_mode.value,
            "component_stats": {
                "dom_inspector": self.dom_inspector.get_inspection_statistics(),
                "browser_controller": self.browser_controller.get_session_status(),
                "javascript_injector": self.javascript_injector.get_injection_statistics()
            }
        }