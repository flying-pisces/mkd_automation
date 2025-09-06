"""
Example conversation templates for MKD Automation GUI.

This module provides pre-defined conversation examples that users can load
to see how the system works and get inspiration for their own automations.
"""

import json
from datetime import datetime
from typing import List, Dict, Any


class ConversationTemplate:
    """Represents a conversation template."""
    
    def __init__(self, name: str, description: str, messages: List[Dict[str, Any]]):
        self.name = name
        self.description = description
        self.messages = messages
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'messages': self.messages,
            'created_at': self.created_at
        }
        
    def save_to_file(self, filename: str):
        """Save template to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


# Example conversation templates
CONVERSATION_TEMPLATES = {
    "emailjs_automation": ConversationTemplate(
        name="EmailJS Template Creation",
        description="Demonstrates creating an EmailJS template for contact forms",
        messages=[
            {
                'content': "Hi! I need help creating an EmailJS template for my contact form.",
                'sender': 'user',
                'timestamp': '2024-01-01T10:00:00',
                'message_type': 'text'
            },
            {
                'content': "I'll help you create an EmailJS template! What email should receive the messages?",
                'sender': 'mkd',
                'timestamp': '2024-01-01T10:00:01',
                'message_type': 'text'
            },
            {
                'content': "Create EmailJS template with email admin@mycompany.com",
                'sender': 'user',
                'timestamp': '2024-01-01T10:00:30',
                'message_type': 'text'
            },
            {
                'content': "🚀 Creating EmailJS template 'Contact Form' for admin@mycompany.com...",
                'sender': 'mkd',
                'timestamp': '2024-01-01T10:00:31',
                'message_type': 'action'
            },
            {
                'content': "✅ EmailJS template created successfully! ID: template_abc123",
                'sender': 'mkd',
                'timestamp': '2024-01-01T10:01:15',
                'message_type': 'success'
            }
        ]
    ),
    
    "web_search": ConversationTemplate(
        name="Web Search Automation",
        description="Shows how to automate web searches and navigation",
        messages=[
            {
                'content': "I want to research Python automation tools. Can you help me search?",
                'sender': 'user',
                'timestamp': '2024-01-01T11:00:00',
                'message_type': 'text'
            },
            {
                'content': "I'll help you search for Python automation tools. Let me start by opening a browser.",
                'sender': 'mkd',
                'timestamp': '2024-01-01T11:00:01',
                'message_type': 'text'
            },
            {
                'content': "Open google.com",
                'sender': 'user',
                'timestamp': '2024-01-01T11:00:15',
                'message_type': 'text'
            },
            {
                'content': "🌐 Browser session started",
                'sender': 'mkd',
                'timestamp': '2024-01-01T11:00:16',
                'message_type': 'action'
            },
            {
                'content': "✅ Navigated to https://google.com",
                'sender': 'mkd',
                'timestamp': '2024-01-01T11:00:18',
                'message_type': 'success'
            },
            {
                'content': "Search for Python automation tools",
                'sender': 'user',
                'timestamp': '2024-01-01T11:00:25',
                'message_type': 'text'
            },
            {
                'content': "✅ Searched google for: Python automation tools",
                'sender': 'mkd',
                'timestamp': '2024-01-01T11:00:27',
                'message_type': 'success'
            }
        ]
    ),
    
    "form_filling": ConversationTemplate(
        name="Form Filling Automation", 
        description="Demonstrates automated form filling and submission",
        messages=[
            {
                'content': "I need to fill out a contact form repeatedly with different data. Can you help automate this?",
                'sender': 'user',
                'timestamp': '2024-01-01T12:00:00',
                'message_type': 'text'
            },
            {
                'content': "Absolutely! I can help you automate form filling. First, let's navigate to the form page.",
                'sender': 'mkd',
                'timestamp': '2024-01-01T12:00:01',
                'message_type': 'text'
            },
            {
                'content': "Go to example.com/contact",
                'sender': 'user',
                'timestamp': '2024-01-01T12:00:15',
                'message_type': 'text'
            },
            {
                'content': "✅ Navigated to https://example.com/contact",
                'sender': 'mkd',
                'timestamp': '2024-01-01T12:00:17',
                'message_type': 'success'
            },
            {
                'content': 'Type "John Doe" in the name field',
                'sender': 'user',
                'timestamp': '2024-01-01T12:00:30',
                'message_type': 'text'
            },
            {
                'content': "✅ Typed 'John Doe' in name",
                'sender': 'mkd',
                'timestamp': '2024-01-01T12:00:32',
                'message_type': 'success'
            },
            {
                'content': 'Type "john@example.com" in email field',
                'sender': 'user',
                'timestamp': '2024-01-01T12:00:40',
                'message_type': 'text'
            },
            {
                'content': "✅ Typed 'john@example.com' in email",
                'sender': 'mkd',
                'timestamp': '2024-01-01T12:00:42',
                'message_type': 'success'
            },
            {
                'content': 'Click the submit button',
                'sender': 'user',
                'timestamp': '2024-01-01T12:00:50',
                'message_type': 'text'
            },
            {
                'content': "✅ Clicked: submit button",
                'sender': 'mkd',
                'timestamp': '2024-01-01T12:00:52',
                'message_type': 'success'
            }
        ]
    ),
    
    "recording_session": ConversationTemplate(
        name="Recording Browser Actions",
        description="Shows how to record and replay browser interactions",
        messages=[
            {
                'content': "I want to record my actions on a website so I can replay them later. How do I do this?",
                'sender': 'user',
                'timestamp': '2024-01-01T13:00:00',
                'message_type': 'text'
            },
            {
                'content': "Great idea! I can record your browser actions and save them for replay. Let me start a recording session.",
                'sender': 'mkd',
                'timestamp': '2024-01-01T13:00:01',
                'message_type': 'text'
            },
            {
                'content': "Start recording",
                'sender': 'user',
                'timestamp': '2024-01-01T13:00:10',
                'message_type': 'text'
            },
            {
                'content': "🌐 Browser session started",
                'sender': 'mkd',
                'timestamp': '2024-01-01T13:00:11',
                'message_type': 'action'
            },
            {
                'content': "✅ Browser recording started. Say 'stop recording' when done",
                'sender': 'mkd',
                'timestamp': '2024-01-01T13:00:12',
                'message_type': 'success'
            },
            {
                'content': "Now I'll perform some actions in the browser... [user performs actions]",
                'sender': 'user',
                'timestamp': '2024-01-01T13:02:00',
                'message_type': 'text'
            },
            {
                'content': "Stop recording",
                'sender': 'user',
                'timestamp': '2024-01-01T13:03:30',
                'message_type': 'text'
            },
            {
                'content': "✅ Recording stopped. Captured 15 actions",
                'sender': 'mkd',
                'timestamp': '2024-01-01T13:03:31',
                'message_type': 'success'
            },
            {
                'content': "Perfect! Now I can replay these actions anytime. The recording captured 15 different interactions.",
                'sender': 'mkd',
                'timestamp': '2024-01-01T13:03:32',
                'message_type': 'text'
            }
        ]
    ),
    
    "help_session": ConversationTemplate(
        name="Getting Help and Commands",
        description="Shows how to get help and learn available commands",
        messages=[
            {
                'content': "I'm new to MKD. What can you help me with?",
                'sender': 'user',
                'timestamp': '2024-01-01T14:00:00',
                'message_type': 'text'
            },
            {
                'content': "Welcome to MKD! I can help you automate various tasks. Let me show you what I can do.",
                'sender': 'mkd',
                'timestamp': '2024-01-01T14:00:01',
                'message_type': 'text'
            },
            {
                'content': "help",
                'sender': 'user',
                'timestamp': '2024-01-01T14:00:10',
                'message_type': 'text'
            },
            {
                'content': """🤖 MKD Assistant Commands

