/**
 * MKD Automation Chrome Extension - Popup Script
 * Controls the extension popup interface
 */

console.log('[MKD Popup] Popup script loaded');

// DOM Elements
let elements = {};
let extensionState = {
    connected: false,
    recording: false,
    playing: false,
    debugMode: true,
    autoRecord: false
};

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', initializePopup);

/**
 * Initialize popup interface
 */
function initializePopup() {
    console.log('[MKD Popup] Initializing popup interface');
    
    // Get DOM elements
    elements = {
        statusDot: document.getElementById('statusDot'),
        statusText: document.getElementById('statusText'),
        hostStatus: document.getElementById('hostStatus'),
        versionInfo: document.getElementById('versionInfo'),
        recordBtn: document.getElementById('recordBtn'),
        stopBtn: document.getElementById('stopBtn'),
        playBtn: document.getElementById('playBtn'),
        pauseBtn: document.getElementById('pauseBtn'),
        debugMode: document.getElementById('debugMode'),
        autoRecord: document.getElementById('autoRecord'),
        errorSection: document.getElementById('errorSection'),
        errorMessage: document.getElementById('errorMessage'),
        openDesktopApp: document.getElementById('openDesktopApp')
    };
    
    // Set up event listeners
    setupEventListeners();
    
    // Load saved settings
    loadSettings();
    
    // Check extension status
    checkExtensionStatus();
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
    // Recording controls
    elements.recordBtn.addEventListener('click', toggleRecording);
    elements.stopBtn.addEventListener('click', stopRecording);
    elements.playBtn.addEventListener('click', startPlayback);
    elements.pauseBtn.addEventListener('click', pausePlayback);
    
    // Settings
    elements.debugMode.addEventListener('change', onDebugModeChange);
    elements.autoRecord.addEventListener('change', onAutoRecordChange);
    
    // Desktop app
    elements.openDesktopApp.addEventListener('click', openDesktopApp);
}

/**
 * Load saved settings from storage
 */
function loadSettings() {
    chrome.storage.local.get([
        'mkd_debug',
        'mkd_auto_record',
        'mkd_recording_state',
        'mkd_playback_state'
    ], (result) => {
        if (chrome.runtime.lastError) {
            console.error('[MKD Popup] Failed to load settings:', chrome.runtime.lastError);
            return;
        }
        
        // Update UI with saved settings
        elements.debugMode.checked = result.mkd_debug ?? true;
        elements.autoRecord.checked = result.mkd_auto_record ?? false;
        
        // Update states
        extensionState.debugMode = elements.debugMode.checked;
        extensionState.autoRecord = elements.autoRecord.checked;
        extensionState.recording = result.mkd_recording_state ?? false;
        extensionState.playing = result.mkd_playback_state ?? false;
        
        updateUI();
    });
}

/**
 * Check extension status
 */
function checkExtensionStatus() {
    // Send message to background script to get status
    chrome.runtime.sendMessage({ type: 'get_status' }, (response) => {
        if (chrome.runtime.lastError) {
            console.error('[MKD Popup] Failed to get status:', chrome.runtime.lastError);
            updateConnectionStatus(false, 'Extension Error');
            showError('Failed to communicate with background script');
            return;
        }
        
        if (response) {
            console.log('[MKD Popup] Extension status:', response);
            extensionState.connected = response.connected;
            
            updateConnectionStatus(
                response.connected,
                response.connected ? 'Connected' : 'Disconnected',
                response.error
            );
            
            if (response.version) {
                elements.versionInfo.textContent = response.version;
            }
        }
    });
}

/**
 * Update connection status display
 */
function updateConnectionStatus(connected, statusText, error = null) {
    extensionState.connected = connected;
    
    // Update status indicator
    elements.statusDot.className = `status-dot ${connected ? 'connected' : 'disconnected'}`;
    elements.statusText.textContent = statusText;
    elements.hostStatus.textContent = connected ? 'Connected' : 'Disconnected';
    
    // Show/hide error
    if (error) {
        showError(error);
    } else {
        hideError();
    }
    
    updateUI();
}

/**
 * Update UI based on current state
 */
function updateUI() {
    // Recording controls
    elements.recordBtn.disabled = !extensionState.connected;
    elements.stopBtn.disabled = !extensionState.recording;
    elements.playBtn.disabled = !extensionState.connected || extensionState.recording;
    elements.pauseBtn.disabled = !extensionState.playing;
    
    // Update recording button text and style
    if (extensionState.recording) {
        elements.recordBtn.querySelector('.btn-text').textContent = 'Recording...';
        elements.recordBtn.classList.add('recording');
        document.body.classList.add('recording');
    } else {
        elements.recordBtn.querySelector('.btn-text').textContent = 'Start Recording';
        elements.recordBtn.classList.remove('recording');
        document.body.classList.remove('recording');
    }
    
    // Update playback button
    if (extensionState.playing) {
        elements.playBtn.querySelector('.btn-text').textContent = 'Playing...';
    } else {
        elements.playBtn.querySelector('.btn-text').textContent = 'Play Recording';
    }
}

