/**
 * Native Messaging Handler for MKD Automation Chrome Extension
 * 
 * Handles communication between Chrome extension and native host application.
 * Provides command routing, error handling, and connection management.
 */

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
        // Check connection health every 30 seconds
        setInterval(() => {
            this.checkConnectionHealth();
        }, 30000);
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
            const messageId = this.generateMessageId();
            const message = {
                id: messageId,
                command: command,
                params: params,
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
            
            try {
                // Send message to native host
                chrome.runtime.sendNativeMessage(
                    this.nativeHostName,
                    message,
                    (response) => {
                        this.handleNativeResponse(messageId, response);
                    }
                );
            } catch (error) {
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
            pendingMessage.resolve(response);
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
     * Check connection health with native host
     */
    async checkConnectionHealth() {
        try {
            await this.sendMessage('GET_STATUS', {});
            console.log('Native host connection healthy');
        } catch (error) {
            console.error('Native host connection health check failed:', error);
            this.isConnected = false;
            this.lastError = error.message;
        }
    }
    
    /**
     * Start recording
     * @param {Object} config - Recording configuration
     * @returns {Promise<Object>} Recording session info
     */
    async startRecording(config = {}) {
        const defaultConfig = {
            captureVideo: true,
            captureAudio: false,
            showBorder: true,
            borderColor: '#FF0000',
            mouseSampleRate: 60,
            keyboardCapture: true
        };
        
        const recordingConfig = { ...defaultConfig, ...config };
        
        try {
            const response = await this.sendMessage('START_RECORDING', recordingConfig);
            
            // Notify other parts of extension
            chrome.runtime.sendMessage({
                type: 'RECORDING_STARTED',
                data: response.data
            });
            
            return response.data;
        } catch (error) {
            console.error('Failed to start recording:', error);
            throw error;
        }
    }
    
    /**
     * Stop recording
     * @param {string} sessionId - Recording session ID
     * @returns {Promise<Object>} Recording results
     */
    async stopRecording(sessionId) {
        try {
            const response = await this.sendMessage('STOP_RECORDING', {
                sessionId: sessionId
            });
            
            // Notify other parts of extension
            chrome.runtime.sendMessage({
                type: 'RECORDING_STOPPED',
                data: response.data
            });
            
            return response.data;
        } catch (error) {
            console.error('Failed to stop recording:', error);
            throw error;
        }
    }
    
    /**
     * Pause recording
     * @param {string} sessionId - Recording session ID
     * @returns {Promise<Object>} Response
     */
    async pauseRecording(sessionId) {
        try {
            const response = await this.sendMessage('PAUSE_RECORDING', {
                sessionId: sessionId
            });
            
            chrome.runtime.sendMessage({
                type: 'RECORDING_PAUSED',
                data: response.data
            });
            
            return response.data;
        } catch (error) {
            console.error('Failed to pause recording:', error);
            throw error;
        }
    }
    
    /**
     * Resume recording
     * @param {string} sessionId - Recording session ID
     * @returns {Promise<Object>} Response
     */
    async resumeRecording(sessionId) {
        try {
            const response = await this.sendMessage('RESUME_RECORDING', {
                sessionId: sessionId
            });
            
            chrome.runtime.sendMessage({
                type: 'RECORDING_RESUMED',
                data: response.data
            });
            
            return response.data;
        } catch (error) {
            console.error('Failed to resume recording:', error);
            throw error;
        }
    }
    
    /**
     * Get recording status
     * @returns {Promise<Object>} Current status
     */
    async getStatus() {
        try {
            const response = await this.sendMessage('GET_STATUS', {});
            return response.data;
        } catch (error) {
            console.error('Failed to get status:', error);
            throw error;
        }
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

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NativeMessagingHandler;
} else {
    // Browser environment
    window.NativeMessagingHandler = NativeMessagingHandler;
}