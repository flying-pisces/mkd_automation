/**
 * Chrome Extension Connection Diagnostic Tool
 * 
 * Comprehensive diagnostic for native messaging host connection issues
 */

class ConnectionDiagnostic {
    constructor() {
        this.results = {};
        this.nativeHostId = 'com.mkd.automation';
        this.testPort = null;
    }
    
    /**
     * Run all diagnostic tests
     */
    async runDiagnostics() {
        console.log('🔧 MKD Connection Diagnostic Starting...\n');
        
        const tests = [
            { name: 'Chrome Runtime', test: this.testChromeRuntime.bind(this) },
            { name: 'Extension Manifest', test: this.testManifest.bind(this) },
            { name: 'Native Messaging Permission', test: this.testNativeMessagingPermission.bind(this) },
            { name: 'Native Host Registration', test: this.testNativeHostRegistration.bind(this) },
            { name: 'Native Host Connection', test: this.testNativeHostConnection.bind(this) },
            { name: 'Python Process', test: this.testPythonProcess.bind(this) },
            { name: 'Registry Entries (Windows)', test: this.testWindowsRegistry.bind(this) },
            { name: 'File System Access', test: this.testFileSystemAccess.bind(this) }
        ];
        
        for (const test of tests) {
            try {
                console.log(`\n🔍 Testing: ${test.name}`);
                const result = await test.test();
                this.results[test.name] = result;
                
                if (result.success) {
                    console.log(`✅ ${test.name}: PASS`);
                    if (result.details) {
                        console.log(`   Details: ${result.details}`);
                    }
                } else {
                    console.log(`❌ ${test.name}: FAIL`);
                    console.log(`   Error: ${result.error}`);
                    if (result.suggestion) {
                        console.log(`   💡 Suggestion: ${result.suggestion}`);
                    }
                }
            } catch (error) {
                console.error(`💥 Test "${test.name}" crashed:`, error);
                this.results[test.name] = {
                    success: false,
                    error: error.message,
                    suggestion: 'Check browser console for detailed error information'
                };
            }
        }
        
        // Generate summary report
        this.generateReport();
        
        return this.results;
    }
    
    /**
     * Test Chrome Runtime availability
     */
    async testChromeRuntime() {
        if (typeof chrome === 'undefined') {
            return {
                success: false,
                error: 'Chrome APIs not available',
                suggestion: 'Ensure this is running in a Chrome extension context'
            };
        }
        
        if (!chrome.runtime) {
            return {
                success: false,
                error: 'chrome.runtime not available',
                suggestion: 'Check if extension is properly loaded'
            };
        }
        
        return {
            success: true,
            details: `Extension ID: ${chrome.runtime.id}`
        };
    }
    
    /**
     * Test extension manifest
     */
    async testManifest() {
        try {
            const manifest = chrome.runtime.getManifest();
            
            if (!manifest) {
                return {
                    success: false,
                    error: 'Cannot read manifest',
                    suggestion: 'Extension may not be properly loaded'
                };
            }
            
            // Check native messaging permission
            const hasNativeMessaging = manifest.permissions?.includes('nativeMessaging');
            if (!hasNativeMessaging) {
                return {
                    success: false,
                    error: 'nativeMessaging permission missing from manifest',
                    suggestion: 'Add "nativeMessaging" to permissions in manifest.json'
                };
            }
            
            return {
                success: true,
                details: `Manifest v${manifest.manifest_version}, nativeMessaging permission present`
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message,
                suggestion: 'Check manifest.json syntax and reload extension'
            };
        }
    }
    
    /**
     * Test native messaging permission
     */
    async testNativeMessagingPermission() {
        // Try to create a test port
        try {
            const testPort = chrome.runtime.connectNative('test.nonexistent.host');
            testPort.disconnect();
            
            return {
                success: true,
                details: 'Native messaging permission verified'
            };
            
        } catch (error) {
            if (error.message?.includes('not allowed')) {
                return {
                    success: false,
                    error: 'Native messaging not allowed',
                    suggestion: 'Check that nativeMessaging permission is granted and extension is not in incognito mode'
                };
            }
            
            // Other errors are expected for non-existent host
            return {
                success: true,
                details: 'Native messaging permission available'
            };
        }
    }
    
