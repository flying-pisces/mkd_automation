/**
 * Enhanced Debug Logger for MKD Chrome Extension
 * 
 * Provides verbose logging with different levels and log file output
 */

class DebugLogger {
    constructor() {
        this.logLevel = this.getLogLevel();
        this.logs = [];
        this.maxLogs = 1000;
        this.logToConsole = true;
        this.logToStorage = true;
        
        // Log levels
        this.LEVELS = {
            ERROR: 0,
            WARN: 1, 
            INFO: 2,
            DEBUG: 3,
            TRACE: 4
        };
        
        this.initializeLogger();
    }
    
    /**
     * Initialize the logger
     */
    initializeLogger() {
        // Load settings from storage
        if (typeof chrome !== 'undefined' && chrome.storage) {
            chrome.storage.local.get(['mkd_debug_level'], (result) => {
                if (result.mkd_debug_level !== undefined) {
                    this.logLevel = result.mkd_debug_level;
                }
            });
        }
        
        this.info('DebugLogger initialized', {
            level: this.logLevel,
            timestamp: new Date().toISOString()
        });
    }
    
    /**
     * Get current log level
     */
    getLogLevel() {
        // Default to INFO level, DEBUG in development
        const isDev = typeof chrome === 'undefined' || chrome.runtime.id === undefined;
        return isDev ? this.LEVELS.DEBUG : this.LEVELS.INFO;
    }
    
    /**
     * Set log level
     */
    setLogLevel(level) {
        this.logLevel = level;
        
        if (typeof chrome !== 'undefined' && chrome.storage) {
            chrome.storage.local.set({ mkd_debug_level: level });
        }
        
        this.info('Log level changed', { newLevel: level });
    }
    
    /**
     * Add log entry
     */
    addLog(level, message, data = null, context = null) {
        if (level > this.logLevel) {
            return; // Skip if below log level
        }
        
        const timestamp = new Date().toISOString();
        const levelName = Object.keys(this.LEVELS)[level];
        
        const logEntry = {
            timestamp,
            level: levelName,
            message,
            data,
            context: context || this.getContext(),
            stackTrace: level <= this.LEVELS.WARN ? this.getStackTrace() : null
        };
        
        // Add to internal log buffer
        this.logs.push(logEntry);
        
        // Keep only recent logs
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }
        
        // Console output
        if (this.logToConsole) {
            this.outputToConsole(logEntry);
        }
        
