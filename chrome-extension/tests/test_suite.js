/**
 * MKD Automation Chrome Extension - Comprehensive Test Suite
 * 
 * This test suite provides comprehensive testing for all Chrome extension components
 * including background script, popup UI, content script, and native messaging.
 */

// Test configuration
const TEST_CONFIG = {
    TIMEOUT: 10000,
    NATIVE_HOST_ID: 'com.mkdautomation.native',
    TEST_URL: 'https://example.com',
    MOCK_SESSION_ID: 'test_session_123',
    MOCK_USER_ID: 1
};

/**
 * Test utilities and helpers
 */
class TestUtils {
    static async sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    static generateMockEvent(type, data = {}) {
        return {
            type,
            timestamp: Date.now(),
            data: {
                x: 100,
                y: 200,
                target: 'button',
                ...data
            }
        };
    }

    static createMockPort() {
        const listeners = {};
        return {
            onMessage: {
                addListener: (fn) => { listeners.onMessage = fn; }
            },
            onDisconnect: {
                addListener: (fn) => { listeners.onDisconnect = fn; }
            },
            postMessage: jest.fn(),
            disconnect: jest.fn(),
            _trigger: (event, data) => {
                if (listeners[event]) {
                    listeners[event](data);
                }
            }
        };
    }

    static mockChromeAPI() {
        global.chrome = {
            runtime: {
                id: 'test-extension-id',
                sendMessage: jest.fn(),
                onMessage: {
                    addListener: jest.fn()
                },
                connectNative: jest.fn(),
                lastError: null
            },
            tabs: {
                query: jest.fn(),
                sendMessage: jest.fn(),
                create: jest.fn(),
                update: jest.fn()
            },
            storage: {
                local: {
                    get: jest.fn(),
                    set: jest.fn(),
                    clear: jest.fn()
                },
                sync: {
                    get: jest.fn(),
                    set: jest.fn()
                }
            },
            action: {
                setBadgeText: jest.fn(),
                setBadgeBackgroundColor: jest.fn(),
                setIcon: jest.fn()
            }
        };
    }
}

/**
 * Background Script Tests
 */
