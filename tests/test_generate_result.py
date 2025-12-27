import unittest
from src.generate_result import GenerateResult


class TestGenerateResult(unittest.TestCase):
    def test_instantiation(self):
        """GenerateResultが正しくインスタンス化され、値を保持することを確認する"""
        binary_data = b"\x01\x02\x03"
        plain_text = "Hello"
        texty_json = {"key": "value"}

        result = GenerateResult(
            binary_data=binary_data, plain_text=plain_text, texty_json=texty_json
        )

        self.assertEqual(result.binary_data, binary_data)
        self.assertEqual(result.plain_text, plain_text)
        self.assertEqual(result.texty_json, texty_json)
