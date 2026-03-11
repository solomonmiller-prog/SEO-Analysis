#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
preflight.py — Pre-flight checks for SEO audit.

Verifies site is reachable, detects CMS, checks robots.txt for AI crawler
directives, checks llms.txt, sitemap presence, and estimates page count.

Usage:
    python scripts/preflight.py <url>

Output:
    JSON to stdout with preflight results.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_page import fetch


CMS_SIGNATURES = {
    "duda": [
        'class="dmBody"',
        "FLAVOR: FLAVOR_FLAVOR_FLAVOR",
        "dudaone.com",
        "dm-home-page",
    ],
    "wordpress": [
        "wp-content/",
        "wp-includes/",
        '<meta name="generator" content="WordPress',
    ],
    "shopify": [
        "cdn.shopify.com",
        "Shopify.theme",
        "shopify-section",
    ],
    "wix": [
        "wix.com",
        "X-Wix-",
        "wixsite.com",
    ],
    "squarespace": [
        "squarespace.com",
        '<meta name="generator" content="Squarespace',
        "squarespace-cdn.com",
    ],
}

AI_CRAWLERS = [
    "GPTBot",
    "ChatGPT-User",
    "ClaudeBot",
    "PerplexityBot",
    "OAI-SearchBot",
    "Google-Extended",
    "CCBot",
    "Bytespider",
]


def detect_cms(html, headers):
    """Detect CMS from HTML signatures and headers."""
    for cms, signatures in CMS_SIGNATURES.items():
        for sig in signatures:
            if sig in html or sig in str(headers):
                return cms
    return "custom"


def parse_robots_txt(robots_text):
    """Parse robots.txt and extract disallow rules and AI crawler directives."""
    result = {
        "found": True,
        "raw_length": len(robots_text),
        "disallow_rules": [],
        "ai_crawlers": {},
        "sitemaps": [],
    }

    current_agent = None
    for line in robots_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Parse User-agent
        match = re.match(r"^User-agent:\s*(.+)$", line, re.IGNORECASE)
        if match:
            current_agent = match.group(1).strip()
            continue

        # Parse Disallow
        match = re.match(r"^Disallow:\s*(.*)$", line, re.IGNORECASE)
        if match:
            path = match.group(1).strip()
            if path:
                result["disallow_rules"].append({
                    "agent": current_agent or "*",
                    "path": path,
                })
            continue

        # Parse Sitemap
        match = re.match(r"^Sitemap:\s*(.+)$", line, re.IGNORECASE)
        if match:
            result["sitemaps"].append(match.group(1).strip())
            continue

    # Check AI crawler access
    for crawler in AI_CRAWLERS:
        status = "allowed"  # default if not mentioned
        for rule in result["disallow_rules"]:
            agent = rule["agent"]
            if agent == crawler or agent == "*":
                if rule["path"] == "/":
                    # Specific crawler block overrides wildcard allow
                    if agent == crawler:
                        status = "blocked"
                        break
                    elif agent == "*":
                        status = "blocked_by_wildcard"
        # Check if crawler has its own User-agent section that allows
        # (specific allow overrides wildcard block)
        result["ai_crawlers"][crawler] = status

    return result


def check_llms_txt(base_url):
    """Check for /llms.txt presence and content."""
    llms_url = urllib.parse.urljoin(base_url, "/llms.txt")
    try:
        content, _, status, _ = fetch(llms_url, timeout=10, retries=2)
        if status == 200 and len(content.strip()) > 0:
            return {
                "found": True,
                "url": llms_url,
                "length": len(content),
                "content": content[:2000],  # Truncate for JSON
            }
    except RuntimeError:
        pass
    return {"found": False, "url": llms_url}


def check_sitemap(base_url):
    """Check sitemap.xml presence and count URLs."""
    sitemap_url = urllib.parse.urljoin(base_url, "/sitemap.xml")
    try:
        content, _, status, _ = fetch(sitemap_url, timeout=15, retries=2)
        if status == 200:
            # Count <loc> tags
            url_count = len(re.findall(r"<loc>", content))
            # Check if it's a sitemap index
            is_index = "<sitemapindex" in content
            return {
                "found": True,
                "url": sitemap_url,
                "is_index": is_index,
                "url_count": url_count,
            }
    except RuntimeError:
        pass
    return {"found": False, "url": sitemap_url}


def estimate_pages(html, base_url):
    """Estimate page count from homepage internal links."""
    from html.parser import HTMLParser

    base_parsed = urllib.parse.urlparse(base_url)
    base_domain = base_parsed.netloc.lower().lstrip("www.")

    class LinkCounter(HTMLParser):
        def __init__(self):
            super().__init__()
            self.internal_links = set()

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                attrs_dict = dict(attrs)
                href = attrs_dict.get("href", "")
                if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
                    return
                resolved = urllib.parse.urljoin(base_url, href)
                parsed = urllib.parse.urlparse(resolved)
                domain = parsed.netloc.lower().lstrip("www.")
                if domain == base_domain:
                    # Normalize
                    normalized = parsed.path.rstrip("/") or "/"
                    self.internal_links.add(normalized)

    counter = LinkCounter()
    try:
        counter.feed(html)
    except Exception:
        pass

    return len(counter.internal_links)


def run_preflight(url):
    """Run all pre-flight checks."""
    parsed = urllib.parse.urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    domain = parsed.netloc.lower().lstrip("www.")

    result = {
        "url": url,
        "domain": domain,
        "base_url": base_url,
        "reachable": False,
        "status_code": None,
        "final_url": None,
        "cms": None,
        "robots_txt": None,
        "llms_txt": None,
        "sitemap": None,
        "estimated_pages": 0,
    }

    # 1. Fetch homepage
    print(f"[preflight] Fetching {url}...", file=sys.stderr)
    try:
        html, final_url, status, headers = fetch(url)
        result["reachable"] = True
        result["status_code"] = status
        result["final_url"] = final_url
    except RuntimeError as e:
        result["error"] = str(e)
        return result

    # 2. Detect CMS
    result["cms"] = detect_cms(html, headers)
    print(f"[preflight] CMS detected: {result['cms']}", file=sys.stderr)

    # 3. Check robots.txt
    print("[preflight] Checking robots.txt...", file=sys.stderr)
    robots_url = urllib.parse.urljoin(base_url, "/robots.txt")
    try:
        robots_text, _, robots_status, _ = fetch(robots_url, timeout=10, retries=2)
        if robots_status == 200:
            result["robots_txt"] = parse_robots_txt(robots_text)
        else:
            result["robots_txt"] = {"found": False}
    except RuntimeError:
        result["robots_txt"] = {"found": False}

    # 4. Check llms.txt
    print("[preflight] Checking llms.txt...", file=sys.stderr)
    result["llms_txt"] = check_llms_txt(base_url)

    # 5. Check sitemap
    print("[preflight] Checking sitemap.xml...", file=sys.stderr)
    result["sitemap"] = check_sitemap(base_url)

    # 6. Estimate pages
    result["estimated_pages"] = estimate_pages(html, base_url)
    print(f"[preflight] Estimated {result['estimated_pages']} internal pages from homepage links", file=sys.stderr)

    return result


def main():
    parser = argparse.ArgumentParser(description="SEO audit pre-flight checks")
    parser.add_argument("url", help="URL to check")
    args = parser.parse_args()

    result = run_preflight(args.url)
    print(json.dumps(result, indent=2))

    if not result["reachable"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
