from AppKit import NSPasteboard  # type: ignore


def debug_clipboard() -> None:
    """
    デバッグ用。クリップボードの内容をデバッグ出力する関数。
    利用可能なタイプ一覧と、主要なタイプ（HTML, Textなど）の内容を表示します。
    """
    # クリップボードのインスタンスを取得
    pb = NSPasteboard.generalPasteboard()
    # 現在クリップボードにあるデータタイプの一覧を取得
    types = pb.types()
    print(f"Available types: {list(types)}")

    # 調査対象のデータタイプ
    target_types = [
        "public.html",
        "public.utf8-plain-text",
        "com.apple.webarchive",
        "org.chromium.web-custom-data",
    ]

    for t in target_types:
        if t in types:
            print(f"\n\n=== Content of {t} ===")
            try:
                # テキスト形式の場合は文字列として取得して表示
                if t == "public.html" or t == "public.utf8-plain-text":
                    data = pb.stringForType_(t)
                    print(data)
                # バイナリ形式の場合はサイズのみ表示
                else:
                    data = pb.dataForType_(t)
                    print(f"<Binary data: {len(data)} bytes>")
            except Exception as e:
                print(f"Error reading {t}: {e}")


if __name__ == "__main__":
    debug_clipboard()
