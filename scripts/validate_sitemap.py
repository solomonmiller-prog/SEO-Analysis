#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
validate_sitemap.py — Validate XML sitemap structure and content.

Usage:
    python scripts/validate_sitemap.py <sitemap_url> [--crawl-manifest <path>]

Output:
    JSON to stdout with validation results.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_page import fetch

NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SPOT_CHECK_LIMIT = 20


def fetch_sitemap(url):
    """Fetch and parse a sitemap XML."""
    try:
        content, final_url, status, _ = fetch(url, timeout=20, retries=2)
        if status != 200:
            return None, f"HTTP {status}"
        return content, None
    except RuntimeError as e:
        return None, str(e)


def parse_sitemap(xml_content, sitemap_url):
    """Parse a sitemap or sitemap index and return URLs."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        return {"error": f"Invalid XML: {e}", "urls": [], "is_index": False}

    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag

    if tag == "sitemapindex":
        # Sitemap index — collect child sitemap URLs
        sitemaps = []
        for sitemap in root.findall("sm:sitemap", NS):
            loc = sitemap.find("sm:loc", NS)
            lastmod = sitemap.find("sm:lastmod", NS)
            if loc is not None:
                sitemaps.append({
                    "loc": loc.text.strip(),
                    "lastmod": lastmod.text.strip() if lastmod is not None else None,
                })
        return {"is_index": True, "sitemaps": sitemaps, "urls": []}

    elif tag == "urlset":
        urls = []
        deprecated_tags = {"changefreq": 0, "priority": 0}
        lastmod_values = set()

        for url_elem in root.findall("sm:url", NS):
            loc = url_elem.find("sm:loc", NS)
            lastmod = url_elem.find("sm:lastmod", NS)
            changefreq = url_elem.find("sm:changefreq", NS)
            priority = url_elem.find("sm:priority", NS)

            entry = {}
            if loc is not None:
                entry["loc"] = loc.text.strip()
            if lastmod is not None:
                entry["lastmod"] = lastmod.text.strip()
                lastmod_values.add(lastmod.text.strip())
            if changefreq is not None:
                deprecated_tags["changefreq"] += 1
            if priority is not None:
                deprecated_tags["priority"] += 1

            urls.append(entry)

        return {
            "is_index": False,
            "urls": urls,
            "deprecated_tags": deprecated_tags,
            "identical_lastmod": len(lastmod_values) <= 1 and len(urls) > 1,
            "lastmod_values": list(lastmod_values)[:10],
        }

    return {"error": f"Unknown root element: {tag}", "urls": [], "is_index": False}


def spot_check_urls(urls, limit=SPOT_CHECK_LIMIT):
    """Spot-check a sample of URLs for HTTP status."""
    import random

    sample = urls[:limit] if len(urls) <= limit else random.sample(urls, limit)
    results = []

    for entry in sample:
        url = entry.get("loc", "")
        if not url:
            continue
        try:
            _, final_url, status, _ = fetch(url, timeout=10, retries=1)
            redirected = final_url != url
            results.append({
                "url": url,
                "status": status,
                "redirected": redirected,
                "final_url": final_url if redirected else None,
            })
        except RuntimeError as e:
            error_msg = str(e)
            status_match = re.search(r"HTTP (\d+)", error_msg)
            results.append({
                "url": url,
                "status": int(status_match.group(1)) if status_match else "error",
                "error": error_msg,
            })
        time.sleep(0.5)

    return results


def cross_reference_crawl(sitemap_urls, manifest_path):
    """Cross-reference sitemap URLs against crawl manifest."""
    if not manifest_path or not os.path.exists(manifest_path):
        return None

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    crawled_urls = set()
    crawl_status = {}
    for page in manifest.get("pages", []):
        url = page.get("url", "")
        final_url = page.get("final_url", url)
        crawled_urls.add(url)
        crawled_urls.add(final_url)
        crawl_status[url] = page.get("status", "unknown")

    sitemap_url_set = {u.get("loc", "").rstrip("/") for u in sitemap_urls}
    crawled_normalized = {u.rstrip("/") for u in crawled_urls}

    # In sitemap but not crawled
    in_sitemap_only = sitemap_url_set - crawled_normalized
    # Crawled but not in sitemap
    in_crawl_only = crawled_normalized - sitemap_url_set

    # Non-200 URLs in sitemap (from crawl data)
    non_200_in_sitemap = []
    for url in sitemap_url_set:
        for crawl_url, status in crawl_status.items():
            if crawl_url.rstrip("/") == url and status != 200 and status != "error":
                non_200_in_sitemap.append({"url": url, "status": status})

    return {
        "in_sitemap_only": list(in_sitemap_only)[:50],
        "in_sitemap_only_count": len(in_sitemap_only),
        "in_crawl_only": list(in_crawl_only)[:50],
        "in_crawl_only_count": len(in_crawl_only),
        "non_200_in_sitemap": non_200_in_sitemap,
    }


def check_location_pages(urls):
    """Check for location page patterns and apply quality gates."""
    location_patterns = [
        r"/locations?/",
        r"/service-areas?/",
        r"/cities/",
        r"/suburbs?/",
        r"/areas?/",
        r"-(suburb|city|area|location)-",
    ]

    location_urls = []
    for entry in urls:
        url = entry.get("loc", "")
        path = urllib.parse.urlparse(url).path.lower()
        for pattern in location_patterns:
            if re.search(pattern, path):
                location_urls.append(url)
                break

    count = len(location_urls)
    result = {
        "location_pages_count": count,
        "location_urls_sample": location_urls[:10],
    }

    if count >= 50:
        result["quality_gate"] = "HARD_STOP"
        result["message"] = f"{count} location pages detected. Requires explicit justification — high risk of doorway page penalty."
    elif count >= 30:
        result["quality_gate"] = "WARNING"
        result["message"] = f"{count} location pages detected. Require 60%+ unique content per page to avoid thin content penalty."
    else:
        result["quality_gate"] = "PASS"

    return result


def validate(sitemap_url, crawl_manifest=None):
    """Run full sitemap validation."""
    result = {
        "sitemap_url": sitemap_url,
        "fetchable": False,
        "valid_xml": False,
        "is_index": False,
        "total_urls": 0,
        "issues": [],
    }

    # 1. Fetch sitemap
    print(f"[sitemap] Fetching {sitemap_url}...", file=sys.stderr)
    content, error = fetch_sitemap(sitemap_url)
    if error:
        result["error"] = error
        return result
    result["fetchable"] = True

    # 2. Parse
    parsed = parse_sitemap(content, sitemap_url)
    if "error" in parsed:
        result["error"] = parsed["error"]
        return result
    result["valid_xml"] = True
    result["is_index"] = parsed["is_index"]

    if parsed["is_index"]:
        # Process sitemap index
        result["child_sitemaps"] = parsed["sitemaps"]
        all_urls = []

        for i, sm in enumerate(parsed["sitemaps"]):
            print(f"[sitemap] Fetching child sitemap {i + 1}/{len(parsed['sitemaps'])}...", file=sys.stderr)
            child_content, child_error = fetch_sitemap(sm["loc"])
            if child_error:
                result["issues"].append({"type": "child_fetch_error", "sitemap": sm["loc"], "error": child_error})
                continue
            child_parsed = parse_sitemap(child_content, sm["loc"])
            if "error" in child_parsed:
                result["issues"].append({"type": "child_parse_error", "sitemap": sm["loc"], "error": child_parsed["error"]})
                continue
            all_urls.extend(child_parsed.get("urls", []))

            # Collect deprecated tag info
            if child_parsed.get("deprecated_tags"):
                for tag, count in child_parsed["deprecated_tags"].items():
                    if count > 0:
                        result["issues"].append({
                            "type": "deprecated_tag",
                            "tag": tag,
                            "count": count,
                            "sitemap": sm["loc"],
                        })
            if child_parsed.get("identical_lastmod"):
                result["issues"].append({
                    "type": "identical_lastmod",
                    "sitemap": sm["loc"],
                })

        parsed["urls"] = all_urls
    else:
        # Single sitemap
        if parsed.get("deprecated_tags"):
            for tag, count in parsed["deprecated_tags"].items():
                if count > 0:
                    result["issues"].append({"type": "deprecated_tag", "tag": tag, "count": count})
        if parsed.get("identical_lastmod"):
            result["issues"].append({"type": "identical_lastmod"})

    urls = parsed.get("urls", [])
    result["total_urls"] = len(urls)

    # 3. Check 50k limit
    if len(urls) > 50000:
        result["issues"].append({
            "type": "exceeds_limit",
            "count": len(urls),
            "limit": 50000,
        })

    # 4. Spot-check URLs
    if urls:
        print(f"[sitemap] Spot-checking up to {SPOT_CHECK_LIMIT} URLs...", file=sys.stderr)
        result["spot_check"] = spot_check_urls(urls)

    # 5. Cross-reference with crawl
    if crawl_manifest:
        print("[sitemap] Cross-referencing with crawl manifest...", file=sys.stderr)
        result["cross_reference"] = cross_reference_crawl(urls, crawl_manifest)

    # 6. Location page quality gates
    result["location_pages"] = check_location_pages(urls)

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate XML sitemap")
    parser.add_argument("sitemap_url", help="URL of sitemap.xml")
    parser.add_argument("--crawl-manifest", help="Path to crawl_manifest.json for cross-reference")
    args = parser.parse_args()

    result = validate(args.sitemap_url, args.crawl_manifest)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