📍 Browser Navigation:
• "Open google.com" or "Go to website.com"
• "Navigate to dashboard.emailjs.com"

🔍 Web Search:
• "Search for Python tutorials" 
• "Google machine learning"

🖱️ Browser Interaction:
• "Click the login button"
• "Type 'username' in the email field"
• "Fill name field with 'John Doe'"

📸 Screenshots:
• "Take screenshot" or "Capture page"
• "Screenshot the browser"

📧 EmailJS Automation:
• "Create EmailJS template"
• "Setup email template for contact form"

🎬 Recording:
• "Start recording" or "Record my actions"
• "Stop recording" 
• "Save recording as myfile.json"

⌨️ Desktop Actions:
• "Press Ctrl+C" or "Use hotkey Alt+Tab"
• "Take desktop screenshot"

💾 File Operations:
• "Save conversation"
• "Load recording file.json"

❓ Help & Status:
• "Help" - Show this help
• "Status" - Show current status

🔧 Tips:
• Be specific: "Click submit button" vs "click button"
• Use quotes for exact text: Type "Hello World"
• Commands are case-insensitive""",
                'sender': 'mkd',
                'timestamp': '2024-01-01T14:00:11',
                'message_type': 'system'
            },
            {
                'content': "That's really helpful! Let me try a simple command.",
                'sender': 'user',
                'timestamp': '2024-01-01T14:00:30',
                'message_type': 'text'
            },
            {
                'content': "status",
                'sender': 'user',
                'timestamp': '2024-01-01T14:00:40',
                'message_type': 'text'
            },
            {
                'content': """📊 MKD Status:

