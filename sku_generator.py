import json
import random
import re

with open("brand_codes.json", "r", encoding="utf-8") as f:
    BRAND_CODES = json.load(f)

with open("subbrands.json", "r", encoding="utf-8") as f:
    SUBBRANDS = json.load(f)

SUBBRAND_CODES = {}

for brand, values in SUBBRANDS.items():
    for value in values:

        value = str(value).upper().strip()

        words = re.findall(r"[A-Z0-9]+", value)

        if not words:
            continue

        if len(words) >= 2:
            code = words[0][:2] + words[1][:1]
        else:
            code = words[0][:3]

        SUBBRAND_CODES[value] = code[:3]


def detect_subbrand(title):

    title = str(title).upper()

    best_match = None
    longest = 0

    for subbrand in SUBBRAND_CODES:

        if subbrand in title:

            if len(subbrand) > longest:
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

    brand_code = BRAND_CODES.get(
        vendor,
        vendor[:3]
    )

    subbrand_code = detect_subbrand(title)

    unique_number = generate_unique_number(
        used_numbers
    )

    return f"{brand_code}-{subbrand_code}-{unique_number}"