import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from click.testing import CliRunner

# srcディレクトリをパスに追加して、スクリプト内のインポート(from slack_list_generator import ...)が解決できるようにする
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
# ルートディレクトリも追加して main.py をインポートできるようにする
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import main as docs_main  # noqa: E402


class TestMain(unittest.TestCase):
    @patch("main.ClipboardUtil.get_clipboard_html")
    @patch("main.ClipboardUtil.set_rich_text")
    @patch("main.SlackListGenerator")
    def test_main_success(
        self, mock_generator_class, mock_set_rich_text, mock_get_clipboard
    ):
        """main.pyの正常系テスト"""
        # Setup
        mock_get_clipboard.return_value = "<html></html>"

        mock_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.plain_text = "plain"
        mock_result.binary_data = b"binary"
        mock_instance.generate.return_value = mock_result
        mock_generator_class.return_value = mock_instance

        # Execute
        runner = CliRunner()
        result = runner.invoke(docs_main)

        # Verify
        self.assertEqual(result.exit_code, 0)
        mock_get_clipboard.assert_called_once()
        mock_instance.generate.assert_called_with("<html></html>")
        mock_set_rich_text.assert_called_with(b"binary", "plain")

    @patch("main.ClipboardUtil.get_clipboard_html")
    @patch("main.ClipboardUtil.set_text")
    @patch("main.SlackListGenerator")
    def test_main_text_option(
        self, mock_generator_class, mock_set_text, mock_get_clipboard
    ):
        """-tオプション指定時のテスト"""
        # Setup
        mock_get_clipboard.return_value = "<html></html>"

        mock_instance = MagicMock()
        mock_result = MagicMock()
        mock_result.plain_text = "plain text output"
        mock_result.binary_data = b"binary"
        mock_instance.generate.return_value = mock_result
        mock_generator_class.return_value = mock_instance

        # Execute
        runner = CliRunner()
        result = runner.invoke(docs_main, ["-t"])

        # Verify
        self.assertEqual(result.exit_code, 0)
        # -tオプション指定時は標準出力には何も出ないはず（デバッグモードでない限り）
        self.assertEqual(result.output, "")
        # set_textが呼ばれていることを確認
        mock_set_text.assert_called_with("plain text output")
