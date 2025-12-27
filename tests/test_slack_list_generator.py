import pytest
import struct
import json
import textwrap
from src.slack_list_generator import SlackListGenerator


@pytest.fixture
def generator():
    return SlackListGenerator()


def test_parse_html_nested_list(generator):
    """
    ネストされたリストのHTMLをパースし、期待されるプレーンテキストとJSON構造になるか検証する。
    仕様:
    - <ul> は bullet リストになる
    - ネストレベルに応じてインデントが増える (indent: 1, 2, ...)
    - plain_text はタブ文字(\t)でインデントを表現する
    """
    # 入力: ネストされたリストを含むHTML
    # <ul>
    #   <li>Level 1
    #     <ul>
    #       <li>Level 2</li>
    #     </ul>
    #   </li>
    # </ul>
    input_html = """
    <ul>
        <li>Level 1
            <ul>
                <li>Level 2</li>
            </ul>
        </li>
    </ul>
    """

    # 期待される出力 (plain_text)
    # - Level 1
    #     - Level 2
    expected_plain_text = "- Level 1\n    - Level 2"

    # 期待される出力 (texty_json)
    # ops配列に操作が格納される
    expected_texty_json = {
        "ops": [
            # Level 1 item
            {"insert": "Level 1"},
            {"attributes": {"list": "bullet"}, "insert": "\n"},
            # Level 2 item (nested)
            {"insert": "Level 2"},
            {"attributes": {"list": "bullet", "indent": 1}, "insert": "\n"},
        ]
    }

    # 実行
    actual_plain_text, actual_texty_json = generator._parse_html(input_html)

    # 検証
    assert actual_plain_text == expected_plain_text
    assert actual_texty_json == expected_texty_json


def test_simple_list(generator):
    """単純なリストの変換テスト"""
    input_html = """
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    """

    expected_plain_text = "- Item 1\n- Item 2"
    expected_texty_json = {
        "ops": [
            {"insert": "Item 1"},
            {"attributes": {"list": "bullet"}, "insert": "\n"},
            {"insert": "Item 2"},
            {"attributes": {"list": "bullet"}, "insert": "\n"},
        ]
    }

    actual_plain_text, actual_texty_json = generator._parse_html(input_html)

    assert actual_plain_text == expected_plain_text
    assert actual_texty_json == expected_texty_json


def test_deeply_nested_list(generator):
    """3段階ネストされた箇条書きのテスト"""
    input_html = """
    <ul>
        <li>Level 1
            <ul>
                <li>Level 2
                    <ul>
                        <li>Level 3</li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>
    """

    expected_plain_text = "- Level 1\n    - Level 2\n        - Level 3"
    expected_texty_json = {
        "ops": [
            {"insert": "Level 1"},
            {"attributes": {"list": "bullet"}, "insert": "\n"},
            {"insert": "Level 2"},
            {"attributes": {"list": "bullet", "indent": 1}, "insert": "\n"},
            {"insert": "Level 3"},
            {"attributes": {"list": "bullet", "indent": 2}, "insert": "\n"},
        ]
    }

    actual_plain_text, actual_texty_json = generator._parse_html(input_html)

    assert actual_plain_text == expected_plain_text
    assert actual_texty_json == expected_texty_json


def test_mixed_list_types(generator):
    """順序付きリストと箇条書きの混在テスト"""
    input_html = """
    <ul>
        <li>Bullet
            <ol>
                <li>Ordered</li>
            </ol>
        </li>
    </ul>
    """

    expected_plain_text = "- Bullet\n    1. Ordered"
    expected_texty_json = {
        "ops": [
            {"insert": "Bullet"},
            {"attributes": {"list": "bullet"}, "insert": "\n"},
            {"insert": "Ordered"},
            {"attributes": {"list": "ordered", "indent": 1}, "insert": "\n"},
        ]
    }

    actual_plain_text, actual_texty_json = generator._parse_html(input_html)

    assert actual_plain_text == expected_plain_text
    assert actual_texty_json == expected_texty_json


def test_fallback_text(generator):
    """リスト以外のテキストのフォールバックテスト"""
    input_html = "<p>Just some text</p>"

    expected_plain_text = "Just some text"
    expected_texty_json = {
        "ops": [
            {"insert": "Just some text"},
            {"insert": "\n"},
        ]
    }

    actual_plain_text, actual_texty_json = generator._parse_html(input_html)

    assert actual_plain_text == expected_plain_text
    assert actual_texty_json == expected_texty_json


