#!/usr/bin/env python3
"""
IONOS Cloud Network Hub - Local Proxy Server

Part of IONOS Cloud Network Hub - an interactive force-directed graph
visualization of IONOS Cloud Virtual Data Center network topology.

This lightweight server does two things:
  1. Serves the ionos-cloud-network-hub.html frontend
  2. Proxies API requests to IONOS Cloud APIs (avoids CORS issues)

Usage:
  python3 serve.py
  python3 serve.py --port 8080

Then open http://localhost:8080 in your browser.
No pip dependencies required - uses only Python standard library.

License: Apache-2.0
"""

import http.server
import urllib.request
import urllib.parse
import urllib.error
import ssl
import json
import socket
import sys
import re
import time
import webbrowser
import argparse
from pathlib import Path
from typing import Optional

PORT = 8080
HTML_FILE = "ionos-cloud-network-hub.html"
SCRIPT_DIR = Path(__file__).parent.resolve()
MAX_PORT_RETRIES = 10
REQUEST_TIMEOUT_SECONDS = 30
MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves static files and proxies IONOS API calls."""

    server_port: int = PORT  # set at runtime from main()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

    # ── Routing ──────────────────────────────────────────────────────

    def do_GET(self) -> None:
        """Route GET requests to the proxy, health endpoint, or static files."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/proxy":
            self._handle_proxy(parsed)
        elif parsed.path == "/price-list":
            self._handle_price_list()
        elif parsed.path == "/health":
            self._send_json_response(200, {"status": "ok"})
        elif parsed.path in ("/", ""):
            self.path = f"/{HTML_FILE}"
            super().do_GET()
        else:
            super().do_GET()

    def end_headers(self) -> None:
        """Add no-cache headers for static files to prevent stale content."""
        if not self.path.startswith("/proxy"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def do_POST(self) -> None:
        """Route POST requests to the proxy or MCP docs endpoint."""
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/proxy":
            self._handle_proxy(parsed, method="POST")
        elif parsed.path == "/mcp-docs":
            self._handle_mcp_docs(self.MCP_DOCS_URL)
        elif parsed.path == "/mcp-docs-support":
            self._handle_mcp_docs(self.MCP_DOCS_SUPPORT_URL)
        elif parsed.path == "/mcp-docs-tutorials":
            self._handle_mcp_docs(self.MCP_DOCS_TUTORIALS_URL)
        else:
            self._send_json_error(501, f"Unsupported POST path: {parsed.path}")

    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self._add_cors_headers()
        self.end_headers()

    # ── Proxy ────────────────────────────────────────────────────────

    def _handle_proxy(self, parsed: urllib.parse.ParseResult, method: str = "GET") -> None:
        """Forward a request to the IONOS API and relay the response."""
        params = urllib.parse.parse_qs(parsed.query)
        target_url = params.get("url", [""])[0].strip()

        if not target_url:
            self._send_json_error(400, "Missing 'url' query parameter")
            return

        # Validate URL scheme (prevent file://, gopher://, etc.)
        target_parsed = urllib.parse.urlparse(target_url)
        if target_parsed.scheme not in ("http", "https"):
            self._send_json_error(400, "Only HTTP/HTTPS URLs are allowed")
            return

        # Validate the target is an IONOS API endpoint
        target_host = (target_parsed.hostname or "").lower()
        allowed_hosts = ["api.ionos.com"]
        is_allowed = any(
            target_host == h or target_host.endswith(f".{h}")
            for h in allowed_hosts
        )
        is_ionos_regional = target_host.endswith(".ionos.com")

        if not (is_allowed or is_ionos_regional):
            self._send_json_error(
                403, f"Proxy blocked: {target_host} is not an IONOS endpoint"
            )
            return

        # Read auth token from header (never from URL)
        token = self.headers.get("X-Token", "")
        contract = self.headers.get("X-Contract-Number", "")
        if not token:
            self._send_json_error(401, "Missing X-Token header")
            return

        # Build the upstream request
        post_data = None
        if method == "POST":
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)

        req = urllib.request.Request(target_url, method=method, data=post_data)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "IONOS-Cloud-Network-Hub/1.1")
        if contract:
            req.add_header("X-Contract-Number", contract)

        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(
                req, context=ctx, timeout=REQUEST_TIMEOUT_SECONDS
            ) as resp:
                body = resp.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    self._send_json_error(
                        413, f"Response exceeds {MAX_RESPONSE_BYTES // (1024*1024)} MB limit"
                    )
                    return
                self.send_response(resp.status)
                content_type = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", content_type)
                self._add_cors_headers()
                self.end_headers()
                self.wfile.write(body)

        except urllib.error.HTTPError as e:
            try:
                error_body = e.read(2048).decode("utf-8", errors="replace")
            except Exception:
                error_body = "(unable to read error response)"
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self._add_cors_headers()
            self.end_headers()
            self.wfile.write(
                json.dumps({
                    "error": f"IONOS API returned {e.code}",
                    "detail": error_body[:500],
                }).encode()
            )
        except urllib.error.URLError as e:
            self._send_json_error(502, f"Could not reach IONOS API: {e.reason}")
        except socket.timeout:
            self._send_json_error(504, "API request timed out")
        except OSError as e:
            self._send_json_error(502, f"Network error: {e}")

    # ── Price List (direct page fetch + cache) ──────────────────────

    PRICE_LIST_URL = (
        "https://docs.ionos.com/cloud/support/general-information/"
        "price-list/ionos-cloud-se-en"
    )
    _price_list_cache: Optional[str] = None
    _price_list_cache_ts: float = 0
    PRICE_LIST_CACHE_TTL = 3600  # 1 hour

    def _handle_price_list(self) -> None:
        """Fetch the IONOS price list page, extract content, cache, return text."""
        now = time.time()
        # Return cached version if fresh
        cls = type(self)
        if (cls._price_list_cache
                and (now - cls._price_list_cache_ts) < cls.PRICE_LIST_CACHE_TTL):
            self._send_json_response(200, {
                "text": cls._price_list_cache, "cached": True
            })
            return

        try:
            req = urllib.request.Request(
                self.PRICE_LIST_URL,
                method="GET",
            )
            req.add_header("User-Agent", "IONOS-Cloud-Network-Hub/1.1")
            req.add_header("Accept", "text/html")
            ctx = ssl.create_default_context()

            with urllib.request.urlopen(
                req, context=ctx, timeout=REQUEST_TIMEOUT_SECONDS
            ) as resp:
                html = resp.read(512 * 1024).decode("utf-8", errors="replace")

            sys.stderr.write(
                f"  [PriceList] Fetched {len(html)} bytes HTML\n"
            )

            text = ""

            # ── Strategy 1: Extract from __NEXT_DATA__ JSON (GitBook/Next.js) ──
            # GitBook renders pages via JS. The actual content is embedded in a
            # <script id="__NEXT_DATA__"> JSON blob as pre-rendered markdown.
            next_data_match = re.search(
                r'<script\s+id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                html, re.DOTALL
            )
            if next_data_match:
                try:
                    nd = json.loads(next_data_match.group(1))
                    # GitBook embeds page content at various paths in the JSON.
                    # Walk the tree to find markdown/text content.
                    text = self._extract_gitbook_content(nd)
                    if text:
                        sys.stderr.write(
                            f"  [PriceList] Extracted {len(text)} chars "
                            f"from __NEXT_DATA__\n"
                        )
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    sys.stderr.write(
                        f"  [PriceList] __NEXT_DATA__ parse failed: {e}\n"
                    )

            # ── Strategy 2: Look for structured data in page (JSON-LD, tables) ──
            if not text:
                # Try to extract table data specifically (pricing is usually in tables)
                tables = re.findall(
                    r'<table[^>]*>(.*?)</table>', html,
                    flags=re.DOTALL | re.IGNORECASE
                )
                if tables:
                    table_text = []
                    for tbl in tables:
                        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl,
                                          flags=re.DOTALL | re.IGNORECASE)
                        for row in rows:
                            cells = re.findall(
                                r'<t[hd][^>]*>(.*?)</t[hd]>', row,
                                flags=re.DOTALL | re.IGNORECASE
                            )
                            cells = [re.sub(r'<[^>]+>', '', c).strip()
                                     for c in cells]
                            if any(cells):
                                table_text.append(' | '.join(cells))
                    if table_text:
                        text = '\n'.join(table_text)
                        sys.stderr.write(
                            f"  [PriceList] Extracted {len(text)} chars "
                            f"from HTML tables ({len(tables)} tables)\n"
                        )

            # ── Strategy 3: Fallback — strip all HTML ──
            if not text:
                text = re.sub(
                    r'<(script|style|noscript|svg|path)[^>]*>.*?</\1>', '',
                    html, flags=re.DOTALL | re.IGNORECASE
                )
                text = re.sub(r'<[^>]+>', ' ', text)
                # Decode common entities
                for ent, ch in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
                                ('&quot;', '"'), ('&#39;', "'"), ('&nbsp;', ' '),
                                ('&#x20AC;', '€'), ('&euro;', '€')]:
                    text = text.replace(ent, ch)
                text = re.sub(r'[ \t]+', ' ', text)
                text = re.sub(r'\n{3,}', '\n\n', text)
                text = text.strip()
                sys.stderr.write(
                    f"  [PriceList] Fallback HTML strip → {len(text)} chars\n"
                )

            # Truncate to keep context manageable
            if len(text) > 16000:
                text = text[:16000] + '\n\n[Price list truncated — see full list at ' + self.PRICE_LIST_URL + ']'

            # Log a preview so we can debug content quality
            preview = text[:500].replace('\n', '\\n')
            sys.stderr.write(f"  [PriceList] Preview: {preview}\n")

            cls._price_list_cache = text
            cls._price_list_cache_ts = now
            self._send_json_response(200, {
                "text": text, "cached": False
            })

        except urllib.error.HTTPError as e:
            self._send_json_error(e.code, f"Price list fetch failed: {e.code}")
        except urllib.error.URLError as e:
            self._send_json_error(502, f"Could not reach price list: {e.reason}")
        except socket.timeout:
            self._send_json_error(504, "Price list request timed out")
        except OSError as e:
            self._send_json_error(502, f"Network error: {e}")

    @staticmethod
    def _extract_gitbook_content(nd: dict) -> str:
        """Walk a GitBook __NEXT_DATA__ JSON tree to find page content.

        GitBook stores rendered content in various locations depending on
        version. We try several known paths and also do a recursive search
        for markdown-like text blocks.
        """
        # Known paths in GitBook's __NEXT_DATA__ structure
        paths_to_try = [
            # GitBook v2 structure
            lambda d: d['props']['pageProps']['page']['document']['nodes'],
            lambda d: d['props']['pageProps']['page']['markdown'],
            lambda d: d['props']['pageProps']['page']['description'],
            # GitBook v3 / newer structure
            lambda d: d['props']['pageProps']['customization'],
            lambda d: d['props']['pageProps']['body'],
            # Alternative structures
            lambda d: d['props']['pageProps']['content'],
        ]

        for path_fn in paths_to_try:
            try:
                val = path_fn(nd)
                if isinstance(val, str) and len(val) > 200:
                    return val
                elif isinstance(val, (list, dict)):
                    # Recursively extract text from nested structures
                    extracted = ProxyHandler._extract_text_recursive(val)
                    if len(extracted) > 200:
                        return extracted
            except (KeyError, TypeError, IndexError):
                continue

        # Last resort: search the entire JSON for any large text blocks
        # that look like pricing content
        all_text = ProxyHandler._extract_text_recursive(nd)
        if len(all_text) > 200:
            return all_text

        return ""

    @staticmethod
    def _extract_text_recursive(obj, depth: int = 0) -> str:
        """Recursively extract text from nested JSON structures."""
        if depth > 15:
            return ""
        if isinstance(obj, str):
            # Only include substantial text blocks, skip tiny ones
            if len(obj) > 20 and not obj.startswith(('http', 'data:', '/')):
                return obj + '\n'
            return ""
        if isinstance(obj, list):
            parts = []
            for item in obj:
                parts.append(
                    ProxyHandler._extract_text_recursive(item, depth + 1)
                )
            return ''.join(parts)
        if isinstance(obj, dict):
            parts = []
            # Prioritize known content keys
            for key in ('text', 'value', 'content', 'markdown', 'body',
                        'description', 'title', 'name', 'label',
                        'leaves', 'nodes', 'children', 'data'):
                if key in obj:
                    parts.append(
                        ProxyHandler._extract_text_recursive(
                            obj[key], depth + 1
                        )
                    )
            # Also check remaining keys
            for key, val in obj.items():
                if key not in ('text', 'value', 'content', 'markdown', 'body',
                               'description', 'title', 'name', 'label',
                               'leaves', 'nodes', 'children', 'data'):
                    if isinstance(val, (list, dict)):
                        parts.append(
                            ProxyHandler._extract_text_recursive(
                                val, depth + 1
                            )
                        )
            return ''.join(parts)
        return ""

    # ── MCP Docs (GitBook) ─────────────────────────────────────────

    # IONOS docs portal is hosted on GitBook which exposes an MCP server.
    # We proxy JSON-RPC requests to it so the AI assistant can search docs.
    MCP_DOCS_URL = "https://docs.ionos.com/cloud/~gitbook/mcp"
    MCP_DOCS_SUPPORT_URL = "https://docs.ionos.com/cloud/support/~gitbook/mcp"
    MCP_DOCS_TUTORIALS_URL = "https://docs.ionos.com/cloud/tutorials/~gitbook/mcp"

    def _handle_mcp_docs(self, upstream_url: str = None) -> None:
        """Proxy a JSON-RPC request to an IONOS GitBook MCP endpoint.

        GitBook's built-in MCP uses Streamable HTTP transport, which may
        return responses as Server-Sent Events (text/event-stream) instead
        of plain JSON.  We detect this and extract the JSON-RPC message
        from the SSE `data:` lines so the frontend always receives JSON.
        """
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json_error(400, "Empty request body")
            return
        if content_length > 64 * 1024:  # 64 KB max
            self._send_json_error(413, "Request body too large")
            return

        post_data = self.rfile.read(content_length)

        # Forward the session ID if we have one
        mcp_session = self.headers.get("Mcp-Session-Id", "")

        target_url = upstream_url or self.MCP_DOCS_URL
        req = urllib.request.Request(
            target_url,
            method="POST",
            data=post_data,
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json, text/event-stream")
        req.add_header(
            "User-Agent", "IONOS-Cloud-Network-Hub/1.1"
        )
        if mcp_session:
            req.add_header("Mcp-Session-Id", mcp_session)

        ctx = ssl.create_default_context()

        try:
            with urllib.request.urlopen(
                req, context=ctx, timeout=REQUEST_TIMEOUT_SECONDS
            ) as resp:
                raw_body = resp.read(MAX_RESPONSE_BYTES)
                content_type = resp.headers.get("Content-Type", "")
                session_id = resp.headers.get("Mcp-Session-Id", "")
                sys.stderr.write(
                    f"  [MCP] upstream status={resp.status} "
                    f"type={content_type} "
                    f"session={session_id[:20] if session_id else 'none'} "
                    f"body_len={len(raw_body)}\n"
                )
                # Log first 300 chars of body for debugging
                sys.stderr.write(
                    f"  [MCP] body preview: "
                    f"{raw_body[:300].decode('utf-8', errors='replace')}\n"
                )

                # If the response is SSE, extract JSON-RPC from data: lines
                if "text/event-stream" in content_type:
                    body = self._extract_json_from_sse(raw_body)
                else:
                    body = raw_body

                self.send_response(resp.status)
                self.send_header("Content-Type", "application/json")
                if session_id:
                    self.send_header("Mcp-Session-Id", session_id)
                self._add_cors_headers()
                self.end_headers()
                self.wfile.write(body)

        except urllib.error.HTTPError as e:
            try:
                error_body = e.read(2048).decode("utf-8", errors="replace")
            except Exception:
                error_body = ""
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self._add_cors_headers()
            self.end_headers()
            self.wfile.write(
                json.dumps({
                    "error": f"MCP endpoint returned {e.code}",
                    "detail": error_body[:500],
                }).encode()
            )
        except urllib.error.URLError as e:
            self._send_json_error(
                502, f"Could not reach IONOS docs MCP: {e.reason}"
            )
        except socket.timeout:
            self._send_json_error(504, "MCP docs request timed out")
        except OSError as e:
            self._send_json_error(502, f"Network error: {e}")

    @staticmethod
    def _extract_json_from_sse(raw: bytes) -> bytes:
        """Parse an SSE stream and return the last JSON-RPC message.

        GitBook Streamable HTTP responses look like:
            event: message
            data: {"jsonrpc":"2.0","id":1,"result":{...}}

        We collect all `data:` lines, try to parse them as JSON, and
        return the last valid JSON-RPC response (which is the final
        result for the request).
        """
        text = raw.decode("utf-8", errors="replace")
        last_json: bytes = b"{}"
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("data:"):
                payload = stripped[5:].strip()
                if not payload:
                    continue
                try:
                    # Validate it's JSON
                    json.loads(payload)
                    last_json = payload.encode("utf-8")
                except (json.JSONDecodeError, ValueError):
                    pass
        return last_json

    # ── Helpers ──────────────────────────────────────────────────────

    def _send_json_response(self, code: int, data: dict) -> None:
        """Send a JSON response with the given status code."""
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._add_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_json_error(self, code: int, message: str) -> None:
        """Send a JSON error response."""
        self._send_json_response(code, {"error": message})

    def _add_cors_headers(self) -> None:
        """Add CORS headers scoped to localhost origins."""
        origin = self.headers.get("Origin", "")
        if origin.startswith("http://localhost:") or origin.startswith("http://127.0.0.1:"):
            self.send_header("Access-Control-Allow-Origin", origin)
        else:
            # Fallback for direct browser access (no Origin header)
            self.send_header(
                "Access-Control-Allow-Origin",
                f"http://localhost:{ProxyHandler.server_port}",
            )
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Expose-Headers", "Mcp-Session-Id")
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type, X-Token, Authorization, X-Contract-Number, Mcp-Session-Id",
        )

    def log_message(self, format: str, *args) -> None:
        """Quieter logging - only show proxy requests, MCP, and errors."""
        msg = format % args
        if "/proxy?" in msg or "/mcp" in msg or "error" in msg.lower():
            sys.stderr.write(f"  {msg}\n")


