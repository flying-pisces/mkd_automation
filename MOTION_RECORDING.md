# Motion Recording Usage

## Quick Start - Record Motions with One Command

### Option 1: Simple Test Recording
```bash
python test_recording.py
```
This creates a test recording with simulated actions and saves it to `recordings/` folder.

### Option 2: Reliable Motion Recording (RECOMMENDED)
```bash
# Uses pynput library - most reliable
python record_motions_pynput.py
```

### Option 3: Alternative Recording (if pynput has issues)
```bash
# Install required libraries first
python install_recording_deps.py

# Then start recording (may have compatibility issues)
python record_motions.py
```

### Option 4: Test pynput Recording
```bash
python test_pynput_recording.py
```
This tests the pynput recording system with 5 seconds of simulated actions.

## Files Created

### `record_motions_pynput.py` ⭐ RECOMMENDED
**Most reliable recording script** using pynput library - equivalent to clicking "Start Recording" in Chrome extension.

**Features:**
- ✅ Stable cross-platform mouse/keyboard capture
- ✅ Simple controls ('q' to stop, 'p' to pause)
- ✅ Automatic file saving
- ✅ No crashes from event handling

**Controls:**
- **'q'** - Stop recording and save
- **'p'** - Pause/Resume recording

### `record_motions.py`
**Alternative recording script** - may have compatibility issues on some systems.

**Features:**
- ✅ Records mouse movements and clicks
- ✅ Records keyboard input  
- ✅ Global hotkeys for control
- ✅ Automatic file saving
- ✅ Real-time feedback

**Controls:**
- **Ctrl+Shift+S** - Stop and save recording
- **Ctrl+Shift+Q** - Quit without saving  
- **Ctrl+Shift+P** - Pause/Resume
- **Enter** - Manual stop (when input libs unavailable)

### `test_recording.py` 
**Test script** that simulates recording without requiring mouse/keyboard input.

### `install_recording_deps.py`
**Dependency installer** for motion capture libraries.

## Usage Examples

### Basic Recording
```bash
# Start recording immediately
python record_motions.py

# Your mouse/keyboard actions are now being recorded
# Press Ctrl+Shift+S to stop and save
```

### Test Without Hardware Input
```bash
# Test the recording system
python test_recording.py

# Check the recordings/ folder for output file
```

### Install Dependencies
```bash
# Install mouse and keyboard libraries
python install_recording_deps.py
```

## Output Files

Recordings are saved to `recordings/` folder with format:
- `recording_YYYYMMDD_HHMMSS.mkd` - Live recordings
- `test_recording_YYYYMMDD_HHMMSS.mkd` - Test recordings

## Technical Details

The recording system uses:
- **SessionManager** - Manages recording sessions
- **ScriptStorage** - Saves/loads .mkd files  
- **Action models** - Structured action data
- **Platform detection** - Windows/Mac/Linux support
- **Input libraries** - `keyboard` and `mouse` packages

## Integration with Chrome Extension

This standalone script provides the same core recording functionality as the Chrome extension's "Start Recording" button, but runs independently without requiring a browser.

Both approaches create the same `.mkd` file format for automation scripts.