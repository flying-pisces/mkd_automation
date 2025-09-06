/**
 * MKD Web Recorder - GitHub Pages Edition
 * Browser-only screen recording with action replay
 * No backend dependencies - works on any static host
 */

class MKDWebRecorder {
    constructor() {
        this.isRecording = false;
        this.startTime = null;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        this.screenStream = null;
        this.actions = [];
        this.currentRecording = null;
        
        // Statistics
        this.mouseActionCount = 0;
        this.keyActionCount = 0;
        this.recordingDuration = 0;
        
        this.initializeUI();
        this.setupEventListeners();
        this.loadStoredRecordings();
    }
    
    initializeUI() {
        // Control elements
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.replayBtn = document.getElementById('replayBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        
        // Status and stats
        this.statusIndicator = document.getElementById('status');
        this.durationDisplay = document.getElementById('duration');
        this.mouseActionsDisplay = document.getElementById('mouseActions');
        this.keyActionsDisplay = document.getElementById('keyActions');
        this.videoSizeDisplay = document.getElementById('videoSize');
        
        // Settings
        this.recordVideoSetting = document.getElementById('recordVideo');
        this.recordActionsSetting = document.getElementById('recordActions');
        this.showOverlaysSetting = document.getElementById('showOverlays');
        
        // Replay modal elements
        this.replayModal = document.getElementById('replayModal');
        this.replayVideo = document.getElementById('replayVideo');
        this.actionsOverlay = document.getElementById('actionsOverlay');
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.stopReplayBtn = document.getElementById('stopReplayBtn');
        this.speedSlider = document.getElementById('speedSlider');
        this.speedDisplay = document.getElementById('speedDisplay');
        this.replayTime = document.getElementById('replayTime');
        this.progressFill = document.getElementById('progressFill');
        
        // Initialize status
        this.updateStatus('ready');
        this.updateStatistics();
    }
    
    setupEventListeners() {
        // Control buttons
        this.startBtn.addEventListener('click', () => this.startRecording());
        this.stopBtn.addEventListener('click', () => this.stopRecording());
        this.replayBtn.addEventListener('click', () => this.openReplayModal());
        this.downloadBtn.addEventListener('click', () => this.downloadRecording());
        
        // Replay controls
        this.playPauseBtn.addEventListener('click', () => this.togglePlayback());
        this.stopReplayBtn.addEventListener('click', () => this.stopReplay());
        this.speedSlider.addEventListener('input', () => this.updatePlaybackSpeed());
        
        // Action capture (when recording)
        this.setupActionCapture();
        
        // Stats update interval
        this.statsInterval = setInterval(() => {
            if (this.isRecording) {
                this.recordingDuration = this.startTime ? (Date.now() - this.startTime) / 1000 : 0;
                this.updateStatistics();
            }
        }, 100);
    }
    
    setupActionCapture() {
        // Mouse event tracking
        document.addEventListener('mousemove', (e) => {
            if (this.isRecording && this.recordActionsSetting.checked) {
                // Throttle mouse moves (every 10th event)
                if (this.mouseActionCount % 10 === 0) {
                    this.recordAction('mouse_move', {
                        x: e.clientX,
                        y: e.clientY,
                        pageX: e.pageX,
                        pageY: e.pageY
                    });
                }
                this.mouseActionCount++;
            }
        });
        
        document.addEventListener('mousedown', (e) => {
            if (this.isRecording && this.recordActionsSetting.checked) {
                this.recordAction('mouse_down', {
                    x: e.clientX,
                    y: e.clientY,
                    pageX: e.pageX,
                    pageY: e.pageY,
                    button: ['left', 'middle', 'right'][e.button] || 'unknown'
                });
                this.mouseActionCount++;
            }
        });
        
        document.addEventListener('mouseup', (e) => {
            if (this.isRecording && this.recordActionsSetting.checked) {
                this.recordAction('mouse_up', {
                    x: e.clientX,
                    y: e.clientY,
                    pageX: e.pageX,
                    pageY: e.pageY,
                    button: ['left', 'middle', 'right'][e.button] || 'unknown'
                });
                this.mouseActionCount++;
            }
        });
        
        // Keyboard event tracking
        document.addEventListener('keydown', (e) => {
            if (this.isRecording && this.recordActionsSetting.checked) {
                this.recordAction('key_down', {
                    key: e.key,
                    code: e.code,
                    ctrlKey: e.ctrlKey,
                    altKey: e.altKey,
                    shiftKey: e.shiftKey,
                    metaKey: e.metaKey
                });
                this.keyActionCount++;
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (this.isRecording && this.recordActionsSetting.checked) {
                this.recordAction('key_up', {
                    key: e.key,
                    code: e.code,
                    ctrlKey: e.ctrlKey,
                    altKey: e.altKey,
                    shiftKey: e.shiftKey,
                    metaKey: e.metaKey
                });
                this.keyActionCount++;
            }
        });
    }
    
    recordAction(type, data) {
        const timestamp = this.getRecordingTime();
        this.actions.push({
            type,
            data,
            timestamp
        });
    }
    
    getRecordingTime() {
        return this.startTime ? (Date.now() - this.startTime) / 1000 : 0;
    }
    
    async startRecording() {
        try {
            // Request screen capture permission
            this.screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: {
                    mediaSource: 'screen',
                    width: { ideal: 1920 },
                    height: { ideal: 1080 },
                    frameRate: { ideal: 30 }
                },
                audio: false
            });
            
            // Setup video recording if enabled
            if (this.recordVideoSetting.checked && 
                typeof MediaRecorder !== 'undefined' && 
                MediaRecorder.isTypeSupported('video/webm')) {
                
                const options = {
                    mimeType: 'video/webm;codecs=vp8',
                    videoBitsPerSecond: 2500000
                };
                
                this.mediaRecorder = new MediaRecorder(this.screenStream, options);
                
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.recordedChunks.push(event.data);
                    }
                };
                
                this.mediaRecorder.onstop = () => {
                    console.log('MediaRecorder stopped');
                };
                
                this.mediaRecorder.start(1000); // 1-second chunks
            }
            