def main() -> None:
    """Start the local proxy server."""
    parser = argparse.ArgumentParser(
        description="IONOS Cloud Network Hub - Local Server"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=PORT,
        help=f"Port to listen on (default: {PORT})",
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1",
        help="Address to bind to (default: 127.0.0.1, use 0.0.0.0 for Docker)",
    )
    parser.add_argument(
        "--no-browser", action="store_true",
        help="Don't auto-open the browser",
    )
    args = parser.parse_args()

    html_path = SCRIPT_DIR / HTML_FILE
    if not html_path.exists():
        print(f"ERROR: {HTML_FILE} not found in {SCRIPT_DIR}")
        print(
            "Make sure ionos-cloud-network-hub.html is in the same "
            "directory as this script."
        )
        sys.exit(1)

    # Auto-fallback: try requested port, then next ports if busy
    port = args.port
    server: Optional[http.server.HTTPServer] = None
    for attempt in range(MAX_PORT_RETRIES + 1):
        try:
            server = http.server.HTTPServer((args.host, port), ProxyHandler)
            break
        except OSError:
            if attempt < MAX_PORT_RETRIES:
                print(
                    f"  Port {port} is busy, trying {port + 1}...",
                    file=sys.stderr,
                )
                port += 1
            else:
                print(
                    f"ERROR: Could not bind to any port in range "
                    f"{args.port}-{port}",
                    file=sys.stderr,
                )
                sys.exit(1)

    ProxyHandler.server_port = port
    url = f"http://localhost:{port}"

    print()
    print("  ╔═══════════════════════════════════════════════════╗")
    print("  ║     IONOS Cloud Network Hub                       ║")
    print("  ╠═══════════════════════════════════════════════════╣")
    print(f"  ║  Running at: {url:<36} ║")
    if port != args.port:
        note = f"(port {args.port} was busy)"
        print(f"  ║  {note:<49} ║")
    print("  ║  Press Ctrl+C to stop                             ║")
    print("  ╚═══════════════════════════════════════════════════╝")
    print()

    if not args.no_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
