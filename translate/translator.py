# Main translator dispatcher - clean and modular
from io import BytesIO
from pathlib import Path
import zipfile
from .translators import translate_docx, translate_pdf, translate_csv, translate_xlsx
import magic


MIME_MAPPINGS = {
    ".docx": ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"],
    ".csv": ["text/csv", "text/plain", "application/csv"],
    ".xlsx": [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        'application/zip',
    ],
    ".pdf": ["application/pdf"]
}




def translate_file(in_path, out_path=None, src="English", tgt="Turkish"):
    """
    Main function to translate files of different formats.
    
    Args:
        in_path: Input file path
        out_path: Output file path (optional, auto-generated if None)
        src: Source language (default: "English")
        tgt: Target language (default: "Turkish")
    
    Returns:
        str: Path to the translated file
    """
    in_path = Path(in_path)
    if out_path is None:
        # e.g., report.xlsx -> report.tr.xlsx  (using 2-letter of tgt)
        out_path = in_path.with_suffix(f".{tgt[:2]}{in_path.suffix}")
    else:
        out_path = Path(out_path)

    ext = in_path.suffix.lower()
    in_path_str = str(in_path)
    out_path_str = str(out_path)
    
    mime = detect_mime(in_path).lower()
    valid_mimes = [m.lower() for m in MIME_MAPPINGS[ext]] 
    if mime not in valid_mimes:
        raise ValueError(f"Invalid MIME '{mime}' for {ext}. Expected one of {valid_mimes}")
        
    if ext == ".docx":
        translate_docx(in_path_str, out_path_str, src, tgt)
    elif ext == ".csv":
        translate_csv(in_path_str, out_path_str, src, tgt)
    elif ext == ".xlsx":
        check_xlsx(in_path_str)
        translate_xlsx(in_path_str, out_path_str, src, tgt)
    elif ext == ".pdf":                                       
        translate_pdf(in_path_str, out_path_str, src, tgt)   
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return out_path_str

# For backward compatibility, keep the original function name
def translate_any(in_path, out_path=None, src="English", tgt="Turkish"):
    """Alias for translate_file for backward compatibility"""
    return translate_file(in_path, out_path, src, tgt)


def detect_mime(path: Path) -> str:
    """Detect real MIME type of a file using magic bytes."""
    with open(path, "rb") as f:
        sample = f.read(2048)
    return magic.from_buffer(sample, mime=True)

def check_xlsx(in_path):
    try:
        with zipfile.ZipFile(in_path) as z:
            return 'xl/workbook.xml' in z.namelist()
    except zipfile.BadZipFile:
        return False