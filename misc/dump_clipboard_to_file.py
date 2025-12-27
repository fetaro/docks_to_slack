import AppKit
import os


def dump_clipboard_to_file() -> None:
    """
    検証データ作成用。クリップボード内のHTMLコンテンツをファイルにダンプする関数。
    'public.html' 形式のデータを取得し、'invest/debug_dump.html' に保存します。
    """
    pb = AppKit.NSPasteboard.generalPasteboard()  # type: ignore

    # HTMLの取得
    html_content = pb.stringForType_("public.html")

    output_dir = "invest"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    html_path = os.path.join(output_dir, "debug_dump.html")

    if html_content:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML content saved to: {html_path}")
    else:
        print("No public.html found in clipboard.")


if __name__ == "__main__":
    dump_clipboard_to_file()
