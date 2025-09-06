"""
Desktop Automation Examples
Real-world scenarios demonstrating MKD's desktop automation capabilities.
"""
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mkd.desktop.controller import DesktopController
from mkd.desktop.application_manager import ApplicationManager
from mkd.desktop.file_operations import FileOperations
from mkd.desktop.windows_automation import WindowsDesktopAutomation


class DesktopAutomationExamples:
    """Collection of practical desktop automation examples."""
    
    def __init__(self):
        self.desktop = DesktopController()
        self.app_manager = ApplicationManager()
        self.file_ops = FileOperations()
        self.win_auto = WindowsDesktopAutomation()
    
    def example_1_organize_desktop(self):
        """
        Example 1: Desktop Organization
        Creates folders and organizes files on desktop.
        """
        print("Example 1: Desktop Organization")
        print("-" * 35)
        
        desktop_path = Path.home() / "Desktop"
        
        # Create organization folders
        folders = ["Documents", "Images", "Downloads", "Projects"]
        
        for folder in folders:
            folder_path = desktop_path / folder
            print(f"Creating folder: {folder}")
            self.file_ops.create_folder(str(folder_path))
        
        # List desktop contents
        print("\nDesktop contents after organization:")
        contents = self.file_ops.list_directory(str(desktop_path))
        for item in contents[:10]:  # Show first 10 items
            print(f"  {'[DIR]' if item['is_directory'] else '[FILE]'} {item['name']}")
    
    def example_2_system_maintenance(self):
        """
        Example 2: System Maintenance Tasks
        Opens system tools and performs maintenance checks.
        """
        print("\nExample 2: System Maintenance")
        print("-" * 30)
        
        if not self.win_auto.is_available:
            print("Windows APIs not available for this example.")
            return
        
        print("Opening system maintenance tools...")
        
        # Open Task Manager to check system performance
        print("1. Opening Task Manager")
        self.win_auto.open_task_manager()
        time.sleep(3)
        
        # Open Device Manager
        print("2. Opening Device Manager")
        self.win_auto.open_device_manager()
        time.sleep(3)
        
        # Open Services
        print("3. Opening Services")
        self.win_auto.open_services()
        time.sleep(3)
        
        print("System tools opened. Check them manually and close when done.")
    
    def example_3_development_workflow(self):
        """
        Example 3: Development Workflow Automation
        Sets up a development environment.
        """
        print("\nExample 3: Development Workflow Setup")
        print("-" * 40)
        
        # Create project structure
        project_path = Path("new_project")
        print(f"Creating project structure in: {project_path}")
        
        project_folders = [
            "src",
            "tests",
            "docs", 
            "config",
            "data"
        ]
        
        for folder in project_folders:
            folder_path = project_path / folder
            self.file_ops.create_folder(str(folder_path))
            print(f"  Created: {folder}")
        
        # Create initial files
        files_to_create = {
            "README.md": "# New Project\n\nProject description here.",
            "requirements.txt": "# Project dependencies\n",
            "src/main.py": "#!/usr/bin/env python3\n\"\"\"\nMain application entry point.\n\"\"\"\n\nif __name__ == '__main__':\n    print('Hello, World!')\n",
            ".gitignore": "__pycache__/\n*.pyc\n.env\n"
        }
        
        for file_path, content in files_to_create.items():
            full_path = project_path / file_path
            self.file_ops.create_file(str(full_path), content)
            print(f"  Created: {file_path}")
        
        # Open project folder
        print("Opening project folder...")
        self.file_ops.open_folder(str(project_path))
    
    def example_4_batch_file_processing(self):
        """
        Example 4: Batch File Processing
        Creates multiple files and demonstrates batch operations.
        """
        print("\nExample 4: Batch File Processing")
        print("-" * 35)
        
        batch_folder = Path("batch_processing_demo")
        self.file_ops.create_folder(str(batch_folder))
        
        # Create sample files
        print("Creating sample files for batch processing...")
        for i in range(1, 6):
            file_name = f"sample_{i:02d}.txt"
            file_path = batch_folder / file_name
            content = f"Sample file #{i}\nCreated for batch processing demo.\nTimestamp: {time.ctime()}"
            self.file_ops.create_file(str(file_path), content)
            print(f"  Created: {file_name}")
        
        # Demonstrate batch operations
        print("\nBatch operations:")
        
        # List all files
        files = self.file_ops.search_files(str(batch_folder), "*.txt")
        print(f"Found {len(files)} text files")
        
        # Create backup folder and copy files
        backup_folder = batch_folder / "backup"
        self.file_ops.create_folder(str(backup_folder))
        
        for file_path in files:
            source_file = Path(file_path)
            backup_file = backup_folder / source_file.name
            self.file_ops.copy_file(str(source_file), str(backup_file))
            print(f"  Backed up: {source_file.name}")
        
        print("Batch processing completed!")
    
    def example_5_application_automation(self):
        """
        Example 5: Application Automation
        Launches applications and demonstrates basic automation.
        """
        print("\nExample 5: Application Automation")
        print("-" * 35)
        
        # Launch multiple applications
        apps_to_launch = ["notepad", "calculator"]
        launched_apps = []
        
        for app in apps_to_launch:
            print(f"Launching {app}...")
            app_info = self.app_manager.launch_application(app)
            if app_info:
                launched_apps.append(app_info)
                print(f"  {app} launched with PID: {app_info['pid']}")
        
        time.sleep(2)
        
        # Demonstrate basic automation in Notepad
        if any(app['command'] == 'notepad.exe' for app in launched_apps):
            print("\nAutomating Notepad...")
            
            # Type some text (assuming Notepad is active)
            sample_text = "This text was typed automatically by MKD Automation!\n"
            sample_text += "Demonstrating desktop automation capabilities.\n"
            sample_text += f"Current time: {time.ctime()}"
            
            from mkd.desktop.actions import DesktopAction
            
            type_action = DesktopAction.type_text(sample_text)
            self.desktop.execute_action(type_action)
            print("  Text typed into Notepad")
            
            # Save file using keyboard shortcut
            time.sleep(1)
            ctrl_s_action = DesktopAction.key_combination(["ctrl", "s"])
            self.desktop.execute_action(ctrl_s_action)
            print("  Save dialog opened")
            
            time.sleep(1)
            # Type filename
            filename_action = DesktopAction.type_text("automation_demo.txt")
            self.desktop.execute_action(filename_action)
            
            # Press Enter to save
            enter_action = DesktopAction.key_press("Return")
            self.desktop.execute_action(enter_action)
            print("  File saved")
        
        # Clean up - close applications
        print("\nCleaning up applications...")
        time.sleep(2)
        
        for app in apps_to_launch:
            if self.app_manager.is_application_running(app):
                self.app_manager.close_application(app)
                print(f"  Closed {app}")
    
    def example_6_screen_automation(self):
        """
        Example 6: Screen Automation
        Demonstrates screen capture and mouse automation.
        """
        print("\nExample 6: Screen Automation")
        print("-" * 30)
        
        # Take screenshot
        print("Taking desktop screenshot...")
        try:
            from mkd.desktop.actions import DesktopAction
            screenshot_path = "desktop_screenshot.png"
            screenshot_action = DesktopAction.screenshot(screenshot_path)
            result = self.desktop.execute_action(screenshot_action)
            print(f"Screenshot saved to: {result}")
        except Exception as e:
            print(f"Screenshot failed: {e}")
        
        # Demonstrate mouse movements in a pattern
        print("Demonstrating mouse movement pattern...")
        
        # Move mouse in a square pattern
        center_x, center_y = 800, 400
        square_size = 100
        
        positions = [
            (center_x - square_size, center_y - square_size),  # Top-left
            (center_x + square_size, center_y - square_size),  # Top-right
            (center_x + square_size, center_y + square_size),  # Bottom-right
            (center_x - square_size, center_y + square_size),  # Bottom-left
            (center_x - square_size, center_y - square_size),  # Back to start
        ]
        
        from mkd.desktop.actions import DesktopAction
        
        for i, (x, y) in enumerate(positions):
            print(f"  Moving to position {i+1}: ({x}, {y})")
            move_action = DesktopAction.mouse_move(x, y)
            self.desktop.execute_action(move_action)
            time.sleep(0.5)
        
        print("Mouse pattern completed!")
    
    def run_all_examples(self):
        """Run all desktop automation examples."""
        print("MKD Desktop Automation - Practical Examples")
        print("=" * 55)
        print("These examples demonstrate real-world automation scenarios.")
        print("Each example showcases different aspects of desktop control.\n")
        
        try:
            self.example_1_organize_desktop()
            time.sleep(2)
            
            self.example_2_system_maintenance()
            time.sleep(2)
            
            self.example_3_development_workflow()
            time.sleep(2)
            
            self.example_4_batch_file_processing()
            time.sleep(2)
            
            self.example_5_application_automation()
            time.sleep(2)
            
            self.example_6_screen_automation()
            
            print("\n" + "=" * 55)
            print("All examples completed successfully!")
            print("You can now use these patterns in your own automation scripts.")
            
        except KeyboardInterrupt:
            print("\nExamples interrupted by user.")
        except Exception as e:
            print(f"\nExample error: {e}")


def main():
    """Main entry point for desktop automation examples."""
    examples = DesktopAutomationExamples()
    examples.run_all_examples()


if __name__ == "__main__":
    main()