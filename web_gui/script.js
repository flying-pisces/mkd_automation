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
        
        // Screen capture state
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.screenStream = null;
        this.captureInterval = null;
        this.screenshots = [];
        
        // Replay state
        this.replayFrames = [];
        this.currentFrame = 0;
        this.isPlaying = false;
        this.playbackSpeed = 1.0;
        this.playbackInterval = null;
        this.replayVideo = null;
        
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
                this.recordKeyPress(e.key, true, e);
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (this.isRecording && !this.isPaused && this.elements.captureKeyboard.checked) {
                this.recordKeyPress(e.key, false, e);
            }
        });
    }
    
    recordMouseMove(x, y) {
        // Throttle mouse move events (record every 10th event)
        if (this.actionsRecorded % 10 === 0) {
            const action = {
                type: 'mouse_move',
                data: { 
                    x, 
                    y,
                    screenX: x,
                    screenY: y,
                    clientX: x,
                    clientY: y
                },
                timestamp: this.getTimestamp()
            };
            this.sendAction(action);
            this.storeActionLocally(action);  // Also store locally
            this.addEvent(`Mouse Move: (${x}, ${y})`, true);
        }
        this.actionsRecorded++;
    }
    
    recordMouseClick(x, y, button, pressed) {
        const buttonNames = ['left', 'middle', 'right'];
        const action = {
            type: pressed ? 'mouse_down' : 'mouse_up',
            data: { 
                x, 
                y, 
                button: buttonNames[button] || 'unknown',
                screenX: x,
                screenY: y,
                clientX: x,
                clientY: y
            },
            timestamp: this.getTimestamp()
        };
        this.sendAction(action);
        this.storeActionLocally(action);  // Also store locally
        this.actionsRecorded++;
        
        const status = pressed ? 'Press' : 'Release';
        this.addEvent(`Mouse ${status}: ${buttonNames[button]} at (${x}, ${y})`);
    }
    
    recordKeyPress(key, pressed, event) {
        const action = {
            type: pressed ? 'key_down' : 'key_up',
            data: { 
                key: key.toUpperCase(),
                code: key,
                shiftKey: event ? event.shiftKey : false,
                ctrlKey: event ? event.ctrlKey : false,
                altKey: event ? event.altKey : false,
                metaKey: event ? event.metaKey : false
            },
            timestamp: this.getTimestamp()
        };
        this.sendAction(action);
        this.storeActionLocally(action);  // Also store locally
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
    
    async startRecording() {
        if (this.isRecording) return;
        
        this.isRecording = true;
        this.isPaused = false;
        this.startTime = Date.now();
        this.actionsRecorded = 0;
        this.screenshotCount = 0;
        this.recordedChunks = [];
        this.screenshots = [];
        
        // Clear local storage
        localStorage.removeItem('mkd_actions');
        localStorage.removeItem('mkd_screenshots');
        
        // Update UI
        this.elements.statusDot.className = 'status-dot recording';
        this.elements.statusText.textContent = 'Recording';
        this.elements.startBtn.disabled = true;
        this.elements.stopBtn.disabled = false;
        
        // Show recording boundary if enabled
        if (this.elements.showBoundary.checked) {
            this.elements.recordingBoundary.classList.remove('hidden');
        }
        
        // Start screen capture if enabled
        if (this.elements.captureScreenshots.checked) {
            await this.startScreenCapture();
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
    
    async stopRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        this.isPaused = false;
        
        // Stop screen capture
        await this.stopScreenCapture();
        
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
    
    async saveRecording(actions) {
        // Save to localStorage with timestamp
        const timestamp = new Date().toISOString();
        
        // Process video if available
        let videoData = null;
        if (this.recordedChunks.length > 0) {
            const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
            videoData = await this.blobToBase64(blob);
        }
        
        // Combine all recorded data
        const recording = {
            timestamp,
            duration: this.startTime ? (Date.now() - this.startTime) / 1000 : 0,
            actions: actions,  // Mouse and keyboard actions with timestamps
            screenshots: this.screenshots,
            screenshotCount: this.screenshotCount,
            video: videoData,
            hasVideo: !!videoData,
            hasActions: actions && actions.length > 0,
            captureSettings: {
                mouse: this.elements.captureMouse.checked,
                keyboard: this.elements.captureKeyboard.checked,
                screen: this.elements.captureScreenshots.checked
            }
        };
        
        const recordings = JSON.parse(localStorage.getItem('mkd_recordings') || '[]');
        recordings.push(recording);
        
        // Keep only last 5 recordings due to storage limitations
        if (recordings.length > 5) {
            recordings.shift();
        }
        
        localStorage.setItem('mkd_recordings', JSON.stringify(recordings));
        localStorage.setItem('mkd_last_recording', JSON.stringify(recording));
        
        this.addEvent(`Recording saved: ${actions.length} actions, ${videoData ? 'with video' : this.screenshots.length + ' screenshots'}`);
    }
    
    blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
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
    
    // Screen capture methods
    async startScreenCapture() {
        try {
            // Request screen capture permission
            this.screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    mediaSource: 'screen',
                    width: { max: 1920 },
                    height: { max: 1080 },
                    frameRate: { max: 30 }
                },
                audio: false
            });
            
            // Check if browser supports MediaRecorder
            if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported('video/webm')) {
                // Setup video recording
                const options = {
                    mimeType: 'video/webm;codecs=vp8,opus',
                    videoBitsPerSecond: 2500000
                };
                
                this.mediaRecorder = new MediaRecorder(this.screenStream, options);
                
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.recordedChunks.push(event.data);
                    }
                };
                
                this.mediaRecorder.onstop = () => {
                    this.addEvent('Screen recording stopped');
                };
                
                this.mediaRecorder.onerror = (error) => {
                    console.error('MediaRecorder error:', error);
                    this.addEvent('Screen recording error');
                };
                
                // Start recording
                this.mediaRecorder.start(1000); // Capture in 1-second chunks
                this.addEvent('Screen recording started (video)');
            } else {
                // Fallback to screenshot capture
                await this.startScreenshotCapture();
            }
            
            // Handle stream end
            this.screenStream.getVideoTracks()[0].onended = () => {
                this.addEvent('Screen share ended by user');
                if (this.isRecording) {
                    this.stopRecording();
                }
            };
            
        } catch (error) {
            if (error.name === 'NotAllowedError') {
                this.addEvent('Screen capture permission denied');
            } else {
                console.error('Error starting screen capture:', error);
                this.addEvent('Failed to start screen capture');
            }
        }
    }
    
    async startScreenshotCapture() {
        // Capture screenshots at intervals
        const video = document.createElement('video');
        video.srcObject = this.screenStream;
        video.autoplay = true;
        video.style.display = 'none';
        document.body.appendChild(video);
        
        // Wait for video to be ready
        await new Promise(resolve => {
            video.onloadedmetadata = resolve;
        });
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Capture screenshots every 500ms (2 FPS)
        this.captureInterval = setInterval(() => {
            if (!this.isRecording) {
                clearInterval(this.captureInterval);
                document.body.removeChild(video);
                return;
            }
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            
            // Convert to base64 and store
            canvas.toBlob((blob) => {
                if (blob) {
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const screenshot = {
                            timestamp: this.getTimestamp(),
                            data: reader.result
                        };
                        this.screenshots.push(screenshot);
                        this.screenshotCount++;
                        
                        // Limit stored screenshots to prevent memory issues
                        if (this.screenshots.length > 120) { // Max 60 seconds at 2 FPS
                            this.screenshots.shift();
                        }
                        
                        this.updateStats();
                    };
                    reader.readAsDataURL(blob);
                }
            }, 'image/jpeg', 0.7);
        }, 500);
        
        this.addEvent('Screenshot capture started (2 FPS)');
    }
    
    async stopScreenCapture() {
        // Stop video recording
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        // Stop screenshot capture
        if (this.captureInterval) {
            clearInterval(this.captureInterval);
            this.captureInterval = null;
        }
        
        // Stop screen stream
        if (this.screenStream) {
            this.screenStream.getTracks().forEach(track => track.stop());
            this.screenStream = null;
        }
        
        // Clean up any video elements
        const videos = document.querySelectorAll('video[style*="display: none"]');
        videos.forEach(video => video.remove());
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
        // Load actual video or screenshots
        this.replayFrames = [];
        this.replayVideo = null;
        this.replayActions = recording.actions || [];
        this.replayDuration = recording.duration || 0;
        
        // Store the full recording for combined replay
        this.currentRecording = recording;
        
        if (recording.video) {
            // Load video data
            this.replayVideo = recording.video;
            this.setupVideoReplay();
        } else if (recording.screenshots && recording.screenshots.length > 0) {
            // Load screenshot frames
            this.replayFrames = recording.screenshots;
            this.currentFrame = 0;
            this.elements.totalFrames.textContent = this.replayFrames.length;
            this.elements.currentFrame.textContent = '1';
        } else {
            // No visual data available
            this.replayFrames = [];
            this.elements.totalFrames.textContent = '0';
            this.elements.currentFrame.textContent = '0';
        }
        
        // Display recording info
        const info = [];
        if (recording.hasVideo) info.push('Video');
        if (recording.screenshots?.length > 0) info.push(`${recording.screenshots.length} Screenshots`);
        if (recording.hasActions) info.push(`${recording.actions.length} Actions`);
        
        if (info.length > 0) {
            this.addEvent(`Loaded recording: ${info.join(', ')}`);
        }
    }
    
    openReplayModal() {
        this.elements.replayModal.classList.remove('hidden');
        
        if (this.replayVideo) {
            // Show video player
            this.elements.noFramesMessage.classList.add('hidden');
            this.elements.replayCanvas.style.display = 'block';
            this.showVideo();
        } else if (this.replayFrames.length > 0) {
            // Show screenshots
            this.elements.noFramesMessage.classList.add('hidden');
            this.elements.replayCanvas.style.display = 'block';
            this.showFrame(0);
        } else {
            // No visual data
            this.elements.noFramesMessage.classList.remove('hidden');
            this.elements.replayCanvas.style.display = 'none';
        }
    }
    
    closeReplayModal() {
        this.stopPlayback();
        this.elements.replayModal.classList.add('hidden');
        
        // Restore canvas if video was playing
        const container = this.elements.replayCanvas.parentElement;
        const videoElement = container.querySelector('video');
        if (videoElement) {
            container.innerHTML = '<canvas id="replayCanvas"></canvas>';
            this.elements.replayCanvas = document.getElementById('replayCanvas');
        }
    }
    
    showFrame(index) {
        if (index >= this.replayFrames.length) return;
        
        this.currentFrame = index;
        this.elements.currentFrame.textContent = index + 1;
        
        // Update progress bar
        const progress = this.replayFrames.length > 1 ? 
            (index / (this.replayFrames.length - 1)) * 100 : 0;
        this.elements.progressFill.style.width = `${progress}%`;
        
        // Get the screenshot data
        const frame = this.replayFrames[index];
        
        if (frame.data) {
            // Load and display the actual screenshot
            const img = new Image();
            img.onload = () => {
                const canvas = this.elements.replayCanvas;
                const ctx = canvas.getContext('2d');
                
                // Set canvas size to maintain aspect ratio
                const maxWidth = 1024;
                const maxHeight = 576;
                let width = img.width;
                let height = img.height;
                
                if (width > maxWidth || height > maxHeight) {
                    const ratio = Math.min(maxWidth / width, maxHeight / height);
                    width *= ratio;
                    height *= ratio;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                // Draw the screenshot
                ctx.drawImage(img, 0, 0, width, height);
                
                // Draw timestamp overlay
                ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
                ctx.fillRect(0, height - 30, width, 30);
                ctx.fillStyle = '#fff';
                ctx.font = '14px Arial';
                ctx.textAlign = 'left';
                ctx.fillText(`Time: ${frame.timestamp.toFixed(1)}s`, 10, height - 10);
            };
            img.src = frame.data;
        }
    }
    
    setupVideoReplay() {
        // Create container for video and overlay
        const container = this.elements.replayCanvas.parentElement;
        container.innerHTML = '';
        
        // Create video element
        const videoElement = document.createElement('video');
        videoElement.src = this.replayVideo;
        videoElement.controls = false; // We'll use custom controls
        videoElement.style.width = '100%';
        videoElement.style.maxHeight = '576px';
        videoElement.style.display = 'block';
        
        // Create overlay canvas for action indicators
        const overlayCanvas = document.createElement('canvas');
        overlayCanvas.style.position = 'absolute';
        overlayCanvas.style.top = '0';
        overlayCanvas.style.left = '0';
        overlayCanvas.style.pointerEvents = 'none';
        overlayCanvas.style.zIndex = '10';
        
        // Create wrapper for positioning
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';
        
        wrapper.appendChild(videoElement);
        wrapper.appendChild(overlayCanvas);
        container.appendChild(wrapper);
        
        // Store references
        this.replayVideoElement = videoElement;
        this.overlayCanvas = overlayCanvas;
        this.overlayCtx = overlayCanvas.getContext('2d');
        
        // Update overlay canvas size when video loads
        videoElement.addEventListener('loadedmetadata', () => {
            overlayCanvas.width = videoElement.videoWidth || videoElement.offsetWidth;
            overlayCanvas.height = videoElement.videoHeight || videoElement.offsetHeight;
        });
        
        // Update progress and action overlays based on video playback
        videoElement.addEventListener('timeupdate', () => {
            const currentTime = videoElement.currentTime;
            const progress = (currentTime / videoElement.duration) * 100;
            this.elements.progressFill.style.width = `${progress}%`;
            this.elements.currentFrame.textContent = Math.floor(currentTime);
            this.elements.totalFrames.textContent = Math.floor(videoElement.duration);
            
            // Update action overlays
            this.updateActionOverlays(currentTime);
        });\n        \n        // Handle playback controls\n        this.elements.playBtn.onclick = () => {\n            if (videoElement.paused) {\n                videoElement.play();\n                this.elements.playBtn.textContent = '⏸ Pause';\n            } else {\n                videoElement.pause();\n                this.elements.playBtn.textContent = '▶ Play';\n            }\n        };\n        \n        this.elements.pauseBtn.onclick = () => {\n            videoElement.pause();\n            this.elements.playBtn.textContent = '▶ Play';\n        };\n        \n        this.elements.stopPlaybackBtn.onclick = () => {\n            videoElement.pause();\n            videoElement.currentTime = 0;\n            this.elements.playBtn.textContent = '▶ Play';\n            this.clearActionOverlays();\n        };\n        \n        // Handle speed control\n        this.elements.speedSlider.addEventListener('input', (e) => {\n            videoElement.playbackRate = parseFloat(e.target.value);\n        });\n    }"}
    
    showVideo() {
        if (!this.replayVideo) return;
        this.setupVideoReplay();
    }
    
    playPause() {
        if (this.isPlaying) {
            this.pausePlayback();
        } else {
            this.startPlayback();
        }
    }
    
    startPlayback() {
        if (this.replayVideo) {
            // Video playback is handled by video element
            const videoElement = this.elements.replayCanvas.parentElement.querySelector('video');
            if (videoElement) videoElement.play();
            return;
        }
        
        if (this.replayFrames.length === 0) return;
        
        this.isPlaying = true;
        this.elements.playBtn.textContent = '⏸ Pause';
        
        const frameDelay = 500 / this.playbackSpeed; // Base 500ms between frames (2 FPS)
        
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
    
    // Action overlay methods for combined video + action replay
    updateActionOverlays(currentTime) {
        if (!this.overlayCanvas || !this.replayActions) return;
        
        // Clear previous overlays
        this.clearActionOverlays();
        
        // Find actions that should be visible at current time
        const timeWindow = 0.5; // Show actions for 500ms
        const visibleActions = this.replayActions.filter(action => {
            return Math.abs(action.timestamp - currentTime) <= timeWindow;
        });
        
        // Draw action indicators
        visibleActions.forEach(action => this.drawActionIndicator(action, currentTime));
    }
    
    clearActionOverlays() {
        if (!this.overlayCanvas) return;
        this.overlayCtx.clearRect(0, 0, this.overlayCanvas.width, this.overlayCanvas.height);
    }
    
    drawActionIndicator(action, currentTime) {
        if (!this.overlayCtx) return;
        
        const ctx = this.overlayCtx;
        const age = currentTime - action.timestamp;
        const opacity = Math.max(0, 1 - (Math.abs(age) / 0.5)); // Fade over 500ms
        
        // Scale coordinates if needed (assuming screen coordinates map to canvas)
        const x = action.data.x || action.data.clientX || 0;
        const y = action.data.y || action.data.clientY || 0;
        
        ctx.save();
        ctx.globalAlpha = opacity;
        
        if (action.type.startsWith('mouse')) {
            this.drawMouseIndicator(ctx, x, y, action);
        } else if (action.type.startsWith('key')) {
            this.drawKeyboardIndicator(ctx, action);
        }
        
        ctx.restore();
    }
    
    drawMouseIndicator(ctx, x, y, action) {
        const radius = 15;
        
        // Draw circle
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        
        if (action.type === 'mouse_down') {
            // Click indicator - filled circle
            ctx.fillStyle = action.data.button === 'left' ? '#ff4444' : 
                           action.data.button === 'right' ? '#4444ff' : '#44ff44';
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();
        } else if (action.type === 'mouse_move') {
            // Move indicator - hollow circle
            ctx.strokeStyle = '#ffff44';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
        
        // Add ripple effect for clicks
        if (action.type === 'mouse_down') {
            ctx.beginPath();
            ctx.arc(x, y, radius + 10, 0, 2 * Math.PI);
            ctx.strokeStyle = ctx.fillStyle;
            ctx.globalAlpha *= 0.5;
            ctx.lineWidth = 1;
            ctx.stroke();
        }
    }
    
    drawKeyboardIndicator(ctx, action) {
        if (action.type !== 'key_down') return;
        
        const key = action.data.key;
        const x = 50; // Fixed position for keyboard indicators
        let y = 50;
        
        // Stack multiple key presses
        const recentKeys = this.replayActions.filter(a => 
            a.type === 'key_down' && 
            Math.abs(a.timestamp - action.timestamp) <= 0.1
        );
        const keyIndex = recentKeys.indexOf(action);
        y += keyIndex * 30;
        
        // Draw key background
        ctx.fillStyle = '#333333';
        ctx.fillRect(x, y, 80, 25);
        
        // Draw key border
        ctx.strokeStyle = '#666666';
        ctx.lineWidth = 1;
        ctx.strokeRect(x, y, 80, 25);
        
        // Draw key text
        ctx.fillStyle = '#ffffff';
        ctx.font = '14px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(key, x + 40, y + 12.5);
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