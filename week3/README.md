# Week 3 MCP Server: US Stock Quotes

This project implements a local (STDIO) MCP server that wraps a real external API to fetch the latest US stock/ETF quote data.

## External API Used

- Provider: Stooq public quote endpoint
- Endpoint: `GET https://stooq.com/q/l/?s=<symbol>.us&f=sd2t2ohlcv&h&e=csv`
- Fields used:
  - `Close` (latest price)
  - `Volume` (latest volume)
  - `Date`, `Time`, `Open`, `High`, `Low`

## Features

- Local MCP server over STDIO
- Two MCP tools (single and batch quote lookup)
- Input normalization and validation for US format like `US VOO`
- Resilience for timeout/network/HTTP failures
- Basic rate-limit handling (429 retry with short backoff)
- Logs routed to stderr (safe for STDIO MCP transport)

## Folder Structure

- `week3/server/main.py` - MCP server entrypoint
- `week3/server/requirements.txt` - Python dependencies

## Prerequisites

- Python 3.10+
- pip
- An MCP-capable client (Claude Desktop, Cursor, etc.)

## Setup

From `week3/server`:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run (Local STDIO)

From `week3/server`:

```bash
python main.py
```

## MCP Client Configuration (Cursor Example)

Example `mcp.json` entry:

```json
{
  "mcpServers": {
    "us-stock-quote-server": {
      "command": "D:/Anaconda/envs/cs146s/python.exe",
      "args": [
        "D:/Github/cs146S/modern-software-dev-assignments/week3/server/main.py"
      ],
      "env": {
        "LOG_LEVEL": "INFO",
        "STOOQ_USER_AGENT": "us-stock-mcp-server/1.0"
      }
    }
  }
}
```

Notes:
- `LOG_LEVEL` and `STOOQ_USER_AGENT` are optional.
- Keep logs on stderr only for STDIO transport.
- Replace the Python path with your local interpreter if needed.

## Tool Reference

### 1) `get_latest_us_stock_quote`

Get latest US stock/ETF price and volume from one input string.

- Parameters:
  - `stock` (`string`): input like `US VOO` or `VOO`
- Returns:
  - normalized symbol
  - latest quote object including `price` and `volume`
- Example input:
  - `stock = "US VOO"`
- Example output shape:

```json
{
  "input": "US VOO",
  "normalized_symbol": "VOO",
  "quote": {
    "symbol": "VOO",
    "source_symbol": "VOO.US",
    "exchange": "US",
    "currency": "USD",
    "price": 632.21,
    "volume": 80095,
    "open": 627.15,
    "high": 633.09,
    "low": 625.4,
    "quote_date": "2026-02-24",
    "quote_time": "22:00:19"
  }
}
```

### 2) `get_latest_us_stock_quotes`

Get latest US stock/ETF price and volume for multiple input strings.

- Parameters:
  - `stocks` (`string[]`): each item like `US VOO` or `VOO`
- Returns:
  - `requested_count`
  - `results` array with one entry per input:
    - `input`
    - `normalized_symbol`
    - `quote` (object or `null`)
    - `error` (`null` on success, message string on fetch/parse failure)
- Important behavior:
  - If `stocks` is empty, the tool raises an error.
  - If any input has invalid format/symbol syntax, the tool raises an error before returning results.
  - For valid symbols, upstream failures are captured per item (`quote = null`, `error` populated).
- Example input:
  - `stocks = ["US VOO", "US SPY", "QQQ"]`
- Example output shape:

```json
{
  "requested_count": 3,
  "results": [
    {
      "input": "US VOO",
      "normalized_symbol": "VOO",
      "quote": {
        "symbol": "VOO",
        "price": 632.21,
        "volume": 80095
      },
      "error": null
    }
  ]
}
```

## Example Invocation Flow

In your MCP client:
1. Start/reload MCP servers.
2. Select `us-stock-quote-server`.
3. Call `get_latest_us_stock_quote` with `stock="US VOO"`.
4. Call `get_latest_us_stock_quotes` with `stocks=["US VOO","US SPY"]`.
5. Verify that returned `quote.price` and `quote.volume` are populated.

## Error Handling Behavior

- Invalid input format -> clear validation errors
- Invalid ticker format (`^[A-Z][A-Z0-9.\-]{0,9}$`) -> validation error
- Timeout/network failure -> user-facing upstream error
- HTTP failure -> user-facing status error
- Empty upstream result -> no-data error
- Missing required upstream fields (`Close`/`Volume`) -> no-data error
- Batch tool returns per-item `error` for fetch failures while continuing other symbols
- Rate limit (`429`) -> one retry with short backoff and warning log

## Optional Improvements

- Add API key based provider as fallback
- Add an MCP `resource` for market status metadata
- Add tests with mocked API responses
