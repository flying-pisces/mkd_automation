// MKD Automation Web GUI JavaScript
// Handles recording, playback, and WebSocket communication with backend

class MKDRecorder {
    constructor() {
        this.isRecording = false;
        this.isPaused = false;
        this.startTime = null;
        this.actionsRecorded = 0;
        this.screenshotCount = 0;
        this.ws = null;
        this.updateInterval = null;
        this.eventBuffer = [];
        this.maxEvents = 20;
        
        // Replay state
        this.replayFrames = [];
        this.currentFrame = 0;
        this.isPlaying = false;
        this.playbackSpeed = 1.0;
        this.playbackInterval = null;
        
        this.initializeUI();
        this.detectBrowser();
        this.setupWebSocket();
    }
    
    initializeUI() {
        // Get UI elements
        this.elements = {
            startBtn: document.getElementById('startBtn'),
            stopBtn: document.getElementById('stopBtn'),
            replayBtn: document.getElementById('replayBtn'),
            openReplayBtn: document.getElementById('openReplayBtn'),
            statusDot: document.getElementById('statusDot'),
            statusText: document.getElementById('statusText'),
            recordingBoundary: document.getElementById('recordingBoundary'),
            eventsLog: document.getElementById('eventsLog'),
            
            // Settings
            captureMouse: document.getElementById('captureMouse'),
            captureKeyboard: document.getElementById('captureKeyboard'),
            captureScreenshots: document.getElementById('captureScreenshots'),
            showBoundary: document.getElementById('showBoundary'),
            
            // Stats
            statDuration: document.getElementById('statDuration'),
            statActions: document.getElementById('statActions'),
            statRate: document.getElementById('statRate'),
            statScreenshots: document.getElementById('statScreenshots'),
            
            // Info
            infoPlatform: document.getElementById('infoPlatform'),
            infoBrowser: document.getElementById('infoBrowser'),
            infoConnection: document.getElementById('infoConnection'),
            
            // Replay Modal
            replayModal: document.getElementById('replayModal'),
            playBtn: document.getElementById('playBtn'),
            pauseBtn: document.getElementById('pauseBtn'),
            stopPlaybackBtn: document.getElementById('stopPlaybackBtn'),
            speedSlider: document.getElementById('speedSlider'),
            speedValue: document.getElementById('speedValue'),
            currentFrame: document.getElementById('currentFrame'),
            totalFrames: document.getElementById('totalFrames'),
            progressFill: document.getElementById('progressFill'),
            replayCanvas: document.getElementById('replayCanvas'),
            noFramesMessage: document.getElementById('noFramesMessage')
        };
        
        // Bind event listeners
        this.elements.startBtn.addEventListener('click', () => this.startRecording());
        this.elements.stopBtn.addEventListener('click', () => this.stopRecording());
        this.elements.replayBtn.addEventListener('click', () => this.replayLastRecording());
        this.elements.openReplayBtn.addEventListener('click', () => this.openRecording());
        
        // Replay controls
        this.elements.playBtn.addEventListener('click', () => this.playPause());
        this.elements.pauseBtn.addEventListener('click', () => this.pausePlayback());
        this.elements.stopPlaybackBtn.addEventListener('click', () => this.stopPlayback());
        this.elements.speedSlider.addEventListener('input', (e) => {
            this.playbackSpeed = parseFloat(e.target.value);
            this.elements.speedValue.textContent = `${this.playbackSpeed}x`;
        });
        
        // Capture mouse and keyboard events when recording
        this.setupEventCapture();
    }
    
    detectBrowser() {
        const userAgent = navigator.userAgent;
        let browserInfo = 'Unknown';
        
        if (userAgent.indexOf('Chrome') > -1) {
            browserInfo = 'Chrome';
        } else if (userAgent.indexOf('Safari') > -1) {
            browserInfo = 'Safari';
        } else if (userAgent.indexOf('Firefox') > -1) {
            browserInfo = 'Firefox';
        } else if (userAgent.indexOf('Edge') > -1) {
            browserInfo = 'Edge';
        }
        
        this.elements.infoBrowser.textContent = browserInfo;
        this.elements.infoPlatform.textContent = navigator.platform || 'Web Browser';
    }
    
    setupWebSocket() {
        // Try to connect to backend WebSocket server
        const wsUrl = 'ws://localhost:8765';
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.updateConnectionStatus('Connected', true);
                this.addEvent('Connected to backend server');
            };
            
