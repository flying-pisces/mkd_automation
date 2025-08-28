"""
JavaScript Injection System

Provides advanced JavaScript injection and execution capabilities:
- Dynamic script injection with context isolation
- Custom function libraries and utilities
- Asynchronous script execution with promises
- Script result handling and serialization
- Security sandboxing and validation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import time
import json
import re
import logging
import asyncio
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


class ScriptType(Enum):
    """Types of JavaScript scripts"""
    INLINE = "inline"
    MODULE = "module"
    FUNCTION = "function"
    LIBRARY = "library"
    UTILITY = "utility"
    AUTOMATION = "automation"


class ExecutionContext(Enum):
    """JavaScript execution contexts"""
    PAGE = "page"              # Main page context
    ISOLATED = "isolated"      # Isolated world (Chrome extension style)
    CONTENT_SCRIPT = "content_script"  # Content script context
    BACKGROUND = "background"   # Background/service worker context
    DEVTOOLS = "devtools"      # DevTools context


class ScriptSecurity(Enum):
    """Security levels for script execution"""
    UNRESTRICTED = "unrestricted"  # No security restrictions
    SANDBOXED = "sandboxed"        # Basic sandboxing
    RESTRICTED = "restricted"      # Limited API access
    READ_ONLY = "read_only"        # Only read operations allowed


@dataclass
class ScriptContext:
    """Context for script execution"""
    context_id: str
    execution_context: ExecutionContext
    security_level: ScriptSecurity
    isolated_world: bool = False
    csp_bypass: bool = False
    frame_id: Optional[str] = None
    tab_id: Optional[str] = None
    origin: Optional[str] = None
    permissions: List[str] = field(default_factory=list)


@dataclass
class ScriptResult:
    """Result of script execution"""
    success: bool
    result_value: Any
    script_id: str
    execution_time: float
    context: ScriptContext
    console_output: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    returned_functions: List[str] = field(default_factory=list)
    side_effects: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScriptLibrary:
    """JavaScript library definition"""
    library_id: str
    name: str
    version: str
    source_code: str
    functions: List[str]
    dependencies: List[str] = field(default_factory=list)
    auto_inject: bool = False
    cache_key: Optional[str] = None


class JavaScriptInjector:
    """Advanced JavaScript injection and execution system"""
    
    def __init__(self, browser_interface=None):
        self.browser_interface = browser_interface
        self.script_cache: Dict[str, str] = {}
        self.libraries: Dict[str, ScriptLibrary] = {}
        self.execution_contexts: Dict[str, ScriptContext] = {}
        self.active_scripts: Dict[str, Dict[str, Any]] = {}
        self.security_validator = ScriptSecurityValidator()
        self.performance_monitor = ScriptPerformanceMonitor()
        
        # Pre-loaded utility libraries
        self._load_builtin_libraries()
        
        # Execution statistics
        self.execution_stats = defaultdict(list)
    
    def _load_builtin_libraries(self) -> None:
        """Load built-in utility libraries"""
        
        # DOM Utilities Library
        dom_utils = ScriptLibrary(
            library_id="dom_utils",
            name="DOM Utilities",
            version="1.0.0",
            source_code="""
            const DOMUtils = {
                // Enhanced element selection
                selectSmart: function(selector, options = {}) {
                    const elements = document.querySelectorAll(selector);
                    if (options.visible) {
                        return Array.from(elements).filter(el => {
                            const style = window.getComputedStyle(el);
                            return style.display !== 'none' && 
                                   style.visibility !== 'hidden' && 
                                   style.opacity !== '0';
                        });
                    }
                    return Array.from(elements);
                },
                
                // Wait for element to appear
                waitForElement: function(selector, timeout = 5000) {
                    return new Promise((resolve, reject) => {
                        const element = document.querySelector(selector);
                        if (element) return resolve(element);
                        
                        const observer = new MutationObserver(() => {
                            const element = document.querySelector(selector);
                            if (element) {
                                observer.disconnect();
                                resolve(element);
                            }
                        });
                        
                        observer.observe(document.body, {
                            childList: true,
                            subtree: true
                        });
                        
                        setTimeout(() => {
                            observer.disconnect();
                            reject(new Error(`Element ${selector} not found within ${timeout}ms`));
                        }, timeout);
                    });
                },
                
                // Safe click with retry
                safeClick: function(element, options = {}) {
                    if (typeof element === 'string') {
                        element = document.querySelector(element);
                    }
                    
                    if (!element) throw new Error('Element not found');
                    
                    // Scroll element into view
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    // Wait for potential animations
                    return new Promise(resolve => {
                        setTimeout(() => {
                            element.click();
                            resolve(true);
                        }, options.delay || 100);
                    });
                },
                
                // Get element information
                getElementInfo: function(element) {
                    if (typeof element === 'string') {
                        element = document.querySelector(element);
                    }
                    
                    if (!element) return null;
                    
                    const rect = element.getBoundingClientRect();
                    const style = window.getComputedStyle(element);
                    
                    return {
                        tagName: element.tagName,
                        id: element.id,
                        className: element.className,
                        textContent: element.textContent.trim(),
                        innerHTML: element.innerHTML,
                        attributes: Array.from(element.attributes).reduce((acc, attr) => {
                            acc[attr.name] = attr.value;
                            return acc;
                        }, {}),
                        position: {
                            x: rect.left,
                            y: rect.top,
                            width: rect.width,
                            height: rect.height
                        },
                        computed_styles: {
                            display: style.display,
                            visibility: style.visibility,
                            opacity: style.opacity,
                            position: style.position,
                            zIndex: style.zIndex
                        },
                        isVisible: rect.width > 0 && rect.height > 0 && 
                                  style.display !== 'none' && 
                                  style.visibility !== 'hidden' && 
                                  style.opacity !== '0'
                    };
                }
            };
            
            // Make globally available
            window.DOMUtils = DOMUtils;
            """,
            functions=["selectSmart", "waitForElement", "safeClick", "getElementInfo"],
            auto_inject=True
        )
        
        # Automation Utilities Library
        automation_utils = ScriptLibrary(
            library_id="automation_utils",
            name="Automation Utilities",
            version="1.0.0",
            source_code="""
            const AutomationUtils = {
                // Form filling utilities
                fillForm: function(formSelector, data) {
                    const form = document.querySelector(formSelector);
                    if (!form) throw new Error('Form not found');
                    
                    Object.entries(data).forEach(([name, value]) => {
                        const field = form.querySelector(`[name="${name}"]`);
                        if (field) {
                            if (field.type === 'checkbox' || field.type === 'radio') {
                                field.checked = Boolean(value);
                            } else if (field.tagName === 'SELECT') {
                                field.value = value;
                                field.dispatchEvent(new Event('change'));
                            } else {
                                field.value = value;
                                field.dispatchEvent(new Event('input'));
                            }
                        }
                    });
                },
                
                // Simulate typing with realistic delays
                typeText: async function(element, text, options = {}) {
                    if (typeof element === 'string') {
                        element = document.querySelector(element);
                    }
                    
                    if (!element) throw new Error('Element not found');
                    
                    element.focus();
                    element.value = '';
                    
                    const delay = options.delay || 50;
                    const variation = options.variation || 0.3;
                    
                    for (let char of text) {
                        element.value += char;
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        // Random delay for realistic typing
                        const currentDelay = delay + (Math.random() - 0.5) * delay * variation;
                        await new Promise(resolve => setTimeout(resolve, currentDelay));
                    }
                    
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                },
                
                // Wait for page stability
                waitForStability: function(timeout = 5000) {
                    return new Promise((resolve, reject) => {
                        let lastActivityTime = Date.now();
                        let stabilityTimer = null;
                        
                        const checkStability = () => {
                            const now = Date.now();
                            if (now - lastActivityTime >= 1000) { // 1 second of stability
                                resolve(true);
                            } else {
                                stabilityTimer = setTimeout(checkStability, 100);
                            }
                        };
                        
                        const resetTimer = () => {
                            lastActivityTime = Date.now();
                            if (stabilityTimer) {
                                clearTimeout(stabilityTimer);
                                stabilityTimer = setTimeout(checkStability, 100);
                            }
                        };
                        
                        // Monitor various activity indicators
                        const observer = new MutationObserver(resetTimer);
                        observer.observe(document.body, {
                            childList: true,
                            subtree: true,
                            attributes: true
                        });
                        
                        // Monitor network requests
                        const originalFetch = window.fetch;
                        window.fetch = function(...args) {
                            resetTimer();
                            return originalFetch.apply(this, args);
                        };
                        
                        // Start stability check
                        stabilityTimer = setTimeout(checkStability, 100);
                        
                        // Overall timeout
                        setTimeout(() => {
                            observer.disconnect();
                            window.fetch = originalFetch;
                            if (stabilityTimer) clearTimeout(stabilityTimer);
                            reject(new Error('Stability timeout'));
                        }, timeout);
                    });
                },
                
                // Extract data from page
                extractData: function(extractors) {
                    const result = {};
                    
                    Object.entries(extractors).forEach(([key, config]) => {
                        try {
                            if (typeof config === 'string') {
                                // Simple selector
                                const element = document.querySelector(config);
                                result[key] = element ? element.textContent.trim() : null;
                            } else {
                                // Complex extractor
                                const elements = document.querySelectorAll(config.selector);
                                
                                if (config.multiple) {
                                    result[key] = Array.from(elements).map(el => {
                                        if (config.attribute) {
                                            return el.getAttribute(config.attribute);
                                        }
                                        return config.property ? el[config.property] : el.textContent.trim();
                                    });
                                } else {
                                    const element = elements[0];
                                    if (element) {
                                        if (config.attribute) {
                                            result[key] = element.getAttribute(config.attribute);
                                        } else {
                                            result[key] = config.property ? element[config.property] : element.textContent.trim();
                                        }
                                    } else {
                                        result[key] = null;
                                    }
                                }
                            }
                        } catch (error) {
                            result[key] = { error: error.message };
                        }
                    });
                    
                    return result;
                }
            };
            
            // Make globally available
            window.AutomationUtils = AutomationUtils;
            """,
            functions=["fillForm", "typeText", "waitForStability", "extractData"],
            auto_inject=True
        )
        
        # Debugging Utilities Library
        debug_utils = ScriptLibrary(
            library_id="debug_utils",
            name="Debug Utilities",
            version="1.0.0",
            source_code="""
            const DebugUtils = {
                // Highlight elements for debugging
                highlightElement: function(element, options = {}) {
                    if (typeof element === 'string') {
                        element = document.querySelector(element);
                    }
                    
                    if (!element) return;
                    
                    const highlight = document.createElement('div');
                    highlight.style.cssText = `
                        position: absolute;
                        border: ${options.border || '3px solid red'};
                        background: ${options.background || 'rgba(255, 0, 0, 0.1)'};
                        pointer-events: none;
                        z-index: 999999;
                        box-sizing: border-box;
                    `;
                    
                    const rect = element.getBoundingClientRect();
                    highlight.style.left = (rect.left + window.scrollX) + 'px';
                    highlight.style.top = (rect.top + window.scrollY) + 'px';
                    highlight.style.width = rect.width + 'px';
                    highlight.style.height = rect.height + 'px';
                    
                    document.body.appendChild(highlight);
                    
                    // Remove after delay
                    setTimeout(() => {
                        if (highlight.parentNode) {
                            highlight.parentNode.removeChild(highlight);
                        }
                    }, options.duration || 3000);
                },
                
                // Console logging with context
                log: function(message, data = null, level = 'info') {
                    const timestamp = new Date().toISOString();
                    const logMessage = `[AutomationDebug ${timestamp}] ${message}`;
                    
                    if (data) {
                        console[level](logMessage, data);
                    } else {
                        console[level](logMessage);
                    }
                },
                
                // Performance timing
                timeStart: function(label) {
                    console.time(`AutomationTimer_${label}`);
                },
                
                timeEnd: function(label) {
                    console.timeEnd(`AutomationTimer_${label}`);
                },
                
                // Capture page state
                captureState: function() {
                    return {
                        url: window.location.href,
                        title: document.title,
                        readyState: document.readyState,
                        elementCount: document.querySelectorAll('*').length,
                        focusedElement: document.activeElement ? {
                            tagName: document.activeElement.tagName,
                            id: document.activeElement.id,
                            className: document.activeElement.className
                        } : null,
                        viewport: {
                            width: window.innerWidth,
                            height: window.innerHeight,
                            scrollX: window.scrollX,
                            scrollY: window.scrollY
                        },
                        timestamp: Date.now()
                    };
                }
            };
            
            // Make globally available
            window.DebugUtils = DebugUtils;
            """,
            functions=["highlightElement", "log", "timeStart", "timeEnd", "captureState"],
            auto_inject=False  # Only inject when debugging is enabled
        )
        
        # Store libraries
        self.libraries["dom_utils"] = dom_utils
        self.libraries["automation_utils"] = automation_utils
        self.libraries["debug_utils"] = debug_utils
    
    def inject_script(self, script: str, 
                     context: ScriptContext,
                     script_type: ScriptType = ScriptType.INLINE,
                     libraries: List[str] = None,
                     async_execution: bool = False) -> ScriptResult:
        """Inject and execute JavaScript in specified context"""
        
        start_time = time.time()
        script_id = self._generate_script_id(script)
        
        logger.debug(f"Injecting script {script_id} in {context.execution_context.value} context")
        
        result = ScriptResult(
            success=False,
            result_value=None,
            script_id=script_id,
            execution_time=0.0,
            context=context
        )
        
        try:
            # Security validation
            if not self.security_validator.validate_script(script, context.security_level):
                result.errors.append("Script failed security validation")
                return result
            
            # Prepare script with libraries
            prepared_script = self._prepare_script_with_libraries(script, libraries or [])
            
            # Execute script
            if async_execution:
                # Handle asynchronous execution
                execution_result = self._execute_async_script(prepared_script, context)
            else:
                # Synchronous execution
                execution_result = self._execute_sync_script(prepared_script, context)
            
            result.success = execution_result.get('success', False)
            result.result_value = execution_result.get('result')
            result.console_output = execution_result.get('console_output', [])
            result.errors = execution_result.get('errors', [])
            result.warnings = execution_result.get('warnings', [])
            result.side_effects = execution_result.get('side_effects', {})
            
            # Cache successful scripts
            if result.success and script_type in [ScriptType.FUNCTION, ScriptType.UTILITY]:
                self.script_cache[script_id] = prepared_script
            
            # Monitor performance
            self.performance_monitor.record_execution(script_id, result.execution_time, result.success)
            
        except Exception as e:
            logger.error(f"Script injection failed: {e}")
            result.errors.append(f"Injection error: {str(e)}")
        
        result.execution_time = time.time() - start_time
        self.execution_stats['total_executions'].append(result.execution_time)
        
        return result
    
    def _prepare_script_with_libraries(self, script: str, library_ids: List[str]) -> str:
        """Prepare script by injecting required libraries"""
        
        # Collect library dependencies
        all_libraries = set(library_ids)
        for lib_id in library_ids:
            if lib_id in self.libraries:
                all_libraries.update(self.libraries[lib_id].dependencies)
        
        # Build combined script
        script_parts = []
        
        # Add library code
        for lib_id in all_libraries:
            if lib_id in self.libraries:
                library = self.libraries[lib_id]
                script_parts.append(f"// Library: {library.name} v{library.version}")
                script_parts.append(library.source_code)
                script_parts.append("")
        
        # Add main script
        script_parts.append("// Main script")
        script_parts.append(script)
        
        return "\n".join(script_parts)
    
    def _execute_sync_script(self, script: str, context: ScriptContext) -> Dict[str, Any]:
        """Execute script synchronously"""
        
        # Mock implementation - in real implementation would use CDP, selenium, etc.
        execution_result = {
            'success': True,
            'result': 'script_executed_successfully',
            'console_output': ['Script executed in ' + context.execution_context.value],
            'errors': [],
            'warnings': [],
            'side_effects': {}
        }
        
        # Simulate script analysis
        if 'document.querySelector' in script:
            execution_result['side_effects']['dom_access'] = True
        
        if 'console.log' in script:
            execution_result['console_output'].append('Custom console output from script')
        
        if 'throw new Error' in script or 'error' in script.lower():
            execution_result['success'] = False
            execution_result['errors'].append('Script execution error')
        
        return execution_result
    
    def _execute_async_script(self, script: str, context: ScriptContext) -> Dict[str, Any]:
        """Execute script asynchronously"""
        
        # Wrap script in async function if needed
        if 'await' in script and not script.strip().startswith('async'):
            wrapped_script = f"""
            (async function() {{
                {script}
            }})().then(result => {{
                window.__scriptResult = result;
            }}).catch(error => {{
                window.__scriptError = error;
            }});
            """
        else:
            wrapped_script = script
        
        return self._execute_sync_script(wrapped_script, context)
    
    def inject_function(self, function_name: str, 
                       function_code: str,
                       context: ScriptContext,
                       persistent: bool = True) -> ScriptResult:
        """Inject a reusable function into the page context"""
        
        # Wrap function code
        wrapped_function = f"""
        window.{function_name} = {function_code};
        
        // Return function info
        ({{ 
            name: '{function_name}',
            injected: true,
            type: 'function'
        }});
        """
        
        result = self.inject_script(
            wrapped_function,
            context,
            ScriptType.FUNCTION,
            async_execution=False
        )
        
        if result.success and persistent:
            # Store in active scripts for re-injection on navigation
            if context.tab_id:
                if context.tab_id not in self.active_scripts:
                    self.active_scripts[context.tab_id] = {}
                
                self.active_scripts[context.tab_id][function_name] = {
                    'code': function_code,
                    'type': 'function',
                    'context': context
                }
        
        return result
    
    def inject_library(self, library_id: str, context: ScriptContext) -> ScriptResult:
        """Inject a pre-defined library"""
        
        if library_id not in self.libraries:
            result = ScriptResult(False, None, f"lib_{library_id}", 0.0, context)
            result.errors.append(f"Library '{library_id}' not found")
            return result
        
        library = self.libraries[library_id]
        
        return self.inject_script(
            library.source_code,
            context,
            ScriptType.LIBRARY,
            libraries=library.dependencies
        )
    
    def create_automation_script(self, actions: List[Dict[str, Any]], 
                                context: ScriptContext) -> str:
        """Create automation script from action sequence"""
        
        script_parts = [
            "// Generated automation script",
            "const AutomationRunner = {",
            "    actions: [],",
            "    currentIndex: 0,",
            "    ",
            "    async execute() {",
            "        try {",
            "            DebugUtils.log('Starting automation script execution');",
            "            ",
            "            for (let i = 0; i < this.actions.length; i++) {",
            "                const action = this.actions[i];",
            "                DebugUtils.log(`Executing action ${i + 1}/${this.actions.length}: ${action.type}`);",
            "                ",
            "                await this.executeAction(action);",
            "                ",
            "                // Wait for stability between actions",
            "                await AutomationUtils.waitForStability(2000);",
            "            }",
            "            ",
            "            DebugUtils.log('Automation script completed successfully');",
            "            return { success: true, completedActions: this.actions.length };",
            "        } catch (error) {",
            "            DebugUtils.log('Automation script failed', error, 'error');",
            "            return { success: false, error: error.message, failedAt: this.currentIndex };",
            "        }",
            "    },",
            "    ",
            "    async executeAction(action) {",
            "        this.currentIndex++;",
            "        ",
            "        switch (action.type) {",
        ]
        
        # Add action handlers based on action types
        action_types = set(action.get('type') for action in actions)
        
        for action_type in action_types:
            if action_type == 'click':
                script_parts.extend([
                    "            case 'click':",
                    "                const clickElement = await DOMUtils.waitForElement(action.selector, 5000);",
                    "                DebugUtils.highlightElement(clickElement, { border: '2px solid blue' });",
                    "                await AutomationUtils.safeClick(clickElement);",
                    "                break;"
                ])
            elif action_type == 'type':
                script_parts.extend([
                    "            case 'type':",
                    "                const typeElement = await DOMUtils.waitForElement(action.selector, 5000);",
                    "                DebugUtils.highlightElement(typeElement, { border: '2px solid green' });",
                    "                await AutomationUtils.typeText(typeElement, action.text);",
                    "                break;"
                ])
            elif action_type == 'wait':
                script_parts.extend([
                    "            case 'wait':",
                    "                await new Promise(resolve => setTimeout(resolve, action.duration || 1000));",
                    "                break;"
                ])
            elif action_type == 'navigate':
                script_parts.extend([
                    "            case 'navigate':",
                    "                window.location.href = action.url;",
                    "                await new Promise(resolve => {",
                    "                    const checkLoad = () => {",
                    "                        if (document.readyState === 'complete') resolve();",
                    "                        else setTimeout(checkLoad, 100);",
                    "                    };",
                    "                    checkLoad();",
                    "                });",
                    "                break;"
                ])
        
        script_parts.extend([
            "            default:",
            "                throw new Error(`Unknown action type: ${action.type}`);",
            "        }",
            "    }",
            "};",
            "",
            "// Set actions and execute",
            f"AutomationRunner.actions = {json.dumps(actions)};",
            "AutomationRunner.execute();"
        ])
        
        return "\n".join(script_parts)
    
    def _generate_script_id(self, script: str) -> str:
        """Generate unique ID for script"""
        return f"script_{hashlib.md5(script.encode()).hexdigest()[:8]}_{int(time.time())}"
    
    def add_library(self, library: ScriptLibrary) -> None:
        """Add a custom JavaScript library"""
        # Generate cache key
        library.cache_key = hashlib.md5(library.source_code.encode()).hexdigest()
        
        self.libraries[library.library_id] = library
        logger.info(f"Added library '{library.name}' v{library.version}")
    
    def remove_library(self, library_id: str) -> bool:
        """Remove a JavaScript library"""
        if library_id in self.libraries:
            del self.libraries[library_id]
            logger.info(f"Removed library '{library_id}'")
            return True
        return False
    
    def get_injection_statistics(self) -> Dict[str, Any]:
        """Get comprehensive injection statistics"""
        total_executions = len(self.execution_stats['total_executions'])
        
        if total_executions == 0:
            return {"status": "No executions recorded"}
        
        execution_times = self.execution_stats['total_executions']
        
        return {
            "total_executions": total_executions,
            "average_execution_time": sum(execution_times) / len(execution_times),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "cached_scripts": len(self.script_cache),
            "available_libraries": len(self.libraries),
            "active_script_contexts": len(self.active_scripts),
            "performance_metrics": self.performance_monitor.get_metrics()
        }


class ScriptSecurityValidator:
    """Security validator for JavaScript code"""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'eval\s*\(',
            r'Function\s*\(',
            r'document\.write',
            r'innerHTML\s*=.*<script',
            r'on\w+\s*=',  # Event handlers
            r'javascript\s*:',
            r'data\s*:\s*text/html'
        ]
        
        self.restricted_apis = [
            'XMLHttpRequest',
            'fetch',
            'WebSocket',
            'localStorage',
            'sessionStorage',
            'indexedDB'
        ]
    
    def validate_script(self, script: str, security_level: ScriptSecurity) -> bool:
        """Validate script against security policies"""
        
        if security_level == ScriptSecurity.UNRESTRICTED:
            return True
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                logger.warning(f"Script contains dangerous pattern: {pattern}")
                if security_level == ScriptSecurity.RESTRICTED:
                    return False
        
        # Check for restricted APIs
        if security_level in [ScriptSecurity.RESTRICTED, ScriptSecurity.READ_ONLY]:
            for api in self.restricted_apis:
                if api in script:
                    logger.warning(f"Script uses restricted API: {api}")
                    return False
        
        # Read-only validation
        if security_level == ScriptSecurity.READ_ONLY:
            write_patterns = [
                r'\.innerHTML\s*=',
                r'\.value\s*=',
                r'\.setAttribute\s*\(',
                r'\.style\.',
                r'document\.createElement',
                r'\.appendChild\s*\(',
                r'\.removeChild\s*\('
            ]
            
            for pattern in write_patterns:
                if re.search(pattern, script):
                    logger.warning(f"Script contains write operation in read-only mode: {pattern}")
                    return False
        
        return True


class ScriptPerformanceMonitor:
    """Monitor script execution performance"""
    
    def __init__(self):
        self.execution_records = []
        self.performance_thresholds = {
            'slow_execution': 1000,  # ms
            'very_slow_execution': 5000,  # ms
            'failure_rate_threshold': 0.1  # 10%
        }
    
    def record_execution(self, script_id: str, execution_time: float, success: bool) -> None:
        """Record script execution metrics"""
        self.execution_records.append({
            'script_id': script_id,
            'execution_time': execution_time * 1000,  # Convert to ms
            'success': success,
            'timestamp': time.time()
        })
        
        # Keep only recent records (last 1000)
        if len(self.execution_records) > 1000:
            self.execution_records = self.execution_records[-1000:]
        
        # Log performance warnings
        execution_time_ms = execution_time * 1000
        if execution_time_ms > self.performance_thresholds['very_slow_execution']:
            logger.warning(f"Very slow script execution: {script_id} took {execution_time_ms:.2f}ms")
        elif execution_time_ms > self.performance_thresholds['slow_execution']:
            logger.info(f"Slow script execution: {script_id} took {execution_time_ms:.2f}ms")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        if not self.execution_records:
            return {"status": "No performance data available"}
        
        recent_records = self.execution_records[-100:]  # Last 100 executions
        
        execution_times = [r['execution_time'] for r in recent_records]
        successful_executions = [r for r in recent_records if r['success']]
        
        return {
            "total_executions": len(self.execution_records),
            "recent_executions": len(recent_records),
            "success_rate": len(successful_executions) / len(recent_records),
            "average_execution_time": sum(execution_times) / len(execution_times),
            "slow_executions": len([t for t in execution_times if t > self.performance_thresholds['slow_execution']]),
            "very_slow_executions": len([t for t in execution_times if t > self.performance_thresholds['very_slow_execution']])
        }