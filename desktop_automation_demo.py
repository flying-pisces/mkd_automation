"""
Desktop Automation Demo
Comprehensive examples showcasing MKD's desktop automation capabilities.
"""
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mkd.desktop.controller import DesktopController
from mkd.desktop.application_manager import ApplicationManager
from mkd.desktop.file_operations import FileOperations
from mkd.desktop.windows_automation import WindowsDesktopAutomation
from mkd.ui.conversation_panel import ConversationPanel


def demo_basic_desktop_actions():
    """Demonstrate basic mouse and keyboard actions."""
    print("Desktop Automation Demo - Basic Actions")
    print("=" * 50)
    
    from mkd.desktop.controller import DesktopController
    from mkd.desktop.actions import DesktopAction
    
    controller = DesktopController()
    
    # Example 1: Mouse movements and clicks
    print("\n1. Mouse Control Examples:")
    print("- Moving mouse to center of screen")
    move_action = DesktopAction.mouse_move(800, 400)
    controller.execute_action(move_action)
    time.sleep(1)
    
    print("- Clicking at current position")
    click_action = DesktopAction.mouse_click(800, 400)
    controller.execute_action(click_action)
    
    print("- Double-clicking")
    controller.execute_action(click_action)
    time.sleep(0.1)
    controller.execute_action(click_action)
    
    # Example 2: Keyboard input
    print("\n2. Keyboard Control Examples:")
    print("- Typing text")
    type_action = DesktopAction.type_text("Hello from MKD Automation!")
    controller.execute_action(type_action)
    
    print("- Key combinations")
    ctrl_a_action = DesktopAction.key_combination(["ctrl", "a"])
    controller.execute_action(ctrl_a_action)
    
    ctrl_c_action = DesktopAction.key_combination(["ctrl", "c"])
    controller.execute_action(ctrl_c_action)
    

def demo_application_management():
    """Demonstrate application launching and management."""
    print("\nApplication Management Demo")
    print("=" * 40)
    
    app_manager = ApplicationManager()
    
    # Example 1: Launch common applications
    print("\n1. Launching Applications:")
    
    print("- Opening Notepad")
    notepad_info = app_manager.launch_application("notepad")
    if notepad_info:
        print(f"  Notepad launched with PID: {notepad_info['pid']}")
    
    print("- Opening Calculator")
    calc_info = app_manager.launch_application("calculator")
    if calc_info:
        print(f"  Calculator launched with PID: {calc_info['pid']}")
    
    time.sleep(2)
    
    # Example 2: Find and manage applications
    print("\n2. Managing Applications:")
    
    print("- Listing running applications (top 5 by memory):")
    running_apps = app_manager.get_running_applications()[:5]
    for app in running_apps:
        print(f"  {app['name']} - PID: {app['pid']} - Memory: {app['memory_mb']}MB")
    
    # Example 3: Close applications
    print("\n3. Closing Applications:")
    if app_manager.is_application_running("notepad"):
        print("- Closing Notepad")
        app_manager.close_application("notepad")
    
    if app_manager.is_application_running("calculator"):
        print("- Closing Calculator") 
        app_manager.close_application("calculator")


def demo_file_operations():
    """Demonstrate file system operations."""
    print("\nFile Operations Demo")
    print("=" * 30)
    
    file_ops = FileOperations()
    demo_folder = Path("demo_files")
    
    # Example 1: Create folders and files
    print("\n1. Creating Files and Folders:")
    
    print(f"- Creating demo folder: {demo_folder}")
    file_ops.create_folder(str(demo_folder))
    
    demo_file = demo_folder / "sample.txt"
    print(f"- Creating sample file: {demo_file}")
    file_ops.create_file(str(demo_file), "This is a sample file created by MKD Automation!")
    
    # Example 2: File information
    print("\n2. File Information:")
    file_info = file_ops.get_file_info(str(demo_file))
    if file_info:
        print(f"  Name: {file_info['name']}")
        print(f"  Size: {file_info['size']} bytes")
        print(f"  Extension: {file_info['extension']}")
    
    # Example 3: Directory listing
    print("\n3. Directory Contents:")
    contents = file_ops.list_directory(str(demo_folder))
    for item in contents:
        print(f"  {'[DIR]' if item['is_directory'] else '[FILE]'} {item['name']}")
    
    # Example 4: File operations
    print("\n4. File Operations:")
    backup_file = demo_folder / "sample_backup.txt"
    print(f"- Copying file to: {backup_file}")
    file_ops.copy_file(str(demo_file), str(backup_file))
    
    print("- Opening demo folder")
    file_ops.open_folder(str(demo_folder))


