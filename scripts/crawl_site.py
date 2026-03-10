#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
crawl_site.py — Crawl a website following internal links, respecting robots.txt.

Outputs a JSON manifest of all discovered pages with metadata.

Usage:
    python scripts/crawl_site.py <start_url> <output_dir> [options]

Examples:
    python scripts/crawl_site.py https://example.com /tmp/crawl_example
    python scripts/crawl_site.py https://example.com /tmp/crawl_example --max-pages 50 --delay 2

Output:
    <output_dir>/crawl_manifest.json  — JSON list of page records
    <output_dir>/pages/<slug>.html    — Raw HTML for each page
    <output_dir>/robots.txt           — Cached robots.txt (if found)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.robotparser
from html.parser import HTMLParser

# Import the fetch function from fetch_page.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_page import fetch


class LinkExtractor(HTMLParser):
    """Extract href values from <a> tags and metadata from HTML."""

    def __init__(self):
        super().__init__()
        self.links = []
        self.title = ""
        self.meta_description = ""
        self.og_title = ""
        self.h1s = []
        self._in_title = False
        self._in_h1 = False
        self._title_parts = []
        self._h1_parts = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "a" and "href" in attrs_dict:
            self.links.append(attrs_dict["href"])
        elif tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag == "h1":
            self._in_h1 = True
            self._h1_parts = []
        elif tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")
            if name == "description":
                self.meta_description = content
            elif prop == "og:title":
                self.og_title = content

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self._in_title = False
            self.title = " ".join(self._title_parts).strip()
        elif tag == "h1" and self._in_h1:
            self._in_h1 = False
            self.h1s.append(" ".join(self._h1_parts).strip())

    def handle_data(self, data):
        if self._in_title:
            self._title_parts.append(data.strip())
        elif self._in_h1:
            self._h1_parts.append(data.strip())


def url_to_slug(url, base_domain):
    """Convert a URL to a filesystem-safe slug."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "homepage"
    # Replace slashes and special chars with underscores
    slug = re.sub(r'[^a-zA-Z0-9\-]', '_', path)
    slug = re.sub(r'_+', '_', slug).strip('_')
    return slug[:100]  # Limit length


def normalize_url(url, base_url):
    """Normalize a URL relative to a base URL."""
    # Resolve relative URLs
    resolved = urllib.parse.urljoin(base_url, url)
    parsed = urllib.parse.urlparse(resolved)

    # Strip fragments
    normalized = urllib.parse.urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),
        parsed.path.rstrip('/') or '/',
        parsed.params,
        '',  # Drop query string for dedup (keep if needed)
        '',  # Drop fragment
    ))
    return normalized


def is_internal(url, base_domain):
    """Check if a URL belongs to the same domain."""
    parsed = urllib.parse.urlparse(url)
    url_domain = parsed.netloc.lower().lstrip('www.')
    return url_domain == base_domain


def should_skip(url):
    """Skip non-HTML resources and common noise URLs."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path.lower()

    # Skip file extensions that aren't HTML pages
    skip_extensions = (
        '.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.avif',
        '.css', '.js', '.xml', '.json', '.txt', '.zip', '.mp4', '.mp3',
        '.woff', '.woff2', '.ttf', '.eot', '.ico', '.map',
    )
    if any(path.endswith(ext) for ext in skip_extensions):
        return True

    # Skip common non-content paths
    skip_paths = (
        '/wp-admin', '/wp-login', '/wp-json', '/feed',
        '/cart', '/checkout', '/my-account',
        'mailto:', 'tel:', 'javascript:', '#',
    )
    if any(url.lower().startswith(p) or path.startswith(p) for p in skip_paths):
        return True

    return False


def get_robots_parser(base_url, output_dir, timeout=10):
    """Fetch and parse robots.txt, return RobotFileParser."""
    rp = urllib.robotparser.RobotFileParser()
    robots_url = urllib.parse.urljoin(base_url, '/robots.txt')

    try:
        html, _, status, _ = fetch(robots_url, timeout=timeout, retries=2)
        if status == 200:
            # Save a copy
            robots_path = os.path.join(output_dir, 'robots.txt')
            with open(robots_path, 'w', encoding='utf-8') as f:
                f.write(html)
            rp.parse(html.splitlines())
            print(f"[crawl] robots.txt loaded ({len(html)} chars)", file=sys.stderr)
        else:
            print(f"[crawl] robots.txt returned {status}, allowing all", file=sys.stderr)
    except RuntimeError:
        print("[crawl] robots.txt not found, allowing all", file=sys.stderr)

    return rp


