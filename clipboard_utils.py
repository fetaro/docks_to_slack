import AppKit

def set_clipboard_html(html_content: str, plain_text: str = None):
    """
    Sets the macOS clipboard to the given HTML content.
    Optionally sets a plain text fallback.
    """
    pasteboard = AppKit.NSPasteboard.generalPasteboard()
    pasteboard.clearContents()
    
    # Define the types we are writing
    # NSPasteboardTypeHTML is 'public.html'
    # NSPasteboardTypeString is 'public.utf8-plain-text'
    
    # Note: In some PyObjC versions/macOS versions, constants might need to be strings if not imported.
    # We will try to use the constants from AppKit.
    
    types = [AppKit.NSPasteboardTypeHTML]
    if plain_text:
        types.append(AppKit.NSPasteboardTypeString)
        
    pasteboard.declareTypes_owner_(types, None)
    
    # Set HTML
    pasteboard.setString_forType_(html_content, AppKit.NSPasteboardTypeHTML)
    
    # Set Plain Text
    if plain_text:
        pasteboard.setString_forType_(plain_text, AppKit.NSPasteboardTypeString)

def get_clipboard_types():
    """
    Returns a list of types currently on the clipboard.
    """
    pasteboard = AppKit.NSPasteboard.generalPasteboard()
    return pasteboard.types()

def get_clipboard_content(type_name):
    """
    Returns the string content for a specific type.
    """
    pasteboard = AppKit.NSPasteboard.generalPasteboard()
    return pasteboard.stringForType_(type_name)
