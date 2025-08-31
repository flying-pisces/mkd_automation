# MKD Automation - Replay System Usage Guide

## 🎯 Overview

The MKD Automation Replay System provides two powerful modes for working with recorded sessions:

1. **👁️ Visual Replay** - Review and analyze recordings with visual annotations
2. **🤖 Action Replay** - Reproduce recorded actions programmatically

---

## 📋 Prerequisites

### Required Dependencies
```bash
pip install pynput pillow
```

### System Requirements
- **Python 3.8+**
- **Windows/macOS/Linux** support
- **Screen resolution**: Any (adapts automatically)
- **Input permissions**: Required for Action Replay mode

---

## 🚀 Quick Start

### 1. Record a Session
First, create a recording using the GUI recorder:

```bash
# Launch the recorder with stopwatch
python gui_recorder_stopwatch.py
```

1. Click **"Start Recording"** (main window minimizes)
2. Perform your actions (stopwatch shows in corner)
3. Click **X** on stopwatch to stop
4. Recording saved to `recordings/` directory

### 2. Launch Replay Manager
```bash
# Start replay mode selector
python -m mkd.replay.replay_manager

# Or directly specify recording
python -m mkd.replay.replay_manager recordings/your_recording_folder
```

---

## 👁️ Visual Replay Mode

### Purpose
- **Review** what actions were performed
- **Training** new users on workflows  
- **Debugging** automation issues
- **Documentation** and audit trails

### How to Use

#### Step 1: Select Visual Replay
1. Launch Replay Manager
2. Load your recording directory
3. Click **"▶ Start Visual Replay"**

#### Step 2: Review Interface
```
┌─── Visual Replay Window ────────────────────────┐
│  ┌─────────────────────────────────────────┐    │
│  │                                         │    │
│  │     [Screenshot with annotations]       │    │  
│  │                                         │    │
│  │  🔴 Click indicators                    │    │
│  │  🟢 Mouse trails                        │    │
│  │  📝 Keyboard overlays                   │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ▶ ⏸ ⏹ ⏮ ⏭    [Timeline Slider]    1.0x       │
│                                                  │
│  Display Settings: ☑Click ☑Mouse ☑Keyboard     │
│                                                  │
│  Action Timeline: [Event list with timestamps]  │
└──────────────────────────────────────────────────┘
```

#### Step 3: Navigation Controls
- **▶ Play**: Start automatic playback
- **⏸ Pause**: Pause playback
- **⏹ Stop**: Stop and return to start
- **⏮ Previous**: Go to previous frame
- **⏭ Next**: Go to next frame
- **Slider**: Seek to specific time
- **Speed**: Adjust playback speed (0.5x to 5x)

#### Step 4: Visual Elements
- **Red ripples**: Mouse clicks with button labels
- **Green dots**: Mouse movement trails
- **Text overlays**: Keyboard input display
- **Timestamps**: Show exact timing of actions

### Features
- **Frame-by-frame control** for detailed analysis
- **Action synchronization** with screenshots
- **Customizable annotations** (show/hide elements)
- **Export capability** (screenshots, sequences)
- **Multi-speed playback** (slow motion to fast forward)

---

## 🤖 Action Replay Mode

### Purpose
- **Automate** repetitive tasks
- **Reproduce** exact workflows
- **Test** applications with recorded scenarios
- **Cross-system** task replication

### ⚠️ Safety First
Action Replay **controls your mouse and keyboard**. Before starting:

- ✅ Save all open work
- ✅ Close sensitive applications  
- ✅ Understand what will be replayed
- ✅ Know emergency stop (ESC key)
- ✅ Test with dry run first

### How to Use

#### Step 1: Select Action Replay
1. Launch Replay Manager
2. Load your recording directory
3. Click **"▶ Start Action Replay"**
4. **Read and accept** the safety warning

#### Step 2: Control Panel
```
┌─── Action Replay Control Panel ─────────────────┐
│                                                  │
│  ⚠️ AUTOMATION MODE ACTIVE                      │
│                                                  │
│  Progress: ████████░░░░░░░ 60%                 │
│  Action: 45 of 75                              │
│  Current: Clicking button at (450, 300)        │
│                                                  │
│  Speed: ◯0.5x ●1.0x ◯2.0x ◯5.0x               │
│                                                  │
│  Options:                                       │
│  ☑ Use original timing                         │
│  ☐ Skip mouse movements                        │
│  ☐ Dry run (preview only)                      │
│                                                  │
│  [▶ Start] [⏸ Pause] [⏹ Stop]                 │
│                                                  │
│  Press ESC at any time for emergency stop      │
└──────────────────────────────────────────────────┘
```

#### Step 3: Configuration Options
- **Speed Control**: Adjust playback speed
  - **0.5x**: Slow motion (good for debugging)
  - **1.0x**: Original speed
  - **2.0x**: Fast (quick automation)
  - **5.0x**: Very fast (bulk operations)

- **Timing Options**:
  - **Use original timing**: Preserve delays between actions
  - **Skip mouse movements**: Only execute clicks/keys
  - **Dry run**: Preview without executing (safe testing)

#### Step 4: Execution Control
- **▶ Start**: Begin action replay
- **⏸ Pause/Resume**: Temporarily halt execution
- **⏹ Stop**: Terminate replay immediately
- **ESC Key**: Emergency stop (works anytime)

#### Step 5: Safety Features
- **Pre-execution confirmation** with action count
- **Real-time progress** monitoring
- **Error handling** with pause-on-error option
- **Boundary validation** (keeps actions on screen)
- **Duration limits** to prevent runaway automation

### Advanced Features

