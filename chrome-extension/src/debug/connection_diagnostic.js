/**
 * Connection Diagnostic Tool for MKD Automation Chrome Extension
 * 
 * Helps diagnose issues with the native messaging connection.
 */

const connectionDiagnostic = (() => {
    const checkConnection = () => {
        return new Promise((resolve) => {
            chrome.runtime.sendMessage({ type: 'GET_CONNECTION_STATUS' }, (response) => {
                if (chrome.runtime.lastError) {
                    resolve({ status: 'error', message: chrome.runtime.lastError.message });
                } else {
                    resolve({ status: 'success', response });
                }
            });
        });
    };

    return {
        checkConnection,
    };
})();
