import unittest
from unittest.mock import patch

from mkd.platform.linux import LinuxPlatform

class TestLinuxPlatform(unittest.TestCase):

    @patch('builtins.print')
    def test_start_capture(self, mock_print):
        platform = LinuxPlatform()
        platform.start_capture(None)
        mock_print.assert_called_with("Starting capture on Linux")

    @patch('builtins.print')
    def test_stop_capture(self, mock_print):
        platform = LinuxPlatform()
        platform.stop_capture()
        mock_print.assert_called_with("Stopping capture on Linux")

if __name__ == '__main__':
    unittest.main()
