#!/usr/bin/env python3
"""
Fetch historical OHLCV klines from the Binance public REST API
and save them to a JSONL (one JSON object per line) and/or CSV file.

No API key required - uses public endpoints only.

Usage:
    python fetch_klines.py --symbol BTCUSDT --interval 1h \
        --start 2024-01-01 --end 2024-02-01 --out btc_1h
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://api.binance.com"
KLINES_ENDPOINT = "/api/v3/klines"
MAX_LIMIT = 1000          # max rows per request (Binance limit)
REQUEST_PAUSE = 0.25      # seconds between requests, be polite
COLUMNS = [
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_volume", "trades",
    "taker_buy_base", "taker_buy_quote", "ignore",
]


def parse_date(s: str) -> int:
    """Convert 'YYYY-MM-DD' to a millisecond timestamp (UTC)."""
    dt = datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_range(symbol: str, interval: str, start_ms: int, end_ms: int):
    """Yield kline rows for [start_ms, end_ms), paginating automatically."""
    session = requests.Session()
    cursor = start_ms
    while cursor < end_ms:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": cursor,
            "endTime": end_ms - 1,
            "limit": MAX_LIMIT,
        }
        resp = session.get(BASE_URL + KLINES_ENDPOINT, params=params, timeout=15)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        for row in rows:
            yield dict(zip(COLUMNS, row))
        cursor = rows[-1][6] + 1  # jump past last close_time
        time.sleep(REQUEST_PAUSE)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch Binance klines to JSONL/CSV.")
    ap.add_argument("--symbol", default="BTCUSDT", help="e.g. BTCUSDT")
    ap.add_argument("--interval", default="1h",
                    help="1m 5m 15m 1h 4h 1d ...")
    ap.add_argument("--start", required=True, help="start date YYYY-MM-DD (UTC)")
    ap.add_argument("--end", required=True, help="end date YYYY-MM-DD (UTC)")
    ap.add_argument("--out", default="klines", help="output file basename")
    args = ap.parse_args()

    start_ms, end_ms = parse_date(args.start), parse_date(args.end)
    if start_ms >= end_ms:
        print("error: --start must be earlier than --end", file=sys.stderr)
        return 1

    jsonl_path = Path(f"{args.out}.jsonl")
    csv_path = Path(f"{args.out}.csv")
    n = 0
    with jsonl_path.open("w") as fj, csv_path.open("w", newline="") as fc:
        writer = csv.DictWriter(fc, fieldnames=COLUMNS)
        writer.writeheader()
        for row in fetch_range(args.symbol, args.interval, start_ms, end_ms):
            fj.write(json.dumps(row) + "\n")
            writer.writerow(row)
            n += 1

    print(f"saved {n} rows -> {jsonl_path} / {csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
