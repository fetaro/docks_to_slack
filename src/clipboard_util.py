import subprocess
from AppKit import NSPasteboard, NSPasteboardTypeString  # type: ignore

# カスタムクリップボードタイプの定義
CHROMIUM_WEB_CUSTOM_DATA_TYPE = "org.chromium.web-custom-data"


class ClipboardUtil:
    @staticmethod
    def get_clipboard_html() -> str:
        """
        macOSのクリップボードからpbpasteを使用してHTMLコンテンツを取得します。
        """
        try:
            # 'public.html' はmacOSクリップボード上のHTMLデータの標準タイプです
            p = subprocess.Popen(
                ["pbpaste", "-prefer", "public.html"], stdout=subprocess.PIPE
            )
            data, _ = p.communicate()
            return data.decode("utf-8")
        except Exception as e:
            raise RuntimeError(f"クリップボードの読み込みエラー: {e}") from e

    @staticmethod
    def set_text(plain_text: str) -> None:
        """
        クリップボードにプレーンテキストのみを設定します。
        """
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()
        pb.setString_forType_(plain_text, NSPasteboardTypeString)

    @staticmethod
    def set_rich_text(data: bytes, plain_text: str) -> None:
        """
        カスタムChromium形式とプレーンテキストのフォールバックを使用してクリップボードデータを設定します。
        """
        pb = NSPasteboard.generalPasteboard()
        pb.clearContents()

        # 互換性のためにプレーンテキストを設定
        pb.setString_forType_(plain_text, NSPasteboardTypeString)

        # カスタムバイナリデータを設定
        pb.setData_forType_(data, CHROMIUM_WEB_CUSTOM_DATA_TYPE)