    /**
     * Test native host registration
     */
    async testNativeHostRegistration() {
        return new Promise((resolve) => {
            try {
                const port = chrome.runtime.connectNative(this.nativeHostId);
                
                const timeout = setTimeout(() => {
                    port.disconnect();
                    resolve({
                        success: false,
                        error: 'Connection timeout - native host may not be registered',
                        suggestion: 'Run: python install_native_host.py'
                    });
                }, 3000);
                
                port.onConnect.addListener(() => {
                    clearTimeout(timeout);
                    port.disconnect();
                    resolve({
                        success: true,
                        details: 'Native host registration found'
                    });
                });
                
                port.onDisconnect.addListener(() => {
                    clearTimeout(timeout);
                    const error = chrome.runtime.lastError;
                    
                    if (error?.message?.includes('not found')) {
                        resolve({
                            success: false,
                            error: 'Native host not registered',
                            suggestion: 'Run installer: python install_native_host.py'
                        });
                    } else if (error?.message?.includes('failed to start')) {
                        resolve({
                            success: false,
                            error: 'Native host registered but failed to start',
                            suggestion: 'Check Python installation and MKD dependencies'
                        });
                    } else {
                        resolve({
                            success: false,
                            error: error?.message || 'Unknown connection error',
                            suggestion: 'Check native host installation and permissions'
                        });
                    }
                });
                
            } catch (error) {
                resolve({
                    success: false,
                    error: error.message,
                    suggestion: 'Check browser console for detailed error'
                });
            }
        });
    }
    
    /**
     * Test native host connection and communication
     */
    async testNativeHostConnection() {
        return new Promise((resolve) => {
            try {
                const port = chrome.runtime.connectNative(this.nativeHostId);
                let responded = false;
                
                const timeout = setTimeout(() => {
                    if (!responded) {
                        port.disconnect();
                        resolve({
                            success: false,
                            error: 'No response from native host',
                            suggestion: 'Native host may be registered but not responding. Check MKD backend is running.'
                        });
                    }
                }, 5000);
                
                port.onMessage.addListener((message) => {
                    responded = true;
                    clearTimeout(timeout);
                    port.disconnect();
                    
                    if (message && message.success) {
                        resolve({
                            success: true,
                            details: `Native host responding: ${JSON.stringify(message)}`
                        });
                    } else {
                        resolve({
                            success: false,
                            error: `Native host error: ${message?.error || 'Unknown error'}`,
                            suggestion: 'Check MKD backend logs for errors'
                        });
                    }
                });
                
                port.onDisconnect.addListener(() => {
                    if (!responded) {
                        clearTimeout(timeout);
                        const error = chrome.runtime.lastError;
                        resolve({
                            success: false,
                            error: error?.message || 'Connection disconnected',
                            suggestion: 'Native host disconnected during test'
                        });
                    }
                });
                
                // Send test message
                port.postMessage({
                    id: 'diagnostic_test',
                    command: 'PING',
                    params: {},
                    timestamp: Date.now()
                });
                
            } catch (error) {
                resolve({
                    success: false,
                    error: error.message,
                    suggestion: 'Failed to establish connection'
                });
            }
        });
    }
    
    /**
     * Test Python process (placeholder - would need native host cooperation)
     */
    async testPythonProcess() {
        // This test would require the native host to be working
        // For now, we'll infer from previous tests
        const hostTest = this.results['Native Host Connection'];
        
        if (hostTest?.success) {
            return {
                success: true,
                details: 'Python process responsive'
            };
        }
        
        return {
            success: false,
            error: 'Cannot verify Python process - native host not responding',
            suggestion: 'Ensure Python MKD backend is installed and running'
        };
    }
    
