from fastapi import FastAPI
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
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Empty input")

    # -------- Currency --------
    currency_match = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    currency = (
        currency_match.group(1).upper()
        if currency_match
        else "USD"
    )

    # -------- Date --------
    date_match = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", text)
    date = date_match.group(0) if date_match else "1970-01-01"

    # -------- Amount --------
    amount = 0.0

    patterns = [
        r"Total\s*(?:Due)?[:\s]*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"Amount\s*(?:Due)?[:\s]*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"Due[:\s]*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",
        r"[$€£]\s*([0-9]+(?:\.[0-9]+)?)"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    # -------- Vendor --------
    vendor = ""

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    ignore = [
        "invoice",
        "bill",
        "date",
        "due",
        "total",
        "amount",
        "currency",
        "payment",
    ]

    for line in lines:
        low = line.lower()

        if any(word in low for word in ignore):
            continue

        if re.search(r"[A-Za-z]", line):
            vendor = line
            break

    if vendor == "":
        vendor = "Unknown"

    return ExtractResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date,
    )