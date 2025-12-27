import sys
import argparse
from slack_list_generator import SlackListGenerator
from clipboard_util import ClipboardUtil


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert HTML list to Slack clipboard format."
    )
    parser.add_argument("html_file", help="Path to the HTML file to convert")
    args = parser.parse_args()

    try:
        with open(args.html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        generator = SlackListGenerator()
        result = generator.generate(html_content)

        print("Generated Plain Text:")
        print(result.plain_text)

        ClipboardUtil.set_clipboard_data(result.binary_data, result.plain_text)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
