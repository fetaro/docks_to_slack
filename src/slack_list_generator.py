import json
import struct
from dataclasses import dataclass
from bs4 import BeautifulSoup, NavigableString, Tag

@dataclass
class GenerateResult:
    binary_data: bytes
    plain_text: str

class PickleWriter:
    def __init__(self):
        self.data = bytearray()

    def write_uint32(self, value):
        self.data.extend(struct.pack('<I', value))

    def write_string16(self, s):
        """
        Writes a String16:
        - Length: uint32 (Number of CHARACTERS)
        - Data: UTF-16 LE bytes
        - Padding: Align to 4 bytes
        """
        encoded = s.encode('utf-16-le')
        char_count = len(encoded) // 2
        self.write_uint32(char_count)
        self.data.extend(encoded)
        
        # Padding
        padding = (4 - (len(encoded) % 4)) % 4
        if padding > 0:
            self.data.extend(b'\x00' * padding)

    def get_payload(self):
        return bytes(self.data)

class SlackListGenerator:
    def generate(self, html_content: str) -> GenerateResult:
        """
        Parses HTML content and returns the binary data for 'org.chromium.web-custom-data'
        and the plain text representation.
        
        Returns:
            GenerateResult: Object containing binary_data and plain_text
        """
        plain_text, texty_json = self._parse_html(html_content)
        binary_data = self._create_chromium_data(plain_text, texty_json)
        return GenerateResult(binary_data=binary_data, plain_text=plain_text)

    def _parse_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        ops = []
        plain_text_lines = []
        
        def process_list(list_element, level=0):
            list_type = 'bullet' if list_element.name == 'ul' else 'ordered'
            
            for child in list_element.children:
                if isinstance(child, Tag) and child.name == 'li':
                    # Extract text from this li, excluding nested lists for now
                    item_text = ""
                    nested_lists = []
                    
                    for content in child.contents:
                        if isinstance(content, NavigableString):
                            item_text += str(content)
                        elif isinstance(content, Tag):
                            if content.name in ['ul', 'ol']:
                                nested_lists.append(content)
                            else:
                                item_text += content.get_text()
                    
                    item_text = item_text.strip()
                    if item_text:
                        # Add operation for this item
                        ops.append({"insert": item_text})
                        
                        attributes = {"list": list_type}
                        if level > 0:
                            attributes["indent"] = level
                        
                        ops.append({"attributes": attributes, "insert": "\n"})
                        
                        # Add to plain text
                        indent_str = "\t" * level
                        plain_text_lines.append(f"{indent_str}{item_text}")
                    
                    # Process nested lists
                    for nested in nested_lists:
                        process_list(nested, level + 1)

        # Find the first list to start processing
        first_list = soup.find(['ul', 'ol'])
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

    def _create_chromium_data(self, plain_text, texty_json):
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
        json_str = json.dumps(texty_json, separators=(',', ':'))
        writer.write_string16(json_str)
        
        payload = writer.get_payload()
        
        # Prepend the total size (uint32)
        final_data = struct.pack('<I', len(payload)) + payload
        return final_data
