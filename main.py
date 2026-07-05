
vendor = "Unknown"

patterns = [
    r"Vendor\s*[:\-]\s*(.+)",
    r"From\s*[:\-]\s*(.+)",
    r"Supplier\s*[:\-]\s*(.+)",
    r"Billed By\s*[:\-]\s*(.+)",
]

for p in patterns:
    m = re.search(p, text, re.IGNORECASE)
    if m:
        vendor = m.group(1).strip()
        break

if vendor == "Unknown":
    company = re.search(
        r"([A-Z][A-Za-z0-9\-&., ]*(?:Ltd\.?|LLC|Inc\.?|Industries|Company|Corp\.?|Limited))",
        text,
    )
    if company:
        vendor = company.group(1).strip()

if vendor == "Unknown":
    ignore = {
        "invoice",
        "invoice number",
        "invoice #",
        "date",
        "due date",
        "payment due",
        "total",
        "amount",
        "subtotal",
        "tax",
        "currency",
    }

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        low = line.lower()

        if any(word in low for word in ignore):
            continue

        if re.search(r"[A-Za-z]", line):
            vendor = line
            break