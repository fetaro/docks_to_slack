import json
import struct
from bs4 import BeautifulSoup, NavigableString, Tag  # type: ignore
from src.generate_result import GenerateResult
from src.pickle_writer import PickleWriter


class SlackListGenerator:
    def generate(self, html_content: str) -> GenerateResult:
        """
        HTMLコンテンツを解析し、'org.chromium.web-custom-data'のバイナリデータと
        プレーンテキスト表現を返します。

        Returns:
            GenerateResult: binary_dataとplain_textを含むオブジェクト
        """
        plain_text, texty_json = self._parse_html(html_content)
        binary_data = self._create_chromium_data(plain_text, texty_json)
        return GenerateResult(
            binary_data=binary_data, plain_text=plain_text, texty_json=texty_json
        )

    def _parse_html(self, html_content) -> tuple[str, dict]:
        soup = BeautifulSoup(html_content, "html.parser")

        ops = []
        plain_text_lines = []

        def process_list(list_element, level=0) -> None:
            list_type = "bullet" if list_element.name == "ul" else "ordered"
            index = 1

            for child in list_element.children:
                if not isinstance(child, Tag):
                    continue

                if child.name == "li":
                    # Determine level from aria-level if present
                    current_level = level
                    aria_level = child.get("aria-level")
                    if aria_level and aria_level.isdigit():  # type: ignore
                        # aria-level is 1-based
                        current_level = int(aria_level) - 1  # type: ignore

                    # Extract text from this li, excluding nested lists for now
                    item_text = ""
                    nested_lists = []

                    for content in child.contents:
                        if isinstance(content, NavigableString):
                            item_text += str(content)
                        elif isinstance(content, Tag):
                            if content.name in ["ul", "ol"]:
                                nested_lists.append(content)
                            else:
                                item_text += content.get_text()

                    item_text = item_text.strip()
                    if item_text:
                        # Add operation for this item
                        ops.append({"insert": item_text})

                        attributes = {"list": list_type}
                        if current_level > 0:
                            attributes["indent"] = current_level  # type: ignore

                        ops.append({"attributes": attributes, "insert": "\n"})

                        # Add to plain text
                        indent_str = "    " * current_level
                        prefix = "- " if list_type == "bullet" else f"{index}. "
                        plain_text_lines.append(f"{indent_str}{prefix}{item_text}")

                        if list_type == "ordered":
                            index += 1

                    # Process nested lists
                    for nested in nested_lists:
                        process_list(nested, current_level + 1)

                elif child.name in ["ul", "ol"]:
                    # Handle nested lists as siblings (Google Docs structure)
                    process_list(child, level + 1)

        # Find the first list to start processing
        first_list = soup.find(["ul", "ol"])
        if first_list:
            process_list(first_list)
        else:
            # Fallback if no list found, just treat as text
            text = soup.get_text().strip()
            ops.append({"insert": text})
            ops.append({"insert": "\n"})
            plain_text_lines.append(text)

        texty_json = {"ops": ops}
        plain_text = "\n".join(plain_text_lines)

        return plain_text, texty_json

    def _create_chromium_data(self, plain_text, texty_json) -> bytes:
        writer = PickleWriter()

        # Entry Count (uint32)
        writer.write_uint32(2)

        # --- Entry 1: public.utf8-plain-text ---
        # Key
        writer.write_string16("public.utf8-plain-text")

        # Value: String16 (Length = Char Count)
        writer.write_string16(plain_text)

        # --- Entry 2: slack/texty ---
        # Key
        writer.write_string16("slack/texty")

        # Value: String16 (Length = Char Count)
        # Content is JSON string
        # Use compact separators
        json_str = json.dumps(texty_json, separators=(",", ":"))
        writer.write_string16(json_str)

        payload = writer.get_payload()

        # Prepend the total size (uint32)
        final_data = struct.pack("<I", len(payload)) + payload
        return final_data
