from celery import shared_task
from .helper import translate_file

@shared_task
def translate_file_task(in_path, out_path, src, tgt):
    """ 
    Task wrapper function for translate_file function. 
    Handles errors and provides formatted error messages.
    """
    try:
        return translate_file(in_path, out_path, src, tgt)
    except ValueError as e:
        # Format the error message to be more user-friendly
        if "Invalid MIME" in str(e):
            raise ValueError(f"The file format doesn't match its extension. {str(e)}")
        raise  # Re-raise other ValueError exceptions
    except Exception as e:
        # Handle other unexpected errors
        raise Exception(f"Translation failed: {str(e)}")