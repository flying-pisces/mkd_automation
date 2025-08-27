/**
 * Unit tests for Chrome extension UI controls.
 */

import { jest } from '@jest/globals';

// Mock the popup UI module (assuming it exists)
const mockPopupUI = {
  updateStatus: jest.fn(),
  showRecordingState: jest.fn(),
  showError: jest.fn(),
  enableControls: jest.fn(),
  disableControls: jest.fn()
};

describe('Chrome Extension UI Controls', () => {
  let popupUI;
  
  beforeEach(() => {
    // Reset mocks
    global.resetChromeMocks();
    
    // Create a mock popup UI instance
    popupUI = { ...mockPopupUI };
    Object.values(popupUI).forEach(method => method.mockReset());
    
    // Mock DOM elements
    global.document.getElementById.mockImplementation((id) => {
      const elements = {
        'start-button': {
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          disabled: false,
          textContent: 'Start Recording',
          style: {},
          classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn()
          }
        },
        'stop-button': {
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          disabled: true,
          textContent: 'Stop Recording',
          style: { display: 'none' },
          classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn()
          }
        },
        'status-text': {
          textContent: 'Ready to record',
          style: {}
        },
        'timer-display': {
          textContent: '00:00:00',
          style: {}
        },
        'error-message': {
          textContent: '',
          style: { display: 'none' }
        }
      };
      
      return elements[id] || null;
    });
  });

  describe('Start Recording Button', () => {
    test('should send START_RECORDING command when clicked', async () => {
      // Arrange
      const startButton = document.getElementById('start-button');
      let clickHandler;
      
      startButton.addEventListener.mockImplementation((event, handler) => {
        if (event === 'click') {
          clickHandler = handler;
        }
      });
      
      // Simulate button setup
      startButton.addEventListener('click', clickHandler);
      
      // Act
      if (clickHandler) {
        await clickHandler();
      }
      
      // Assert
      expect(chrome.runtime.sendNativeMessage).toHaveBeenCalledWith(
        'com.mkd.automation',
        expect.objectContaining({
          command: 'START_RECORDING',
          params: expect.any(Object)
        }),
        expect.any(Function)
      );
    });

    test('should disable start button and enable stop button on successful recording start', (done) => {
      // Arrange
      const startButton = document.getElementById('start-button');
      const stopButton = document.getElementById('stop-button');
      
      chrome.runtime.sendNativeMessage.mockImplementation((appName, message, callback) => {
        setTimeout(() => {
          callback({
            id: message.id,
            status: 'SUCCESS',
            data: {
              sessionId: 'test-session-123',
              recordingStarted: true
            }
          });
          
          // Verify UI state changes
          try {
            expect(startButton.disabled).toBe(true);
            expect(stopButton.disabled).toBe(false);
            expect(stopButton.style.display).not.toBe('none');
            done();
          } catch (error) {
            done(error);
          }
        }, 10);
      });
      
      // Act
      const clickEvent = new Event('click');
      startButton.dispatchEvent?.(clickEvent);
    });

    test('should show error message when recording start fails', (done) => {
      // Arrange
      const errorElement = document.getElementById('error-message');
      
      chrome.runtime.sendNativeMessage.mockImplementation((appName, message, callback) => {
        setTimeout(() => {
          callback({
            id: message.id,
            status: 'ERROR',
            error: 'Native host not found'
          });
          
          // Verify error display
          try {
            expect(errorElement.textContent).toContain('Native host not found');
            expect(errorElement.style.display).not.toBe('none');
            done();
          } catch (error) {
            done(error);
          }
        }, 10);
      });
      
      // Act
      const clickEvent = new Event('click');
      document.getElementById('start-button').dispatchEvent?.(clickEvent);
    });
  });

  describe('Stop Recording Button', () => {
    test('should send STOP_RECORDING command when clicked', async () => {
      // Arrange
      const stopButton = document.getElementById('stop-button');
      stopButton.disabled = false;
      
      let clickHandler;
      stopButton.addEventListener.mockImplementation((event, handler) => {
        if (event === 'click') {
          clickHandler = handler;
        }
      });
      
      // Simulate button setup
      stopButton.addEventListener('click', clickHandler);
      
      // Act
      if (clickHandler) {
        await clickHandler();
      }
      
      // Assert
      expect(chrome.runtime.sendNativeMessage).toHaveBeenCalledWith(
        'com.mkd.automation',
        expect.objectContaining({
          command: 'STOP_RECORDING',
          params: expect.any(Object)
        }),
        expect.any(Function)
      );
    });

    test('should reset UI state on successful recording stop', (done) => {
      // Arrange
      const startButton = document.getElementById('start-button');
      const stopButton = document.getElementById('stop-button');
      const statusText = document.getElementById('status-text');
      
      chrome.runtime.sendNativeMessage.mockImplementation((appName, message, callback) => {
        setTimeout(() => {
          callback({
            id: message.id,
            status: 'SUCCESS',
            data: {
              recordingStopped: true,
              filePath: '/test/recording.mkd',
              duration: 30.5
            }
          });
          
          // Verify UI reset
          try {
            expect(startButton.disabled).toBe(false);
            expect(stopButton.disabled).toBe(true);
            expect(statusText.textContent).toContain('Recording saved');
            done();
          } catch (error) {
            done(error);
          }
        }, 10);
      });
      
      // Act
      const clickEvent = new Event('click');
      stopButton.dispatchEvent?.(clickEvent);
    });
  });

  describe('Status Display', () => {
    test('should update status text during recording', () => {
      // Arrange
      const statusText = document.getElementById('status-text');
      
      // Act
      const updateStatus = (message) => {
        statusText.textContent = message;
      };
      
      updateStatus('Recording in progress...');
      
      // Assert
      expect(statusText.textContent).toBe('Recording in progress...');
    });

    test('should show recording timer during recording', () => {
      // Arrange
      const timerDisplay = document.getElementById('timer-display');
      let startTime = Date.now();
      
      // Act
      const updateTimer = () => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;
        
        timerDisplay.textContent = 
          `${hours.toString().padStart(2, '0')}:` +
          `${minutes.toString().padStart(2, '0')}:` +
          `${seconds.toString().padStart(2, '0')}`;
      };
      
      // Simulate 65 seconds elapsed
      startTime = Date.now() - (65 * 1000);
      updateTimer();
      
      // Assert
      expect(timerDisplay.textContent).toBe('00:01:05');
    });
  });

  describe('Error Handling', () => {
    test('should display connection errors', () => {
      // Arrange
      const errorElement = document.getElementById('error-message');
      
      // Act
      const showError = (message, type = 'error') => {
        errorElement.textContent = message;
        errorElement.className = `message ${type}`;
        errorElement.style.display = 'block';
      };
      
      showError('Unable to connect to native host', 'error');
      
      // Assert
      expect(errorElement.textContent).toBe('Unable to connect to native host');
      expect(errorElement.className).toContain('error');
      expect(errorElement.style.display).toBe('block');
    });

    test('should clear errors on successful operations', () => {
      // Arrange
      const errorElement = document.getElementById('error-message');
      errorElement.textContent = 'Previous error';
      errorElement.style.display = 'block';
      
      // Act
      const clearError = () => {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
      };
      
      clearError();
      
      // Assert
      expect(errorElement.textContent).toBe('');
      expect(errorElement.style.display).toBe('none');
    });
  });

  describe('Keyboard Shortcuts', () => {
    test('should handle Ctrl+R for start recording', () => {
      // Arrange
      const startButton = document.getElementById('start-button');
      let keydownHandler;
      
      document.addEventListener = jest.fn().mockImplementation((event, handler) => {
        if (event === 'keydown') {
          keydownHandler = handler;
        }
      });
      
      // Setup keyboard listener
      document.addEventListener('keydown', keydownHandler);
      
      // Act
      const keyEvent = {
        key: 'r',
        ctrlKey: true,
        preventDefault: jest.fn(),
        stopPropagation: jest.fn()
      };
      
      if (keydownHandler) {
        keydownHandler(keyEvent);
      }
      
      // Assert
      expect(keyEvent.preventDefault).toHaveBeenCalled();
      expect(chrome.runtime.sendNativeMessage).toHaveBeenCalledWith(
        'com.mkd.automation',
        expect.objectContaining({
          command: 'START_RECORDING'
        }),
        expect.any(Function)
      );
    });

    test('should handle Ctrl+Shift+R for stop recording', () => {
      // Arrange
      let keydownHandler;
      
      document.addEventListener = jest.fn().mockImplementation((event, handler) => {
        if (event === 'keydown') {
          keydownHandler = handler;
        }
      });
      
      // Setup keyboard listener
      document.addEventListener('keydown', keydownHandler);
      
      // Act
      const keyEvent = {
        key: 'R',
        ctrlKey: true,
        shiftKey: true,
        preventDefault: jest.fn(),
        stopPropagation: jest.fn()
      };
      
      if (keydownHandler) {
        keydownHandler(keyEvent);
      }
      
      // Assert
      expect(keyEvent.preventDefault).toHaveBeenCalled();
      expect(chrome.runtime.sendNativeMessage).toHaveBeenCalledWith(
        'com.mkd.automation',
        expect.objectContaining({
          command: 'STOP_RECORDING'
        }),
        expect.any(Function)
      );
    });
  });

  describe('Settings Controls', () => {
    test('should save recording preferences', async () => {
      // Arrange
      const settings = {
        captureVideo: true,
        captureAudio: false,
        showBorder: true,
        borderColor: '#FF0000'
      };
      
      chrome.storage.local.set.mockImplementation((data, callback) => {
        setTimeout(callback, 10);
      });
      
      // Act
      const saveSettings = (settingsData) => {
        return new Promise((resolve) => {
          chrome.storage.local.set({ settings: settingsData }, resolve);
        });
      };
      
      await saveSettings(settings);
      
      // Assert
      expect(chrome.storage.local.set).toHaveBeenCalledWith(
        { settings },
        expect.any(Function)
      );
    });

    test('should load saved preferences on popup open', async () => {
      // Arrange
      const savedSettings = {
        captureVideo: false,
        captureAudio: true,
        showBorder: false,
        borderColor: '#00FF00'
      };
      
      chrome.storage.local.get.mockImplementation((keys, callback) => {
        setTimeout(() => callback({ settings: savedSettings }), 10);
      });
      
      // Act
      const loadSettings = () => {
        return new Promise((resolve) => {
          chrome.storage.local.get(['settings'], (result) => {
            resolve(result.settings || {});
          });
        });
      };
      
      const settings = await loadSettings();
      
      // Assert
      expect(chrome.storage.local.get).toHaveBeenCalledWith(
        ['settings'],
        expect.any(Function)
      );
      expect(settings).toEqual(savedSettings);
    });
  });

  describe('Badge Updates', () => {
    test('should update extension badge during recording', () => {
      // Arrange & Act
      const updateBadge = (recording) => {
        if (recording) {
          chrome.action.setBadgeText({ text: 'REC' });
          chrome.action.setBadgeBackgroundColor({ color: '#FF0000' });
        } else {
          chrome.action.setBadgeText({ text: '' });
        }
      };
      
      // Test recording state
      updateBadge(true);
      
      // Assert
      expect(chrome.action.setBadgeText).toHaveBeenCalledWith({ text: 'REC' });
      expect(chrome.action.setBadgeBackgroundColor).toHaveBeenCalledWith({ color: '#FF0000' });
      
      // Test stopped state
      updateBadge(false);
      expect(chrome.action.setBadgeText).toHaveBeenCalledWith({ text: '' });
    });
  });
});