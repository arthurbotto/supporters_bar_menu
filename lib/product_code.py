import re


def slugify(value):
    v = (value or "").strip().lower()
    v = re.sub(r"[^a-z0-9]+", "_", v)
    v = re.sub(r"_+", "_", v).strip("_")
    return v or "item"


def make_product_code(category, name, producer=None):
    parts = [category or "", name or ""]
    if producer:
        parts.append(producer)
    return slugify("_".join(parts))
