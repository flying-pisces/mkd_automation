# Conversation UI Examples

This document provides examples of natural language commands that can be used with MKD's conversation interface for desktop automation.

## Mouse Control

### Basic Mouse Actions
```
click at 500, 300
double click at 100, 200
right click at 800, 400
move mouse to 1000, 500
drag from 100, 100 to 200, 200
```

### Mouse with Applications
```
click on the calculator button
double click on the desktop icon
right click on the file manager
click the close button at 950, 20
```

## Keyboard Control

### Text Input
```
type "Hello, World!"
type the message "This is automated text"
enter the text "automation demo"
write "MKD Desktop Automation"
```

### Key Combinations
```
press ctrl+c
press ctrl+v
press alt+tab
press windows+r
press ctrl+shift+esc
hold shift and press arrow down
```

### Special Keys
```
press enter
press escape
press tab
press backspace
press delete
press f5
press windows key
```

## Application Management

### Launching Applications
```
open notepad
launch calculator
start firefox browser
open file explorer
run command prompt
start powershell
open task manager
launch microsoft word
```

### Application Control
```
close notepad
minimize the calculator
maximize the browser window
switch to firefox
bring notepad to front
close all browser windows
restart the application
```

## File and Folder Operations

### Opening Files/Folders
```
open folder C:\Users\Documents
open file C:\temp\example.txt
browse to the downloads folder
open the desktop folder
navigate to C:\Program Files
```

### File Management
```
create folder "New Project"
create file "readme.txt"
copy file from C:\source.txt to C:\dest.txt
move the file to another folder
delete the temporary file
rename file to "new_name.txt"
```

### File Information
```
show file properties
list folder contents
get file size information
show disk usage
search for *.txt files
```

## System Operations

### System Tools
```
open control panel
show task manager
open device manager
launch registry editor
open system services
show system information
```

### System Actions
```
take a screenshot
lock the workstation
show running processes
display window list
get active window info
set clipboard text to "copied text"
get clipboard content
```

## Window Management

### Window Control
```
resize window to 800x600
move window to position 100, 100
minimize all windows
restore the window
tile windows side by side
bring window to front
```

### Window Information
```
list all open windows
show active window details
find window with title "Notepad"
get window position and size
```

## Advanced Automation Sequences

### Development Workflow
```
1. open folder "C:\Projects\MyApp"
2. launch visual studio code
3. open terminal in current folder
4. type "npm install"
5. press enter
```

### File Organization
```
1. create folder "Organized Files" on desktop
2. move all .txt files to the new folder
3. create subfolders for different file types
4. take screenshot of organized desktop
```

### System Maintenance
```
1. open task manager to check performance
2. launch disk cleanup utility
3. open device manager to check drivers
4. take system screenshot for documentation
```

## Command Patterns Recognized

The conversation UI recognizes various natural language patterns:

### Click Commands
- "click at X, Y"
- "click on [target]"
- "double click at X, Y"
- "right click on [target]"

### Type Commands
- "type [text]"
- "enter [text]"
- "write [text]"

### Application Commands
- "open [app]"
- "launch [app]"
- "start [app]"
- "close [app]"

### File Commands
- "open folder [path]"
- "create file [name]"
- "copy file [source] to [destination]"

### Key Commands
- "press [key]"
- "press [modifier]+[key]"
- "hold [key] and press [key]"

## Tips for Best Results

1. **Be Specific**: Use exact coordinates for mouse actions
2. **Use Full Paths**: Specify complete file paths when possible
3. **Wait Commands**: Add "wait 2 seconds" between actions if needed
4. **Error Handling**: The system will report if commands cannot be executed
5. **Natural Language**: You can use conversational language - the parser is flexible

## Error Messages and Solutions

### Common Issues
- **"Application not found"**: Check if the application is installed
- **"File does not exist"**: Verify the file path is correct
- **"Invalid coordinates"**: Ensure mouse coordinates are within screen bounds
- **"Permission denied"**: Some actions may require administrator privileges

### Solutions
- Use full application names or paths
- Check file paths and permissions
- Verify screen resolution for coordinate commands
- Run MKD as administrator for system-level operations

## Integration with Recording

The conversation UI can be combined with MKD's recording capabilities:

1. **Record First**: Record complex sequences manually
2. **Refine with Commands**: Use conversation UI to adjust specific actions
3. **Playback and Modify**: Test sequences and make refinements
4. **Save Scripts**: Store frequently used command sequences

This creates a powerful workflow where you can use both manual recording and natural language commands to create sophisticated desktop automation scripts.