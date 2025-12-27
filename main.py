import subprocess
import sys
from bs4 import BeautifulSoup
import AppKit

def get_clipboard_html():
    """
    Get HTML content from the clipboard on macOS.
    """
    try:
        # 'public.html' is the standard type for HTML data on macOS clipboard
        p = subprocess.Popen(['pbpaste', '-prefer', 'public.html'], stdout=subprocess.PIPE)
        data, _ = p.communicate()
        return data.decode('utf-8')
    except Exception as e:
        print(f"Error reading clipboard: {e}", file=sys.stderr)
        return None

def set_clipboard_html_with_appkit(html_content, plain_text=None):
    """
    Sets the macOS clipboard to the given HTML content using AppKit.
    This ensures the type is 'public.html' which Slack prefers.
    """
    try:
        pasteboard = AppKit.NSPasteboard.generalPasteboard()
        pasteboard.clearContents()
        
        # Define the types we are writing
        types = [AppKit.NSPasteboardTypeHTML]
        if plain_text:
            types.append(AppKit.NSPasteboardTypeString)
            
        pasteboard.declareTypes_owner_(types, None)
        
        # Set HTML
        pasteboard.setString_forType_(html_content, AppKit.NSPasteboardTypeHTML)
        
        # Set Plain Text (Fallback)
        if plain_text:
            pasteboard.setString_forType_(plain_text, AppKit.NSPasteboardTypeString)
            
    except Exception as e:
        print(f"Error writing to clipboard with AppKit: {e}", file=sys.stderr)

def parse_html_to_clean_html(html_content):
    """
    Parse HTML list structure and reconstruct a clean HTML string.
    """
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')
    
    def get_text_clean(element):
        text = ""
        for child in element.contents:
            if child.name not in ['ul', 'ol']:
                if hasattr(child, 'get_text'):
                    text += child.get_text()
                else:
                    text += str(child)
        return text.strip().replace('\n', ' ')

    def process_list(list_element):
        html_parts = ["<ul>"]
        
        children = list(list_element.children)
        i = 0
        while i < len(children):
            child = children[i]
            if child.name == 'li':
                text = get_text_clean(child)
                html_parts.append(f"<li>{text}")
                
                # Handle nested lists inside this li
                for grandchild in child.children:
                    if grandchild.name in ['ul', 'ol']:
                        html_parts.append(process_list(grandchild))
                
                # Handle nested lists that are next siblings (Google Docs issue)
                # We need to skip whitespace/text nodes to find the next element
                j = i + 1
                while j < len(children):
                    next_sibling = children[j]
                    if next_sibling.name in ['ul', 'ol']:
                        html_parts.append(process_list(next_sibling))
                        j += 1
                    elif isinstance(next_sibling, str) and not next_sibling.strip():
                        # Skip whitespace
                        j += 1
                    else:
                        # Found something else (another li, or text), stop looking for nested lists
                        break
                
                # Update i to point to the last processed element
                # We processed up to j-1
                i = j - 1
                html_parts.append("</li>")
            
            elif child.name in ['ul', 'ol']:
                # Handle orphan lists (shouldn't happen often if structure is valid, but just in case)
                html_parts.append(process_list(child))
                
            i += 1
            
        html_parts.append("</ul>")
        return "".join(html_parts)

    lists = soup.find_all(['ul', 'ol'])
    
    top_level_lists = []
    for l in lists:
        parents = l.find_parents(['ul', 'ol'])
        if not parents:
            top_level_lists.append(l)
            
    final_html = ""
    for l in top_level_lists:
        final_html += process_list(l)
        
    return final_html

def main():
    html = get_clipboard_html()
    if not html:
        print("No HTML found in clipboard.")
        return

    clean_html = parse_html_to_clean_html(html)
    
    if clean_html:
        # Create a plain text version for fallback (simple indentation)
        # We can reuse the logic or just strip tags, but let's just pass None for now 
        # or implement a simple text converter if needed. 
        # For now, let's trust the HTML.
        
        # Actually, having a text fallback is good for debugging.
        # Let's make a simple one.
        soup = BeautifulSoup(clean_html, 'html.parser')
        plain_text = soup.get_text()
        
        set_clipboard_html_with_appkit(clean_html, plain_text)
        print("Converted text copied to clipboard (HTML format)!")
    else:
        print("Could not parse list structure or clipboard was empty.")

if __name__ == "__main__":
    main()
