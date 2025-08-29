/**
 * Background Service Worker for MKD Automation Chrome Extension
 *
 * Handles persistent functionality including:
 * - Native messaging coordination
 * - Global state management
 * - Keyboard shortcuts
 * - Badge updates
 * - Extension lifecycle events
 */

// Simple native messaging handler for Week 1
class SimpleNativeMessagingHandler {
    constructor() {
        this.hostName = 'com.mkd.automation';
        this.port = null;
        this.isConnected = false;
        this.messageId = 0;
        this.pendingRequests = new Map();
    }

    async startRecording(config) {
        return this.sendMessage('START_RECORDING', config);
    }

    async stopRecording(sessionId) {
        return this.sendMessage('STOP_RECORDING', { sessionId });
    }

    async pauseRecording(sessionId) {
        return this.sendMessage('PAUSE_RECORDING', { sessionId });
    }

    async resumeRecording(sessionId) {
        return this.sendMessage('RESUME_RECORDING', { sessionId });
    }

    async getStatus() {
        return this.sendMessage('GET_STATUS', {});
    }

    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            hostName: this.hostName,
            lastError: this.lastError || null
        };
    }

    async sendMessage(command, params = {}) {
        return new Promise((resolve, reject) => {
            const messageId = ++this.messageId;
            const message = {
                id: messageId,
                command: command,
                params: params,
                timestamp: Date.now()
            };

            try {
                // Connect to native host if not already connected
                if (!this.port || this.port.error) {
                    this.port = chrome.runtime.connectNative(this.hostName);
                    this.setupPortHandlers();
                }

                // Store pending request
                this.pendingRequests.set(messageId, { resolve, reject });

                // Send message
                this.port.postMessage(message);

                // Set timeout for response
                setTimeout(() => {
                    if (this.pendingRequests.has(messageId)) {
                        this.pendingRequests.delete(messageId);
                        reject(new Error('Request timeout'));
                    }
                }, 10000); // 10 second timeout

            } catch (error) {
                reject(new Error(`Native messaging error: ${error.message}`));
            }
        });
    }

    setupPortHandlers() {
        if (!this.port) return;

        this.port.onMessage.addListener((response) => {
            const messageId = response.id;
            if (this.pendingRequests.has(messageId)) {
                const { resolve, reject } = this.pendingRequests.get(messageId);
                this.pendingRequests.delete(messageId);

                if (response.success) {
                    resolve(response);
                } else {
                    reject(new Error(response.error));
                }
            }
        });

        this.port.onDisconnect.addListener(() => {
            this.isConnected = false;
            this.lastError = chrome.runtime.lastError?.message || 'Connection lost';

            // Reject all pending requests
            for (const [messageId, { reject }] of this.pendingRequests) {
                reject(new Error('Native host disconnected'));
            }
            this.pendingRequests.clear();

            console.warn('Native host disconnected:', this.lastError);
        });

        // Mark as connected
        this.isConnected = true;
        this.lastError = null;
    }

    cleanup() {
        if (this.port) {
            this.port.disconnect();
            this.port = null;
        }
        this.isConnected = false;
    }
}