            this.ws.onclose = () => {
                this.updateConnectionStatus('Disconnected', false);
                this.addEvent('Disconnected from backend server');
                // Attempt reconnection after 5 seconds
                setTimeout(() => this.setupWebSocket(), 5000);
            };
            
            this.ws.onerror = (error) => {
                this.updateConnectionStatus('Connection Error', false);
                this.addEvent('WebSocket error - backend may be offline');
            };
            
            this.ws.onmessage = (event) => {
                this.handleWebSocketMessage(event.data);
            };
        } catch (error) {
            this.updateConnectionStatus('Not Connected', false);
            this.addEvent('Failed to connect to backend');
        }
    }
    
    updateConnectionStatus(status, isConnected) {
        this.elements.infoConnection.textContent = status;
        this.elements.infoConnection.className = isConnected ? 'info-value connected' : 'info-value disconnected';
    }
    
    handleWebSocketMessage(data) {
        try {
            const message = JSON.parse(data);
            
            switch (message.type) {
                case 'recording_started':
                    this.addEvent('Backend: Recording started');
                    break;
                case 'recording_stopped':
                    this.addEvent(`Backend: Recording saved - ${message.actions} actions`);
                    break;
                case 'screenshot_captured':
                    this.screenshotCount = message.count;
                    this.updateStats();
                    break;
                case 'error':
                    this.addEvent(`Backend Error: ${message.message}`);
                    break;
            }
        } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
        }
    }
    
    setupEventCapture() {
        // Capture mouse events
        document.addEventListener('mousemove', (e) => {
            if (this.isRecording && !this.isPaused && this.elements.captureMouse.checked) {
                this.recordMouseMove(e.clientX, e.clientY);
            }
        });
        
        document.addEventListener('mousedown', (e) => {
            if (this.isRecording && !this.isPaused && this.elements.captureMouse.checked) {
                this.recordMouseClick(e.clientX, e.clientY, e.button, true);
            }
        });
        
        document.addEventListener('mouseup', (e) => {
            if (this.isRecording && !this.isPaused && this.elements.captureMouse.checked) {
                this.recordMouseClick(e.clientX, e.clientY, e.button, false);
            }
        });
        
        // Capture keyboard events
        document.addEventListener('keydown', (e) => {
            if (this.isRecording && !this.isPaused && this.elements.captureKeyboard.checked) {
                this.recordKeyPress(e.key, true);
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (this.isRecording && !this.isPaused && this.elements.captureKeyboard.checked) {
                this.recordKeyPress(e.key, false);
            }
        });
    }
    
    recordMouseMove(x, y) {
        // Throttle mouse move events (record every 10th event)
        if (this.actionsRecorded % 10 === 0) {
            const action = {
                type: 'mouse_move',
                data: { x, y },
                timestamp: this.getTimestamp()
            };
            this.sendAction(action);
            this.addEvent(`Mouse Move: (${x}, ${y})`, true);
        }
        this.actionsRecorded++;
    }
    
    recordMouseClick(x, y, button, pressed) {
        const buttonNames = ['left', 'middle', 'right'];
        const action = {
            type: pressed ? 'mouse_down' : 'mouse_up',
            data: { x, y, button: buttonNames[button] || 'unknown' },
            timestamp: this.getTimestamp()
        };
        this.sendAction(action);
        this.actionsRecorded++;
        
        const status = pressed ? 'Press' : 'Release';
        this.addEvent(`Mouse ${status}: ${buttonNames[button]} at (${x}, ${y})`);
    }
    
    recordKeyPress(key, pressed) {
        const action = {
            type: pressed ? 'key_down' : 'key_up',
            data: { key: key.toUpperCase() },
            timestamp: this.getTimestamp()
        };
        this.sendAction(action);
        this.actionsRecorded++;
        
        if (pressed) {
            this.addEvent(`Keyboard: ${key.toUpperCase()}`);
        }
    }
    
    sendAction(action) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'action',
                action: action
            }));
        } else {
            // Store locally if not connected
            this.storeActionLocally(action);
        }
    }
    
    storeActionLocally(action) {
        // Store in localStorage as fallback
        const storedActions = JSON.parse(localStorage.getItem('mkd_actions') || '[]');
        storedActions.push(action);
        localStorage.setItem('mkd_actions', JSON.stringify(storedActions));
    }
    
    getTimestamp() {
        if (!this.startTime) return 0;
        return (Date.now() - this.startTime) / 1000;
    }
    
    startRecording() {
        if (this.isRecording) return;
        
        this.isRecording = true;
        this.isPaused = false;
        this.startTime = Date.now();
        this.actionsRecorded = 0;
        this.screenshotCount = 0;
        
        // Clear local storage
        localStorage.removeItem('mkd_actions');
        
        // Update UI
        this.elements.statusDot.className = 'status-dot recording';
        this.elements.statusText.textContent = 'Recording';
        this.elements.startBtn.disabled = true;
        this.elements.stopBtn.disabled = false;
        
        // Show recording boundary if enabled
        if (this.elements.showBoundary.checked) {
            this.elements.recordingBoundary.classList.remove('hidden');
        }
        
        // Send start command to backend
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'start_recording',
                settings: {
                    capture_mouse: this.elements.captureMouse.checked,
                    capture_keyboard: this.elements.captureKeyboard.checked,
                    capture_screenshots: this.elements.captureScreenshots.checked
                }
            }));
        }
        
        // Start stats update
        this.updateInterval = setInterval(() => this.updateStats(), 100);
        
        this.addEvent('Recording started');
    }
    
    stopRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        this.isPaused = false;
        
        // Update UI
        this.elements.statusDot.className = 'status-dot stopped';
        this.elements.statusText.textContent = 'Stopped';
        this.elements.startBtn.disabled = false;
        this.elements.stopBtn.disabled = true;
        
        // Hide recording boundary
        this.elements.recordingBoundary.classList.add('hidden');
        
        // Send stop command to backend
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'stop_recording'
            }));
        }
        
        // Save local actions if any
        const localActions = JSON.parse(localStorage.getItem('mkd_actions') || '[]');
        if (localActions.length > 0) {
            this.saveRecording(localActions);
        }
        
        // Stop stats update
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        
        const duration = this.startTime ? (Date.now() - this.startTime) / 1000 : 0;
        this.addEvent(`Recording stopped - Duration: ${duration.toFixed(1)}s, Actions: ${this.actionsRecorded}`);
        
        this.updateStats();
    }
    
    saveRecording(actions) {
        // Save to localStorage with timestamp
        const timestamp = new Date().toISOString();
        const recording = {
            timestamp,
            duration: this.startTime ? (Date.now() - this.startTime) / 1000 : 0,
            actions: actions,
            screenshots: this.screenshotCount
        };
        
        const recordings = JSON.parse(localStorage.getItem('mkd_recordings') || '[]');
        recordings.push(recording);
        
        // Keep only last 10 recordings
        if (recordings.length > 10) {
            recordings.shift();
        }
        
        localStorage.setItem('mkd_recordings', JSON.stringify(recordings));
        localStorage.setItem('mkd_last_recording', JSON.stringify(recording));
    }
    
    updateStats() {
        const duration = this.isRecording && this.startTime ? 
            (Date.now() - this.startTime) / 1000 : 0;
        const rate = duration > 0 ? this.actionsRecorded / duration : 0;
        
        this.elements.statDuration.textContent = `${duration.toFixed(1)} seconds`;
        this.elements.statActions.textContent = this.actionsRecorded;
        this.elements.statRate.textContent = `${rate.toFixed(1)} actions/sec`;
        this.elements.statScreenshots.textContent = this.screenshotCount;
    }
    
    addEvent(message, throttle = false) {
        // Skip if throttled and buffer is full
        if (throttle && this.eventBuffer.length >= 5) return;
        
        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3
        });
        
        const eventLine = document.createElement('div');
        eventLine.className = 'event-line';
        eventLine.innerHTML = `<span class="event-timestamp">[${timestamp}]</span> ${message}`;
        
        this.elements.eventsLog.appendChild(eventLine);
        
        // Keep only last N events
        while (this.elements.eventsLog.children.length > this.maxEvents) {
            this.elements.eventsLog.removeChild(this.elements.eventsLog.firstChild);
        }
        
        // Scroll to bottom
        this.elements.eventsLog.scrollTop = this.elements.eventsLog.scrollHeight;
    }
    
    // Replay functionality
    replayLastRecording() {
        const lastRecording = localStorage.getItem('mkd_last_recording');
        if (!lastRecording) {
            alert('No recording found. Please record something first.');
            return;
        }
        
        const recording = JSON.parse(lastRecording);
        this.loadReplayData(recording);
        this.openReplayModal();
    }
    
    openRecording() {
        // For web version, load from localStorage
        const recordings = JSON.parse(localStorage.getItem('mkd_recordings') || '[]');
        
        if (recordings.length === 0) {
            alert('No recordings found.');
            return;
        }
        
        // Show selection dialog (simplified for demo)
        const selected = recordings[recordings.length - 1]; // Get most recent
        this.loadReplayData(selected);
        this.openReplayModal();
    }
    
    loadReplayData(recording) {
        // Simulate frames from actions (in real app, would load actual screenshots)
        this.replayFrames = [];
        
        // Create synthetic frames from actions for demonstration
        const frameCount = Math.min(recording.screenshots || 30, 100);
        for (let i = 0; i < frameCount; i++) {
            this.replayFrames.push({
                index: i,
                timestamp: (i * 0.5) // 2 FPS
            });
        }
        
        this.currentFrame = 0;
        this.elements.totalFrames.textContent = this.replayFrames.length;
        this.elements.currentFrame.textContent = '0';
    }
    
    openReplayModal() {
        this.elements.replayModal.classList.remove('hidden');
        
        if (this.replayFrames.length === 0) {
            this.elements.noFramesMessage.classList.remove('hidden');
            this.elements.replayCanvas.style.display = 'none';
        } else {
            this.elements.noFramesMessage.classList.add('hidden');
            this.elements.replayCanvas.style.display = 'block';
            this.showFrame(0);
        }
    }
    
    closeReplayModal() {
        this.stopPlayback();
        this.elements.replayModal.classList.add('hidden');
    }
    
    showFrame(index) {
        if (index >= this.replayFrames.length) return;
        
        this.currentFrame = index;
        this.elements.currentFrame.textContent = index + 1;
        
        // Update progress bar
        const progress = (index / (this.replayFrames.length - 1)) * 100;
        this.elements.progressFill.style.width = `${progress}%`;
        
        // Draw frame on canvas (placeholder visualization)
        const ctx = this.elements.replayCanvas.getContext('2d');
        const width = this.elements.replayCanvas.width = 800;
        const height = this.elements.replayCanvas.height = 400;
        
        // Clear canvas
        ctx.fillStyle = '#222';
        ctx.fillRect(0, 0, width, height);
        
        // Draw frame number
        ctx.fillStyle = '#fff';
        ctx.font = '48px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`Frame ${index + 1}`, width / 2, height / 2);
        
        // Draw timestamp
        ctx.font = '24px Arial';
        ctx.fillText(`Time: ${this.replayFrames[index].timestamp.toFixed(1)}s`, width / 2, height / 2 + 60);
    }
    
    playPause() {
        if (this.isPlaying) {
            this.pausePlayback();
        } else {
            this.startPlayback();
        }
    }
    
    startPlayback() {
        if (this.replayFrames.length === 0) return;
        
        this.isPlaying = true;
        this.elements.playBtn.textContent = '⏸ Pause';
        
        const frameDelay = 500 / this.playbackSpeed; // Base 500ms between frames
        
        this.playbackInterval = setInterval(() => {
            if (this.currentFrame >= this.replayFrames.length - 1) {
                this.stopPlayback();
                return;
            }
            
            this.showFrame(this.currentFrame + 1);
        }, frameDelay);
    }
    
    pausePlayback() {
        this.isPlaying = false;
        this.elements.playBtn.textContent = '▶ Play';
        
        if (this.playbackInterval) {
            clearInterval(this.playbackInterval);
            this.playbackInterval = null;
        }
    }
    
    stopPlayback() {
        this.pausePlayback();
        this.currentFrame = 0;
        if (this.replayFrames.length > 0) {
            this.showFrame(0);
        }
    }
}

// Close modal function (global for onclick handler)
function closeReplayModal() {
    if (window.recorder) {
        window.recorder.closeReplayModal();
    }
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.recorder = new MKDRecorder();
    
    // Show initial message
    window.recorder.addEvent('MKD Web Recorder initialized');
    window.recorder.addEvent('Waiting for backend connection...');
});