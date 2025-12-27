import unittest
from unittest.mock import patch, MagicMock
import subprocess
from src.clipboard_util import (
    ClipboardUtil,
    CHROMIUM_WEB_CUSTOM_DATA_TYPE,
)
from AppKit import NSPasteboardTypeString  # type: ignore


class TestClipboardUtil(unittest.TestCase):
    @patch("subprocess.Popen")
    def test_get_clipboard_html(self, mock_popen):
        """get_clipboard_htmlがpbpasteを呼び出して結果を返すことをテスト"""
        # Setup mock
        process_mock = MagicMock()
        # communicate returns (stdout, stderr)
        process_mock.communicate.return_value = (b"<html></html>", b"")
        mock_popen.return_value = process_mock

        # Execute
        result = ClipboardUtil.get_clipboard_html()

        # Verify
        self.assertEqual(result, "<html></html>")
        mock_popen.assert_called_with(
            ["pbpaste", "-prefer", "public.html"], stdout=subprocess.PIPE
        )

    @patch("src.clipboard_util.NSPasteboard")
    def test_set_rich_text(self, mock_nspasteboard):
        """set_rich_textがNSPasteboardを正しく呼び出すことをテスト"""
        # Setup mock
        mock_pb = MagicMock()
        mock_nspasteboard.generalPasteboard.return_value = mock_pb

        # Execute
        data = b"\x00\x01"
        plain_text = "text"
        ClipboardUtil.set_rich_text(data, plain_text)

        # Verify
        mock_pb.clearContents.assert_called_once()
        mock_pb.setString_forType_.assert_any_call(plain_text, NSPasteboardTypeString)
        mock_pb.setData_forType_.assert_any_call(data, CHROMIUM_WEB_CUSTOM_DATA_TYPE)

    @patch("src.clipboard_util.NSPasteboard")
    def test_set_text(self, mock_nspasteboard):
        """set_textがNSPasteboardを正しく呼び出すことをテスト"""
        # Setup mock
        mock_pb = MagicMock()
        mock_nspasteboard.generalPasteboard.return_value = mock_pb

        # Execute
        plain_text = "text"
        ClipboardUtil.set_text(plain_text)

        # Verify
        mock_pb.clearContents.assert_called_once()
        mock_pb.setString_forType_.assert_any_call(plain_text, NSPasteboardTypeString)
        # setData_forType_ should NOT be called
        mock_pb.setData_forType_.assert_not_called()