            // Initialize recording state
            this.isRecording = true;
            this.startTime = Date.now();
            this.actions = [];
            this.mouseActionCount = 0;
            this.keyActionCount = 0;
            this.recordedChunks = [];
            
            // Update UI
            this.updateStatus('recording');
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            this.replayBtn.disabled = true;
            this.downloadBtn.disabled = true;
            
            // Handle stream end (user stops sharing)
            this.screenStream.getVideoTracks()[0].onended = () => {
                if (this.isRecording) {
                    this.stopRecording();
                }
            };
            
            console.log('Recording started');
            
        } catch (error) {
            console.error('Error starting recording:', error);
            alert('Failed to start screen recording. Please ensure you grant screen capture permission.');
            this.updateStatus('ready');
        }
    }
    
    async stopRecording() {
        if (!this.isRecording) return;
        
        this.isRecording = false;
        
        // Stop media recorder
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        // Stop screen stream
        if (this.screenStream) {
            this.screenStream.getTracks().forEach(track => track.stop());
        }
        
        // Create recording object
        const duration = this.getRecordingTime();
        let videoBlob = null;
        let videoSize = 0;
        
        if (this.recordedChunks.length > 0) {
            videoBlob = new Blob(this.recordedChunks, { type: 'video/webm' });
            videoSize = videoBlob.size;
        }
        
        this.currentRecording = {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            duration: duration,
            actions: [...this.actions],
            mouseActions: this.mouseActionCount,
            keyActions: this.keyActionCount,
            videoBlob: videoBlob,
            videoSize: videoSize,
            settings: {
                recordVideo: this.recordVideoSetting.checked,
                recordActions: this.recordActionsSetting.checked
            }
        };
        
        // Save to localStorage
        this.saveRecording(this.currentRecording);
        
        // Update UI
        this.updateStatus('ready');
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.replayBtn.disabled = false;
        this.downloadBtn.disabled = false;
        
        // Final stats update
        this.updateStatistics();
        
        console.log(`Recording stopped. Duration: ${duration.toFixed(1)}s, Actions: ${this.actions.length}`);
    }
    
    saveRecording(recording) {
        // Save recording metadata to localStorage (without video blob for storage efficiency)
        const recordingMeta = {
            ...recording,
            videoBlob: null, // Don't store blob in localStorage
            hasVideo: !!recording.videoBlob
        };
        
        const recordings = JSON.parse(localStorage.getItem('mkd_recordings') || '[]');
        recordings.push(recordingMeta);
        
        // Keep only last 10 recordings
        if (recordings.length > 10) {
            recordings.shift();
        }
        
        localStorage.setItem('mkd_recordings', JSON.stringify(recordings));
        localStorage.setItem('mkd_current_recording', JSON.stringify(recordingMeta));
    }
    
    loadStoredRecordings() {
        const recordings = JSON.parse(localStorage.getItem('mkd_recordings') || '[]');
        console.log(`Loaded ${recordings.length} stored recordings`);
    }
    
    openReplayModal() {
        if (!this.currentRecording) return;
        
        this.replayModal.style.display = 'block';
        
        if (this.currentRecording.videoBlob) {
            // Setup video replay
            const videoUrl = URL.createObjectURL(this.currentRecording.videoBlob);
            this.replayVideo.src = videoUrl;
            this.replayVideo.style.display = 'block';
            
            // Setup overlay canvas
            this.setupOverlayCanvas();
            
            // Setup video event listeners
            this.replayVideo.addEventListener('timeupdate', () => {
                this.updateActionOverlays();
                this.updateReplayProgress();
            });
            
            this.replayVideo.addEventListener('loadedmetadata', () => {
                this.actionsOverlay.width = this.replayVideo.videoWidth;
                this.actionsOverlay.height = this.replayVideo.videoHeight;
            });
            
        } else {
            // No video, show actions only
            this.replayVideo.style.display = 'none';
            alert('This recording contains actions but no video. Video recording was disabled during capture.');
        }
    }
    
    setupOverlayCanvas() {
        const video = this.replayVideo;
        const canvas = this.actionsOverlay;
        
        // Position overlay canvas over video
        const updateCanvasPosition = () => {
            const rect = video.getBoundingClientRect();
            canvas.style.position = 'absolute';
            canvas.style.left = '0';
            canvas.style.top = '0';
            canvas.style.width = '100%';
            canvas.style.height = '100%';
        };
        
        video.addEventListener('loadedmetadata', updateCanvasPosition);
        window.addEventListener('resize', updateCanvasPosition);
    }
    
    updateActionOverlays() {
        if (!this.showOverlaysSetting.checked || !this.currentRecording) return;
        
        const canvas = this.actionsOverlay;
        const ctx = canvas.getContext('2d');
        const currentTime = this.replayVideo.currentTime;
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Find actions to display (within 0.5 seconds of current time)
        const timeWindow = 0.5;
        const visibleActions = this.currentRecording.actions.filter(action => 
            Math.abs(action.timestamp - currentTime) <= timeWindow
        );
        
        // Draw action overlays
        visibleActions.forEach(action => {
            const age = Math.abs(currentTime - action.timestamp);
            const opacity = Math.max(0, 1 - (age / timeWindow));
            
            ctx.save();
            ctx.globalAlpha = opacity;
            
            if (action.type.startsWith('mouse')) {
                this.drawMouseAction(ctx, action, canvas);
            } else if (action.type.startsWith('key')) {
                this.drawKeyboardAction(ctx, action, canvas);
            }
            
            ctx.restore();
        });
    }
    
    drawMouseAction(ctx, action, canvas) {
        // Scale coordinates from page coordinates to video coordinates
        const scaleX = canvas.width / window.innerWidth;
        const scaleY = canvas.height / window.innerHeight;
        
        const x = (action.data.x || 0) * scaleX;
        const y = (action.data.y || 0) * scaleY;
        const radius = 20;
        
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);
        
        if (action.type === 'mouse_down') {
            // Click indicator - filled circle
            ctx.fillStyle = action.data.button === 'left' ? '#ff4444' : 
                           action.data.button === 'right' ? '#4444ff' : '#44ff44';
            ctx.fill();
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.stroke();
            
            // Ripple effect
            ctx.beginPath();
            ctx.arc(x, y, radius + 15, 0, 2 * Math.PI);
            ctx.strokeStyle = ctx.fillStyle;
            ctx.globalAlpha *= 0.3;
            ctx.lineWidth = 2;
            ctx.stroke();
            
        } else if (action.type === 'mouse_move') {
            // Move indicator - hollow circle
            ctx.strokeStyle = '#ffff44';
            ctx.lineWidth = 3;
            ctx.stroke();
        }
    }
    
    drawKeyboardAction(ctx, action, canvas) {
        if (action.type !== 'key_down') return;
        
        const key = action.data.key;
        if (key.length > 1 && !['Enter', 'Space', 'Tab', 'Escape'].includes(key)) return;
        
        const x = 50;
        let y = 50;
        
        // Stack multiple keys vertically
        const recentKeys = this.currentRecording.actions.filter(a => 
            a.type === 'key_down' && 
            Math.abs(a.timestamp - action.timestamp) <= 0.1
        );
        const keyIndex = recentKeys.indexOf(action);
        y += keyIndex * 35;
        
        // Draw key background
        ctx.fillStyle = '#333333';
        ctx.fillRect(x, y, 100, 30);
        
        // Draw key border
        ctx.strokeStyle = '#666666';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, 100, 30);
        
        // Draw key text
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 16px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        let displayKey = key === ' ' ? 'Space' : key;
        if (displayKey.length > 8) displayKey = displayKey.substring(0, 8);
        
        ctx.fillText(displayKey, x + 50, y + 15);
    }
    
    updateReplayProgress() {
        const video = this.replayVideo;
        if (!video.duration) return;
        
        const progress = (video.currentTime / video.duration) * 100;
        this.progressFill.style.width = `${progress}%`;
        
        const currentMin = Math.floor(video.currentTime / 60);
        const currentSec = Math.floor(video.currentTime % 60);
        const totalMin = Math.floor(video.duration / 60);
        const totalSec = Math.floor(video.duration % 60);
        
        this.replayTime.textContent = 
            `${currentMin}:${currentSec.toString().padStart(2, '0')} / ${totalMin}:${totalSec.toString().padStart(2, '0')}`;
    }
    
    togglePlayback() {
        const video = this.replayVideo;
        
        if (video.paused) {
            video.play();
            this.playPauseBtn.textContent = '⏸️ Pause';
        } else {
            video.pause();
            this.playPauseBtn.textContent = '▶️ Play';
        }
    }
    
    stopReplay() {
        const video = this.replayVideo;
        video.pause();
        video.currentTime = 0;
        this.playPauseBtn.textContent = '▶️ Play';
    }
    
    updatePlaybackSpeed() {
        const speed = parseFloat(this.speedSlider.value);
        this.replayVideo.playbackRate = speed;
        this.speedDisplay.textContent = `${speed}x`;
    }
    
    closeReplay() {
        this.replayModal.style.display = 'none';
        
        // Clean up video URL
        if (this.replayVideo.src) {
            URL.revokeObjectURL(this.replayVideo.src);
        }
    }
    
    downloadRecording() {
        if (!this.currentRecording) return;
        
        if (this.currentRecording.videoBlob) {
            // Download video
            const url = URL.createObjectURL(this.currentRecording.videoBlob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mkd-recording-${new Date().toISOString().slice(0, 19)}.webm`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        // Download actions as JSON
        const actionsData = {
            recording: {
                timestamp: this.currentRecording.timestamp,
                duration: this.currentRecording.duration,
                mouseActions: this.currentRecording.mouseActions,
                keyActions: this.currentRecording.keyActions,
                settings: this.currentRecording.settings
            },
            actions: this.currentRecording.actions
        };
        
        const jsonBlob = new Blob([JSON.stringify(actionsData, null, 2)], { 
            type: 'application/json' 
        });
        const jsonUrl = URL.createObjectURL(jsonBlob);
        const jsonA = document.createElement('a');
        jsonA.href = jsonUrl;
        jsonA.download = `mkd-actions-${new Date().toISOString().slice(0, 19)}.json`;
        document.body.appendChild(jsonA);
        jsonA.click();
        document.body.removeChild(jsonA);
        URL.revokeObjectURL(jsonUrl);
    }
    
    updateStatus(status) {
        this.statusIndicator.className = `status-indicator ${status}`;
    }
    
    updateStatistics() {
        this.durationDisplay.textContent = `${this.recordingDuration.toFixed(1)}s`;
        this.mouseActionsDisplay.textContent = this.mouseActionCount.toString();
        this.keyActionsDisplay.textContent = this.keyActionCount.toString();
        
        if (this.currentRecording && this.currentRecording.videoSize) {
            const sizeMB = (this.currentRecording.videoSize / 1024 / 1024).toFixed(1);
            this.videoSizeDisplay.textContent = `${sizeMB} MB`;
        } else {
            this.videoSizeDisplay.textContent = '0 MB';
        }
    }
}

// Global function for modal close
function closeReplay() {
    if (window.recorder) {
        window.recorder.closeReplay();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.recorder = new MKDWebRecorder();
    console.log('MKD Web Recorder initialized');
});

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.recorder && window.recorder.isRecording) {
        console.log('Page hidden during recording - recording continues');
    }
});