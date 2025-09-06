"""
EmailJS template automation example.

This module demonstrates how to automate EmailJS dashboard interactions
to create and save email templates with variable substitutions.
"""
import logging
import time
from typing import Dict, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .controller import BrowserController, BrowserConfig, BrowserType
from .actions import BrowserAction, BrowserActionType, BrowserActionExecutor

logger = logging.getLogger(__name__)


class EmailJSAutomation:
    """
    Automates EmailJS dashboard template operations.
    
    This class provides methods to:
    - Login to EmailJS dashboard
    - Create new email templates
    - Configure template settings
    - Save templates with variable substitutions
    """
    
    def __init__(self, browser_config: Optional[BrowserConfig] = None):
        """Initialize EmailJS automation."""
        config = browser_config or BrowserConfig(
            browser_type=BrowserType.CHROME,
            headless=False,  # Show browser for user verification
            window_size=(1920, 1080)
        )
        
        self.controller = BrowserController(config)
        self.executor = BrowserActionExecutor(self.controller)
        self.template_id = None
        
    def start(self) -> None:
        """Start the browser automation."""
        self.controller.start()
        logger.info("EmailJS automation started")
        
    def stop(self) -> None:
        """Stop the browser automation."""
        self.controller.stop()
        logger.info("EmailJS automation stopped")
        
    def create_template(self, template_config: Dict[str, str]) -> str:
        """
        Create and save an EmailJS template.
        
        Args:
            template_config: Dictionary containing:
                - url: The EmailJS dashboard URL (e.g., dashboard.emailjs.com/admin/templates/new/content)
                - template_name: Name for the template
                - subject: Email subject with variables (e.g., "Message from {{from_name}}")
                - content: Email content with variables
                - to_email: Recipient email address
                - reply_to: Reply-to variable (e.g., "{{from_email}}")
                
        Returns:
            Template ID after successful save
        """
        try:
            # Navigate to the template creation URL
            url = template_config.get('url', 'https://dashboard.emailjs.com/admin/templates/new/content')
            self.controller.navigate(url)
            
            # Wait for page load
            time.sleep(3)
            
            # Check if we need to log in first
            if "login" in self.controller.get_current_url().lower():
                logger.info("Login required. Please log in manually and press Enter to continue...")
                input("Press Enter after logging in...")
            
            # Step 1: Edit Content
            logger.info("Step 1: Editing template content")
            
            # Click Edit Content button if present
            try:
                edit_content_btn = self.controller.wait_for_element(
                    "button:contains('Edit Content'), .edit-content-btn, [data-action='edit-content']",
                    By.CSS_SELECTOR, 
                    timeout=5
                )
                self.controller.click(edit_content_btn, wait=False)
                time.sleep(1)
            except:
                logger.debug("Edit Content button not found, assuming we're already in edit mode")
            
            # Find and fill the subject field
            subject = template_config.get('subject', 'Message from {{from_name}}')
            try:
                # Try different selectors for subject field
                subject_selectors = [
                    "input[name='subject']",
                    "input[placeholder*='Subject']",
                    "#subject",
                    ".subject-input"
                ]
                
                for selector in subject_selectors:
                    try:
                        self.controller.type_text(selector, subject, clear=True, wait=False)
                        logger.info(f"Set subject: {subject}")
                        break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Could not set subject: {e}")
            
            # Find and fill the content/body field
            content = template_config.get('content', '''
Hi,

You have received a new message:

Name: {{from_name}}
Email: {{from_email}}
Message: {{message}}

Best regards,
Your Website
            ''').strip()
            
            try:
                # Try different selectors for content field
                content_selectors = [
                    "textarea[name='content']",
                    "textarea[name='body']",
                    "textarea[placeholder*='Content']",
                    "textarea[placeholder*='Message']",
                    "#content",
                    "#body",
                    ".content-textarea",
                    ".template-content",
                    "textarea"  # Fallback to any textarea
                ]
                
                for selector in content_selectors:
                    try:
                        self.controller.type_text(selector, content, clear=True, wait=False)
                        logger.info("Set template content")
                        break
                    except:
                        continue
            except Exception as e:
                logger.warning(f"Could not set content: {e}")
            
            # Step 2: Configure Settings
            logger.info("Step 2: Configuring template settings")
            
            # Click Settings tab
            try:
                settings_selectors = [
                    "a:contains('Settings')",
                    "button:contains('Settings')",
                    "[data-tab='settings']",
                    ".settings-tab",
                    "li:contains('Settings') a"
                ]
                
                for selector in settings_selectors:
                    try:
                        self.controller.click(selector, wait=False)
                        time.sleep(1)
                        logger.info("Clicked Settings tab")
                        break
                    except:
                        continue
            except:
                logger.warning("Could not find Settings tab")
            
            # Set To Email
            to_email = template_config.get('to_email', 'chuckyeyin@gmail.com')
            try:
                to_selectors = [
                    "input[name='to_email']",
                    "input[name='to']",
                    "input[placeholder*='To Email']",
                    "#to_email",
                    ".to-email-input"
                ]
                
                for selector in to_selectors:
                    try:
                        self.controller.type_text(selector, to_email, clear=True, wait=False)
                        logger.info(f"Set To Email: {to_email}")
                        break
                    except:
                        continue
            except:
                logger.warning("Could not set To Email")
            
            # Set Reply To
            reply_to = template_config.get('reply_to', '{{from_email}}')
            try:
                reply_selectors = [
                    "input[name='reply_to']",
                    "input[name='replyTo']",
                    "input[placeholder*='Reply']",
                    "#reply_to",
                    ".reply-to-input"
                ]
                
                for selector in reply_selectors:
                    try:
                        self.controller.type_text(selector, reply_to, clear=True, wait=False)
                        logger.info(f"Set Reply To: {reply_to}")
                        break
                    except:
                        continue
            except:
                logger.warning("Could not set Reply To")
            
            # Set Template Name if provided
            template_name = template_config.get('template_name', 'Contact Form Template')
            try:
                name_selectors = [
                    "input[name='name']",
                    "input[name='template_name']",
                    "input[placeholder*='Template Name']",
                    "#template_name",
                    ".template-name-input"
                ]
                
                for selector in name_selectors:
                    try:
                        self.controller.type_text(selector, template_name, clear=True, wait=False)
                        logger.info(f"Set template name: {template_name}")
                        break
                    except:
                        continue
            except:
                logger.warning("Could not set template name")
            
            # Step 3: Save the template
            logger.info("Step 3: Saving template")
            
            # Click Save button
            save_selectors = [
                "button:contains('Save')",
                "button.save",
                "button.btn-primary:contains('Save')",
                "[data-action='save']",
                ".save-button",
                "button[type='submit']"
            ]
            
            for selector in save_selectors:
                try:
                    # Try with JavaScript click as fallback
                    try:
                        self.controller.click(selector, wait=False)
                    except:
                        # Try JavaScript click
                        element = self.controller._find_element(selector, wait=False)
                        self.controller.execute_script("arguments[0].click();", element)
                    
                    logger.info("Clicked Save button")
                    break
                except:
                    continue
            
            # Wait for save to complete
            time.sleep(3)
            
            # Check if save was successful
            current_url = self.controller.get_current_url()
            if "/new/" not in current_url:
                # URL changed, extract template ID
                import re
                match = re.search(r'/templates/([^/]+)/', current_url)
                if match:
                    self.template_id = match.group(1)
                    logger.info(f"Template saved successfully! Template ID: {self.template_id}")
                    return self.template_id
                else:
                    logger.info("Template saved but could not extract ID from URL")
                    return "saved"
            else:
                logger.warning("Template may not have been saved (still on /new/ URL)")
                logger.info("Please manually click the Save button if needed")
                return None
                
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise
            
    def verify_template(self, template_id: str) -> bool:
        """
        Verify that a template was created successfully.
        
        Args:
            template_id: The template ID to verify
            
        Returns:
            True if template exists, False otherwise
        """
        try:
            # Navigate to templates list
            self.controller.navigate("https://dashboard.emailjs.com/admin/templates")
            time.sleep(2)
            
            # Look for template ID in the page
            page_source = self.controller.execute_script("return document.body.innerText;")
            return template_id in page_source
            
        except Exception as e:
            logger.error(f"Error verifying template: {e}")
            return False


def automate_emailjs_template():
    """
    Example function to automate EmailJS template creation.
    
    This function demonstrates the complete workflow.
    """
    automation = EmailJSAutomation()
    
    try:
        # Start browser
        automation.start()
        
        # Configure template
        template_config = {
            'url': 'https://dashboard.emailjs.com/admin/templates/new/content',
            'template_name': 'Contact Form',
            'subject': 'New message from {{from_name}}',
            'content': '''Hello,

You have received a new message from your website:

From: {{from_name}}
Email: {{from_email}}
Message:
{{message}}

Best regards,
Your Website Team''',
            'to_email': 'chuckyeyin@gmail.com',
            'reply_to': '{{from_email}}'
        }
        
        # Create template
        template_id = automation.create_template(template_config)
        
        if template_id:
            print(f"✅ Template created successfully!")
            print(f"📝 Template ID: {template_id}")
            
            # Verify template
            if automation.verify_template(template_id):
                print("✅ Template verified in dashboard")
        else:
            print("❌ Failed to create template")
            print("Please check the browser and complete any remaining steps manually")
            
        # Keep browser open for user to verify
        input("\nPress Enter to close the browser...")
        
    finally:
        automation.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    automate_emailjs_template()