import unittest
from unittest.mock import patch

from mkd.platform.windows import WindowsPlatform

class TestWindowsPlatform(unittest.TestCase):

    @patch('builtins.print')
    def test_start_capture(self, mock_print):
        platform = WindowsPlatform()
        platform.start_capture(None)
        mock_print.assert_called_with("Starting capture on Windows")

    @patch('builtins.print')
    def test_stop_capture(self, mock_print):
        platform = WindowsPlatform()
        platform.stop_capture()
        mock_print.assert_called_with("Stopping capture on Windows")

if __name__ == '__main__':
    unittest.main()
