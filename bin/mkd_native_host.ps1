# MKD Automation Native Host - PowerShell Launcher
param($args)

$ErrorActionPreference = "Stop"
$ProjectRoot = "C:\project\mkd_automation"

try {
    # Check Python availability
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Python not found. Please install Python 3.8+ and add to PATH."
        exit 1
    }
    
    # Set working directory and PYTHONPATH
    Set-Location $ProjectRoot
    $env:PYTHONPATH = "$ProjectRoot\src;$($env:PYTHONPATH)"
    
    # Launch native host
    python -m mkd_v2.native_host.host @args
    exit $LASTEXITCODE
}
catch {
    Write-Error "Failed to start MKD native host: $_"
    exit 1
}
