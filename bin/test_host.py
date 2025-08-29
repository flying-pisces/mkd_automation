#!/usr/bin/env python3
"""
Minimal native messaging host for testing Chrome extension communication.
"""

import sys
import json
import struct
import logging

def setup_logging():
    """Setup logging to file."""
    logging.basicConfig(
        filename='/Users/cyin/.mkd/test_host.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def read_message():
    """Read message from Chrome using native messaging protocol."""
    try:
        # Read message length (4 bytes, little endian)
        raw_length = sys.stdin.buffer.read(4)
        if not raw_length or len(raw_length) != 4:
            return None
        
        message_length = struct.unpack('=I', raw_length)[0]
        
        # Validate message length
        if message_length == 0 or message_length > 1024 * 1024:  # Max 1MB
            return None
        
        # Read message content
        raw_message = sys.stdin.buffer.read(message_length)
        if len(raw_message) != message_length:
            return None
        
        # Parse JSON
        message_text = raw_message.decode('utf-8')
        message = json.loads(message_text)
        
        return message
        
    except Exception as e:
        logger.error(f"Error reading message: {e}")
        return None

def send_message(message):
    """Send message to Chrome using native messaging protocol."""
    try:
        # Serialize message
        message_json = json.dumps(message)
        message_bytes = message_json.encode('utf-8')
        
        # Send message length (4 bytes, little endian)
        length_bytes = struct.pack('=I', len(message_bytes))
        sys.stdout.buffer.write(length_bytes)
        
        # Send message content
        sys.stdout.buffer.write(message_bytes)
        sys.stdout.buffer.flush()
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")

def main():
    """Main function."""
    global logger
    logger = setup_logging()
    logger.info("Test native host starting...")
    
    try:
        while True:
            # Read message from Chrome
            message = read_message()
            if message is None:
                logger.info("No message received, exiting")
                break
            
            logger.info(f"Received message: {message}")
            
            # Process message
            message_id = message.get('id', 0)
            command = message.get('command', 'unknown')
            
            # Create response
            response = {
                'id': message_id,
                'success': True,
                'data': {
                    'status': 'ok',
                    'command': command,
                    'message': f'Test host received: {command}'
                }
            }
            
            # Send response
            send_message(response)
            logger.info(f"Sent response: {response}")
            
    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        logger.info("Test native host stopping...")

if __name__ == '__main__':
    main()