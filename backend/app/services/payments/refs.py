import re
from typing import Tuple


def normalize_ref_string(ref: str) -> str:
    if not ref:
        return ""
    cleaned = str(ref).strip().lower()
    return re.sub(r"[\s_]+", "-", cleaned)


def extract_utr_and_batch_from_narration(narration: str) -> Tuple[str, str]:
    utr = ""
    batch_id = ""
    if not narration:
        return utr, batch_id
    utr_match = re.search(r"(UTR\w+RZP|UTR[:\s-]*\w+)", narration, re.IGNORECASE)
    if utr_match:
        utr = utr_match.group(1).replace(":", "").replace(" ", "").strip().upper()
    batch_match = re.search(r"(STL-BB-\d+|STL-\d+)", narration, re.IGNORECASE)
    if batch_match:
        batch_id = batch_match.group(1).upper()
    return utr, batch_id


def rupees_to_paise(value) -> int:
    try:
        return int(round(float(value) * 100))
    except (TypeError, ValueError):
        return 0


def razorpay_fee_split(gross_paise: int) -> tuple[int, int, int]:
    fee = int(round(gross_paise * 0.02))
    gst = int(round(fee * 0.18))
    net = gross_paise - fee - gst
    return fee, gst, net
