import unittest
from unittest.mock import MagicMock, patch

from mkd.playback.action_executor import ActionExecutor

class TestActionExecutor(unittest.TestCase):

    @patch('mkd.playback.action_executor.get_platform')
    def test_execute_action(self, mock_get_platform):
        mock_platform = MagicMock()
        mock_get_platform.return_value = mock_platform

        executor = ActionExecutor()
        executor.execute_action("test_action")

        mock_platform.execute_action.assert_called_once_with("test_action")

if __name__ == '__main__':
    unittest.main()