        // Storage output
        if (this.logToStorage) {
            this.saveToStorage(logEntry);
        }
    }
    
    /**
     * Get execution context
     */
    getContext() {
        try {
            if (typeof chrome !== 'undefined' && chrome.runtime) {
                const manifest = chrome.runtime.getManifest();
                return {
                    extension: manifest.name,
                    version: manifest.version,
                    context: this.getContextType(),
                    url: typeof window !== 'undefined' ? window.location?.href : 'background'
                };
            }
        } catch (e) {
            // Ignore context errors
        }
        
        return { context: 'unknown' };
    }
    
    /**
     * Determine context type
     */
    getContextType() {
        if (typeof window === 'undefined') {
            return 'service_worker';
        }
        
        if (window.location?.protocol === 'chrome-extension:') {
            if (window.location?.pathname?.includes('popup')) {
                return 'popup';
            }
            return 'extension_page';
        }
        
        return 'content_script';
    }
    
    /**
     * Get stack trace
     */
    getStackTrace() {
        try {
            throw new Error();
        } catch (e) {
            return e.stack?.split('\n').slice(3, 8).join('\n') || 'Stack trace not available';
        }
    }
    
    /**
     * Output to console
     */
    outputToConsole(logEntry) {
        const { level, message, data, timestamp } = logEntry;
        const prefix = `[MKD ${level}] ${timestamp.substr(11, 12)}`;
        
        switch (level) {
            case 'ERROR':
                console.error(prefix, message, data || '');
                break;
            case 'WARN':
                console.warn(prefix, message, data || '');
                break;
            case 'INFO':
                console.info(prefix, message, data || '');
                break;
            default:
                console.log(prefix, message, data || '');
        }
    }
    
    /**
     * Save to storage for later retrieval
     */
    async saveToStorage(logEntry) {
        try {
            if (typeof chrome !== 'undefined' && chrome.storage) {
                const key = `mkd_log_${Date.now()}`;
                const storageData = {};
                storageData[key] = logEntry;
                
                await chrome.storage.local.set(storageData);
                
                // Clean up old logs
                this.cleanupOldLogs();
            }
        } catch (e) {
            // Ignore storage errors to prevent infinite loops
        }
    }
    
    /**
     * Clean up old log entries from storage
     */
    async cleanupOldLogs() {
        try {
            if (typeof chrome !== 'undefined' && chrome.storage) {
                const result = await chrome.storage.local.get(null);
                const logKeys = Object.keys(result).filter(key => key.startsWith('mkd_log_'));
                
                if (logKeys.length > this.maxLogs) {
                    // Sort by timestamp and remove oldest
                    logKeys.sort();
                    const keysToRemove = logKeys.slice(0, logKeys.length - this.maxLogs);
                    await chrome.storage.local.remove(keysToRemove);
                }
            }
        } catch (e) {
            // Ignore cleanup errors
        }
    }
    
    /**
     * Export all logs
     */
    async exportLogs() {
        try {
            let allLogs = [...this.logs];
            
            // Add logs from storage
            if (typeof chrome !== 'undefined' && chrome.storage) {
                const result = await chrome.storage.local.get(null);
                const logKeys = Object.keys(result).filter(key => key.startsWith('mkd_log_'));
                
                const storageLogs = logKeys.map(key => result[key]).filter(log => log);
                allLogs = [...allLogs, ...storageLogs];
            }
            
            // Sort by timestamp
            allLogs.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
            
            return allLogs;
        } catch (e) {
            this.error('Failed to export logs', e);
            return this.logs;
        }
    }
    
    /**
     * Download logs as file
     */
    async downloadLogs() {
        try {
            const logs = await this.exportLogs();
            const logText = logs.map(log => {
                const data = log.data ? ` | ${JSON.stringify(log.data)}` : '';
                return `${log.timestamp} [${log.level}] ${log.message}${data}`;
            }).join('\n');
            
            const blob = new Blob([logText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            
            if (typeof chrome !== 'undefined' && chrome.downloads) {
                await chrome.downloads.download({
                    url: url,
                    filename: `mkd-debug-${timestamp}.txt`
                });
            } else {
                // Fallback for popup/content script
                const a = document.createElement('a');
                a.href = url;
                a.download = `mkd-debug-${timestamp}.txt`;
                a.click();
                URL.revokeObjectURL(url);
            }
            
            this.info('Logs downloaded successfully');
        } catch (e) {
            this.error('Failed to download logs', e);
        }
    }
    
    /**
     * Clear all logs
     */
    async clearLogs() {
        this.logs = [];
        
        try {
            if (typeof chrome !== 'undefined' && chrome.storage) {
                const result = await chrome.storage.local.get(null);
                const logKeys = Object.keys(result).filter(key => key.startsWith('mkd_log_'));
                if (logKeys.length > 0) {
                    await chrome.storage.local.remove(logKeys);
                }
            }
        } catch (e) {
            this.error('Failed to clear storage logs', e);
        }
        
        this.info('All logs cleared');
    }
    
    /**
     * Log methods
     */
    error(message, data = null) {
        this.addLog(this.LEVELS.ERROR, message, data);
    }
    
    warn(message, data = null) {
        this.addLog(this.LEVELS.WARN, message, data);
    }
    
    info(message, data = null) {
        this.addLog(this.LEVELS.INFO, message, data);
    }
    
    debug(message, data = null) {
        this.addLog(this.LEVELS.DEBUG, message, data);
    }
    
    trace(message, data = null) {
        this.addLog(this.LEVELS.TRACE, message, data);
    }
    
    /**
     * Special logging methods
     */
    
    /**
     * Log native messaging activity
     */
    nativeMessage(direction, message, success = true) {
        const level = success ? this.LEVELS.DEBUG : this.LEVELS.ERROR;
        this.addLog(level, `Native messaging ${direction}`, {
            message: message,
            success: success,
            timestamp: Date.now()
        });
    }
    
    /**
     * Log Chrome API calls
     */
    chromeApi(api, method, params = null, result = null, error = null) {
        const level = error ? this.LEVELS.ERROR : this.LEVELS.DEBUG;
        this.addLog(level, `Chrome API: ${api}.${method}`, {
            params,
            result,
            error: error?.message || error,
            lastError: chrome.runtime?.lastError?.message
        });
    }
    
    /**
     * Log extension events
     */
    extensionEvent(eventType, details = null) {
        this.addLog(this.LEVELS.INFO, `Extension event: ${eventType}`, details);
    }
    
    /**
     * Log recording activity
     */
    recordingActivity(action, data = null) {
        this.addLog(this.LEVELS.INFO, `Recording: ${action}`, data);
    }
    
    /**
     * Performance timing
     */
    performance(label, startTime, endTime = null) {
        const duration = (endTime || performance.now()) - startTime;
        this.addLog(this.LEVELS.DEBUG, `Performance: ${label}`, {
            duration: `${duration.toFixed(2)}ms`,
            startTime,
            endTime: endTime || performance.now()
        });
    }
}

// Create global instance
const debugLogger = new DebugLogger();

// Export for different environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DebugLogger;
}

if (typeof window !== 'undefined') {
    window.DebugLogger = DebugLogger;
    window.debugLogger = debugLogger;
}