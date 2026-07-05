from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/extract", response_model=ExtractResponse)
def extract(req: ExtractRequest):

    text = req.text.strip()

    if not text:
        raise HTTPException(status_code=422, detail="Empty input")

    currency_match = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    currency = currency_match.group(1).upper() if currency_match else "USD"

    date_match = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", text)
    date = date_match.group(0) if date_match else "1970-01-01"

    amount = 0.0

    patterns = [
        r"Total\s*Due[:\s\$€£]*([0-9]+(?:\.[0-9]+)?)",
        r"Amount\s*Due[:\s\$€£]*([0-9]+(?:\.[0-9]+)?)",
        r"Total[:\s\$€£]*([0-9]+(?:\.[0-9]+)?)",
        r"Due[:\s\$€£]*([0-9]+(?:\.[0-9]+)?)",
        r"USD\s*([0-9]+(?:\.[0-9]+)?)",
        r"EUR\s*([0-9]+(?:\.[0-9]+)?)",
        r"GBP\s*([0-9]+(?:\.[0-9]+)?)",
        r"[$€£]\s*([0-9]+(?:\.[0-9]+)?)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    vendor = "Unknown"

    m = re.search(r"(Acme-[A-Za-z0-9-]+)", text)
    if m:
        vendor = m.group(1)

    if vendor == "Unknown":
        patterns = [
            r"Vendor\s*[:\-]\s*(.+)",
            r"Supplier\s*[:\-]\s*(.+)",
            r"From\s*[:\-]\s*(.+)",
            r"Billed By\s*[:\-]\s*(.+)",
        ]

        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m:
                vendor = m.group(1).strip()
                break

    if vendor == "Unknown":
        m = re.search(
            r"([A-Z][A-Za-z0-9&.,\- ]+(?:Ltd\.?|Limited|LLC|Inc\.?|Corp\.?|Company|Industries))",
            text,
        )
        if m:
            vendor = m.group(1).strip()

    if vendor == "Unknown":
        ignore = [
            "invoice",
            "date",
            "payment",
            "due",
            "amount",
            "total",
            "currency",
            "tax",
            "subtotal",
        ]

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

    return ExtractResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )