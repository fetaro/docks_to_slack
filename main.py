import click
from src.slack_list_generator import SlackListGenerator
from src.clipboard_util import ClipboardUtil


@click.command()
@click.option("-d", "--debug", is_flag=True, help="デバッグ出力を有効にします")
@click.option(
    "-t",
    "--text",
    is_flag=True,
    help="プレーンテキスト形式のみをクリップボードにコピーします",
)
def main(debug: bool, text: bool) -> None:
    if debug:
        print("クリップボードから読み込んでいます...")
    html_content = ClipboardUtil.get_clipboard_html()

    if debug:
        print(f"----変換前(html)-----------------\n{html_content}")
    generator = SlackListGenerator()
    result = generator.generate(html_content)

    if debug:
        if text:
            print(
                f"----変換後(text)-----------------\n{result.plain_text}\n-----------------\n"
            )
        else:
            print(
                f"----変換後(slack/texty)-----------------\n{result.texty_json}\n-----------------\n"
            )

    if text:
        ClipboardUtil.set_text(result.plain_text)
    else:
        ClipboardUtil.set_rich_text(result.binary_data, result.plain_text)


if __name__ == "__main__":
    main()