def crawl(start_url, output_dir, max_pages=500, delay=1.0, timeout=30, retries=3):
    """Crawl a website starting from start_url.

    Args:
        start_url: The starting URL.
        output_dir: Directory to save HTML files and manifest.
        max_pages: Maximum number of pages to crawl.
        delay: Delay between requests in seconds.
        timeout: Timeout per request.
        retries: Retries per request.

    Returns:
        list: List of page record dicts.
    """
    parsed_start = urllib.parse.urlparse(start_url)
    base_domain = parsed_start.netloc.lower().lstrip('www.')
    base_url = f"{parsed_start.scheme}://{parsed_start.netloc}"

    # Create output directories
    pages_dir = os.path.join(output_dir, 'pages')
    os.makedirs(pages_dir, exist_ok=True)

    # Load robots.txt
    rp = get_robots_parser(base_url, output_dir, timeout)

    # Crawl state
    queue = [normalize_url(start_url, start_url)]
    visited = set()
    pages = []

    print(f"[crawl] Starting crawl of {base_domain} (max {max_pages} pages)", file=sys.stderr)

    while queue and len(pages) < max_pages:
        url = queue.pop(0)

        if url in visited:
            continue

        # Check robots.txt
        if not rp.can_fetch("*", url):
            print(f"[crawl] Blocked by robots.txt: {url}", file=sys.stderr)
            visited.add(url)
            continue

        visited.add(url)

        # Fetch the page
        try:
            html, final_url, status, headers = fetch(url, timeout=timeout, retries=retries)
        except RuntimeError as e:
            print(f"[crawl] Failed: {url} — {e}", file=sys.stderr)
            pages.append({
                "url": url,
                "status": "error",
                "error": str(e),
            })
            continue

        # Check content type — skip non-HTML (but allow missing Content-Type
        # since some CDNs like Duda don't set it)
        content_type = headers.get("Content-Type", "")
        if content_type and "text/html" not in content_type and "application/xhtml" not in content_type:
            # Content-Type is set but not HTML — skip
            print(f"[crawl] Skipping non-HTML: {url} ({content_type})", file=sys.stderr)
            continue
        if not content_type and not html.strip().lstrip('\ufeff').startswith(('<', '<!', '<html', '<HTML')):
            # No Content-Type and doesn't look like HTML — skip
            print(f"[crawl] Skipping non-HTML (no Content-Type, not HTML-like): {url}", file=sys.stderr)
            continue

        # Handle redirects to external sites
        if final_url != url and not is_internal(final_url, base_domain):
            print(f"[crawl] Redirected external: {url} -> {final_url}", file=sys.stderr)
            continue

        # Parse HTML
        extractor = LinkExtractor()
        try:
            extractor.feed(html)
        except Exception:
            pass  # Best-effort parsing

        # Save HTML file
        slug = url_to_slug(final_url, base_domain)
        html_path = os.path.join(pages_dir, f"{slug}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # Build page record — prefer og:title if <title> is empty, too short,
        # or looks like Duda JS-rendered garbage (e.g. "Divider Icon")
        title = extractor.title
        if not title or len(title) < 10 or title in ("Divider Icon",):
            title = extractor.og_title or extractor.title or ""
        page_record = {
            "url": url,
            "final_url": final_url,
            "status": status,
            "slug": slug,
            "file": html_path,
            "title": title,
            "meta_description": extractor.meta_description,
            "h1": extractor.h1s,
            "word_count": len(html.split()),  # Raw estimate, refine per platform
            "internal_links_found": 0,
        }
        pages.append(page_record)

        page_num = len(pages)
        print(f"[crawl] [{page_num}/{max_pages}] {status} {url} — \"{title[:50]}\"", file=sys.stderr)

        # Extract and queue internal links
        links_added = 0
        for href in extractor.links:
            if should_skip(href):
                continue

            normalized = normalize_url(href, final_url)

            if not is_internal(normalized, base_domain):
                continue

            if normalized not in visited and normalized not in queue:
                queue.append(normalized)
                links_added += 1

        page_record["internal_links_found"] = links_added

        # Polite delay
        if queue and len(pages) < max_pages:
            time.sleep(delay)

    # Save manifest
    manifest_path = os.path.join(output_dir, 'crawl_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump({
            "domain": base_domain,
            "start_url": start_url,
            "pages_crawled": len(pages),
            "pages_in_queue": len(queue),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "pages": pages,
        }, f, indent=2)

    print(f"\n[crawl] Done: {len(pages)} pages crawled, {len(queue)} remaining in queue", file=sys.stderr)
    print(f"[crawl] Manifest: {manifest_path}", file=sys.stderr)

    return pages


def main():
    parser = argparse.ArgumentParser(description="Crawl a website following internal links")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("output_dir", help="Directory to save crawl output")
    parser.add_argument("--max-pages", type=int, default=500, help="Maximum pages to crawl (default: 500)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds (default: 1.0)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per request in seconds (default: 30)")
    parser.add_argument("--retries", type=int, default=3, help="Retries per request (default: 3)")
    args = parser.parse_args()

    pages = crawl(
        args.url,
        args.output_dir,
        max_pages=args.max_pages,
        delay=args.delay,
        timeout=args.timeout,
        retries=args.retries,
    )

    # Summary to stdout
    print(json.dumps({
        "total_pages": len(pages),
        "successful": sum(1 for p in pages if p.get("status") != "error"),
        "errors": sum(1 for p in pages if p.get("status") == "error"),
    }))


if __name__ == "__main__":
    main()