def demo_windows_specific():
    """Demonstrate Windows-specific automation."""
    print("\nWindows-Specific Automation Demo")
    print("=" * 45)
    
    win_auto = WindowsDesktopAutomation()
    
    if not win_auto.is_available:
        print("Windows APIs not available. Skipping Windows-specific demo.")
        return
    
    # Example 1: Window management
    print("\n1. Window Management:")
    
    print("- Getting list of open windows:")
    windows = win_auto.get_window_list()[:5]  # Show first 5 windows
    for window in windows:
        try:
            title = window['title'].encode('ascii', 'ignore').decode('ascii')
            print(f"  {title} (PID: {window['pid']})")
        except:
            print(f"  [Window] (PID: {window['pid']})")
    
    print("- Getting active window:")
    active_window = win_auto.get_active_window()
    if active_window:
        try:
            title = active_window['title'].encode('ascii', 'ignore').decode('ascii')
            print(f"  Active: {title}")
        except:
            print("  Active: [Window]")
    
    # Example 2: System tools
    print("\n2. System Tools:")
    print("- Opening Task Manager")
    win_auto.open_task_manager()
    
    time.sleep(2)
    
    # Find and close task manager
    task_mgr_hwnd = win_auto.find_window("Task Manager")
    if task_mgr_hwnd:
        print("- Closing Task Manager")
        win_auto.close_window(task_mgr_hwnd)


def demo_conversation_interface():
    """Demonstrate natural language conversation interface."""
    print("\nConversation Interface Demo")
    print("=" * 40)
    
    # Note: ConversationPanel requires GUI parent, so we'll just demonstrate commands
    print("The conversation UI supports natural language commands like:")
    
    # Example commands that would work in the conversation UI
    example_commands = [
        "click at 500, 300",
        "type 'Hello World'",
        "open notepad",
        "press ctrl+c",
        "open folder C:\\Users",
        "create file test.txt",
        "take screenshot",
        "list running applications"
    ]
    
    print("\nExample commands you can use in the conversation UI:")
    for i, cmd in enumerate(example_commands, 1):
        print(f"{i}. \"{cmd}\"")
    
    print("\nThe conversation UI supports natural language commands like:")
    print("- 'Click at coordinates 100, 200'")
    print("- 'Type some text here'")
    print("- 'Open the calculator application'")
    print("- 'Press the Windows key'")
    print("- 'Create a new folder called Documents'")
    print("- 'Take a screenshot of the desktop'")


def cleanup_demo_files():
    """Clean up demo files created during the demonstration."""
    print("\nCleaning up demo files...")
    
    file_ops = FileOperations()
    demo_folder = Path("demo_files")
    
    if demo_folder.exists():
        file_ops.delete_folder(str(demo_folder))
        print("Demo files cleaned up.")


def main():
    """Run all desktop automation demos."""
    print("MKD Desktop Automation - Comprehensive Demo")
    print("=" * 60)
    print("This demo showcases the full desktop automation capabilities of MKD.")
    print("Including mouse/keyboard control, application management, file operations,")
    print("Windows-specific features, and natural language interface.")
    print("\nPress Ctrl+C at any time to stop the demo.")
    
    try:
        # Run all demo sections
        demo_basic_desktop_actions()
        time.sleep(2)
        
        demo_application_management()
        time.sleep(2)
        
        demo_file_operations()
        time.sleep(2)
        
        demo_windows_specific()
        time.sleep(2)
        
        demo_conversation_interface()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("You now have full desktop automation capabilities through MKD.")
        print("Use the GUI conversation interface to control your desktop with natural language.")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    
    except Exception as e:
        print(f"\nDemo error: {e}")
    
    finally:
        # Clean up
        cleanup_demo_files()


if __name__ == "__main__":
    main()