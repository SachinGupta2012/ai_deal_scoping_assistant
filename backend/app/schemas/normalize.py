"""Tolerant ID normalization for AI output — semantic suffixes (COMP_FE) mapped to numeric contract (COMP_01)."""
import re


def normalize_ids(items, prefix: str, key: str, ref_fields) -> tuple:
    """Return (items, mermaid_or_text) untouched; remap ids in-place. Returns items list."""
    if not isinstance(items, list):
        return items
    valid = re.compile(rf"^{prefix}_[0-9]{{2,}}$")
    mapping: dict = {}
    for item in items:
        raw = str((item or {}).get(key, ""))
        if raw and not valid.match(raw) and raw not in mapping:
            mapping[raw] = None
    for i, raw in enumerate(mapping, start=1):
        mapping[raw] = f"{prefix}_{i:02d}"
    for item in items:
        raw = str((item or {}).get(key, ""))
        if raw in mapping:
            item[key] = mapping[raw]
            for rf in ref_fields:
                if isinstance(item.get(rf), list):
                    item[rf] = [mapping.get(x, x) if not valid.match(str(x)) else x for x in item[rf]]
    return items


def remap_text(text: str, mapping: dict) -> str:
    """Replace ids inside mermaid/diagram text using word boundaries."""
    if not text or not mapping:
        return text
    for raw, new in mapping.items():
        text = re.sub(rf"(?<![A-Za-z0-9_]){re.escape(raw)}(?![A-Za-z0-9_])", new, text)
    return text
