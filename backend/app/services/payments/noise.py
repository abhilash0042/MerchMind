import random
from datetime import date, timedelta


def inject_ref_typo(ref: str, rng: random.Random) -> str:
    if len(ref) < 4:
        return ref.lower()
    choice = rng.choice(["case", "swap", "transpose", "hyphen"])
    if choice == "case":
        return ref.lower() if rng.random() < 0.5 else ref.upper()
    if choice == "swap":
        prefix, num_part = ref.split("-", 1) if "-" in ref else ("", ref)
        if len(num_part) >= 2:
            idx = rng.randint(0, len(num_part) - 2)
            swapped_num = num_part[:idx] + num_part[idx + 1] + num_part[idx] + num_part[idx + 2 :]
            return f"{prefix}-{swapped_num}" if prefix else swapped_num
        return ref
    if choice == "transpose":
        chars = list(ref)
        digit_indices = [i for i, c in enumerate(chars) if c.isdigit()]
        if digit_indices:
            idx = rng.choice(digit_indices)
            curr_d = int(chars[idx])
            chars[idx] = str((curr_d + rng.choice([-1, 1])) % 10)
            return "".join(chars)
        return ref
    return ref.replace("-", rng.choice(["", "_", " "]))


def inject_amount_drift(amount: int, rng: random.Random) -> int:
    drift = rng.randint(1, 5) * rng.choice([-1, 1])
    return max(100, amount + drift)


def generate_messy_narration(utr: str, batch_id: str, rng: random.Random) -> str:
    templates = [
        f"NEFT/CMS/RAZORPAY/{utr}/SETTLEMENT",
        f"ACH CR-RAZORPAY SOFTWARE PRIVATE LIMITED-{utr}-SETL",
        f"RTGS/CORP/{utr}/RAZORPAY RECON/{batch_id}",
        f"CMS-RAZORPAY SETTLEMENT {batch_id} UTR:{utr}",
        f"IMPS/P2A/{utr}/RZPY/{batch_id}",
        f"NEFT CR-{utr}-RAZORPAY-{batch_id}",
    ]
    narration = rng.choice(templates)
    if rng.random() < 0.05:
        narration = narration[: rng.randint(max(8, len(narration) - 6), len(narration) - 1)]
    return narration


def shift_date(dt: date, rng: random.Random, max_days: int = 2) -> date:
    return dt + timedelta(days=rng.choice([-1, 1]) * rng.randint(1, max_days))
