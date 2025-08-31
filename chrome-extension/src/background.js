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

/**
 * Input validation and sanitization utilities
 */
class SecurityUtils {
    /**
     * Validate and sanitize string input
     */
    static validateString(input, maxLength = 1000) {
        if (typeof input !== 'string') {
            throw new Error('Input must be a string');
        }
        
        if (input.length > maxLength) {
            throw new Error(`Input exceeds maximum length of ${maxLength}`);
        }
        
        // Remove dangerous characters and HTML
        return input.replace(/<[^>]*>/g, '').replace(/[<>'"&]/g, '');
    }
    
    /**
     * Validate message type
     */
    static validateMessageType(type) {
        const validTypes = [
            'START_RECORDING', 'STOP_RECORDING', 'PAUSE_RECORDING', 
            'RESUME_RECORDING', 'GET_STATUS', 'GET_RECENT_RECORDINGS',
            'START_PLAYBACK'
        ];
        
        if (!validTypes.includes(type)) {
            throw new Error(`Invalid message type: ${type}`);
        }
        
        return type;
    }
    
    /**
     * Validate recording configuration
     */
    static validateRecordingConfig(config) {
        if (!config || typeof config !== 'object') {
            throw new Error('Invalid recording configuration');
        }
        
        const validatedConfig = {
            captureVideo: Boolean(config.captureVideo),
            captureAudio: Boolean(config.captureAudio),
            showBorder: Boolean(config.showBorder),
            keyboardCapture: Boolean(config.keyboardCapture)
        };
        
        // Validate color value
        if (config.borderColor) {
            const colorRegex = /^#[0-9A-Fa-f]{6}$/;
            if (!colorRegex.test(config.borderColor)) {
                throw new Error('Invalid border color format');
            }
            validatedConfig.borderColor = config.borderColor;
        }
        
        // Validate mouse sample rate
        if (config.mouseSampleRate !== undefined) {
            const rate = parseInt(config.mouseSampleRate);
            if (isNaN(rate) || rate < 1 || rate > 1000) {
                throw new Error('Invalid mouse sample rate');
            }
            validatedConfig.mouseSampleRate = rate;
        }
        
        return validatedConfig;
    }
    
    /**
     * Validate recording ID
     */
    static validateRecordingId(id) {
        if (typeof id !== 'string' || id.length === 0) {
            throw new Error('Invalid recording ID');
        }
        
        // Allow only alphanumeric, underscore, hyphen
        if (!/^[a-zA-Z0-9_-]+$/.test(id)) {
            throw new Error('Recording ID contains invalid characters');
        }
        
        return id;
    }
}

class NativeMessagingHandler {
    constructor() {
        this.nativeHostName = 'com.mkd.automation';
        this.messageId = 0;
        this.pendingMessages = new Map();
        this.connectionTimeout = 30000; // 30 seconds
        this.isConnected = false;
        this.lastError = null;
        
        // Initialize connection monitoring
        this.initializeConnectionMonitoring();
    }
    
    /**
     * Initialize connection monitoring and health checks
     */
    initializeConnectionMonitoring() {
        // Connection retry configuration
        this.maxRetries = 3;
        this.retryDelay = 2000; // 2 seconds
        this.backoffMultiplier = 2;
        
        // Health check configuration
        this.healthCheckInterval = 30000; // 30 seconds
        this.healthCheckTimeout = 5000; // 5 seconds
        
        // Start health checking
        this.startHealthChecking();
        
        // Initialize fallback state
        this.fallbackMode = false;
        this.fallbackReason = null;
    }
    
    /**
     * Start periodic health checking
     */
    startHealthChecking() {
        if (this.healthCheckTimer) {
            clearInterval(this.healthCheckTimer);
        }
        
        this.healthCheckTimer = setInterval(() => {
            this.performHealthCheck();
        }, this.healthCheckInterval);
    }
    
    /**
     * Perform comprehensive health check
     */
    async performHealthCheck() {
        try {
            const startTime = Date.now();
            
            // Send ping with timeout
            const pingPromise = this.sendMessage('PING');
            const timeoutPromise = new Promise((_, reject) => {
                setTimeout(() => reject(new Error('Health check timeout')), this.healthCheckTimeout);
            });
            
            await Promise.race([pingPromise, timeoutPromise]);
            
            const responseTime = Date.now() - startTime;
            
            // Update connection status
            this.isConnected = true;
            this.lastError = null;
            this.exitFallbackMode();
            
            // console.log(`Health check successful (${responseTime}ms)`);  // Commented for production
            
        } catch (error) {
            console.error('Health check failed:', error);
            this.handleConnectionFailure(error);
        }
    }
    
    /**
     * Handle connection failure with retry logic
     */
    async handleConnectionFailure(error) {
        this.isConnected = false;
        this.lastError = error.message;
        
        console.warn(`Connection failure: ${error.message}`);
        
        // Try to recover connection
        for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
            // console.log(`Connection recovery attempt ${attempt}/${this.maxRetries}`);  // Commented for production
            
            await this.sleep(this.retryDelay * Math.pow(this.backoffMultiplier, attempt - 1));
            
            try {
                await this.sendMessage('PING');
                // console.log('Connection recovery successful');  // Commented for production
                this.isConnected = true;
                this.lastError = null;
                this.exitFallbackMode();
                return;
            } catch (retryError) {
                console.warn(`Recovery attempt ${attempt} failed:`, retryError.message);
            }
        }
        
        // All retry attempts failed, enter fallback mode
        this.enterFallbackMode(error.message);
    }
    
    /**
     * Enter fallback mode when native host is unavailable
     */
    enterFallbackMode(reason) {
        if (this.fallbackMode) {
            return; // Already in fallback mode
        }
        
        this.fallbackMode = true;
        this.fallbackReason = reason;
        this.isConnected = false;
        
        console.warn('Entering fallback mode:', reason);
        
        // Notify all components about fallback mode
        this.notifyFallbackMode(true, reason);
    }
    
    /**
     * Exit fallback mode when connection is restored
     */
    exitFallbackMode() {
        if (!this.fallbackMode) {
            return; // Not in fallback mode
        }
        
        this.fallbackMode = false;
        this.fallbackReason = null;
        
        // console.log('Exiting fallback mode - connection restored');  // Commented for production
        
        // Notify all components about restored connection
        this.notifyFallbackMode(false, null);
    }
    
    /**
     * Notify components about fallback mode changes
     */
    notifyFallbackMode(inFallback, reason) {
        // Broadcast to all extension components
        chrome.runtime.sendMessage({
            type: 'FALLBACK_MODE_CHANGE',
            fallbackMode: inFallback,
            reason: reason
        }).catch(() => {
            // Ignore if no listeners
        });
        
        // Update badge to indicate fallback mode
        if (inFallback) {
            chrome.action.setBadgeText({ text: '!' });
            chrome.action.setBadgeBackgroundColor({ color: '#FF8800' });
        } else {
            chrome.action.setBadgeText({ text: '' });
        }
    }
    
    /**
     * Sleep utility for retry delays
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    /**
     * Generate unique message ID
     */
    generateMessageId() {
        return `msg_${Date.now()}_${++this.messageId}`;
    }
    
    /**
     * Send message to native host
     * @param {string} command - Command to execute
     * @param {Object} params - Command parameters
     * @returns {Promise<Object>} Response from native host
     */
    async sendMessage(command, params = {}) {
        return new Promise((resolve, reject) => {
            try {
                // Validate command
                if (typeof command !== 'string' || command.length === 0) {
                    throw new Error('Invalid command format');
                }
                
                // Validate command type
                const validatedCommand = SecurityUtils.validateMessageType(command);
                
                // Validate params object
                if (params && typeof params !== 'object') {
                    throw new Error('Parameters must be an object');
                }
                
                // Validate specific parameter types based on command
                let validatedParams = {};
                if (params) {
                    switch (validatedCommand) {
                        case 'START_RECORDING':
                            validatedParams = params.config ? 
                                SecurityUtils.validateRecordingConfig(params.config) : {};
                            break;
                        case 'START_PLAYBACK':
                            if (params.recordingId) {
                                validatedParams.recordingId = SecurityUtils.validateRecordingId(params.recordingId);
                            }
                            break;
                        case 'STOP_RECORDING':
                        case 'PAUSE_RECORDING':
                        case 'RESUME_RECORDING':
                            if (params.sessionId) {
                                validatedParams.sessionId = SecurityUtils.validateString(params.sessionId, 100);
                            }
                            break;
                        default:
                            // For other commands, sanitize any string values
                            for (const [key, value] of Object.entries(params)) {
                                if (typeof value === 'string') {
                                    validatedParams[key] = SecurityUtils.validateString(value, 500);
                                } else if (typeof value === 'number' && Number.isFinite(value)) {
                                    validatedParams[key] = value;
                                } else if (typeof value === 'boolean') {
                                    validatedParams[key] = value;
                                }
                            }
                    }
                }
                
                const messageId = this.generateMessageId();
                const message = {
                    id: messageId,
                    command: validatedCommand,
                    params: validatedParams,
                    timestamp: Date.now()
                };
                
                // Set up timeout
                const timeoutId = setTimeout(() => {
                    this.pendingMessages.delete(messageId);
                    reject(new Error(`Message timeout after ${this.connectionTimeout}ms`));
                }, this.connectionTimeout);
                
                // Store pending message
                this.pendingMessages.set(messageId, {
                    resolve,
                    reject,
                    timeoutId,
                    timestamp: Date.now()
                });
                
                // Send message to native host
                chrome.runtime.sendNativeMessage(
                    this.nativeHostName,
                    message,
                    (response) => {
                        this.handleNativeResponse(messageId, response);
                    }
                );
                
            } catch (error) {
                const messageId = this.generateMessageId();
                this.handleMessageError(messageId, error);
            }
        });
    }
    
    /**
     * Handle response from native host
     * @param {string} messageId - Message ID
     * @param {Object} response - Response from native host
     */
    handleNativeResponse(messageId, response) {
        const pendingMessage = this.pendingMessages.get(messageId);
        if (!pendingMessage) {
            console.warn('Received response for unknown message:', messageId);
            return;
        }
        
        // Clear timeout
        clearTimeout(pendingMessage.timeoutId);
        this.pendingMessages.delete(messageId);
        
        // Check for Chrome runtime error
        if (chrome.runtime.lastError) {
            this.lastError = chrome.runtime.lastError.message;
            this.isConnected = false;
            pendingMessage.reject(new Error(chrome.runtime.lastError.message));
            return;
        }
        
        // Check if response is valid
        if (!response) {
            this.isConnected = false;
            pendingMessage.reject(new Error('No response received from native host'));
            return;
        }
        
        // Update connection status
        this.isConnected = true;
        this.lastError = null;
        
        // Handle response based on status
        if (response.status === 'SUCCESS') {
            pendingMessage.resolve(response.data);
        } else if (response.status === 'ERROR') {
            pendingMessage.reject(new Error(response.error || 'Unknown error'));
        } else {
            pendingMessage.reject(new Error(`Invalid response status: ${response.status}`));
        }
    }
    
    /**
     * Handle message sending error
     * @param {string} messageId - Message ID
     * @param {Error} error - Error object
     */
    handleMessageError(messageId, error) {
        const pendingMessage = this.pendingMessages.get(messageId);
        if (!pendingMessage) {
            return;
        }
        
        clearTimeout(pendingMessage.timeoutId);
        this.pendingMessages.delete(messageId);
        
        this.isConnected = false;
        this.lastError = error.message;
        
        pendingMessage.reject(error);
    }
    
    /**
     * Enhanced sendMessage with fallback support
     */
    async sendMessageWithFallback(command, params = {}) {
        // If in fallback mode, provide fallback responses for certain commands
        if (this.fallbackMode) {
            return this.handleFallbackCommand(command, params);
        }
        
        try {
            return await this.sendMessage(command, params);
        } catch (error) {
            console.warn(`Command ${command} failed, checking fallback options:`, error.message);
            
            // Handle specific command failures
            this.handleConnectionFailure(error);
            
            // Try to provide fallback response
            return this.handleFallbackCommand(command, params);
        }
    }
    
    /**
     * Handle commands in fallback mode
     */
    handleFallbackCommand(command, params) {
        switch (command) {
            case 'GET_STATUS':
                return {
                    recording: {
                        isRecording: false,
                        isPaused: false,
                        sessionId: null,
                        startTime: null
                    },
                    connection: {
                        isConnected: false,
                        lastError: this.fallbackReason,
                        fallbackMode: true
                    },
                    error: 'Python backend not available'
                };
                
            case 'GET_CONNECTION_STATUS':
                return {
                    isConnected: false,
                    lastError: this.fallbackReason,
                    pendingMessages: this.pendingMessages.size,
                    fallbackMode: true,
                    hostVersion: 'Unknown'
                };
                
            case 'START_RECORDING':
                throw new Error('Cannot start recording: Python backend not available. Please install and start the MKD Automation desktop application.');
                
            case 'STOP_RECORDING':
            case 'PAUSE_RECORDING':
            case 'RESUME_RECORDING':
                throw new Error('Cannot control recording: Python backend not available.');
                
            case 'PING':
                throw new Error('Python backend not available');
                
            default:
                throw new Error(`Command ${command} not available in fallback mode`);
        }
    }

    async startRecording(config = {}) {
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

    async startPlayback(recordingId) {
        // console.log(`Starting playback for recording ID: ${recordingId}`);  // Commented for production
        // This is a placeholder for the actual implementation
        return this.sendMessage('START_PLAYBACK', { recordingId });
    }

    async getRecentRecordings() {
        // This is a placeholder for the actual implementation
        return Promise.resolve([
            { id: 'rec-1', name: 'Login Flow', date: '2025-08-28' },
            { id: 'rec-2', name: 'Signup Form', date: '2025-08-27' },
            { id: 'rec-3', name: 'Checkout Process', date: '2025-08-26' },
        ]);
    }
    
    async getStatus() {
        return this.sendMessage('GET_STATUS', {});
    }
    
    /**
     * Get connection status
     * @returns {Object} Connection information
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            lastError: this.lastError,
            pendingMessages: this.pendingMessages.size
        };
    }
    
    /**
     * Clean up pending messages (for shutdown)
     */
    cleanup() {
        // Reject all pending messages
        for (const [messageId, pendingMessage] of this.pendingMessages) {
            clearTimeout(pendingMessage.timeoutId);
            pendingMessage.reject(new Error('Extension shutting down'));
        }
        this.pendingMessages.clear();
        
        this.isConnected = false;
    }
}

class MKDBackgroundService {
    constructor() {
        this.nativeMessaging = new NativeMessagingHandler();
        this.currentSession = null;
        this.recordingState = {
            isRecording: false,
            isPaused: false,
            sessionId: null,
            startTime: null
        };
        
        this.initializeEventListeners();
        this.initializeKeyboardShortcuts();
        
        // console.log('MKD Automation background service initialized');  // Commented for production
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
        // console.log('MKD Automation installed:', details);  // Commented for production
        
        // Set initial badge
        this.updateBadge('', '#808080');
        
        // Check native host availability
        this.checkNativeHostAvailability();
        
        if (details.reason === 'install') {
            // First time installation
            this.showWelcomeNotification();
        } else if (details.reason === 'update') {
            // Extension update
            // console.log(`Updated from ${details.previousVersion} to ${chrome.runtime.getManifest().version}`);  // Commented for production
        }
    }
    
    /**
     * Handle messages from other parts of the extension
     */
    async handleMessage(message, sender, sendResponse) {
        // console.log('Background received message:', message.type);  // Commented for production
        
        try {
            // Validate message structure
            if (!message || typeof message !== 'object') {
                throw new Error('Invalid message format');
            }
            
            if (!message.type || typeof message.type !== 'string') {
                throw new Error('Message type is required');
            }
            
            // Validate message type
            const messageType = SecurityUtils.validateMessageType(message.type);
            
            switch (messageType) {
                case 'START_RECORDING':
                    // Validate recording config if provided
                    let validatedConfig = {};
                    if (message.config) {
                        validatedConfig = SecurityUtils.validateRecordingConfig(message.config);
                    }
                    const startResult = await this.startRecording(validatedConfig);
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

                case 'START_PLAYBACK':
                    // Validate recording ID
                    if (!message.recordingId) {
                        throw new Error('Recording ID is required for playback');
                    }
                    const validatedRecordingId = SecurityUtils.validateRecordingId(message.recordingId);
                    const playbackResult = await this.startPlayback(validatedRecordingId);
                    sendResponse({ success: true, data: playbackResult });
                    break;

                case 'GET_RECENT_RECORDINGS':
                    const recordings = await this.nativeMessaging.getRecentRecordings();
                    sendResponse({ success: true, data: recordings });
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
                    console.warn('Unknown message type:', messageType);
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
        // console.log('Keyboard command:', command);  // Commented for production
        
        switch (command) {
            case 'stop_recording':
                if (this.recordingState.isRecording) {
                    try {
                        await this.stopRecording();
                        this.showNotification('Recording stopped via keyboard shortcut');
                    } catch (error) {
                        console.error('Failed to stop recording via shortcut:', error);
                        this.showNotification('Failed to stop recording', 'error');
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
            
            // console.log('Recording started:', result.sessionId);  // Commented for production
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
            
            // console.log('Recording stopped:', result);  // Commented for production
            return result;
            
        } catch (error) {
            console.error('Failed to stop recording:', error);
            this.updateBadge('ERR', '#FF8800');
            throw error;
        }
    }

    /**
     * Start playback
     */
    async startPlayback(recordingId) {
        try {
            const result = await this.nativeMessaging.startPlayback(recordingId);
            this.updateBadge('PLAY', '#3498db');
            return result;
        } catch (error) {
            console.error('Failed to start playback:', error);
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
        // console.log(`[${type.toUpperCase()}] ${message}`);  // Commented for production
        // Note: Notifications require permission in manifest
    }
    
    /**
     * Show welcome notification on first install
     */
    showWelcomeNotification() {
        // console.log('MKD Automation installed successfully! Click the extension icon to start recording.');  // Commented for production
    }
    
    /**
     * Check native host availability
     */
    async checkNativeHostAvailability() {
        try {
            await this.nativeMessaging.getStatus();
            // console.log('Native host is available');  // Commented for production
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
        // console.log('Extension suspending...');  // Commented for production
        
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
