/**
 * Jest setup file for Chrome extension tests.
 * This file runs before each test and sets up the Chrome API mocks.
 */

// Mock Chrome APIs globally
global.chrome = {
  runtime: {
    sendMessage: jest.fn(),
    sendNativeMessage: jest.fn(),
    onMessage: {
      addListener: jest.fn(),
      removeListener: jest.fn(),
      hasListener: jest.fn()
    },
    onConnect: {
      addListener: jest.fn(),
      removeListener: jest.fn()
    },
    connectNative: jest.fn(),
    getManifest: jest.fn(() => ({
      version: '2.0.0',
      name: 'MKD Automation'
    })),
    lastError: null,
    id: 'mkd-automation-extension'
  },
  
  action: {
    setBadgeText: jest.fn(),
    setBadgeBackgroundColor: jest.fn(),
    setIcon: jest.fn(),
    setTitle: jest.fn(),
    onClicked: {
      addListener: jest.fn(),
      removeListener: jest.fn()
    }
  },
  
  storage: {
    local: {
      get: jest.fn(),
      set: jest.fn(),
      remove: jest.fn(),
      clear: jest.fn()
    },
    sync: {
      get: jest.fn(),
      set: jest.fn(),
      remove: jest.fn(),
      clear: jest.fn()
    }
  },
  
  tabs: {
    query: jest.fn(),
    get: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    remove: jest.fn(),
    onUpdated: {
      addListener: jest.fn(),
      removeListener: jest.fn()
    },
    onActivated: {
      addListener: jest.fn(),
      removeListener: jest.fn()
    }
  },
  
  windows: {
    getCurrent: jest.fn(),
    getAll: jest.fn(),
    create: jest.fn(),
    update: jest.fn()
  }
};

// Mock native messaging responses
const mockNativeResponses = {
  'GET_STATUS': {
    status: 'SUCCESS',
    data: {
      recording: false,
      connected: true,
      version: '2.0.0'
    }
  },
  'START_RECORDING': {
    status: 'SUCCESS', 
    data: {
      sessionId: 'test-session-123',
      recordingStarted: true
    }
  },
  'STOP_RECORDING': {
    status: 'SUCCESS',
    data: {
      recordingStopped: true,
      filePath: '/test/recording.mkd',
      duration: 30.5
    }
  }
};

// Set up default native messaging behavior
global.chrome.runtime.sendNativeMessage.mockImplementation((appName, message, callback) => {
  const response = mockNativeResponses[message.command] || {
    status: 'ERROR',
    error: `Unknown command: ${message.command}`
  };
  
  // Add message ID to response if present in request
  if (message.id) {
    response.id = message.id;
  }
  
  // Simulate async behavior
  setTimeout(() => {
    if (callback) {
      callback(response);
    }
  }, 10);
});

// Mock DOM APIs that might be used
global.document = global.document || {
  createElement: jest.fn(() => ({
    style: {},
    appendChild: jest.fn(),
    setAttribute: jest.fn(),
    getAttribute: jest.fn(),
    removeAttribute: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    click: jest.fn(),
    focus: jest.fn(),
    blur: jest.fn()
  })),
  getElementById: jest.fn(),
  querySelector: jest.fn(),
  querySelectorAll: jest.fn(() => []),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};

global.window = global.window || {
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  location: {
    href: 'chrome-extension://test-extension-id/popup.html'
  },
  setTimeout: global.setTimeout,
  setInterval: global.setInterval,
  clearTimeout: global.clearTimeout,
  clearInterval: global.clearInterval
};

// Utility function to reset all mocks between tests
global.resetChromeMocks = () => {
  Object.values(chrome).forEach(api => {
    if (typeof api === 'object' && api !== null) {
      Object.values(api).forEach(method => {
        if (jest.isMockFunction(method)) {
          method.mockReset();
        }
      });
    }
  });
  
  // Reset chrome.runtime.lastError
  chrome.runtime.lastError = null;
  
  // Restore default native messaging behavior
  chrome.runtime.sendNativeMessage.mockImplementation((appName, message, callback) => {
    const response = mockNativeResponses[message.command] || {
      status: 'ERROR', 
      error: `Unknown command: ${message.command}`
    };
    
    if (message.id) {
      response.id = message.id;
    }
    
    setTimeout(() => {
      if (callback) {
        callback(response);
      }
    }, 10);
  });
};

// Reset mocks before each test
beforeEach(() => {
  global.resetChromeMocks();
});

// Console suppression for cleaner test output
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = jest.fn();
  console.warn = jest.fn();
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});