/**
 * Toggle recording state
 */
function toggleRecording() {
    if (extensionState.recording) {
        stopRecording();
    } else {
        startRecording();
    }
}

/**
 * Start recording
 */
function startRecording() {
    console.log('[MKD Popup] Starting recording');
    
    // Send message to content script via background
    sendMessageToActiveTab({
        type: 'start_recording'
    }, (response) => {
        if (response && response.success) {
            extensionState.recording = true;
            chrome.storage.local.set({ 'mkd_recording_state': true });
            updateUI();
        } else {
            showError('Failed to start recording: ' + (response?.error || 'Unknown error'));
        }
    });
}

/**
 * Stop recording
 */
function stopRecording() {
    console.log('[MKD Popup] Stopping recording');
    
    sendMessageToActiveTab({
        type: 'stop_recording'
    }, (response) => {
        if (response && response.success) {
            extensionState.recording = false;
            chrome.storage.local.set({ 'mkd_recording_state': false });
            updateUI();
        } else {
            showError('Failed to stop recording: ' + (response?.error || 'Unknown error'));
        }
    });
}

/**
 * Start playback
 */
function startPlayback() {
    console.log('[MKD Popup] Starting playback');
    
    sendMessageToActiveTab({
        type: 'start_playback'
    }, (response) => {
        if (response && response.success) {
            extensionState.playing = true;
            chrome.storage.local.set({ 'mkd_playback_state': true });
            updateUI();
        } else {
            showError('Failed to start playback: ' + (response?.error || 'Unknown error'));
        }
    });
}

/**
 * Pause playback
 */
function pausePlayback() {
    console.log('[MKD Popup] Pausing playback');
    
    sendMessageToActiveTab({
        type: 'pause_playback'
    }, (response) => {
        if (response && response.success) {
            extensionState.playing = false;
            chrome.storage.local.set({ 'mkd_playback_state': false });
            updateUI();
        } else {
            showError('Failed to pause playback: ' + (response?.error || 'Unknown error'));
        }
    });
}

/**
 * Handle debug mode change
 */
function onDebugModeChange() {
    extensionState.debugMode = elements.debugMode.checked;
    chrome.storage.local.set({ 'mkd_debug': extensionState.debugMode });
    
    console.log('[MKD Popup] Debug mode:', extensionState.debugMode ? 'enabled' : 'disabled');
}

/**
 * Handle auto record change
 */
function onAutoRecordChange() {
    extensionState.autoRecord = elements.autoRecord.checked;
    chrome.storage.local.set({ 'mkd_auto_record': extensionState.autoRecord });
    
    console.log('[MKD Popup] Auto record:', extensionState.autoRecord ? 'enabled' : 'disabled');
}

/**
 * Open desktop application
 */
function openDesktopApp() {
    console.log('[MKD Popup] Opening desktop application');
    
    // Send message to background to request desktop app launch
    chrome.runtime.sendMessage({
        type: 'open_desktop_app'
    }, (response) => {
        if (response && response.success) {
            window.close(); // Close popup
        } else {
            showError('Failed to open desktop application: ' + (response?.error || 'Unknown error'));
        }
    });
}

/**
 * Send message to active tab
 */
function sendMessageToActiveTab(message, callback) {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (chrome.runtime.lastError) {
            console.error('[MKD Popup] Failed to query tabs:', chrome.runtime.lastError);
            if (callback) callback({ success: false, error: chrome.runtime.lastError.message });
            return;
        }
        
        if (tabs.length === 0) {
            console.error('[MKD Popup] No active tab found');
            if (callback) callback({ success: false, error: 'No active tab found' });
            return;
        }
        
        chrome.tabs.sendMessage(tabs[0].id, message, (response) => {
            if (chrome.runtime.lastError) {
                console.error('[MKD Popup] Failed to send message to tab:', chrome.runtime.lastError);
                if (callback) callback({ success: false, error: chrome.runtime.lastError.message });
            } else {
                if (callback) callback(response);
            }
        });
    });
}

/**
 * Show error message
 */
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorSection.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(hideError, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    elements.errorSection.style.display = 'none';
    elements.errorMessage.textContent = '';
}

/**
 * Handle messages from background script
 */
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[MKD Popup] Message from background:', message);
    
    switch (message.type) {
        case 'recording_status_changed':
            extensionState.recording = message.data.recording;
            chrome.storage.local.set({ 'mkd_recording_state': extensionState.recording });
            updateUI();
            break;
            
        case 'playback_status_changed':
            extensionState.playing = message.data.playing;
            chrome.storage.local.set({ 'mkd_playback_state': extensionState.playing });
            updateUI();
            break;
            
        case 'connection_status_changed':
            updateConnectionStatus(
                message.data.connected,
                message.data.connected ? 'Connected' : 'Disconnected',
                message.data.error
            );
            break;
            
        default:
            console.log('[MKD Popup] Unknown message type:', message.type);
    }
});

// Refresh status periodically
setInterval(checkExtensionStatus, 5000);

console.log('[MKD Popup] Popup script initialization complete');