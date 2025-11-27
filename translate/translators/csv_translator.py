# CSV Translation Module
import json
import re
import time
import pandas as pd
from openai import OpenAIError
from .utils import batched, client, MODEL


def _tool_schema():
    return [{
        "type": "function",
        "function": {
            "name": "return_translations",
            "description": "Return translations aligned with input indexes",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "i": {"type": "integer"},
                                "t": {"type": "string"}
                            },
                            "required": ["i", "t"]
                        }
                    }
                },
                "required": ["items"]
            }
        }
    }]


def _build_prompt(items, src: str, tgt: str, note: str = "") -> str:
    intro = (
        f"You are a professional translator. Translate from {src} to {tgt}. "
        f"Preserve meaning, tone, punctuation, numbers, and line breaks. "
        f"Translate text exactly as given without adding commentary."
    )
    constraints = (
        "Return results ONLY by calling the function return_translations with an array 'items' "
        "of objects {{i, t}} where 'i' is the provided index and 't' is the translation. "
        "Return translations for ALL provided indexes, no more, no fewer, and do not reorder."
    )
    payload = json.dumps({"items": items}, ensure_ascii=False)
    extra = f"\n\nNote: {note}" if note else ""
    return f"{intro}\n{constraints}{extra}\n\nInput JSON:\n{payload}"


def _extract_items_from_response(r):
    choice = r.choices[0].message
    # Prefer tool call output
    tool_calls = getattr(choice, "tool_calls", None)
    if tool_calls:
        for tc in tool_calls:
            try:
                if getattr(tc, "type", "") == "function" and getattr(tc.function, "name", "") == "return_translations":
                    args = tc.function.arguments
                    data = json.loads(args) if isinstance(args, str) else args
                    return data.get("items")
            except Exception:
                continue
    # Fallback: try to parse content as JSON
    content = (choice.content or "").strip()
    if content:
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            if isinstance(data, list):
                # List of strings
                return [{"i": i, "t": s} for i, s in enumerate(data)]
        except Exception:
            pass
    return None


_SYMBOLS_RE = re.compile(r"^[\W_]+$", re.UNICODE)


def _is_passthrough(text: str) -> bool:
    """Return True if text should bypass translation (numbers/blank/symbol-only)."""
    if text is None:
        return True
    s = str(text)
    if not s.strip():
        return True
    # number-like (int/float) or symbol-only
    try:
        float(s.replace(",", "").replace(" ", ""))
        return True
    except Exception:
        pass
    return bool(_SYMBOLS_RE.match(s))


def translate_csv_chunk(texts, src, tgt, max_attempts: int = 3):
    """Translate a list of CSV cell texts using structured tool-call output.

    Ensures stable index alignment and retries to fill any missing items.
    """
    if not texts:
        return []

    n = len(texts)
    remaining_indexes = list(range(n))
    collected = {}

    # Pre-fill passthrough items to avoid LLM skipping them
    for i, val in enumerate(texts):
        if _is_passthrough(val):
            collected[i] = str(val)

    # Prepare input items with indexes and source text
    full_items = [{"i": i, "s": texts[i]} for i in range(n) if i not in collected]

    attempts = 0
    while attempts < max_attempts and remaining_indexes:
        attempts += 1
        # Build the subset to ask for (all on first pass, missing thereafter)
        ask_items = (
            full_items if attempts == 1 else [{"i": i, "s": texts[i]} for i in remaining_indexes]
        )
        note = "" if attempts == 1 else (
            f"Retry {attempts-1}: Only return translations for the listed missing indexes. "
            f"Do not include any other indexes."
        )

        try:
            r = client.chat.completions.create(
                model=MODEL,
                temperature=0.1,
                messages=[{
                    "role": "user",
                    "content": _build_prompt(ask_items, src, tgt, note)
                }],
                tools=_tool_schema(),
                tool_choice={"type": "function", "function": {"name": "return_translations"}},
            )
        except OpenAIError as e:
            raise RuntimeError(f"I am really sorry an error happened/ Çok ama çok üzgünüm bir hata oluştu {e}")
        except Exception as e:
            raise RuntimeError(f"Your app run into a problem :( {e} ")

        items = _extract_items_from_response(r)
        if not items:
            # Give the model another shot next loop
            time.sleep(0.2)
            continue

        # Merge valid items by index
        for obj in items:
            try:
                i = int(obj.get("i"))
                t = obj.get("t")
            except Exception:
                continue
            if i in range(n) and isinstance(t, str):
                collected[i] = t

        # Update remaining indexes
        remaining_indexes = [i for i in range(n) if i not in collected]
        if remaining_indexes:
            time.sleep(0.2)  # light backoff before retrying missing ones

    # Final fallback: fill any missing with original text to maintain alignment
    if len(collected) != n:
        missing = [i for i in range(n) if i not in collected]
        for i in missing:
            collected[i] = str(texts[i])

    # Build final list in order of original indexes
    return [collected[i] for i in range(n)]

def translate_csv(in_path: str, out_path: str, src: str, tgt: str, batch_size: int = 80):
    """Translate a CSV file"""
    df = pd.read_csv(str(in_path), header=None, dtype=str).fillna('')
    if df.empty:
        df.to_csv(str(out_path), index=False, header=False)
        print(f"Empty CSV. Saved copy → {out_path}")
        return

    original_series = df.stack()
    is_translatable = original_series.astype(str).str.strip().astype(bool)
    to_translate = original_series[is_translatable]

    if to_translate.empty:
        df.to_csv(str(out_path), index=False, header=False)
        print(f"No text to translate in CSV. Saved copy → {out_path}")
        return

    texts = to_translate.tolist()
    translated = []
    for chunk in batched(texts, batch_size):
        translated.extend(translate_csv_chunk(chunk, src, tgt))

    translated_series = pd.Series(translated, index=to_translate.index)
    df.update(translated_series.unstack())
    df.to_csv(str(out_path), index=False, header=False)
    print(f"Translated CSV → {out_path}")

