import os
from pathlib import Path
import shutil
from typing import Optional
from pdf2zh_next import WatermarkOutputMode, do_translate_file, SettingsModel


def _find_generated_pdf(output_dir: Path, original_pdf: Path) -> Optional[Path]:
    """Return the newest PDF in output_dir that is not the original file."""
    candidates = [p for p in output_dir.glob("*.pdf") if p.name != original_pdf.name and p.is_file()]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def translate_pdf(pdf_path, out_path_str, src, tgt):

    # Prepare paths
    out_path = Path(out_path_str)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    original_pdf = Path(pdf_path)
    output_dir = out_path.parent

    settings = SettingsModel(
        basic={'input_files': {str(original_pdf)}},
        translation={
            'lang_in': src, 
            'lang_out': tgt,
            'output': str(output_dir),
            'save_auto_extracted_glossary':False,
            'no_auto_extract_glossary':True},
        translate_engine_settings={
            'translate_engine_type': 'OpenAI',
            'openai_model':'gpt-4o-mini',
            # 'openai_base_url':'https://generativelanguage.googleapis.com/v1beta/openai/', 
            'openai_api_key': os.environ['OPENAI_API_KEY']
            # Add your service-specific settings
        },
        pdf={'no_dual':True, 'watermark_output_mode':WatermarkOutputMode.NoWatermark},

    )

    error_count = do_translate_file(settings, ignore_error=False)

    if error_count == 0:
        generated = _find_generated_pdf(output_dir, original_pdf)
        if generated and generated.exists():
            try:
                shutil.move(str(generated), str(out_path))
            except Exception:
                shutil.copy2(str(generated), str(out_path))

    return str(out_path)
