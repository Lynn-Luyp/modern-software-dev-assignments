from __future__ import annotations

import csv
import io
import logging
import os
import re
import sys
import time
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP


LOGGER = logging.getLogger("us_stock_mcp")
if not LOGGER.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )
    LOGGER.addHandler(handler)
LOGGER.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

MCP_SERVER = FastMCP("us-stock-quote-server")
STOOQ_QUOTE_URL = "https://stooq.com/q/l/"
DEFAULT_TIMEOUT_SECONDS = 8.0
DEFAULT_USER_AGENT = "us-stock-mcp-server/1.0"
TICKER_PATTERN = re.compile(r"^[A-Z][A-Z0-9.\-]{0,9}$")


class QuoteError(ValueError):
    """Raised for user-facing quote request errors."""


def _parse_us_symbol(raw_input: str) -> str:
    value = (raw_input or "").strip().upper()
    if not value:
        raise QuoteError("Input is empty. Use format like 'US VOO' or 'VOO'.")

    parts = value.split()
    if len(parts) == 1:
        symbol = parts[0]
    elif len(parts) == 2 and parts[0] == "US":
        symbol = parts[1]
    else:
        raise QuoteError(
            f"Invalid input '{raw_input}'. Expected 'US <SYMBOL>' or '<SYMBOL>'."
        )

    if not TICKER_PATTERN.match(symbol):
        raise QuoteError(
            f"Invalid symbol '{symbol}'. Symbols must be 1-10 chars: A-Z, 0-9, '.', '-'."
        )
    return symbol


def _request_quote_row(symbol: str) -> dict[str, str]:
    headers = {"User-Agent": os.getenv("STOOQ_USER_AGENT", DEFAULT_USER_AGENT)}
    params = {
        "s": f"{symbol.lower()}.us",
        "f": "sd2t2ohlcv",
        "h": "",
        "e": "csv",
    }
    timeout = httpx.Timeout(DEFAULT_TIMEOUT_SECONDS)

    with httpx.Client(timeout=timeout, headers=headers) as client:
        response = client.get(STOOQ_QUOTE_URL, params=params)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            wait_seconds = 1.0
            if retry_after and retry_after.isdigit():
                wait_seconds = min(float(retry_after), 5.0)
            LOGGER.warning("Rate limited by Stooq API; backing off for %.2fs.", wait_seconds)
            time.sleep(wait_seconds)
            response = client.get(STOOQ_QUOTE_URL, params=params)

        response.raise_for_status()
        csv_text = response.text

    reader = csv.DictReader(io.StringIO(csv_text))
    row = next(reader, None)
    if not row:
        raise QuoteError("No quote data returned from upstream API.")
    return row


def _format_quote(symbol: str, row: dict[str, str]) -> dict[str, Any]:
    if row.get("Close") in (None, "N/D") or row.get("Volume") in (None, "N/D"):
        raise QuoteError("Quote is missing required fields (symbol/price/volume).")

    quote_date = row.get("Date")
    quote_time = row.get("Time")
    if quote_date == "N/D":
        quote_date = None
    if quote_time == "N/D":
        quote_time = None

    return {
        "symbol": symbol,
        "source_symbol": row.get("Symbol"),
        "exchange": "US",
        "currency": "USD",
        "price": float(row["Close"]),
        "volume": int(float(row["Volume"])),
        "open": None if row.get("Open") == "N/D" else float(row["Open"]),
        "high": None if row.get("High") == "N/D" else float(row["High"]),
        "low": None if row.get("Low") == "N/D" else float(row["Low"]),
        "quote_date": quote_date,
        "quote_time": quote_time,
    }


def _fetch_quote(symbol: str) -> dict[str, Any]:
    try:
        row = _request_quote_row(symbol)
    except httpx.TimeoutException as exc:
        LOGGER.exception("Timeout when requesting Stooq.")
        raise QuoteError("Upstream API timeout. Please try again.") from exc
    except httpx.HTTPStatusError as exc:
        LOGGER.exception("HTTP error from Stooq: %s", exc.response.status_code)
        raise QuoteError(f"Upstream API HTTP error: {exc.response.status_code}.") from exc
    except httpx.RequestError as exc:
        LOGGER.exception("Network error when requesting Stooq.")
        raise QuoteError(f"Network error calling upstream API: {exc}.") from exc
    except ValueError as exc:
        LOGGER.exception("Invalid CSV values from Stooq.")
        raise QuoteError("Upstream API returned invalid data.") from exc

    return _format_quote(symbol, row)


@MCP_SERVER.tool()
def get_latest_us_stock_quote(stock: str) -> dict[str, Any]:
    """Get latest US stock/ETF price and volume from input like 'US VOO' or 'VOO'."""
    symbol = _parse_us_symbol(stock)
    return {
        "input": stock,
        "normalized_symbol": symbol,
        "quote": _fetch_quote(symbol),
    }


@MCP_SERVER.tool()
def get_latest_us_stock_quotes(stocks: list[str]) -> dict[str, Any]:
    """Get latest price and volume for multiple US symbols, each in 'US XXX' or 'XXX' format."""
    if not stocks:
        raise QuoteError("Input list is empty. Provide at least one symbol.")

    ordered_quotes = []
    for original in stocks:
        symbol = _parse_us_symbol(original)
        quote: dict[str, Any] | None = None
        error: str | None = None
        try:
            quote = _fetch_quote(symbol)
        except QuoteError as exc:
            error = str(exc)
        ordered_quotes.append(
            {
                "input": original,
                "normalized_symbol": symbol,
                "quote": quote,
                "error": error,
            }
        )

    return {
        "requested_count": len(stocks),
        "results": ordered_quotes,
    }


if __name__ == "__main__":
    MCP_SERVER.run(transport="stdio")
