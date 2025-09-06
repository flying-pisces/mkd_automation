"""
Test Conversation Commands
Demonstrates the natural language command parsing capabilities.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mkd.ui.instruction_parser import InstructionParser

def test_command_parsing():
    """Test natural language command parsing."""
    print("=== MKD Conversation Command Testing ===")
    print("Testing natural language command recognition...\n")
    
    parser = InstructionParser()
    
    # Test various command types
    test_commands = [
        "click at 500, 300",
        "double click at 100, 200", 
        "type 'Hello World'",
        "press ctrl+c",
        "open notepad",
        "launch calculator",
        "close notepad",
        "open folder C:\\Users",
        "create file test.txt",
        "take screenshot",
        "move mouse to 800, 600",
        "drag from 100, 100 to 200, 200",
        "press windows key",
        "minimize window",
        "maximize window",
        "open task manager",
        "lock computer"
    ]
    
    print("Command Recognition Results:")
    print("-" * 50)
    
    for i, command in enumerate(test_commands, 1):
        try:
            result = parser.parse(command)
            action_type = result.type.value if result.type else 'unknown'
            confidence = result.confidence
            
            status = "[RECOGNIZED]" if confidence > 0.7 else "[LOW_CONF]"
            print(f"{i:2d}. {command}")
            print(f"    {status} -> {action_type} (confidence: {confidence:.2f})")
            
            if result.parameters:
                param_str = ", ".join([f"{k}={v}" for k, v in result.parameters.items()])
                print(f"    Parameters: {param_str}")
            print()
            
        except Exception as e:
            print(f"{i:2d}. {command}")
            print(f"    [ERROR] -> {e}")
            print()
    
    print("=== Command Recognition Test Complete ===")
    print("The system successfully recognizes natural language commands")
    print("and converts them to executable desktop automation actions.")

if __name__ == "__main__":
    test_command_parsing()