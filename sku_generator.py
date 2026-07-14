import json
import os
import random
import re

BRAND_FILE = "brand_codes.json"
SUBBRAND_FILE = "subbrands.json"
OVERRIDE_FILE = "subbrand_overrides.json"


def load_json(path, default):
    """Read JSON regardless of BOM / UTF-16 vs UTF-8 encoding."""
    if not os.path.exists(path):
        return default

    with open(path, "rb") as f:
        raw = f.read()

    if not raw.strip():
        return default

    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text = raw.decode("utf-16")
    elif raw.startswith(b"\xef\xbb\xbf"):
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8")

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return default


def save_json(path, data):
    """Always write plain UTF-8, no BOM."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


BRAND_CODES = load_json(BRAND_FILE, {})
SUBBRANDS = load_json(SUBBRAND_FILE, {})
SUBBRAND_OVERRIDES = load_json(OVERRIDE_FILE, {})

SUBBRAND_CODES = {}


def make_subbrand_code(value):
    words = re.findall(r"[A-Z0-9]+", str(value).upper())
    if not words:
        return None
    if len(words) >= 2:
        code = words[0][:2] + words[1][:1]
    else:
        code = words[0][:3]
    return code[:3]


def rebuild_subbrand_codes():
    SUBBRAND_CODES.clear()
    for brand, values in SUBBRANDS.items():
        for value in values:
            value = str(value).upper().strip()
            code = make_subbrand_code(value)
            if code:
                SUBBRAND_CODES[value] = code
    for value, code in SUBBRAND_OVERRIDES.items():
        SUBBRAND_CODES[str(value).upper().strip()] = str(code).upper().strip()[:3]


rebuild_subbrand_codes()


def add_brand(vendor, code=None, save=True):
    vendor = str(vendor).upper().strip()
    if not vendor:
        raise ValueError("Brand name is empty")

    if code:
        code = str(code).upper().strip()[:3]
    else:
        code = re.sub(r"[^A-Z0-9]", "", vendor)[:3]

    BRAND_CODES[vendor] = code
    if save:
        save_json(BRAND_FILE, BRAND_CODES)
    return code


def add_subbrand(vendor, subbrand, code=None, save=True):
    vendor = str(vendor).upper().strip()
    subbrand = str(subbrand).upper().strip()

    if not vendor or not subbrand:
        raise ValueError("Brand and subbrand are required")

    if vendor not in BRAND_CODES:
        add_brand(vendor, save=save)

    SUBBRANDS.setdefault(vendor, [])
    if subbrand not in [str(v).upper().strip() for v in SUBBRANDS[vendor]]:
        SUBBRANDS[vendor].append(subbrand)

    if code:
        SUBBRAND_OVERRIDES[subbrand] = str(code).upper().strip()[:3]

    if save:
        save_json(SUBBRAND_FILE, SUBBRANDS)
        if code:
            save_json(OVERRIDE_FILE, SUBBRAND_OVERRIDES)

    rebuild_subbrand_codes()
    return SUBBRAND_CODES[subbrand]


def detect_subbrand(title):
    title = str(title).upper()
    best_match = None
    longest = 0

    for subbrand in SUBBRAND_CODES:
        if subbrand in title and len(subbrand) > longest:
            longest = len(subbrand)
            best_match = subbrand

    if best_match:
        return SUBBRAND_CODES[best_match]
    return "GEN"


def generate_unique_number(used_numbers):
    while True:
        num = random.randint(1000, 9999)
        if num not in used_numbers:
            used_numbers.add(num)
            return str(num)


def generate_sku(title, vendor, used_numbers):
    vendor = str(vendor).upper().strip()
    brand_code = BRAND_CODES.get(vendor, vendor[:3])
    subbrand_code = detect_subbrand(title)
    unique_number = generate_unique_number(used_numbers)
    return f"{brand_code}-{subbrand_code}-{unique_number}"