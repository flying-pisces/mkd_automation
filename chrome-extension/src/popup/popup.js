/**
 * Popup UI Controller for MKD Automation Chrome Extension
 * 
 * Handles all popup UI interactions and state management.
 */

class MKDPopupController {
    constructor() {
        this.isRecording = false;
        this.isPaused = false;
        this.sessionId = null;
        this.startTime = null;
        this.timerInterval = null;
        this.settingsVisible = false;
        
        this.initializeElements();
        this.initializeEventListeners();
        this.loadSettings();
        this.updateStatus();
        this.loadRecentRecordings();
        
        console.log('MKD Popup Controller initialized');
    }
    
    /**
     * Initialize DOM element references
     */
    initializeElements() {
        // Status elements
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.connectionText = document.getElementById('connectionText');
        
        // Control elements
        this.startStopButton = document.getElementById('startStopButton');
        this.startPlaybackButton = document.getElementById('startPlaybackButton');
        this.buttonIcon = document.getElementById('buttonIcon');
        this.buttonText = document.getElementById('buttonText');
        this.secondaryControls = document.getElementById('secondaryControls');
        this.pauseResumeButton = document.getElementById('pauseResumeButton');
        
        // Info elements
        this.infoSection = document.getElementById('infoSection');
        this.durationText = document.getElementById('durationText');
        this.sessionIdText = document.getElementById('sessionIdText');
        this.eventsCountText = document.getElementById('eventsCountText');
        
        // Recent Recordings
        this.recentRecordingsList = document.getElementById('recentRecordingsList');

        // Settings elements
        this.settingsToggle = document.getElementById('settingsToggle');
        this.settingsPanel = document.getElementById('settingsPanel');
        this.captureVideo = document.getElementById('captureVideo');
        this.captureAudio = document.getElementById('captureAudio');
        this.showBorder = document.getElementById('showBorder');
        this.borderColor = document.getElementById('borderColor');
        this.mouseSampleRate = document.getElementById('mouseSampleRate');
        this.keyboardCapture = document.getElementById('keyboardCapture');
        
        // Error elements
        this.errorSection = document.getElementById('errorSection');
        this.errorMessage = document.getElementById('errorMessage');
        this.errorDismiss = document.getElementById('errorDismiss');
    }
    
    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Main control button
        this.startStopButton.addEventListener('click', () => {
            this.handleStartStopClick();
        });

        // Playback button
        this.startPlaybackButton.addEventListener('click', () => {
            this.handleStartPlaybackClick();
        });
        
        // Pause/Resume button
        this.pauseResumeButton.addEventListener('click', () => {
            this.handlePauseResumeClick();
        });
        
        // Settings toggle
        this.settingsToggle.addEventListener('click', () => {
            this.toggleSettings();
        });
        
        // Settings change handlers
        this.captureVideo.addEventListener('change', () => this.saveSettings());
        this.captureAudio.addEventListener('change', () => this.saveSettings());
        this.showBorder.addEventListener('change', () => this.saveSettings());
        this.borderColor.addEventListener('change', () => this.saveSettings());
        this.mouseSampleRate.addEventListener('change', () => this.saveSettings());
        this.keyboardCapture.addEventListener('change', () => this.saveSettings());
        
        // Error dismiss
        this.errorDismiss.addEventListener('click', () => {
            this.hideError();
        });
        
