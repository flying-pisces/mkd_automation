/**
 * MKD Automation Chrome Extension - Background Script
 * Service worker for handling native messaging and extension lifecycle
 */

console.log('[MKD] Background script loaded');

// Configuration
const CONFIG = {
    NATIVE_HOST_NAME: 'com.mkd.automation.host',
    VERSION: '2.0.0',
    DEBUG: true
};

// Connection state
let nativePort = null;
let connectionState = 'disconnected';
let lastError = null;

/**
 * Initialize extension on startup
 */
chrome.runtime.onStartup.addListener(() => {
    console.log('[MKD] Extension startup');
    initializeExtension();
});

chrome.runtime.onInstalled.addListener((details) => {
    console.log('[MKD] Extension installed/updated:', details.reason);
    initializeExtension();
});

/**
 * Initialize extension components
 */
function initializeExtension() {
    console.log('[MKD] Initializing extension...');
    
    // Set default storage values
    chrome.storage.local.set({
        'mkd_enabled': true,
        'mkd_debug': CONFIG.DEBUG,
        'mkd_version': CONFIG.VERSION,
        'mkd_install_time': Date.now()
    });
    
    // Attempt to connect to native host
    connectToNativeHost();
}

/**
 * Connect to native messaging host
 */
function connectToNativeHost() {
    try {
        console.log('[MKD] Attempting to connect to native host:', CONFIG.NATIVE_HOST_NAME);
        
        nativePort = chrome.runtime.connectNative(CONFIG.NATIVE_HOST_NAME);
        
        if (nativePort) {
            connectionState = 'connected';
            console.log('[MKD] Native host connected successfully');
            
            // Set up message handlers
            nativePort.onMessage.addListener(handleNativeMessage);
            nativePort.onDisconnect.addListener(handleNativeDisconnect);
            
            // Send handshake
            sendToNativeHost({
                type: 'handshake',
                version: CONFIG.VERSION,
                timestamp: Date.now()
            });
        }
        
    } catch (error) {
        console.error('[MKD] Failed to connect to native host:', error);
        connectionState = 'error';
        lastError = error.message;
        
        // Retry connection after delay
        setTimeout(connectToNativeHost, 5000);
    }
}

/**
 * Handle messages from native host
 */
function handleNativeMessage(message) {
    console.log('[MKD] Message from native host:', message);
    
    try {
        switch (message.type) {
            case 'handshake_response':
                console.log('[MKD] Handshake successful with native host');
                break;
                
            case 'recording_status':
                // Forward to content scripts
                broadcastToTabs({
                    type: 'recording_status',
                    data: message.data
                });
                break;
                
            case 'playback_command':
                // Handle playback command
                handlePlaybackCommand(message.data);
                break;
                
            default:
                console.log('[MKD] Unknown message type from native host:', message.type);
        }
    } catch (error) {
        console.error('[MKD] Error handling native message:', error);
    }
}

/**
 * Handle native host disconnect
 */
function handleNativeDisconnect() {
    console.log('[MKD] Native host disconnected');
    connectionState = 'disconnected';
    nativePort = null;
    
    if (chrome.runtime.lastError) {
        console.error('[MKD] Native host disconnect error:', chrome.runtime.lastError.message);
        lastError = chrome.runtime.lastError.message;
    }
    
    // Attempt to reconnect after delay
    setTimeout(connectToNativeHost, 3000);
}

/**
 * Send message to native host
 */
function sendToNativeHost(message) {
    if (nativePort && connectionState === 'connected') {
        try {
            console.log('[MKD] Sending to native host:', message);
            nativePort.postMessage(message);
            return true;
        } catch (error) {
            console.error('[MKD] Failed to send message to native host:', error);
            connectionState = 'error';
            return false;
        }
    } else {
        console.warn('[MKD] Cannot send message - native host not connected');
        return false;
    }
}

/**
 * Broadcast message to all tabs
 */
function broadcastToTabs(message) {
    chrome.tabs.query({}, (tabs) => {
        tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, message).catch(error => {
                // Ignore errors for tabs that don't have content script
                if (CONFIG.DEBUG) {
                    console.log('[MKD] Could not send message to tab:', tab.id, error.message);
                }
            });
        });
    });
}

/**
 * Handle playback commands
 */
function handlePlaybackCommand(commandData) {
    console.log('[MKD] Handling playback command:', commandData);
    
    // Forward to appropriate tab
    if (commandData.tabId) {
        chrome.tabs.sendMessage(commandData.tabId, {
            type: 'execute_action',
            data: commandData
        }).catch(error => {
            console.error('[MKD] Failed to send playback command to tab:', error);
        });
    }
}

/**
 * Handle messages from content scripts
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[MKD] Message from content script:', message, 'from tab:', sender.tab?.id);
    
    try {
        switch (message.type) {
            case 'user_action':
                // Forward user action to native host
                if (sendToNativeHost({
                    type: 'user_action',
                    data: {
                        ...message.data,
                        tabId: sender.tab?.id,
                        url: sender.tab?.url,
                        timestamp: Date.now()
                    }
                })) {
                    sendResponse({ success: true });
                } else {
                    sendResponse({ 
                        success: false, 
                        error: 'Native host not connected' 
                    });
                }
                break;
                
            case 'get_status':
                // Return extension status
                sendResponse({
                    connected: connectionState === 'connected',
                    state: connectionState,
                    version: CONFIG.VERSION,
                    error: lastError
                });
                break;
                
            case 'ping':
                // Health check
                sendResponse({ pong: true, timestamp: Date.now() });
                break;
                
            default:
                console.log('[MKD] Unknown message type from content script:', message.type);
                sendResponse({ success: false, error: 'Unknown message type' });
        }
    } catch (error) {
        console.error('[MKD] Error handling content script message:', error);
        sendResponse({ success: false, error: error.message });
    }
    
    return true; // Keep message channel open for async response
});

/**
 * Handle extension icon click
 */
chrome.action.onClicked.addListener((tab) => {
    console.log('[MKD] Extension icon clicked on tab:', tab.id);
    
    // Toggle recording state or open popup
    chrome.tabs.sendMessage(tab.id, {
        type: 'toggle_recording'
    }).catch(error => {
        console.log('[MKD] Could not send toggle message to tab:', error.message);
    });
});

/**
 * Handle tab updates
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        console.log('[MKD] Tab updated:', tabId, tab.url);
        
        // Notify native host of page change
        sendToNativeHost({
            type: 'tab_updated',
            data: {
                tabId: tabId,
                url: tab.url,
                title: tab.title,
                timestamp: Date.now()
            }
        });
    }
});

/**
 * Cleanup on extension shutdown
 */
chrome.runtime.onSuspend.addListener(() => {
    console.log('[MKD] Extension suspending - cleaning up');
    
    if (nativePort) {
        try {
            sendToNativeHost({
                type: 'disconnect',
                timestamp: Date.now()
            });
            nativePort.disconnect();
        } catch (error) {
            console.error('[MKD] Error during cleanup:', error);
        }
    }
});

// Export for testing (if in test environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        CONFIG,
        connectToNativeHost,
        sendToNativeHost,
        handleNativeMessage,
        broadcastToTabs
    };
}

console.log('[MKD] Background script initialization complete');