def test_google_docs_nested_structure(generator):
    """Google Docsスタイルのネスト構造（ulの直下にulがある）のテスト"""
    input_html = """
    <b style="font-weight:normal;">
        <ul style="margin-top:0;margin-bottom:0;">
            <li aria-level="1">Level 1 Item</li>
            <ul style="margin-top:0;margin-bottom:0;">
                <li aria-level="2">Level 2 Item A</li>
                <li aria-level="2">Level 2 Item B</li>
                <ul style="margin-top:0;margin-bottom:0;">
                    <li aria-level="3">Level 3 Item</li>
                </ul>
            </ul>
        </ul>
    </b>
    """

    # プレーンテキストの検証
    expected_plain_text = textwrap.dedent("""
        - Level 1 Item
            - Level 2 Item A
            - Level 2 Item B
                - Level 3 Item
    """).strip()

    actual_plain_text, actual_texty_json = generator._parse_html(input_html)

    assert actual_plain_text == expected_plain_text

    # JSON構造の検証 (インデント属性)
    ops = actual_texty_json["ops"]

    # Level 1 (indent 0)
    assert ops[0]["insert"] == "Level 1 Item"
    assert "indent" not in ops[1]["attributes"]

    # Level 2 A (indent 1)
    assert ops[2]["insert"] == "Level 2 Item A"
    assert ops[3]["attributes"]["indent"] == 1

    # Level 2 B (indent 1)
    assert ops[4]["insert"] == "Level 2 Item B"
    assert ops[5]["attributes"]["indent"] == 1

    # Level 3 (indent 2)
    assert ops[6]["insert"] == "Level 3 Item"
    assert ops[7]["attributes"]["indent"] == 2


def parse_string16(data, offset):
    """バイナリデータからString16形式の文字列をパースするヘルパー関数"""
    # Read char count (uint32)
    char_count = struct.unpack("<I", data[offset : offset + 4])[0]
    offset += 4

    # Read bytes
    byte_len = char_count * 2
    string_bytes = data[offset : offset + byte_len]
    s = string_bytes.decode("utf-16-le")
    offset += byte_len

    # Skip padding
    padding = (4 - (byte_len % 4)) % 4
    offset += padding

    return s, offset


def test_binary_structure(generator):
    """生成されたバイナリデータの構造検証テスト"""
    html = "<ul><li>Test</li></ul>"
    result = generator.generate(html)
    data = result.binary_data

    # 1. Total Size (uint32)
    # ChromiumのPickle形式では、先頭4バイトにペイロード全体のサイズ(バイト数)が格納される
    total_size = struct.unpack("<I", data[0:4])[0]
    assert total_size == len(data) - 4
    offset = 4

    # 2. Entry Count (uint32)
    # org.chromium.web-custom-data はMap形式でデータを保持する
    # 今回は 'public.utf8-plain-text' と 'slack/texty' の2つのエントリが含まれるため、値は 2 となる
    entry_count = struct.unpack("<I", data[offset : offset + 4])[0]
    assert entry_count == 2
    offset += 4

    # 3. Entry 1 Key
    # 最初のキーは標準的なテキスト形式を示す 'public.utf8-plain-text'
    # 文字列はChromiumのString16形式(文字数 + UTF-16LE + パディング)で格納される
    key1, offset = parse_string16(data, offset)
    assert key1 == "public.utf8-plain-text"

    # 4. Entry 1 Value
    # 値もString16形式。ここでは単純なテキスト "- Test" が入る
    val1, offset = parse_string16(data, offset)
    assert val1 == "- Test"

    # 5. Entry 2 Key
    # 2つ目のキーはSlack独自形式の 'slack/texty'
    key2, offset = parse_string16(data, offset)
    assert key2 == "slack/texty"

    # 6. Entry 2 Value (JSON)
    # 重要: 調査の結果、slack/textyの値もBlobではなくString16形式で格納する必要があることが判明
    # 内容はSlackのリッチテキスト構造を表すJSON文字列
    val2, offset = parse_string16(data, offset)
    json_data = json.loads(val2)

    # JSON構造の検証
    # SlackはQuill Deltaに似た形式(ops配列)を使用する
    assert "ops" in json_data
    assert len(json_data["ops"]) >= 2
    assert json_data["ops"][0]["insert"] == "Test"
    # リスト属性が正しく設定されているか確認
    assert json_data["ops"][1]["attributes"]["list"] == "bullet"
