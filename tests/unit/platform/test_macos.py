import unittest
from unittest.mock import patch

from mkd.platform.macos import MacOSPlatform

class TestMacOSPlatform(unittest.TestCase):

    @patch('builtins.print')
    def test_start_capture(self, mock_print):
        platform = MacOSPlatform()
        platform.start_capture(None)
        mock_print.assert_called_with("Starting capture on macOS")

    @patch('builtins.print')
    def test_stop_capture(self, mock_print):
        platform = MacOSPlatform()
        platform.stop_capture()
        mock_print.assert_called_with("Stopping capture on macOS")

if __name__ == '__main__':
    unittest.main()
