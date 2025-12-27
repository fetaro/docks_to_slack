import textwrap
from src.slack_list_generator import SlackListGenerator, GenerateResult


def test_sample_html_conversion():
    """sample_list.htmlの内容を埋め込んで変換結果を検証するテスト"""

    html_content = textwrap.dedent("""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <title>Sample Nested List</title>
        </head>
        <body>
            <ul>
                <li>Level 1 Item 1</li>
                <li>Level 1 Item 2
                    <ul>
                        <li>Level 2 Item A</li>
                        <li>Level 2 Item B
                            <ul>
                                <li>Level 3 日本語</li>
                            </ul>
                        </li>
                    </ul>
                </li>
                <li>Level 1 Item 3</li>
            </ul>
        </body>
        </html>
    """).strip()

    # 変換実行
    generator = SlackListGenerator()
    result = generator.generate(html_content)

    # 検証
    assert isinstance(result, GenerateResult)

    # プレーンテキストの検証
    expected_plain_text = textwrap.dedent("""
        - Level 1 Item 1
        - Level 1 Item 2
            - Level 2 Item A
            - Level 2 Item B
                - Level 3 日本語
        - Level 1 Item 3
    """).strip()
    assert result.plain_text == expected_plain_text

    # バイナリデータの検証
    assert len(result.binary_data) > 0
