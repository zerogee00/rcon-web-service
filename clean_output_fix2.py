import re

def clean_output_text(text):
    """Clean ANSI color codes and other formatting from text"""
    if not text:
        return text
    
    # Remove ANSI escape sequences like [0m, [1m, etc. (both actual escape codes and literal text)
    ansi_escape = re.compile(r'\x1B\[[0-9;]*m')
    text = ansi_escape.sub('', text)
    
    # Remove literal ANSI codes like [0m
    literal_ansi = re.compile(r'\[[0-9;]*m')
    text = literal_ansi.sub('', text)
    
    # Remove other ANSI sequences
    ansi_escape2 = re.compile(r'\x1B\[[0-9;]*[a-zA-Z]')
    text = ansi_escape2.sub('', text)
    
    # Remove Minecraft formatting codes (§ followed by character)
    minecraft_escape = re.compile(r'§[0-9a-fA-F]')
    text = minecraft_escape.sub('', text)
    
    return text.strip()

# Test the function
test_text = "To view help from the console, type '?'.[0m\n[0m"
print("Original:", repr(test_text))
print("Cleaned:", repr(clean_output_text(test_text)))