describe('Background Script', () => {
    let backgroundScript;
    let mockPort;

    beforeEach(() => {
        TestUtils.mockChromeAPI();
        mockPort = TestUtils.createMockPort();
        chrome.runtime.connectNative.mockReturnValue(mockPort);
        
        // Load background script
        backgroundScript = require('../src/background.js');
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('Native Messaging Connection', () => {
        test('should establish connection on initialization', async () => {
            expect(chrome.runtime.connectNative).toHaveBeenCalledWith(TEST_CONFIG.NATIVE_HOST_ID);
        });

        test('should handle connection success', async () => {
            mockPort._trigger('onMessage', {
                id: 'test_1',
                success: true,
                command: 'PING',
                data: { status: 'alive', version: '2.0.0' }
            });

            await TestUtils.sleep(100);
            expect(backgroundScript.isConnected).toBe(true);
        });

        test('should handle connection failure with retry', async () => {
            mockPort._trigger('onDisconnect', {});
            
            await TestUtils.sleep(100);
            expect(backgroundScript.isConnected).toBe(false);
            expect(chrome.runtime.connectNative).toHaveBeenCalledTimes(2); // Initial + retry
        });

        test('should enter fallback mode after max retries', async () => {
            for (let i = 0; i < 4; i++) {
                mockPort._trigger('onDisconnect', {});
                await TestUtils.sleep(1100);
            }

            expect(backgroundScript.fallbackMode).toBe(true);
        });
    });

    describe('Recording Controls', () => {
        test('should start recording successfully', async () => {
            const response = await backgroundScript.startRecording({
                user_id: TEST_CONFIG.MOCK_USER_ID,
                config: { capture_video: true }
            });

            expect(mockPort.postMessage).toHaveBeenCalledWith(
                expect.objectContaining({
                    command: 'START_RECORDING',
                    params: expect.objectContaining({
                        user_id: TEST_CONFIG.MOCK_USER_ID
                    })
                })
            );
        });

        test('should stop recording and return data', async () => {
            await backgroundScript.startRecording({ user_id: TEST_CONFIG.MOCK_USER_ID });
            
            mockPort._trigger('onMessage', {
                command: 'STOP_RECORDING',
                success: true,
                data: {
                    sessionId: TEST_CONFIG.MOCK_SESSION_ID,
                    filePath: '/recordings/test.mkd',
                    eventCount: 42,
                    duration: 10.5
                }
            });

            const result = await backgroundScript.stopRecording();
            expect(result.success).toBe(true);
            expect(result.data.eventCount).toBe(42);
        });

        test('should handle pause and resume', async () => {
            await backgroundScript.startRecording({ user_id: TEST_CONFIG.MOCK_USER_ID });
            
            await backgroundScript.pauseRecording();
            expect(backgroundScript.recordingState).toBe('paused');

            await backgroundScript.resumeRecording();
            expect(backgroundScript.recordingState).toBe('recording');
        });
    });

    describe('Message Handling', () => {
        test('should handle popup messages', async () => {
            const sendResponse = jest.fn();
            
            chrome.runtime.onMessage.addListener.mock.calls[0][0](
                { action: 'GET_STATUS' },
                { tab: { id: 1 } },
                sendResponse
            );

            await TestUtils.sleep(100);
            expect(sendResponse).toHaveBeenCalledWith(
                expect.objectContaining({
                    success: true,
                    data: expect.objectContaining({
                        isConnected: expect.any(Boolean),
                        recordingState: expect.any(String)
                    })
                })
            );
        });

        test('should broadcast state changes to tabs', async () => {
            chrome.tabs.query.mockResolvedValue([
                { id: 1 }, { id: 2 }
            ]);

            await backgroundScript.broadcastStateChange('RECORDING_STARTED');

            expect(chrome.tabs.sendMessage).toHaveBeenCalledTimes(2);
            expect(chrome.tabs.sendMessage).toHaveBeenCalledWith(
                1,
                { action: 'RECORDING_STARTED' },
                expect.any(Function)
            );
        });
    });

    describe('Error Handling', () => {
        test('should handle native host errors gracefully', async () => {
            mockPort._trigger('onMessage', {
                success: false,
                error: 'Native host error'
            });

            const result = await backgroundScript.getStatus();
            expect(result.success).toBe(false);
            expect(result.error).toBe('Native host error');
        });

        test('should timeout long-running requests', async () => {
            const promise = backgroundScript.sendNativeMessage('TEST_COMMAND', {});
            
            await TestUtils.sleep(TEST_CONFIG.TIMEOUT + 100);
            
            await expect(promise).rejects.toThrow('Request timeout');
        });
    });
});

/**
 * Content Script Tests
 */
describe('Content Script', () => {
    let contentScript;
    let originalDocument;

    beforeEach(() => {
        // Mock DOM
        document.body.innerHTML = `
            <div id="test-container">
                <button id="test-button" data-testid="submit">Click Me</button>
                <input id="test-input" type="text" placeholder="Enter text" />
                <form id="test-form">
                    <input name="username" type="text" />
                    <input name="password" type="password" />
                </form>
            </div>
        `;

        TestUtils.mockChromeAPI();
        contentScript = require('../src/content.js');
    });

    describe('Event Recording', () => {
        test('should record click events with full context', () => {
            const button = document.getElementById('test-button');
            const clickEvent = new MouseEvent('click', {
                clientX: 100,
                clientY: 200,
                button: 0
            });

            contentScript.startRecording();
            button.dispatchEvent(clickEvent);

            const recordedActions = contentScript.getRecordedActions();
            expect(recordedActions).toHaveLength(1);
            expect(recordedActions[0]).toMatchObject({
                type: 'click',
                data: expect.objectContaining({
                    x: 100,
                    y: 200,
                    selector: expect.stringContaining('#test-button'),
                    element: expect.objectContaining({
                        tag: 'button',
                        id: 'test-button'
                    })
                })
            });
        });

        test('should record input events with sanitization', () => {
            const input = document.getElementById('test-input');
            
            contentScript.startRecording();
            input.value = 'test value';
            input.dispatchEvent(new Event('input'));

            const recordedActions = contentScript.getRecordedActions();
            expect(recordedActions[0].data.value).toBe('test value');
        });

        test('should redact password fields', () => {
            const passwordInput = document.querySelector('input[type="password"]');
            
            contentScript.startRecording();
            passwordInput.value = 'secret123';
            passwordInput.dispatchEvent(new Event('input'));

            const recordedActions = contentScript.getRecordedActions();
            expect(recordedActions[0].data.value).toBe('[REDACTED]');
        });

        test('should generate robust CSS selectors', () => {
            const button = document.getElementById('test-button');
            const selector = contentScript.generateElementSelector(button);
            
            expect(selector).toBe('#test-button');
            
            // Test data-testid fallback
            button.removeAttribute('id');
            const selectorWithTestId = contentScript.generateElementSelector(button);
            expect(selectorWithTestId).toBe('[data-testid="submit"]');
        });

        test('should handle scroll events', () => {
            contentScript.startRecording();
            
            window.scrollTo(0, 500);
            document.dispatchEvent(new Event('scroll'));

            const recordedActions = contentScript.getRecordedActions();
            expect(recordedActions[0]).toMatchObject({
                type: 'scroll',
                data: expect.objectContaining({
                    scroll: { x: 0, y: 500 }
                })
            });
        });
    });

    describe('Security', () => {
        test('should sanitize malicious input', () => {
            const maliciousString = '<script>alert("XSS")</script>';
            const sanitized = contentScript.sanitizeString(maliciousString);
            
            expect(sanitized).not.toContain('<script>');
            expect(sanitized).not.toContain('alert');
        });

        test('should validate action types', () => {
            const validType = contentScript.validateActionType('click');
            expect(validType).toBe('click');

            const invalidType = contentScript.validateActionType('malicious');
            expect(invalidType).toBe('unknown');
        });

        test('should enforce maximum recording limit', () => {
            contentScript.startRecording();
            
            for (let i = 0; i < 10005; i++) {
                contentScript.recordAction('click', { x: i, y: i });
            }

            const recordedActions = contentScript.getRecordedActions();
            expect(recordedActions.length).toBeLessThanOrEqual(10000);
        });
    });

    describe('Message Handling', () => {
        test('should respond to start recording message', (done) => {
            chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
                if (request.action === 'startRecording') {
                    sendResponse({ success: true });
                    expect(contentScript.isRecording).toBe(true);
                    done();
                }
            });

            chrome.runtime.sendMessage({ action: 'startRecording' });
        });

        test('should validate message sender', () => {
            const sendResponse = jest.fn();
            
            contentScript.handleMessage(
                { action: 'startRecording' },
                { id: 'malicious-extension' },
                sendResponse
            );

            expect(sendResponse).toHaveBeenCalledWith({
                success: false,
                error: 'Unauthorized sender'
            });
        });
    });
});

