# Main entry point for translation functionality
# This file now imports from the modular translator components

# For backward compatibility and easy imports
from .translator import translate_file
from .translators import translate_docx, translate_pdf, translate_csv, translate_xlsx

# All translation functionality is now available through the modular imports above
# Example usage:
#   from .helper import translate_file
#   translate_file("document.pdf", "output.pdf", "English", "Turkish")

# For backward compatibility, also provide the old function name
def translate_any(in_path, out_path=None, src="English", tgt="Turkish"):
    """Alias for translate_file for backward compatibility"""
    return translate_file(in_path, out_path, src, tgt)
