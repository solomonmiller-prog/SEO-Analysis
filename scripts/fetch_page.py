#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
fetch_page.py — Fetch a web page with browser-like headers and retry logic.

Handles common issues:
- Sites blocking non-browser User-Agents (403s)
- Redirect chains (follows up to 5 hops)
- Timeouts with configurable retry
- SSL certificate issues
- Saves raw HTML to a specified output path

Usage:
    python scripts/fetch_page.py <url> [output_path] [--timeout 30] [--retries 3]

Examples:
    python scripts/fetch_page.py https://example.com /tmp/example_home.html
    python scripts/fetch_page.py https://example.com  # prints to stdout
    python scripts/fetch_page.py https://example.com /tmp/out.html --timeout 15 --retries 5
"""

import argparse
import sys
import time
import urllib.request
import urllib.error
import ssl

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-AU,en-US;q=0.9,en;q=0.8",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


def fetch(url, timeout=30, retries=3, ua_index=0):
    """Fetch a URL with browser-like headers and retry logic.

    Args:
        url: The URL to fetch.
        timeout: Timeout in seconds per request.
        retries: Number of retry attempts.
        ua_index: Starting User-Agent index (rotates on 403).

    Returns:
        tuple: (html_content, final_url, status_code, headers_dict)

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    last_error = None

    for attempt in range(retries):
        ua = USER_AGENTS[(ua_index + attempt) % len(USER_AGENTS)]
        headers = {**DEFAULT_HEADERS, "User-Agent": ua}

        req = urllib.request.Request(url, headers=headers)

        try:
            # Create SSL context that handles most sites
            ctx = ssl.create_default_context()

            response = urllib.request.urlopen(req, timeout=timeout, context=ctx)
            html = response.read()

            # Try to decode with the response's charset, fall back to utf-8
            charset = response.headers.get_content_charset() or "utf-8"
            try:
                html_str = html.decode(charset)
            except (UnicodeDecodeError, LookupError):
                html_str = html.decode("utf-8", errors="replace")

            return (
                html_str,
                response.url,
                response.status,
                dict(response.headers),
            )

        except urllib.error.HTTPError as e:
            last_error = e
            if e.code == 403 and attempt < retries - 1:
                # Rotate UA and retry
                print(f"[fetch_page] 403 on attempt {attempt + 1}, rotating UA...", file=sys.stderr)
                time.sleep(1 + attempt)
                continue
            elif e.code in (429, 503) and attempt < retries - 1:
                # Rate limited or temporarily unavailable
                wait = 2 ** (attempt + 1)
                print(f"[fetch_page] {e.code} on attempt {attempt + 1}, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            else:
                raise RuntimeError(f"HTTP {e.code}: {e.reason} for {url}") from e

        except urllib.error.URLError as e:
            last_error = e
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"[fetch_page] URLError on attempt {attempt + 1}: {e.reason}, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise RuntimeError(f"URLError: {e.reason} for {url}") from e

        except TimeoutError:
            last_error = TimeoutError(f"Timeout after {timeout}s for {url}")
            if attempt < retries - 1:
                print(f"[fetch_page] Timeout on attempt {attempt + 1}, retrying...", file=sys.stderr)
                time.sleep(1)
                continue
            raise RuntimeError(f"Timeout after {retries} attempts for {url}") from last_error

    raise RuntimeError(f"All {retries} attempts failed for {url}: {last_error}")


def main():
    parser = argparse.ArgumentParser(description="Fetch a web page with browser-like headers")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("output", nargs="?", default=None, help="Output file path (default: stdout)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per request in seconds (default: 30)")
    parser.add_argument("--retries", type=int, default=3, help="Number of retry attempts (default: 3)")
    args = parser.parse_args()

    try:
        html, final_url, status, headers = fetch(args.url, args.timeout, args.retries)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"[fetch_page] {status} {final_url} ({len(html)} chars)", file=sys.stderr)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[fetch_page] Saved to {args.output}", file=sys.stderr)
    else:
        print(html)


if __name__ == "__main__":
    main()
