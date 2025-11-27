# Common utilities for all translators
import os
from itertools import islice
from dotenv import load_dotenv
from openai import OpenAI

# -------- OpenAI client --------
# Set OPENAI_API_KEY in your environment.
load_dotenv()

client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],

    
)
MODEL = "gpt-4o-mini"

# -------- Delimiters --------
# DOCX uses a two-level scheme (paragraphs + runs)
PARA_DELIM = "<§§PARA§§>"
RUN_DELIM  = "<§§RUN§§>"

# CSV/XLSX use a single delimiter between cells
CELL_DELIM = "<§§§DELIM§§§>"

# PDF use a single delimiter between blocks
BLOCK_DELIM = "<§§§DELIM§§§>"

# -------- batching --------
def batched(it, n=80):
    """Split an iterable into batches of size n"""
    it = iter(it)
    while True:
        chunk = list(islice(it, n))
        if not chunk:
            break
        yield chunk