        // Listen for messages from background script
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleBackgroundMessage(message);
        });
        
        // Update status periodically
        setInterval(() => {
            this.updateStatus();
        }, 5000);
    }
    
    /**
     * Handle start/stop button click
     */
    async handleStartStopClick() {
        this.startStopButton.disabled = true;
        
        try {
            if (this.isRecording) {
                await this.stopRecording();
            } else {
                await this.startRecording();
            }
        } catch (error) {
            console.error('Start/Stop action failed:', error);
            this.showError(`Failed to ${this.isRecording ? 'stop' : 'start'} recording: ${error.message}`);
        } finally {
            this.startStopButton.disabled = false;
        }
    }

    /**
     * Handle start playback button click
     */
    async handleStartPlaybackClick() {
        this.startPlaybackButton.disabled = true;
        try {
            const selectedRecording = this.recentRecordingsList.querySelector('input[name="recording"]:checked');
            if (!selectedRecording) {
                this.showError('Please select a recording to play.');
                return;
            }

            const recordingId = selectedRecording.value;
            console.log(`Start Playback clicked for recording: ${recordingId}`);

            const response = await this.sendMessageToBackground({
                type: 'START_PLAYBACK',
                recordingId: recordingId,
            });

            if (!response.success) {
                throw new Error(response.error);
            }

        } catch (error) {
            console.error('Start Playback action failed:', error);
            this.showError(`Failed to start playback: ${error.message}`);
        } finally {
            this.startPlaybackButton.disabled = false;
        }
    }
    
    /**
     * Handle pause/resume button click
     */
    async handlePauseResumeClick() {
        this.pauseResumeButton.disabled = true;
        
        try {
            if (this.isPaused) {
                await this.resumeRecording();
            } else {
                await this.pauseRecording();
            }
        } catch (error) {
            console.error('Pause/Resume action failed:', error);
            this.showError(`Failed to ${this.isPaused ? 'resume' : 'pause'} recording: ${error.message}`);
        } finally {
            this.pauseResumeButton.disabled = false;
        }
    }
    
    /**
     * Start recording
     */
    async startRecording() {
        const config = this.getRecordingConfig();
        
        const response = await this.sendMessageToBackground({
            type: 'START_RECORDING',
            config: config
        });
        
        if (response.success) {
            this.handleRecordingStarted(response.data);
        } else {
            throw new Error(response.error);
        }
    }
    
    /**
     * Stop recording
     */
    async stopRecording() {
        const response = await this.sendMessageToBackground({
            type: 'STOP_RECORDING'
        });
        
        if (response.success) {
            this.handleRecordingStopped(response.data);
        } else {
            throw new Error(response.error);
        }
    }
    
    /**
     * Pause recording
     */
    async pauseRecording() {
        const response = await this.sendMessageToBackground({
            type: 'PAUSE_RECORDING'
        });
        
        if (response.success) {
            this.handleRecordingPaused();
        } else {
            throw new Error(response.error);
        }
    }
    
    /**
     * Resume recording
     */
    async resumeRecording() {
        const response = await this.sendMessageToBackground({
            type: 'RESUME_RECORDING'
        });
        
        if (response.success) {
            this.handleRecordingResumed();
        } else {
            throw new Error(response.error);
        }
    }
    
    /**
     * Handle recording started
     */
    handleRecordingStarted(data) {
        this.isRecording = true;
        this.isPaused = false;
        this.sessionId = data.sessionId;
        this.startTime = Date.now();
        
        this.updateUIState();
        this.startTimer();
        this.showInfo();
        
        console.log('Recording started:', data);
    }
    
    /**
     * Handle recording stopped
     */
    handleRecordingStopped(data) {
        this.isRecording = false;
        this.isPaused = false;
        this.sessionId = null;
        this.startTime = null;
        
        this.updateUIState();
        this.stopTimer();
        this.hideInfo();
        
        // Show success message
        this.showSuccess(`Recording saved: ${data.filePath || 'Unknown location'}`);
        this.loadRecentRecordings();
        
        console.log('Recording stopped:', data);
    }
    
    /**
     * Handle recording paused
     */
    handleRecordingPaused() {
        this.isPaused = true;
        this.updateUIState();
    }
    
    /**
     * Handle recording resumed
     */
    handleRecordingResumed() {
        this.isPaused = false;
        this.updateUIState();
    }
    
    /**
     * Update UI state based on recording status
     */
    updateUIState() {
        // Update status indicator
        this.statusDot.className = 'status-dot';
        
        if (this.isRecording) {
            if (this.isPaused) {
                this.statusDot.classList.add('paused');
                this.statusText.textContent = 'Paused';
            } else {
                this.statusDot.classList.add('recording');
                this.statusText.textContent = 'Recording';
            }
        } else {
            this.statusDot.classList.add('ready');
            this.statusText.textContent = 'Ready';
        }
        
        // Update main button
        if (this.isRecording) {
            this.startStopButton.className = 'control-button stop-button';
            this.buttonText.textContent = 'Stop Recording';
            this.buttonIcon.innerHTML = `
                <svg class="stop-icon" viewBox="0 0 24 24">
                    <rect x="6" y="6" width="12" height="12"></rect>
                </svg>
            `;
        } else {
            this.startStopButton.className = 'control-button start-button';
            this.buttonText.textContent = 'Start Recording';
            this.buttonIcon.innerHTML = `
                <svg class="play-icon" viewBox="0 0 24 24">
                    <polygon points="5,3 19,12 5,21"></polygon>
                </svg>
            `;
        }
        
        // Update secondary controls
        if (this.isRecording) {
            this.secondaryControls.style.display = 'block';
            
            if (this.isPaused) {
                this.pauseResumeButton.innerHTML = `
                    <svg class="play-icon" viewBox="0 0 24 24">
                        <polygon points="5,3 19,12 5,21"></polygon>
                    </svg>
                    <span>Resume</span>
                `;
            } else {
                this.pauseResumeButton.innerHTML = `
                    <svg class="pause-icon" viewBox="0 0 24 24">
                        <rect x="6" y="4" width="4" height="16"></rect>
                        <rect x="14" y="4" width="4" height="16"></rect>
                    </svg>
                    <span>Pause</span>
                `;
            }
        } else {
            this.secondaryControls.style.display = 'none';
        }
    }
    
    /**
     * Start recording timer
     */
    startTimer() {
        this.stopTimer(); // Clear any existing timer
        
        this.timerInterval = setInterval(() => {
            if (this.startTime && !this.isPaused) {
                const elapsed = Date.now() - this.startTime;
                this.durationText.textContent = this.formatDuration(elapsed);
            }
        }, 1000);
    }
    
    /**
     * Stop recording timer
     */
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    /**
     * Format duration in HH:MM:SS format
     */
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    /**
     * Show info section
     */
    showInfo() {
        this.infoSection.style.display = 'block';
        this.sessionIdText.textContent = this.sessionId || '-';
        this.eventsCountText.textContent = '0'; // Will be updated via status calls
    }
    
    /**
     * Hide info section
     */
    hideInfo() {
        this.infoSection.style.display = 'none';
        this.durationText.textContent = '00:00:00';
    }

    /**
     * Load recent recordings
     */
    async loadRecentRecordings() {
        try {
            const response = await this.sendMessageToBackground({ type: 'GET_RECENT_RECORDINGS' });
            if (response.success) {
                this.renderRecentRecordings(response.data);
            } else {
                this.showError(`Could not load recent recordings: ${response.error}`);
            }
        } catch (error) {
            this.showError(error.message);
        }
    }

    /**
     * Render recent recordings in the UI
     */
    renderRecentRecordings(recordings) {
        if (recordings && recordings.length > 0) {
            this.recentRecordingsList.innerHTML = recordings.map((rec, index) => `
                <div class="recording-item">
                    <input type="radio" id="rec-${rec.id}" name="recording" value="${rec.id}" ${index === 0 ? 'checked' : ''}>
                    <label for="rec-${rec.id}">${rec.name}</label>
                    <span>${rec.date}</span>
                </div>
            `).join('');
        } else {
            this.recentRecordingsList.innerHTML = '<div class="empty-list-message">No recent recordings found.</div>';
        }
    }
    
    /**
     * Toggle settings panel
     */
    toggleSettings() {
        this.settingsVisible = !this.settingsVisible;
        this.settingsPanel.style.display = this.settingsVisible ? 'block' : 'none';
    }
    
    /**
     * Get recording configuration from settings
     */
    getRecordingConfig() {
        return {
            captureVideo: this.captureVideo.checked,
            captureAudio: this.captureAudio.checked,
            showBorder: this.showBorder.checked,
            borderColor: this.borderColor.value,
            mouseSampleRate: parseInt(this.mouseSampleRate.value),
            keyboardCapture: this.keyboardCapture.checked
        };
    }
    
    /**
     * Load settings from storage
     */
    async loadSettings() {
        try {
            const result = await chrome.storage.local.get(['mkd_settings']);
            const settings = result.mkd_settings || {};
            
            this.captureVideo.checked = settings.captureVideo ?? true;
            this.captureAudio.checked = settings.captureAudio ?? false;
            this.showBorder.checked = settings.showBorder ?? true;
            this.borderColor.value = settings.borderColor || '#FF0000';
            this.mouseSampleRate.value = settings.mouseSampleRate || '60';
            this.keyboardCapture.checked = settings.keyboardCapture ?? true;
            
        } catch (error) {
            console.error('Failed to load settings:', error);
            this.showError('Failed to load settings.');
        }
    }
    
    /**
     * Save settings to storage
     */
    async saveSettings() {
        try {
            const settings = this.getRecordingConfig();
            await chrome.storage.local.set({ mkd_settings: settings });
            console.log('Settings saved:', settings);
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showError('Failed to save settings.');
        }
    }
    
    /**
     * Update status from background script
     */
    async updateStatus() {
        try {
            const response = await this.sendMessageToBackground({
                type: 'GET_STATUS'
            });
            
            if (response.success) {
                this.handleStatusUpdate(response.data);
            } else {
                this.updateConnectionStatus(false, response.error);
            }
        } catch (error) {
            console.error('Failed to get status:', error);
            this.updateConnectionStatus(false, error.message);
        }
    }
    
    /**
     * Handle status update from background
     */
    handleStatusUpdate(status) {
        // Update connection status
        const isConnected = status.connection && status.connection.isConnected;
        this.updateConnectionStatus(isConnected, status.connection?.lastError);
        
        // Update recording state if different
        const recording = status.recording || {};
        
        if (recording.isRecording !== this.isRecording ||
            recording.isPaused !== this.isPaused ||
            recording.sessionId !== this.sessionId) {
            
            this.isRecording = recording.isRecording || false;
            this.isPaused = recording.isPaused || false;
            this.sessionId = recording.sessionId || null;
            this.startTime = recording.startTime || null;
            
            this.updateUIState();
            
            if (this.isRecording) {
                this.startTimer();
                this.showInfo();
            } else {
                this.stopTimer();
                this.hideInfo();
            }
        }
        
        // Update event count if available
        if (status.native && status.native.eventCount) {
            this.eventsCountText.textContent = status.native.eventCount.toString();
        }
        
        // Enable/disable controls based on connection
        this.startStopButton.disabled = !isConnected;
        this.startPlaybackButton.disabled = !isConnected;
    }
    
    /**
     * Update connection status display
     */
    updateConnectionStatus(isConnected, errorMessage) {
        this.connectionText.className = `connection-text ${isConnected ? 'connected' : 'disconnected'}`;
        
        if (isConnected) {
            this.connectionText.textContent = 'Connected to native host';
            this.statusDot.classList.remove('disconnected');
        } else {
            this.connectionText.textContent = `Disconnected: ${errorMessage || 'Check native host installation'}`;
            this.statusDot.classList.add('disconnected');
        }
    }
    
    /**
     * Handle messages from background script
     */
    handleBackgroundMessage(message) {
        console.log('Popup received message:', message.type);
        
        switch (message.type) {
            case 'RECORDING_STARTED':
                this.handleRecordingStarted(message.data);
                break;
                
            case 'RECORDING_STOPPED':
                this.handleRecordingStopped(message.data);
                break;
                
            case 'RECORDING_PAUSED':
                this.handleRecordingPaused();
                break;
                
            case 'RECORDING_RESUMED':
                this.handleRecordingResumed();
                break;
        }
    }
    
    /**
     * Send message to background script
     */
    async sendMessageToBackground(message) {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage(message, (response) => {
                if (chrome.runtime.lastError) {
                    resolve({ success: false, error: chrome.runtime.lastError.message });
                } else {
                    resolve(response || { success: false, error: 'No response from background script' });
                }
            });
        });
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'flex';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        // For now, just log success messages
        // In a full implementation, you might want a success notification
        console.log('Success:', message);
    }
    
    /**
     * Hide error message
     */
    hideError() {
        this.errorSection.style.display = 'none';
        this.errorMessage.textContent = '';
    }
}

// Initialize popup controller when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MKDPopupController();
});
