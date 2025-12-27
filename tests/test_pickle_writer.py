import unittest
from src.pickle_writer import PickleWriter


class TestPickleWriter(unittest.TestCase):
    def test_write_simple_data(self):
        """PickleWriterの基本的な書き込み動作を確認する"""
        writer = PickleWriter()

        # uint32の書き込み (1)
        writer.write_uint32(1)
        # 期待値: 0x01, 0x00, 0x00, 0x00 (リトルエンディアン)

        # string16の書き込み ("A")
        # 文字数: 1 -> uint32で書き込み (0x01, 0x00, 0x00, 0x00)
        # データ: "A" (UTF-16LE) -> 0x41, 0x00
        # パディング: 2バイト (4バイトアライメントのため) -> 0x00, 0x00
        writer.write_string16("A")

        payload = writer.get_payload()

        expected = (
            b"\x01\x00\x00\x00"  # uint32(1)
            b"\x01\x00\x00\x00"  # string length (1 char)
            b"\x41\x00"  # "A" in UTF-16LE
            b"\x00\x00"  # Padding
        )

        self.assertEqual(payload, expected)
