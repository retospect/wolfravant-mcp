"""wolfravant-mcp — Wolfram Alpha MCP server.

Wraps the official ``wolframalpha`` PyPI client (v2 Full Results API).
Requires WOLFRAM_APP_ID environment variable.
"""

from __future__ import annotations

import os

import wolframalpha
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("wolfram-alpha")

_client: wolframalpha.Client | None = None


def _get_client() -> wolframalpha.Client:
    global _client
    if _client is None:
        app_id = os.environ.get("WOLFRAM_APP_ID", "")
        if not app_id:
            raise RuntimeError("WOLFRAM_APP_ID environment variable is not set")
        _client = wolframalpha.Client(app_id)
    return _client


def _format_result(res: wolframalpha.Result) -> str:
    """Parse Wolfram Alpha result pods into clean text for LLMs."""
    if not res.success:
        tips = []
        if hasattr(res, "didyoumeans") and res.didyoumeans:
            dym = res.didyoumeans
            if isinstance(dym, dict):
                dym = [dym]
            suggestions = [d.get("#text", str(d)) for d in dym]
            tips.append(f"Did you mean: {', '.join(suggestions)}")
        if tips:
            return "Query failed. " + " ".join(tips)
        return "No results found for this query."

    sections: list[str] = []
    for pod in res.pods:
        title = pod.get("@title", "Result")
        texts: list[str] = []
        for sub in pod.get("subpod", []):
            if isinstance(sub, str):
                continue
            plaintext = sub.get("plaintext")
            if plaintext:
                texts.append(plaintext)
        if texts:
            sections.append(f"## {title}\n{chr(10).join(texts)}")

    if not sections:
        return "Query succeeded but returned no displayable text."

    return "\n\n".join(sections)


@mcp.tool()
def wolfram_alpha(query: str) -> str:
    """Query Wolfram Alpha for computations, math, science facts, unit conversions, and data lookups.

    query: natural language or mathematical expression (e.g. "integrate sin(x)cos(x)",
           "population of Ireland", "convert 5 miles to km", "derivative of x^3",
           "ISS current position", "nutritional info for 100g of rice")

    Returns structured text with titled sections (Input, Result, Plot descriptions, etc.).
    """
    client = _get_client()
    try:
        res = client.query(query)
    except Exception as e:
        return f"Wolfram Alpha API error: {e}"
    return _format_result(res)


def main():
    """Run the MCP server (stdio transport)."""
    mcp.run()


if __name__ == "__main__":
    main()
