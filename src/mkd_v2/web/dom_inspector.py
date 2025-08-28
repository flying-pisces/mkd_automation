"""
DOM Inspector and Manipulator

Provides deep DOM analysis and manipulation capabilities for web automation:
- Advanced element detection with multiple strategies
- CSS selector generation and optimization  
- XPath generation with fallback options
- Element interaction verification
- Dynamic content handling
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from enum import Enum
import time
import re
import logging
import json
from collections import defaultdict

logger = logging.getLogger(__name__)


class DetectionStrategy(Enum):
    """DOM element detection strategies"""
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath" 
    TEXT_CONTENT = "text_content"
    ATTRIBUTES = "attributes"
    VISUAL_POSITION = "visual_position"
    AI_SEMANTIC = "ai_semantic"


class ElementState(Enum):
    """Element states for interaction"""
    VISIBLE = "visible"
    HIDDEN = "hidden"
    LOADING = "loading"
    DISABLED = "disabled"
    INTERACTIVE = "interactive"
    STALE = "stale"


class SelectorType(Enum):
    """Types of selectors for element targeting"""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    ATTRIBUTE = "attribute"
    COMPOSITE = "composite"


@dataclass
class ElementInfo:
    """Comprehensive element information"""
    tag_name: str
    attributes: Dict[str, str]
    text_content: str
    inner_html: str
    css_classes: List[str]
    computed_styles: Dict[str, str]
    position: Dict[str, float]  # x, y, width, height
    selectors: Dict[SelectorType, str]
    state: ElementState
    parent_info: Optional['ElementInfo'] = None
    children_count: int = 0
    is_unique: bool = False
    interaction_confidence: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class DOMQuery:
    """Query configuration for DOM element detection"""
    strategies: List[DetectionStrategy]
    target_attributes: Dict[str, Any]
    text_patterns: List[str] = field(default_factory=list)
    css_properties: Dict[str, str] = field(default_factory=dict)
    position_tolerance: float = 10.0
    timeout: float = 10.0
    wait_for_stable: bool = True
    include_hidden: bool = False


@dataclass  
class InspectionResult:
    """Result of DOM inspection operation"""
    success: bool
    elements: List[ElementInfo]
    query_time: float
    strategies_used: List[DetectionStrategy]
    best_selector: Optional[str] = None
    confidence_score: float = 0.0
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class DOMInspector:
    """Advanced DOM inspector with multiple detection strategies"""
    
    def __init__(self, browser_interface=None):
        self.browser_interface = browser_interface
        self.element_cache: Dict[str, ElementInfo] = {}
        self.selector_cache: Dict[str, str] = {}
        self.performance_stats = defaultdict(list)
        self.confidence_threshold = 0.7
        
        # Strategy priorities (higher = more preferred)
        self.strategy_priorities = {
            DetectionStrategy.CSS_SELECTOR: 10,
            DetectionStrategy.XPATH: 8,
            DetectionStrategy.ATTRIBUTES: 9,
            DetectionStrategy.TEXT_CONTENT: 6,
            DetectionStrategy.VISUAL_POSITION: 4,
            DetectionStrategy.AI_SEMANTIC: 7
        }
    
    def inspect_element(self, query: DOMQuery, page_context: Dict[str, Any] = None) -> InspectionResult:
        """Inspect DOM element using multiple strategies"""
        start_time = time.time()
        page_context = page_context or {}
        
        logger.info(f"Inspecting element with {len(query.strategies)} strategies")
        
        result = InspectionResult(
            success=False,
            elements=[],
            query_time=0,
            strategies_used=[]
        )
        
        try:
            # Execute detection strategies in priority order
            sorted_strategies = sorted(query.strategies, 
                                     key=lambda s: self.strategy_priorities.get(s, 0), 
                                     reverse=True)
            
            all_elements = []
            for strategy in sorted_strategies:
                try:
                    elements = self._execute_strategy(strategy, query, page_context)
                    if elements:
                        all_elements.extend(elements)
                        result.strategies_used.append(strategy)
                        logger.debug(f"Strategy {strategy.value} found {len(elements)} elements")
                except Exception as e:
                    logger.warning(f"Strategy {strategy.value} failed: {e}")
                    result.errors.append(f"{strategy.value}: {str(e)}")
            
            # Remove duplicates and rank elements
            unique_elements = self._deduplicate_elements(all_elements)
            ranked_elements = self._rank_elements(unique_elements, query)
            
            result.elements = ranked_elements
            result.success = len(ranked_elements) > 0
            
            if result.success:
                # Generate best selector for top element
                best_element = ranked_elements[0]
                result.best_selector = self._generate_optimal_selector(best_element)
                result.confidence_score = best_element.interaction_confidence
                
                # Cache successful results
                cache_key = self._generate_cache_key(query)
                self.element_cache[cache_key] = best_element
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(result, query)
            
        except Exception as e:
            logger.error(f"DOM inspection failed: {e}")
            result.errors.append(f"Inspection error: {str(e)}")
        
        result.query_time = time.time() - start_time
        self.performance_stats['inspection_times'].append(result.query_time)
        
        return result
    
    def _execute_strategy(self, strategy: DetectionStrategy, 
                         query: DOMQuery, 
                         page_context: Dict[str, Any]) -> List[ElementInfo]:
        """Execute a specific detection strategy"""
        
        if strategy == DetectionStrategy.CSS_SELECTOR:
            return self._detect_by_css_selector(query, page_context)
        elif strategy == DetectionStrategy.XPATH:
            return self._detect_by_xpath(query, page_context)
        elif strategy == DetectionStrategy.ATTRIBUTES:
            return self._detect_by_attributes(query, page_context)
        elif strategy == DetectionStrategy.TEXT_CONTENT:
            return self._detect_by_text_content(query, page_context)
        elif strategy == DetectionStrategy.VISUAL_POSITION:
            return self._detect_by_visual_position(query, page_context)
        elif strategy == DetectionStrategy.AI_SEMANTIC:
            return self._detect_by_ai_semantic(query, page_context)
        else:
            raise ValueError(f"Unknown detection strategy: {strategy}")
    
    def _detect_by_css_selector(self, query: DOMQuery, page_context: Dict[str, Any]) -> List[ElementInfo]:
        """Detect elements using CSS selectors"""
        elements = []
        
        # Generate CSS selectors from target attributes
        selectors = self._generate_css_selectors(query.target_attributes)
        
        for selector in selectors:
            try:
                # Execute selector in browser (mock implementation)
                raw_elements = self._execute_browser_query(f"document.querySelectorAll('{selector}')")
                
                for raw_element in raw_elements:
                    element_info = self._create_element_info(raw_element, SelectorType.CSS, selector)
                    if self._matches_query_criteria(element_info, query):
                        elements.append(element_info)
                        
            except Exception as e:
                logger.debug(f"CSS selector '{selector}' failed: {e}")
        
        return elements
    
    def _detect_by_xpath(self, query: DOMQuery, page_context: Dict[str, Any]) -> List[ElementInfo]:
        """Detect elements using XPath expressions"""
        elements = []
        
        # Generate XPath expressions
        xpaths = self._generate_xpath_expressions(query.target_attributes, query.text_patterns)
        
        for xpath in xpaths:
            try:
                # Execute XPath in browser (mock implementation)
                raw_elements = self._execute_browser_query(
                    f"document.evaluate('{xpath}', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)"
                )
                
                for raw_element in raw_elements:
                    element_info = self._create_element_info(raw_element, SelectorType.XPATH, xpath)
                    if self._matches_query_criteria(element_info, query):
                        elements.append(element_info)
                        
            except Exception as e:
                logger.debug(f"XPath '{xpath}' failed: {e}")
        
        return elements
    
    def _detect_by_attributes(self, query: DOMQuery, page_context: Dict[str, Any]) -> List[ElementInfo]:
        """Detect elements by their attributes"""
        elements = []
        
        # Build attribute-based selectors
        for attr_name, attr_value in query.target_attributes.items():
            if attr_name in ['id', 'class', 'data-*', 'aria-*', 'role']:
                selector = f"[{attr_name}='{attr_value}']"
                try:
                    raw_elements = self._execute_browser_query(f"document.querySelectorAll('{selector}')")
                    
                    for raw_element in raw_elements:
                        element_info = self._create_element_info(raw_element, SelectorType.ATTRIBUTE, selector)
                        if self._matches_query_criteria(element_info, query):
                            elements.append(element_info)
                            
                except Exception as e:
                    logger.debug(f"Attribute selector '{selector}' failed: {e}")
        
        return elements
    
    def _detect_by_text_content(self, query: DOMQuery, page_context: Dict[str, Any]) -> List[ElementInfo]:
        """Detect elements by their text content"""
        elements = []
        
        for text_pattern in query.text_patterns:
            try:
                # Create XPath for text matching
                xpath = f"//*[contains(text(), '{text_pattern}')]"
                raw_elements = self._execute_browser_query(
                    f"document.evaluate('{xpath}', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)"
                )
                
                for raw_element in raw_elements:
                    element_info = self._create_element_info(raw_element, SelectorType.TEXT, text_pattern)
                    if self._matches_query_criteria(element_info, query):
                        elements.append(element_info)
                        
            except Exception as e:
                logger.debug(f"Text pattern '{text_pattern}' failed: {e}")
        
        return elements
    
    def _detect_by_visual_position(self, query: DOMQuery, page_context: Dict[str, Any]) -> List[ElementInfo]:
        """Detect elements by their visual position"""
        elements = []
        
        # Get elements at specific coordinates
        target_position = query.target_attributes.get('position')
        if target_position:
            x, y = target_position.get('x', 0), target_position.get('y', 0)
            tolerance = query.position_tolerance
            
            try:
                # Get element at coordinates (mock implementation)
                script = f"document.elementFromPoint({x}, {y})"
                raw_element = self._execute_browser_query(script)
                
                if raw_element:
                    element_info = self._create_element_info(raw_element, SelectorType.CSS, f"position({x},{y})")
                    
                    # Check if position is within tolerance
                    element_x = element_info.position.get('x', 0)
                    element_y = element_info.position.get('y', 0)
                    
                    if (abs(element_x - x) <= tolerance and 
                        abs(element_y - y) <= tolerance and
                        self._matches_query_criteria(element_info, query)):
                        elements.append(element_info)
                        
            except Exception as e:
                logger.debug(f"Position detection failed: {e}")
        
        return elements
    
    def _detect_by_ai_semantic(self, query: DOMQuery, page_context: Dict[str, Any]) -> List[ElementInfo]:
        """Detect elements using AI semantic analysis"""
        elements = []
        
        # This would integrate with AI/ML models for semantic understanding
        # For now, implement rule-based semantic matching
        
        semantic_hints = query.target_attributes.get('semantic_role', [])
        if not isinstance(semantic_hints, list):
            semantic_hints = [semantic_hints]
        
        for hint in semantic_hints:
            try:
                # Map semantic roles to likely selectors
                semantic_selectors = self._map_semantic_to_selectors(hint)
                
                for selector in semantic_selectors:
                    raw_elements = self._execute_browser_query(f"document.querySelectorAll('{selector}')")
                    
                    for raw_element in raw_elements:
                        element_info = self._create_element_info(raw_element, SelectorType.COMPOSITE, selector)
                        # Add semantic confidence scoring
                        element_info.interaction_confidence = self._calculate_semantic_confidence(element_info, hint)
                        
                        if (element_info.interaction_confidence >= self.confidence_threshold and
                            self._matches_query_criteria(element_info, query)):
                            elements.append(element_info)
                            
            except Exception as e:
                logger.debug(f"Semantic detection for '{hint}' failed: {e}")
        
        return elements
    
    def _generate_css_selectors(self, target_attributes: Dict[str, Any]) -> List[str]:
        """Generate CSS selectors from target attributes"""
        selectors = []
        
        # ID selector (highest priority)
        if 'id' in target_attributes:
            selectors.append(f"#{target_attributes['id']}")
        
        # Class selectors
        if 'class' in target_attributes:
            classes = target_attributes['class']
            if isinstance(classes, str):
                classes = classes.split()
            selector = '.' + '.'.join(classes)
            selectors.append(selector)
        
        # Attribute selectors
        attr_selectors = []
        for attr, value in target_attributes.items():
            if attr not in ['id', 'class', 'position', 'semantic_role']:
                if isinstance(value, str):
                    attr_selectors.append(f"[{attr}='{value}']")
                elif isinstance(value, list):
                    for v in value:
                        attr_selectors.append(f"[{attr}='{v}']")
        
        # Combine attribute selectors
        if attr_selectors:
            selectors.extend(attr_selectors)
            # Also create combined selector
            selectors.append(''.join(attr_selectors))
        
        # Tag name selector (if specified)
        if 'tag' in target_attributes:
            tag_selector = target_attributes['tag']
            selectors.append(tag_selector)
            
            # Combine tag with other selectors
            if 'class' in target_attributes:
                classes = target_attributes['class']
                if isinstance(classes, str):
                    classes = classes.split()
                class_selector = '.' + '.'.join(classes)
                selectors.append(f"{tag_selector}{class_selector}")
        
        return selectors
    
    def _generate_xpath_expressions(self, target_attributes: Dict[str, Any], text_patterns: List[str]) -> List[str]:
        """Generate XPath expressions from target attributes and text patterns"""
        xpaths = []
        
        # Attribute-based XPaths
        for attr, value in target_attributes.items():
            if attr not in ['position', 'semantic_role']:
                if isinstance(value, str):
                    xpaths.append(f"//*[@{attr}='{value}']")
                elif isinstance(value, list):
                    for v in value:
                        xpaths.append(f"//*[@{attr}='{v}']")
        
        # Text-based XPaths
        for pattern in text_patterns:
            xpaths.extend([
                f"//*[text()='{pattern}']",
                f"//*[contains(text(), '{pattern}')]",
                f"//*[normalize-space(text())='{pattern.strip()}']"
            ])
        
        # Combined XPaths
        if 'tag' in target_attributes and text_patterns:
            tag = target_attributes['tag']
            for pattern in text_patterns:
                xpaths.append(f"//{tag}[contains(text(), '{pattern}')]")
        
        return xpaths
    
    def _map_semantic_to_selectors(self, semantic_role: str) -> List[str]:
        """Map semantic roles to likely CSS selectors"""
        semantic_map = {
            'button': ['button', '[role="button"]', '.btn', '.button', 'input[type="submit"]', 'input[type="button"]'],
            'link': ['a', '[role="link"]', '.link'],
            'input': ['input', 'textarea', '[role="textbox"]', '.input'],
            'form': ['form', '.form', '[role="form"]'],
            'navigation': ['nav', '[role="navigation"]', '.nav', '.navigation'],
            'menu': ['ul.menu', '.menu', '[role="menu"]', '[role="menubar"]'],
            'dialog': ['dialog', '.modal', '.dialog', '[role="dialog"]'],
            'search': ['[role="search"]', '.search', 'input[type="search"]'],
            'table': ['table', '[role="table"]', '.table'],
            'list': ['ul', 'ol', '[role="list"]', '.list'],
            'heading': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', '[role="heading"]'],
            'image': ['img', '[role="img"]', 'figure'],
            'video': ['video', '.video'],
            'alert': ['[role="alert"]', '.alert', '.notification'],
            'tab': ['[role="tab"]', '.tab'],
            'panel': ['[role="tabpanel"]', '.panel', '.tab-content']
        }
        
        return semantic_map.get(semantic_role.lower(), [])
    
    def _calculate_semantic_confidence(self, element_info: ElementInfo, semantic_role: str) -> float:
        """Calculate confidence score for semantic role matching"""
        confidence = 0.0
        
        # Tag name matching
        tag_scores = {
            'button': {'button': 0.9, 'input': 0.7, 'a': 0.3},
            'link': {'a': 0.9, 'button': 0.2},
            'input': {'input': 0.9, 'textarea': 0.8, 'select': 0.7},
            'form': {'form': 0.9, 'div': 0.2},
            'image': {'img': 0.9, 'svg': 0.7, 'canvas': 0.5}
        }
        
        if semantic_role in tag_scores:
            confidence += tag_scores[semantic_role].get(element_info.tag_name, 0.1)
        
        # Attribute matching
        attrs = element_info.attributes
        if 'role' in attrs and attrs['role'] == semantic_role:
            confidence += 0.8
        
        # Class name matching
        for css_class in element_info.css_classes:
            if semantic_role in css_class.lower():
                confidence += 0.3
                break
        
        # Text content matching
        text_lower = element_info.text_content.lower()
        role_keywords = {
            'button': ['click', 'submit', 'save', 'cancel', 'ok', 'continue'],
            'link': ['read more', 'learn more', 'view', 'details'],
            'search': ['search', 'find', 'query'],
            'menu': ['menu', 'options', 'settings']
        }
        
        if semantic_role in role_keywords:
            for keyword in role_keywords[semantic_role]:
                if keyword in text_lower:
                    confidence += 0.2
                    break
        
        return min(confidence, 1.0)
    
    def _execute_browser_query(self, script: str) -> List[Dict[str, Any]]:
        """Execute JavaScript query in browser"""
        # Mock implementation - in real implementation would use selenium, CDP, or similar
        # This would communicate with browser extension or automation driver
        
        # Return mock elements for demonstration
        return [
            {
                'tagName': 'button',
                'attributes': {'id': 'submit-btn', 'class': 'btn btn-primary'},
                'textContent': 'Submit',
                'innerHTML': 'Submit',
                'computedStyles': {'display': 'block', 'visibility': 'visible'},
                'boundingRect': {'x': 100, 'y': 200, 'width': 80, 'height': 32}
            }
        ]
    
    def _create_element_info(self, raw_element: Dict[str, Any], 
                           selector_type: SelectorType, 
                           selector: str) -> ElementInfo:
        """Create ElementInfo from raw browser element data"""
        
        # Extract position information
        rect = raw_element.get('boundingRect', {})
        position = {
            'x': rect.get('x', 0),
            'y': rect.get('y', 0), 
            'width': rect.get('width', 0),
            'height': rect.get('height', 0)
        }
        
        # Parse CSS classes
        class_attr = raw_element.get('attributes', {}).get('class', '')
        css_classes = class_attr.split() if class_attr else []
        
        # Determine element state
        styles = raw_element.get('computedStyles', {})
        state = self._determine_element_state(styles, raw_element.get('attributes', {}))
        
        # Build selectors dictionary
        selectors = {selector_type: selector}
        
        # Generate additional selectors
        if 'id' in raw_element.get('attributes', {}):
            selectors[SelectorType.CSS] = f"#{raw_element['attributes']['id']}"
        
        element_info = ElementInfo(
            tag_name=raw_element.get('tagName', '').lower(),
            attributes=raw_element.get('attributes', {}),
            text_content=raw_element.get('textContent', ''),
            inner_html=raw_element.get('innerHTML', ''),
            css_classes=css_classes,
            computed_styles=styles,
            position=position,
            selectors=selectors,
            state=state,
            interaction_confidence=0.5  # Base confidence, will be updated
        )
        
        # Calculate interaction confidence
        element_info.interaction_confidence = self._calculate_interaction_confidence(element_info)
        
        return element_info
    
    def _determine_element_state(self, computed_styles: Dict[str, str], attributes: Dict[str, str]) -> ElementState:
        """Determine the current state of an element"""
        
        # Check visibility
        if (computed_styles.get('display') == 'none' or 
            computed_styles.get('visibility') == 'hidden' or
            computed_styles.get('opacity') == '0'):
            return ElementState.HIDDEN
        
        # Check if disabled
        if ('disabled' in attributes and attributes['disabled'] != 'false'):
            return ElementState.DISABLED
        
        # Check if loading (common patterns)
        classes = attributes.get('class', '').lower()
        if any(keyword in classes for keyword in ['loading', 'spinner', 'pending']):
            return ElementState.LOADING
        
        # Default to interactive if visible and not disabled
        return ElementState.INTERACTIVE
    
    def _calculate_interaction_confidence(self, element_info: ElementInfo) -> float:
        """Calculate confidence score for element interaction"""
        confidence = 0.5  # Base confidence
        
        # State-based confidence
        state_scores = {
            ElementState.INTERACTIVE: 1.0,
            ElementState.VISIBLE: 0.8,
            ElementState.DISABLED: 0.2,
            ElementState.HIDDEN: 0.1,
            ElementState.LOADING: 0.3,
            ElementState.STALE: 0.0
        }
        confidence *= state_scores.get(element_info.state, 0.5)
        
        # Selector reliability
        if SelectorType.CSS in element_info.selectors and '#' in element_info.selectors[SelectorType.CSS]:
            confidence += 0.3  # ID selector is very reliable
        elif element_info.css_classes:
            confidence += 0.1  # Class selectors are moderately reliable
        
        # Position reliability
        pos = element_info.position
        if pos.get('width', 0) > 0 and pos.get('height', 0) > 0:
            confidence += 0.1  # Element has valid dimensions
        
        # Text content reliability
        if element_info.text_content.strip():
            confidence += 0.1  # Element has meaningful text
        
        return min(confidence, 1.0)
    
    def _matches_query_criteria(self, element_info: ElementInfo, query: DOMQuery) -> bool:
        """Check if element matches query criteria"""
        
        # Check if hidden elements should be included
        if not query.include_hidden and element_info.state == ElementState.HIDDEN:
            return False
        
        # Check CSS properties
        for prop, expected_value in query.css_properties.items():
            actual_value = element_info.computed_styles.get(prop)
            if actual_value != expected_value:
                return False
        
        # Check text patterns
        if query.text_patterns:
            element_text = element_info.text_content.lower()
            if not any(pattern.lower() in element_text for pattern in query.text_patterns):
                return False
        
        return True
    
    def _deduplicate_elements(self, elements: List[ElementInfo]) -> List[ElementInfo]:
        """Remove duplicate elements from list"""
        seen_elements = set()
        unique_elements = []
        
        for element in elements:
            # Create a unique key based on position and attributes
            key = (
                element.tag_name,
                element.position.get('x', 0),
                element.position.get('y', 0), 
                element.attributes.get('id', ''),
                element.text_content[:50]  # First 50 chars
            )
            
            if key not in seen_elements:
                seen_elements.add(key)
                unique_elements.append(element)
        
        return unique_elements
    
    def _rank_elements(self, elements: List[ElementInfo], query: DOMQuery) -> List[ElementInfo]:
        """Rank elements by interaction confidence and relevance"""
        return sorted(elements, key=lambda e: e.interaction_confidence, reverse=True)
    
    def _generate_optimal_selector(self, element_info: ElementInfo) -> str:
        """Generate the most optimal selector for an element"""
        
        # Prioritize selectors by reliability
        selector_priority = [
            SelectorType.CSS,
            SelectorType.ATTRIBUTE,
            SelectorType.XPATH,
            SelectorType.TEXT,
            SelectorType.COMPOSITE
        ]
        
        for selector_type in selector_priority:
            if selector_type in element_info.selectors:
                return element_info.selectors[selector_type]
        
        # Fallback to generating new CSS selector
        if element_info.attributes.get('id'):
            return f"#{element_info.attributes['id']}"
        elif element_info.css_classes:
            return '.' + '.'.join(element_info.css_classes)
        else:
            return element_info.tag_name
    
    def _generate_recommendations(self, result: InspectionResult, query: DOMQuery) -> List[str]:
        """Generate recommendations for improving element detection"""
        recommendations = []
        
        if not result.success:
            recommendations.append("Consider expanding detection strategies")
            recommendations.append("Check if target element exists and is rendered")
            
            if DetectionStrategy.VISUAL_POSITION not in query.strategies:
                recommendations.append("Try adding visual position detection")
        
        elif result.confidence_score < 0.8:
            recommendations.append("Element detection confidence is low - consider adding more specific attributes")
            
            if not result.elements[0].attributes.get('id'):
                recommendations.append("Adding an ID attribute would improve reliability")
        
        if result.query_time > 2.0:  # >2 seconds
            recommendations.append("Consider optimizing selectors for faster detection")
            recommendations.append("Cache frequently used selectors")
        
        return recommendations
    
    def _generate_cache_key(self, query: DOMQuery) -> str:
        """Generate cache key for query"""
        key_parts = [
            ','.join(s.value for s in query.strategies),
            json.dumps(query.target_attributes, sort_keys=True),
            ','.join(query.text_patterns),
            str(query.timeout)
        ]
        return '|'.join(key_parts)
    
    def manipulate_element(self, element_info: ElementInfo, 
                          action: str, 
                          value: Any = None) -> Dict[str, Any]:
        """Manipulate DOM element with specified action"""
        
        selector = self._generate_optimal_selector(element_info)
        
        manipulation_script = self._generate_manipulation_script(selector, action, value)
        
        try:
            # Execute manipulation in browser
            result = self._execute_browser_query(manipulation_script)
            
            return {
                'success': True,
                'action': action,
                'selector': selector,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Element manipulation failed: {e}")
            return {
                'success': False,
                'action': action,
                'selector': selector,
                'error': str(e)
            }
    
    def _generate_manipulation_script(self, selector: str, action: str, value: Any) -> str:
        """Generate JavaScript for element manipulation"""
        
        base_script = f"const element = document.querySelector('{selector}'); if (!element) throw new Error('Element not found');"
        
        if action == 'click':
            return base_script + " element.click(); return 'clicked';"
        elif action == 'type':
            return base_script + f" element.value = '{value}'; element.dispatchEvent(new Event('input')); return 'typed';"
        elif action == 'clear':
            return base_script + " element.value = ''; element.dispatchEvent(new Event('input')); return 'cleared';"
        elif action == 'focus':
            return base_script + " element.focus(); return 'focused';"
        elif action == 'scroll':
            return base_script + " element.scrollIntoView(); return 'scrolled';"
        elif action == 'set_attribute':
            attr_name, attr_value = value
            return base_script + f" element.setAttribute('{attr_name}', '{attr_value}'); return 'attribute_set';"
        elif action == 'get_property':
            return base_script + f" return element.{value};"
        else:
            raise ValueError(f"Unsupported manipulation action: {action}")
    
    def get_inspection_statistics(self) -> Dict[str, Any]:
        """Get comprehensive inspection statistics"""
        if not self.performance_stats['inspection_times']:
            return {"status": "No inspection data available"}
        
        times = self.performance_stats['inspection_times']
        
        return {
            "total_inspections": len(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "cache_hits": len(self.element_cache),
            "cached_selectors": len(self.selector_cache),
            "strategy_priorities": self.strategy_priorities
        }