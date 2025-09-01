/**
 * Debug Logger for MKD Automation Chrome Extension
 * 
 * Provides a simple logging mechanism.
 */

const debugLogger = (() => {
    let verboseLogger = null;

    const setVerboseLogger = (logger) => {
        verboseLogger = logger;
    };

    const info = (...args) => {
        if (verboseLogger) {
            verboseLogger.info(...args);
        } else {
            console.info('[MKD]', ...args);
        }
    };

    const warn = (...args) => {
        if (verboseLogger) {
            verboseLogger.warn(...args);
        } else {
            console.warn('[MKD]', ...args);
        }
    };

    const error = (...args) => {
        if (verboseLogger) {
            verboseLogger.error(...args);
        } else {
            console.error('[MKD]', ...args);
        }
    };

    return {
        setVerboseLogger,
        info,
        warn,
        error,
    };
})();