console.log('MKD Automation content script loaded');

/**
 * Content script security utilities
 */
class ContentSecurityUtils {
    /**
     * Sanitize string input
     */
    static sanitizeString(input, maxLength = 500) {
        if (typeof input !== 'string') {
            return '';
        }
        
        if (input.length > maxLength) {
            input = input.substring(0, maxLength);
        }
        
        // Remove dangerous characters and HTML
        return input.replace(/<[^>]*>/g, '').replace(/[<>'"&]/g, '');
    }
    
    /**
     * Validate action type
     */
    static validateActionType(type) {
        const validTypes = [
            'click', 'input', 'keydown', 'scroll', 'focus', 'blur', 
            'change', 'submit', 'load', 'resize', 'navigation', 'hover'
        ];
        return validTypes.includes(type) ? type : 'unknown';
    }
    
    /**
     * Validate coordinates
     */
    static validateCoordinates(x, y) {
        const validX = typeof x === 'number' && Number.isFinite(x) && x >= 0 && x <= window.innerWidth;
        const validY = typeof y === 'number' && Number.isFinite(y) && y >= 0 && y <= window.innerHeight;
        
        return {
            x: validX ? Math.floor(x) : 0,
            y: validY ? Math.floor(y) : 0
        };
    }
    
    /**
     * Generate unique selector for element
     */
    static generateElementSelector(element) {
        if (!element || !element.tagName) {
            return null;
        }
        
        // Try ID first
        if (element.id) {
            return `#${element.id}`;
        }
        
        // Try data attributes
        const dataTestId = element.getAttribute('data-testid');
        if (dataTestId) {
            return `[data-testid="${dataTestId}"]`;
        }
        
        const dataTest = element.getAttribute('data-test');
        if (dataTest) {
            return `[data-test="${dataTest}"]`;
        }
        
        // Build path based on classes and structure
        let path = [];
        let current = element;
        
        while (current && current.tagName) {
            let selector = current.tagName.toLowerCase();
            
            // Add class information if available
            if (current.className && typeof current.className === 'string') {
                const classes = current.className.split(' ')
                    .filter(cls => cls && !cls.includes('hover') && !cls.includes('active'))
                    .slice(0, 2); // Limit to 2 most relevant classes
                
                if (classes.length > 0) {
                    selector += '.' + classes.join('.');
                }
            }
            
            // Add position if needed for disambiguation
            if (current.parentElement) {
                const siblings = Array.from(current.parentElement.children)
                    .filter(child => child.tagName === current.tagName);
                
                if (siblings.length > 1) {
                    const index = siblings.indexOf(current);
                    selector += `:nth-of-type(${index + 1})`;
                }
            }
            
            path.unshift(selector);
            current = current.parentElement;
            
            // Stop at body or after reasonable depth
            if (!current || current.tagName === 'BODY' || path.length >= 5) {
                break;
            }
        }
        
        return path.join(' > ');
    }
    
    /**
     * Get element context information
     */
    static getElementContext(element) {
        if (!element) return {};
        
        return {
            tag: element.tagName?.toLowerCase(),
            type: element.type,
            role: element.getAttribute('role'),
            ariaLabel: element.getAttribute('aria-label'),
            placeholder: element.placeholder,
            title: element.title,
            name: element.name,
            value: element.value,
            href: element.href,
            alt: element.alt,
            src: element.src?.substring(0, 200), // Limit URL length
            innerText: element.innerText?.substring(0, 100), // Limit text length
            className: element.className,
            id: element.id
        };
    }
}

let isRecording = false;
let recordedActions = [];
const MAX_RECORDED_ACTIONS = 10000; // Prevent memory exhaustion

function recordAction(type, data) {
    if (!isRecording || recordedActions.length >= MAX_RECORDED_ACTIONS) {
        return;
    }
    
    try {
        // Validate and sanitize the action type
        const validatedType = ContentSecurityUtils.validateActionType(type);
        
        // Create sanitized action object
        const sanitizedAction = {
            type: validatedType,
            data: sanitizeActionData(data),
            timestamp: Date.now(),
            url: ContentSecurityUtils.sanitizeString(window.location.href, 500)
        };
        
        recordedActions.push(sanitizedAction);
    } catch (error) {
        console.error('Failed to record action:', error);
    }
}

function sanitizeActionData(data) {
    if (!data || typeof data !== 'object') {
        return {};
    }
    
    const sanitized = {};
    
    // Sanitize coordinates
    if (typeof data.x === 'number' && typeof data.y === 'number') {
        const coords = ContentSecurityUtils.validateCoordinates(data.x, data.y);
        sanitized.x = coords.x;
        sanitized.y = coords.y;
    }
    
    // Enhanced element information
    if (data.element) {
        sanitized.element = {
            tag: ContentSecurityUtils.sanitizeString(data.element.tag, 20),
            id: ContentSecurityUtils.sanitizeString(data.element.id, 100),
            className: ContentSecurityUtils.sanitizeString(data.element.className, 200),
            type: ContentSecurityUtils.sanitizeString(data.element.type, 50),
            name: ContentSecurityUtils.sanitizeString(data.element.name, 100),
            role: ContentSecurityUtils.sanitizeString(data.element.role, 50),
            ariaLabel: ContentSecurityUtils.sanitizeString(data.element.ariaLabel, 200),
            placeholder: ContentSecurityUtils.sanitizeString(data.element.placeholder, 200),
            title: ContentSecurityUtils.sanitizeString(data.element.title, 200),
            innerText: ContentSecurityUtils.sanitizeString(data.element.innerText, 100),
            href: ContentSecurityUtils.sanitizeString(data.element.href, 500),
            alt: ContentSecurityUtils.sanitizeString(data.element.alt, 200)
        };
    }
    
    // Enhanced selector information
    if (data.selector) {
        sanitized.selector = ContentSecurityUtils.sanitizeString(data.selector, 500);
    }
    
    // Page context
    if (data.pageContext) {
        sanitized.pageContext = {
            title: ContentSecurityUtils.sanitizeString(data.pageContext.title, 200),
            url: ContentSecurityUtils.sanitizeString(data.pageContext.url, 500),
            domain: ContentSecurityUtils.sanitizeString(data.pageContext.domain, 100),
            viewport: data.pageContext.viewport
        };
    }
    
    // Legacy support - sanitize old format
    if (data.target) {
        sanitized.target = ContentSecurityUtils.sanitizeString(data.target, 50);
    }
    
    if (data.id) {
        sanitized.id = ContentSecurityUtils.sanitizeString(data.id, 100);
    }
    
    if (data.className) {
        sanitized.className = ContentSecurityUtils.sanitizeString(data.className, 200);
    }
    
    // Sanitize form input values (be careful with sensitive data)
    if (data.value !== undefined) {
        // Don't record password fields
        const element = document.activeElement;
        if (element && (element.type === 'password' || element.type === 'hidden')) {
            sanitized.value = '[REDACTED]';
        } else {
            sanitized.value = ContentSecurityUtils.sanitizeString(data.value, 1000);
        }
    }
    
    // Sanitize key information
    if (data.key) {
        sanitized.key = ContentSecurityUtils.sanitizeString(data.key, 20);
    }
    
    if (data.code) {
        sanitized.code = ContentSecurityUtils.sanitizeString(data.code, 50);
    }
    
    // Copy boolean flags safely
    const booleanFlags = ['ctrlKey', 'metaKey', 'altKey', 'shiftKey'];
    booleanFlags.forEach(flag => {
        if (typeof data[flag] === 'boolean') {
            sanitized[flag] = data[flag];
        }
    });
    
    // Scroll information
    if (data.scroll) {
        sanitized.scroll = {
            x: Math.floor(data.scroll.x || 0),
            y: Math.floor(data.scroll.y || 0),
            deltaX: Math.floor(data.scroll.deltaX || 0),
            deltaY: Math.floor(data.scroll.deltaY || 0)
        };
    }
    
    return sanitized;
}

// Enhanced event listeners with comprehensive data capture
document.addEventListener('click', (e) => {
  recordAction('click', {
    x: e.clientX,
    y: e.clientY,
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target),
    pageContext: {
      title: document.title,
      url: window.location.href,
      domain: window.location.hostname,
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
        scrollX: window.scrollX,
        scrollY: window.scrollY
      }
    },
    ctrlKey: e.ctrlKey,
    metaKey: e.metaKey,
    altKey: e.altKey,
    shiftKey: e.shiftKey,
    button: e.button
  });
});

