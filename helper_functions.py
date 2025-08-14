import time
import json
from db.schema import settings
from typing import List


def timing_wrapper(func):
    """Measure execution time of a function."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"Time taken by {func.__name__}: {round(time.time() - start, 2)} seconds")
        return result
    return wrapper


def store_data_in_json(filename: str, data: List):
    """Dump all processed interviews to JSON."""
    filepath= settings.BASE_DIR / "03_files" / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)