/**
 * Popup UI Tests
 */
describe('Popup UI', () => {
    let popupScript;

    beforeEach(() => {
        document.body.innerHTML = `
            <div id="status-indicator" class="status-dot"></div>
            <span id="status-text">Ready</span>
            <button id="start-button">Start Recording</button>
            <button id="stop-button" disabled>Stop Recording</button>
            <button id="pause-button" style="display: none;">Pause</button>
            <div id="error-section" style="display: none;"></div>
            <div id="fallback-message" style="display: none;"></div>
        `;

        TestUtils.mockChromeAPI();
        popupScript = require('../src/popup/popup.js');
    });

    describe('UI State Management', () => {
        test('should update UI based on connection status', async () => {
            await popupScript.updateConnectionStatus(true);
            
            const statusDot = document.getElementById('status-indicator');
            expect(statusDot.classList.contains('ready')).toBe(true);
        });

        test('should show recording controls when recording', async () => {
            await popupScript.updateRecordingState('recording');
            
            const startButton = document.getElementById('start-button');
            const stopButton = document.getElementById('stop-button');
            const pauseButton = document.getElementById('pause-button');

            expect(startButton.disabled).toBe(true);
            expect(stopButton.disabled).toBe(false);
            expect(pauseButton.style.display).not.toBe('none');
        });

        test('should display error messages', () => {
            popupScript.showError('Test error message');
            
            const errorSection = document.getElementById('error-section');
            expect(errorSection.style.display).not.toBe('none');
            expect(errorSection.textContent).toContain('Test error message');
        });

        test('should show fallback mode UI', () => {
            popupScript.enterFallbackMode();
            
            const fallbackMessage = document.getElementById('fallback-message');
            expect(fallbackMessage.style.display).not.toBe('none');
        });
    });

    describe('User Interactions', () => {
        test('should handle start recording button click', async () => {
            chrome.runtime.sendMessage.mockResolvedValue({
                success: true,
                data: { sessionId: TEST_CONFIG.MOCK_SESSION_ID }
            });

            const startButton = document.getElementById('start-button');
            startButton.click();

            await TestUtils.sleep(100);

            expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
                action: 'START_RECORDING',
                params: expect.any(Object)
            });
        });

        test('should handle stop recording with data display', async () => {
            chrome.runtime.sendMessage.mockResolvedValue({
                success: true,
                data: {
                    eventCount: 50,
                    duration: 15.5,
                    filePath: '/recordings/test.mkd'
                }
            });

            const stopButton = document.getElementById('stop-button');
            stopButton.disabled = false;
            stopButton.click();

            await TestUtils.sleep(100);

            expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
                action: 'STOP_RECORDING'
            });
        });

        test('should handle retry connection', async () => {
            popupScript.enterFallbackMode();
            
            chrome.runtime.sendMessage.mockResolvedValue({
                success: true,
                data: { isConnected: true }
            });

            const retryButton = document.querySelector('.retry-button');
            retryButton.click();

            await TestUtils.sleep(100);

            expect(chrome.runtime.sendMessage).toHaveBeenCalledWith({
                action: 'RETRY_CONNECTION'
            });
        });
    });

    describe('Keyboard Shortcuts', () => {
        test('should handle Ctrl+Shift+R to start recording', () => {
            const event = new KeyboardEvent('keydown', {
                key: 'R',
                ctrlKey: true,
                shiftKey: true
            });

            document.dispatchEvent(event);

            expect(chrome.runtime.sendMessage).toHaveBeenCalledWith(
                expect.objectContaining({
                    action: 'START_RECORDING'
                })
            );
        });

        test('should handle Escape to stop recording', async () => {
            await popupScript.updateRecordingState('recording');
            
            const event = new KeyboardEvent('keydown', {
                key: 'Escape'
            });

            document.dispatchEvent(event);

            expect(chrome.runtime.sendMessage).toHaveBeenCalledWith(
                expect.objectContaining({
                    action: 'STOP_RECORDING'
                })
            );
        });
    });
});