document.addEventListener('input', (e) => {
  recordAction('input', {
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target),
    value: e.target.value,
    inputType: e.inputType || 'unknown',
    pageContext: {
      title: document.title,
      url: window.location.href,
      domain: window.location.hostname
    }
  });
});

document.addEventListener('keydown', (e) => {
  recordAction('keydown', {
    key: e.key,
    code: e.code,
    ctrlKey: e.ctrlKey,
    metaKey: e.metaKey,
    altKey: e.altKey,
    shiftKey: e.shiftKey,
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target),
    location: e.location,
    repeat: e.repeat
  });
});

// Additional event listeners for comprehensive interaction capture
document.addEventListener('focus', (e) => {
  recordAction('focus', {
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target)
  });
});

document.addEventListener('blur', (e) => {
  recordAction('blur', {
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target)
  });
});

document.addEventListener('change', (e) => {
  recordAction('change', {
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target),
    value: e.target.value,
    checked: e.target.checked,
    selectedIndex: e.target.selectedIndex
  });
});

document.addEventListener('submit', (e) => {
  recordAction('submit', {
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target),
    formData: Array.from(new FormData(e.target)).reduce((obj, [key, value]) => {
      if (typeof value === 'string' && value.length < 100) {
        obj[key] = value;
      }
      return obj;
    }, {})
  });
});

