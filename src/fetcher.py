#!/usr/bin/env python3
import os, time, hmac, base64, hashlib
from urllib.parse import urlsplit
import requests

API_URL  = os.getenv("API_URL", "https://utilities.aperkel.w3.uvm.edu/public/api/unpaid.php")
API_KEY  = os.getenv("API_KEY", "")
HMAC_KEY = os.getenv("HMAC_KEY")  # optional but recommended

def _signed_headers(method: str, url: str, body: bytes = b""):
    if not API_KEY:
        raise RuntimeError("API_KEY not set in environment")
    u = urlsplit(url)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query
    headers = {"X-API-Key": API_KEY}
    if HMAC_KEY:
        ts = str(int(time.time()))
        base = f"{method}\n{path}\n{ts}\n".encode() + (body or b"")
        sig  = base64.b64encode(hmac.new(HMAC_KEY.encode(), base, hashlib.sha256).digest()).decode()
        headers["X-Timestamp"] = ts
        headers["X-Signature"] = sig
    return headers

def get_unpaid_bills_summary():
    headers = _signed_headers("GET", API_URL)
    r = requests.get(API_URL, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        return None, 0.0
    return data.get("perPerson") or [], float(data.get("totalOutstanding") or 0.0)

def get_detailed_unpaid_bills():
    headers = _signed_headers("GET", API_URL)
    r = requests.get(API_URL, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("detail") or []

def main():
    import json
    pp, total = get_unpaid_bills_summary()
    print("TOTAL:", total)
    print("PER PERSON:", pp)
    detail = get_detailed_unpaid_bills()
    print("DETAIL:", json.dumps(detail[:5], indent=2))  # first few

if __name__ == '__main__':
    main()

