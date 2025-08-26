import unittest
from unittest.mock import MagicMock, patch

from mkd.recording.input_capturer import InputCapturer

class TestInputCapturer(unittest.TestCase):

    @patch('mkd.recording.input_capturer.get_platform')
    def test_start_capture(self, mock_get_platform):
        mock_platform = MagicMock()
        mock_get_platform.return_value = mock_platform

        capturer = InputCapturer()
        capturer.start_capture()

        mock_platform.start_capture.assert_called_once()

    @patch('mkd.recording.input_capturer.get_platform')
    def test_stop_capture(self, mock_get_platform):
        mock_platform = MagicMock()
        mock_get_platform.return_value = mock_platform

        capturer = InputCapturer()
        capturer.stop_capture()

        mock_platform.stop_capture.assert_called_once()

if __name__ == '__main__':
    unittest.main()