#### Dry Run Mode
Test your replay without executing actions:
```bash
# Enable dry run in options
☑ Dry run (preview only)
```
- Shows what **would** be executed
- No actual mouse/keyboard control
- Safe for testing unknown recordings
- Validates timing and sequence

#### Smart Adaptation
The system adapts to different environments:
- **Resolution scaling**: Adjusts coordinates for different screens
- **Window detection**: Waits for target applications
- **Error recovery**: Handles unexpected popups or changes

---

## 📁 Working with Recordings

### Recording Structure
```
recordings/
└── recording_20250830_143022/
    ├── recording.mkd           # Action data
    ├── metadata.json          # Recording info
    ├── frame_0000.png         # Screenshots
    ├── frame_0001.png
    └── ...
```

### Loading Recordings
1. **Auto-detect**: Place in `recordings/` directory
2. **Browse**: Use "📁 Load Recording" button
3. **Command line**: Specify path as argument

### Recording Information
The manager shows:
- **Duration**: Total recording time
- **Actions**: Number of recorded actions
- **Screenshots**: Frame count for visual replay
- **Platform**: Where it was recorded

---

## 🛠️ Troubleshooting

### Common Issues

#### Visual Replay Problems

**Issue**: No screenshots displayed
```
Solution: Ensure PNG files exist in recording directory
Check: frame_0000.png, frame_0001.png, etc.
```

**Issue**: Annotations not showing
```
Solution: Check display settings checkboxes
- ☑ Show Click Indicators
- ☑ Show Mouse Trail  
- ☑ Show Keyboard Input
```

**Issue**: Timeline not working
```
Solution: Verify metadata.json contains action timestamps
Check: File exists and has valid JSON format
```

#### Action Replay Problems

**Issue**: Actions not executing
```
Solution: Check pynput installation and permissions
Command: pip install --upgrade pynput
Admin: May need elevated permissions on some systems
```

**Issue**: Mouse clicks in wrong locations
```
Solution: Check screen resolution compatibility
- Recording: 1920x1080
- Current: Different resolution
Workaround: Use same resolution or coordinate scaling
```

**Issue**: Emergency stop not working
```
Solution: Ensure ESC key listener is active
Check: Control panel shows "Press ESC for emergency stop"
Alternative: Close control panel window
```

### Getting Help

#### Test System Health
```bash
python test_replay_system.py
```
Runs comprehensive tests and generates report.

#### Enable Debug Mode
```python
# In replay scripts, add:
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Dependencies
```bash
python -c "import pynput, PIL; print('Dependencies OK')"
```

---

## 📊 Best Practices

### For Visual Replay
1. **Use for training**: Show new users how tasks are performed
2. **Document workflows**: Export frames for procedures
3. **Debug automation**: See exactly what was recorded
4. **Audit compliance**: Review what actions were taken

### For Action Replay
1. **Start with dry run**: Always test before live execution
2. **Use appropriate speed**: Slower for complex UIs, faster for simple tasks
3. **Save critical work**: Before running automation
4. **Monitor progress**: Stay near computer during execution
5. **Test environment**: Run in similar conditions to recording

### Security Considerations
1. **Review recordings**: Understand what will be replayed
2. **Sensitive data**: Be careful with login credentials
3. **System access**: Action replay has full input control
4. **Network actions**: Consider firewall/security implications

---

## 🎯 Use Cases

### Visual Replay Examples
- **Software training**: Show how to use applications
- **Bug documentation**: Capture and review issues
- **Process documentation**: Create step-by-step guides
- **Quality assurance**: Review automated test runs

### Action Replay Examples
- **Data entry**: Automate repetitive form filling
- **Testing**: Replay user scenarios consistently
- **Setup automation**: Configure systems identically
- **Task delegation**: Let computer handle routine work

---

## 🔧 Integration

### With Recording System
```python
# Record → Replay workflow
from mkd.core.session_manager import SessionManager
from mkd.replay.replay_manager import ReplayManager, ReplayMode

# Record
session = SessionManager()
session.start_recording()
# ... perform actions ...
session.stop_recording()

# Replay
manager = ReplayManager()
manager.load_recording(recording_dir)
manager.launch_replay(ReplayMode.VISUAL)  # or ACTION
```

### Custom Integrations
```python
# Custom replay with options
from mkd.replay.action_replay import ActionReplayEngine, ReplayOptions

engine = ActionReplayEngine()
engine.load_recording(recording_dir)

options = ReplayOptions(
    playback_speed=2.0,
    skip_mouse_moves=True,
    dry_run=False
)

engine.start_replay(options)
```

---

## ✅ System Status

### Test Results
```
Total Tests: 25
Passed: 25 (100.0%)
Failed: 0
Duration: 0.28 seconds

✓ Dependencies: pynput, PIL, tkinter
✓ Visual Replay Engine: Functional
✓ Action Replay Engine: Functional  
✓ Safety Systems: Operational
✓ Integration: Complete
```

### Version Information
- **Replay System**: v2.0
- **Python**: 3.8+ required
- **Platform**: Windows/macOS/Linux
- **Status**: ✅ Production Ready

---

## 📞 Support

### Self-Test
Run the test suite to verify system health:
```bash
python test_replay_system.py
```

### Documentation
- **REPLAY_STRATEGIES.md**: Technical architecture details
- **GUI_TESTING.md**: Recording interface guide
- **test_report_replay.txt**: Latest test results

### Feedback
Report issues and suggestions through project issue tracker.

---

**Ready to use both Visual and Action Replay modes! 🎉**

**Remember**: Visual Replay is safe for review, Action Replay controls your system. Always understand what you're replaying before using Action mode.