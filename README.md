# crypto-klines-fetcher

Download historical OHLCV klines from the Binance **public** REST API into
JSONL and CSV files. No API key, no authentication — public endpoints only.

## Features

- Automatic pagination (handles 1000-row request limit transparently)
- Polite rate limiting between requests
- Writes both JSONL (one JSON object per line) and CSV

## Install

```bash
pip install requests
```

## Usage

```bash
python fetch_klines.py --symbol BTCUSDT --interval 1h \
    --start 2024-01-01 --end 2024-02-01 --out btc_1h
```

Output files: `btc_1h.jsonl` and `btc_1h.csv`.

## Supported intervals

`1m 3m 5m 15m 30m 1h 2h 4h 6h 8h 12h 1d 3d 1w 1M`

## Disclaimer

For educational/personal use. Market data via Binance public API; verify
data quality yourself before any analysis. This project provides no
investment advice.

## License

MIT
