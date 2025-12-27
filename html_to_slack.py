import sys
import json
import argparse
from AppKit import NSPasteboard, NSPasteboardTypeString
from src.slack_list_generator import SlackListGenerator

# Define the custom clipboard type
CHROMIUM_WEB_CUSTOM_DATA_TYPE = "org.chromium.web-custom-data"

def set_clipboard_data(data, plain_text):
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    
    # Set plain text for compatibility
    pb.setString_forType_(plain_text, NSPasteboardTypeString)
    
    # Set the custom binary data
    pb.setData_forType_(data, CHROMIUM_WEB_CUSTOM_DATA_TYPE)
    
    print("Clipboard updated with Slack format.")

def main():
    parser = argparse.ArgumentParser(description='Convert HTML list to Slack clipboard format.')
    parser.add_argument('html_file', help='Path to the HTML file to convert')
    args = parser.parse_args()

    try:
        with open(args.html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        generator = SlackListGenerator()
        result = generator.generate(html_content)
        
        print("Generated Plain Text:")
        print(result.plain_text)
        
        set_clipboard_data(result.binary_data, result.plain_text)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