/**
 * Integration Tests
 */
describe('Integration Tests', () => {
    beforeEach(() => {
        TestUtils.mockChromeAPI();
    });

    test('End-to-end recording workflow', async () => {
        // 1. Initialize extension
        const backgroundScript = require('../src/background.js');
        const contentScript = require('../src/content.js');
        const popupScript = require('../src/popup/popup.js');

        // 2. Establish native connection
        const mockPort = TestUtils.createMockPort();
        chrome.runtime.connectNative.mockReturnValue(mockPort);
        await backgroundScript.initialize();

        // 3. Start recording from popup
        await popupScript.startRecording();

        // 4. Simulate user interactions in content script
        contentScript.startRecording();
        
        const button = document.createElement('button');
        button.id = 'test-button';
        document.body.appendChild(button);
        
        button.click();
        
        // 5. Stop recording
        const recordedActions = contentScript.stopRecording();
        
        // 6. Send to background
        mockPort._trigger('onMessage', {
            command: 'STOP_RECORDING',
            success: true,
            data: {
                sessionId: TEST_CONFIG.MOCK_SESSION_ID,
                eventCount: recordedActions.length,
                filePath: '/test.mkd'
            }
        });

        const result = await backgroundScript.stopRecording();

        // 7. Verify complete workflow
        expect(result.success).toBe(true);
        expect(result.data.eventCount).toBe(recordedActions.length);
        expect(recordedActions).toHaveLength(1);
        expect(recordedActions[0].type).toBe('click');
    });

    test('Fallback mode activation and recovery', async () => {
        const backgroundScript = require('../src/background.js');
        const popupScript = require('../src/popup/popup.js');

        // Simulate connection failures
        chrome.runtime.connectNative.mockImplementation(() => {
            const port = TestUtils.createMockPort();
            setTimeout(() => port._trigger('onDisconnect', {}), 100);
            return port;
        });

        await backgroundScript.initialize();

        // Wait for retries
        await TestUtils.sleep(5000);

        // Verify fallback mode
        expect(backgroundScript.fallbackMode).toBe(true);
        expect(popupScript.isFallbackMode()).toBe(true);

        // Simulate successful reconnection
        chrome.runtime.connectNative.mockImplementation(() => {
            const port = TestUtils.createMockPort();
            setTimeout(() => {
                port._trigger('onMessage', {
                    command: 'PING',
                    success: true,
                    data: { status: 'alive' }
                });
            }, 100);
            return port;
        });

        await backgroundScript.retryConnection();

        // Verify recovery
        expect(backgroundScript.fallbackMode).toBe(false);
        expect(backgroundScript.isConnected).toBe(true);
    });
});

// Export test runner
module.exports = {
    TestUtils,
    runAllTests: async () => {
        const results = await Promise.all([
            describe('Background Script'),
            describe('Content Script'),
            describe('Popup UI'),
            describe('Integration Tests')
        ]);
        
        return {
            total: results.reduce((sum, r) => sum + r.total, 0),
            passed: results.reduce((sum, r) => sum + r.passed, 0),
            failed: results.reduce((sum, r) => sum + r.failed, 0),
            skipped: results.reduce((sum, r) => sum + r.skipped, 0)
        };
    }
};