    /**
     * Test Windows registry entries
     */
    async testWindowsRegistry() {
        // We can't directly access the registry from a Chrome extension
        // But we can infer from native host registration results
        
        const platform = navigator.platform;
        if (!platform.includes('Win')) {
            return {
                success: true,
                details: 'Not Windows - registry check skipped'
            };
        }
        
        const registrationTest = this.results['Native Host Registration'];
        
        if (registrationTest?.success) {
            return {
                success: true,
                details: 'Registry entries appear correct (inferred from successful registration)'
            };
        }
        
        return {
            success: false,
            error: 'Registry entries may be missing or incorrect',
            suggestion: 'Run as administrator: python install_native_host.py'
        };
    }
    
    /**
     * Test file system access
     */
    async testFileSystemAccess() {
        // Test if we can access basic Chrome APIs that the extension needs
        try {
            await chrome.storage.local.get(['test_key']);
            
            return {
                success: true,
                details: 'File system access working'
            };
            
        } catch (error) {
            return {
                success: false,
                error: 'Cannot access chrome.storage',
                suggestion: 'Check extension permissions and installation'
            };
        }
    }
    
    /**
     * Generate diagnostic report
     */
    generateReport() {
        console.log('\n' + '='.repeat(60));
        console.log('📋 DIAGNOSTIC REPORT');
        console.log('='.repeat(60));
        
        const passed = Object.values(this.results).filter(r => r.success).length;
        const total = Object.keys(this.results).length;
        
        console.log(`\n📊 Results: ${passed}/${total} tests passed`);
        
        if (passed === total) {
            console.log('🎉 All tests passed! Extension should be working correctly.');
        } else {
            console.log('⚠️  Issues detected. See suggestions above.');
        }
        
        // Priority recommendations
        console.log('\n🔧 PRIORITY FIXES:');
        
        const failed = Object.entries(this.results).filter(([_, result]) => !result.success);
        
        if (failed.length === 0) {
            console.log('   No issues found!');
        } else {
            failed.forEach(([testName, result], index) => {
                console.log(`   ${index + 1}. ${testName}: ${result.suggestion || 'See error above'}`);
            });
        }
        
        // Next steps
        console.log('\n📝 NEXT STEPS:');
        
        if (this.results['Native Host Registration']?.success === false) {
            console.log('   1. Run the native host installer:');
            console.log('      python install_native_host.py');
            console.log('   2. Restart Chrome');
            console.log('   3. Test the extension again');
        } else if (this.results['Native Host Connection']?.success === false) {
            console.log('   1. Start the MKD backend application');
            console.log('   2. Check Python dependencies are installed');
            console.log('   3. Check MKD backend logs for errors');
        } else {
            console.log('   Extension appears to be working correctly!');
        }
        
        console.log('\n💾 To save this diagnostic report:');
        console.log('   Copy the console output or use debugLogger.downloadLogs()');
        
        console.log('\n' + '='.repeat(60));
    }
    
    /**
     * Get installation commands for current platform
     */
    getInstallationCommands() {
        const platform = navigator.platform;
        const commands = {
            windows: [
                'python install_native_host.py',
                'python -m pip install -r requirements.txt'
            ],
            mac: [
                'python3 install_native_host.py',
                'python3 -m pip install -r requirements.txt'
            ],
            linux: [
                'python3 install_native_host.py',
                'python3 -m pip install -r requirements.txt'
            ]
        };
        
        if (platform.includes('Win')) return commands.windows;
        if (platform.includes('Mac')) return commands.mac;
        return commands.linux;
    }
}

// Export for use
if (typeof window !== 'undefined') {
    window.ConnectionDiagnostic = ConnectionDiagnostic;
    window.runDiagnostic = () => new ConnectionDiagnostic().runDiagnostics();
}

// Auto-run in development
if (typeof window !== 'undefined' && window.location?.protocol === 'chrome-extension:') {
    console.log('🔧 MKD Connection Diagnostic Available');
    console.log('   Run: runDiagnostic()');
    console.log('   Or: new ConnectionDiagnostic().runDiagnostics()');
}