document.addEventListener('scroll', (e) => {
  recordAction('scroll', {
    element: ContentSecurityUtils.getElementContext(e.target),
    selector: ContentSecurityUtils.generateElementSelector(e.target),
    scroll: {
      x: e.target === document ? window.scrollX : e.target.scrollLeft,
      y: e.target === document ? window.scrollY : e.target.scrollTop
    }
  });
});

// Mouse hover tracking (throttled to avoid excessive events)
let hoverTimeout;
document.addEventListener('mouseover', (e) => {
  clearTimeout(hoverTimeout);
  hoverTimeout = setTimeout(() => {
    recordAction('hover', {
      element: ContentSecurityUtils.getElementContext(e.target),
      selector: ContentSecurityUtils.generateElementSelector(e.target),
      x: e.clientX,
      y: e.clientY
    });
  }, 500); // Only record hover if mouse stays for 500ms
});

// Page navigation and lifecycle events
window.addEventListener('beforeunload', () => {
  recordAction('navigation', {
    type: 'beforeunload',
    url: window.location.href
  });
});

window.addEventListener('load', () => {
  recordAction('load', {
    url: window.location.href,
    title: document.title,
    readyState: document.readyState,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight
    }
  });
});

window.addEventListener('resize', () => {
  recordAction('resize', {
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight
    }
  });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    try {
        // Validate request structure
        if (!request || typeof request !== 'object') {
            throw new Error('Invalid request format');
        }
        
        if (!request.action || typeof request.action !== 'string') {
            throw new Error('Request action is required');
        }
        
        // Validate sender (ensure it's from our extension)
        if (!sender || !sender.id || sender.id !== chrome.runtime.id) {
            console.warn('Message from unknown sender:', sender);
            sendResponse({ success: false, error: 'Unauthorized sender' });
            return true;
        }
        
        // Sanitize action name
        const action = ContentSecurityUtils.sanitizeString(request.action, 50);
        
        switch (action) {
            case 'startRecording':
                isRecording = true;
                recordedActions = [];
                console.log('Content script: Recording started');
                sendResponse({ success: true });
                break;
                
            case 'stopRecording':
                isRecording = false;
                console.log(`Content script: Recording stopped, captured ${recordedActions.length} actions`);
                
                // Send sanitized actions array (already sanitized when recorded)
                sendResponse({ 
                    success: true, 
                    actions: recordedActions.slice(0, MAX_RECORDED_ACTIONS) 
                });
                recordedActions = [];
                break;
                
            case 'getStatus':
                sendResponse({ 
                    success: true, 
                    isRecording: Boolean(isRecording),
                    actionCount: recordedActions.length
                });
                break;
                
            case 'RECORDING_STARTED':
            case 'RECORDING_STOPPED': 
            case 'RECORDING_PAUSED':
            case 'RECORDING_RESUMED':
            case 'PAGE_UPDATED':
            case 'TAB_ACTIVATED':
                // These are broadcast messages from background script
                // Just acknowledge receipt
                console.log(`Content script received: ${action}`);
                sendResponse({ success: true });
                break;
                
            default:
                console.warn('Unknown action:', action);
                sendResponse({ success: false, error: 'Unknown action' });
        }
        
    } catch (error) {
        console.error('Error handling message in content script:', error);
        sendResponse({ success: false, error: error.message });
    }
    
    return true; // Keep message channel open for async response
});