🌐 Browser: Stopped
💼 Session: Active
💬 Messages: 8""",
                'sender': 'mkd',
                'timestamp': '2024-01-01T14:00:41',
                'message_type': 'success'
            }
        ]
    ),
    
    "mixed_automation": ConversationTemplate(
        name="Mixed Automation Workflow",
        description="Complex workflow combining multiple automation types",
        messages=[
            {
                'content': "I need to automate a complex workflow: take a screenshot, open a website, fill a form, and take another screenshot. Can you do all that?",
                'sender': 'user',
                'timestamp': '2024-01-01T15:00:00',
                'message_type': 'text'
            },
            {
                'content': "Absolutely! I can chain multiple automation tasks together. Let me execute this workflow step by step.",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:01',
                'message_type': 'text'
            },
            {
                'content': "take screenshot",
                'sender': 'user',
                'timestamp': '2024-01-01T15:00:10',
                'message_type': 'text'
            },
            {
                'content': "✅ Browser screenshot saved to mkd_browser_screenshot.png",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:12',
                'message_type': 'success'
            },
            {
                'content': "open example.com/contact-form",
                'sender': 'user',
                'timestamp': '2024-01-01T15:00:20',
                'message_type': 'text'
            },
            {
                'content': "🌐 Browser session started",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:21',
                'message_type': 'action'
            },
            {
                'content': "✅ Navigated to https://example.com/contact-form",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:23',
                'message_type': 'success'
            },
            {
                'content': 'type "Test User" in name field',
                'sender': 'user',
                'timestamp': '2024-01-01T15:00:30',
                'message_type': 'text'
            },
            {
                'content': "✅ Typed 'Test User' in name",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:32',
                'message_type': 'success'
            },
            {
                'content': 'type "test@example.com" in email field',
                'sender': 'user',
                'timestamp': '2024-01-01T15:00:40',
                'message_type': 'text'
            },
            {
                'content': "✅ Typed 'test@example.com' in email",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:42',
                'message_type': 'success'
            },
            {
                'content': "take another screenshot",
                'sender': 'user',
                'timestamp': '2024-01-01T15:00:50',
                'message_type': 'text'
            },
            {
                'content': "✅ Browser screenshot saved to mkd_browser_screenshot.png",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:52',
                'message_type': 'success'
            },
            {
                'content': "Perfect! I've completed the entire workflow: screenshot → navigation → form filling → final screenshot. All steps executed successfully!",
                'sender': 'mkd',
                'timestamp': '2024-01-01T15:00:53',
                'message_type': 'success'
            }
        ]
    )
}


def get_template_names() -> List[str]:
    """Get list of available template names."""
    return list(CONVERSATION_TEMPLATES.keys())


def get_template(name: str) -> ConversationTemplate:
    """Get a specific template by name."""
    return CONVERSATION_TEMPLATES.get(name)


def export_all_templates(output_dir: str = "conversation_templates"):
    """Export all templates to JSON files."""
    import os
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    for template_id, template in CONVERSATION_TEMPLATES.items():
        filename = os.path.join(output_dir, f"{template_id}.json")
        template.save_to_file(filename)
        print(f"Exported {template.name} to {filename}")


def create_template_menu():
    """Create a simple menu for template selection."""
    print("\n🎭 Available Conversation Templates:")
    print("=" * 50)
    
    for i, (template_id, template) in enumerate(CONVERSATION_TEMPLATES.items(), 1):
        print(f"{i}. {template.name}")
        print(f"   {template.description}")
        print()
    
    while True:
        try:
            choice = input("Select template (1-{}) or 'q' to quit: ".format(len(CONVERSATION_TEMPLATES)))
            
            if choice.lower() == 'q':
                return None
                
            choice_num = int(choice)
            if 1 <= choice_num <= len(CONVERSATION_TEMPLATES):
                template_id = list(CONVERSATION_TEMPLATES.keys())[choice_num - 1]
                return CONVERSATION_TEMPLATES[template_id]
            else:
                print("Invalid choice. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.")


if __name__ == "__main__":
    print("MKD Conversation Examples")
    print("========================")
    
    # Show menu and let user select template
    selected_template = create_template_menu()
    
    if selected_template:
        print(f"\n📋 Template: {selected_template.name}")
        print(f"Description: {selected_template.description}")
        print(f"Messages: {len(selected_template.messages)}")
        
        # Ask if user wants to export
        export = input("\nExport this template to JSON file? (y/n): ").lower() == 'y'
        if export:
            filename = f"{selected_template.name.lower().replace(' ', '_')}_example.json"
            selected_template.save_to_file(filename)
            print(f"Template exported to {filename}")
    
    # Ask if user wants to export all templates
    export_all = input("\nExport all templates? (y/n): ").lower() == 'y'
    if export_all:
        export_all_templates()
        print("All templates exported!")