class MKDBackgroundService {
    constructor() {
        this.nativeMessaging = new SimpleNativeMessagingHandler();
        this.currentSession = null;
        this.recordingState = {
            isRecording: false,
            isPaused: false,
            sessionId: null,
            startTime: null
        };

        this.initializeEventListeners();
        this.initializeKeyboardShortcuts();

        console.log('MKD Automation background service initialized');
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Handle extension installation/startup
        chrome.runtime.onInstalled.addListener((details) => {
            this.handleInstall(details);
        });

        // Handle messages from popup and content scripts
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
            return true; // Keep channel open for async responses
        });

        // Handle extension unload
        chrome.runtime.onSuspend.addListener(() => {
            this.handleSuspend();
        });

        // Handle tab updates for context tracking
        chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
            this.handleTabUpdate(tabId, changeInfo, tab);
        });

        // Handle tab activation
        chrome.tabs.onActivated.addListener((activeInfo) => {
            this.handleTabActivated(activeInfo);
        });
    }

    /**
     * Initialize keyboard shortcuts
     */
    initializeKeyboardShortcuts() {
        chrome.commands.onCommand.addListener((command) => {
            this.handleCommand(command);
        });
    }

    /**
     * Handle extension installation
     */
    handleInstall(details) {
        console.log('MKD Automation installed:', details);

        // Set initial badge
        this.updateBadge('', '#808080');

        // Check native host availability
        this.checkNativeHostAvailability();

        if (details.reason === 'install') {
            // First time installation
            this.showWelcomeNotification();
        } else if (details.reason === 'update') {
            // Extension update
            console.log(`Updated from ${details.previousVersion} to ${chrome.runtime.getManifest().version}`);
        }
    }

    /**
     * Handle messages from other parts of the extension
     */
    async handleMessage(message, sender, sendResponse) {
        console.log('Background received message:', message.type);

        try {
            switch (message.type) {
                case 'START_RECORDING':
                    const startResult = await this.startRecording(message.config);
                    sendResponse({ success: true, data: startResult });
                    break;

                case 'STOP_RECORDING':
                    const stopResult = await this.stopRecording();
                    sendResponse({ success: true, data: stopResult });
                    break;

                case 'PAUSE_RECORDING':
                    const pauseResult = await this.pauseRecording();
                    sendResponse({ success: true, data: pauseResult });
                    break;

                case 'RESUME_RECORDING':
                    const resumeResult = await this.resumeRecording();
                    sendResponse({ success: true, data: resumeResult });
                    break;

                case 'GET_STATUS':
                    const status = await this.getStatus();
                    sendResponse({ success: true, data: status });
                    break;

                case 'GET_CONNECTION_STATUS':
                    const connectionStatus = this.nativeMessaging.getConnectionStatus();
                    sendResponse({ success: true, data: connectionStatus });
                    break;

                default:
                    console.warn('Unknown message type:', message.type);
                    sendResponse({ success: false, error: 'Unknown message type' });
            }
        } catch (error) {
            console.error('Error handling message:', error);
            sendResponse({ success: false, error: error.message });
        }
    }

    /**
     * Handle keyboard commands
     */
    async handleCommand(command) {
        console.log('Keyboard command:', command);

        switch (command) {
            case 'toggle-recording':
                if (this.recordingState.isRecording) {
                    try {
                        await this.stopRecording();
                        this.showNotification('Recording stopped via keyboard shortcut');
                    } catch (error) {
                        console.error('Failed to stop recording via shortcut:', error);
                        this.showNotification('Failed to stop recording', 'error');
                    }
                } else {
                    try {
                        await this.startRecording();
                        this.showNotification('Recording started via keyboard shortcut');
                    } catch (error) {
                        console.error('Failed to start recording via shortcut:', error);
                        this.showNotification('Failed to start recording', 'error');
                    }
                }
                break;

            default:
                console.warn('Unknown command:', command);
        }
    }

    /**
     * Start recording
     */
    async startRecording(config = {}) {
        if (this.recordingState.isRecording) {
            throw new Error('Recording already in progress');
        }

        try {
            const result = await this.nativeMessaging.startRecording(config);

            this.recordingState = {
                isRecording: true,
                isPaused: false,
                sessionId: result.sessionId,
                startTime: Date.now()
            };

            this.currentSession = result;
            this.updateBadge('REC', '#FF0000');

            // Notify all tabs about recording start
            this.broadcastToTabs({
                type: 'RECORDING_STARTED',
                sessionId: result.sessionId
            });

            console.log('Recording started:', result.sessionId);
            return result;

        } catch (error) {
            console.error('Failed to start recording:', error);
            this.updateBadge('ERR', '#FF8800');
            throw error;
        }
    }

    /**
     * Stop recording
     */
    async stopRecording() {
        if (!this.recordingState.isRecording) {
            throw new Error('No active recording to stop');
        }

        try {
            const result = await this.nativeMessaging.stopRecording(this.recordingState.sessionId);

            this.recordingState = {
                isRecording: false,
                isPaused: false,
                sessionId: null,
                startTime: null
            };

            this.currentSession = null;
            this.updateBadge('', '#808080');

            // Notify all tabs about recording stop
            this.broadcastToTabs({
                type: 'RECORDING_STOPPED',
                result: result
            });

            console.log('Recording stopped:', result);
            return result;

        } catch (error) {
            console.error('Failed to stop recording:', error);
            this.updateBadge('ERR', '#FF8800');
            throw error;
        }
    }

    /**
     * Pause recording
     */
    async pauseRecording() {
        if (!this.recordingState.isRecording || this.recordingState.isPaused) {
            throw new Error('No active recording to pause');
        }

        try {
            const result = await this.nativeMessaging.pauseRecording(this.recordingState.sessionId);

            this.recordingState.isPaused = true;
            this.updateBadge('PAU', '#FF8800');

            this.broadcastToTabs({
                type: 'RECORDING_PAUSED'
            });

            return result;

        } catch (error) {
            console.error('Failed to pause recording:', error);
            throw error;
        }
    }

    /**
     * Resume recording
     */
    async resumeRecording() {
        if (!this.recordingState.isRecording || !this.recordingState.isPaused) {
            throw new Error('No paused recording to resume');
        }

        try {
            const result = await this.nativeMessaging.resumeRecording(this.recordingState.sessionId);

            this.recordingState.isPaused = false;
            this.updateBadge('REC', '#FF0000');

            this.broadcastToTabs({
                type: 'RECORDING_RESUMED'
            });

            return result;

        } catch (error) {
            console.error('Failed to resume recording:', error);
            throw error;
        }
    }

    /**
     * Get current status
     */
    async getStatus() {
        try {
            const nativeStatus = await this.nativeMessaging.getStatus();
            const connectionStatus = this.nativeMessaging.getConnectionStatus();

            return {
                recording: this.recordingState,
                session: this.currentSession,
                connection: connectionStatus,
                native: nativeStatus
            };

        } catch (error) {
            console.error('Failed to get status:', error);
            return {
                recording: this.recordingState,
                session: this.currentSession,
                connection: this.nativeMessaging.getConnectionStatus(),
                native: null,
                error: error.message
            };
        }
    }

    /**
     * Update extension badge
     */
    updateBadge(text, color) {
        chrome.action.setBadgeText({ text: text });
        chrome.action.setBadgeBackgroundColor({ color: color });
    }

    /**
     * Broadcast message to all tabs
     */
    async broadcastToTabs(message) {
        try {
            const tabs = await chrome.tabs.query({});
            for (const tab of tabs) {
                chrome.tabs.sendMessage(tab.id, message).catch(() => {
                    // Ignore errors for tabs that don't have content script
                });
            }
        } catch (error) {
            console.error('Failed to broadcast to tabs:', error);
        }
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info') {
        console.log(`[${type.toUpperCase()}] ${message}`);
        // Note: Notifications require permission in manifest
    }

    /**
     * Show welcome notification on first install
     */
    showWelcomeNotification() {
        console.log('MKD Automation installed successfully! Click the extension icon to start recording.');
    }

    /**
     * Check native host availability
     */
    async checkNativeHostAvailability() {
        try {
            await this.nativeMessaging.getStatus();
            console.log('Native host is available');
            this.updateBadge('', '#00AA00');
        } catch (error) {
            console.warn('Native host not available:', error.message);
            this.updateBadge('!', '#FF8800');
        }
    }

    /**
     * Handle tab updates
     */
    handleTabUpdate(tabId, changeInfo, tab) {
        if (this.recordingState.isRecording && changeInfo.status === 'complete') {
            // Notify native host about page navigation
            // This helps with context tracking
            chrome.tabs.sendMessage(tabId, {
                type: 'PAGE_UPDATED',
                url: tab.url,
                title: tab.title
            }).catch(() => {
                // Ignore errors for tabs without content script
            });
        }
    }

    /**
     * Handle tab activation
     */
    handleTabActivated(activeInfo) {
        if (this.recordingState.isRecording) {
            // Notify about tab switch for context
            chrome.tabs.get(activeInfo.tabId, (tab) => {
                chrome.tabs.sendMessage(activeInfo.tabId, {
                    type: 'TAB_ACTIVATED',
                    url: tab.url,
                    title: tab.title
                }).catch(() => {
                    // Ignore errors
                });
            });
        }
    }

    /**
     * Handle extension suspend
     */
    handleSuspend() {
        console.log('Extension suspending...');

        // Clean up native messaging
        this.nativeMessaging.cleanup();

        // If recording is active, try to save state
        if (this.recordingState.isRecording) {
            console.warn('Extension suspending during active recording');
            // In a real implementation, you might want to pause or stop recording
        }
    }
}

// Initialize the background service
const mkdBackgroundService = new MKDBackgroundService();