# app/utils/slugify.py
import re
from unicodedata import normalize

def slugify(value: str) -> str:
    """
    Simple slugify: lower, remove non-alnum, replace spaces with hyphens.
    """
    value = normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)
