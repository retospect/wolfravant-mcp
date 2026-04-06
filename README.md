# wolfravant-mcp

MCP server for querying [Wolfram Alpha](https://www.wolframalpha.com/) via the Full Results v2 API.

## Setup

```bash
pip install wolfravant-mcp
```

Set `WOLFRAM_APP_ID` to your Wolfram Alpha App ID (get one at https://developer.wolframalpha.com/portal/myapps/).

## Usage

```bash
export WOLFRAM_APP_ID="your-app-id"
wolfravant-mcp
```

The server runs on stdio transport (MCP standard).

## Tool

**`wolfram_alpha(query)`** — query Wolfram Alpha for computations, math, science facts, unit conversions, and data lookups. Returns structured text with titled sections.

## License

GPL-3.0-or-later
