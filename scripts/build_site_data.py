#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
build_site_data.py — Orchestrate all data collection scripts into site_data.json.

Single entry point for Phase 1A of the SEO audit. Runs preflight, crawl,
metadata extraction, schema validation, CWV measurement, sitemap validation,
security checks, and screenshot capture.

Usage:
    python scripts/build_site_data.py <url> <output_dir> [options]

Output:
    <output_dir>/site_data.json
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

PYTHON = sys.executable
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name, args, timeout=300):
    """Run a Python script and return parsed JSON output."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = [PYTHON, script_path] + args

    print(f"[build] Running {script_name}...", file=sys.stderr)
    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        elapsed = round(time.time() - start, 1)

        if result.returncode != 0 and not result.stdout.strip():
            print(f"[build] {script_name} failed ({elapsed}s): {result.stderr[:300]}", file=sys.stderr)
            return {"status": "error", "error": result.stderr[:500], "elapsed": elapsed}

        print(f"[build] {script_name} completed ({elapsed}s)", file=sys.stderr)

        # Parse JSON from stdout
        stdout = result.stdout.strip()
        if stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError as e:
                return {"status": "error", "error": f"Invalid JSON: {e}", "raw": stdout[:500]}

        return {"status": "error", "error": "No output", "elapsed": elapsed}

    except subprocess.TimeoutExpired:
        print(f"[build] {script_name} timed out after {timeout}s", file=sys.stderr)
        return {"status": "error", "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def build_site_data(url, output_dir, max_pages=500, skip_cwv=False, skip_screenshots=False, skip_external=False):
    """Orchestrate all data collection scripts."""
    os.makedirs(output_dir, exist_ok=True)
    crawl_dir = os.path.join(output_dir, "crawl")

    site_data = {
        "meta": {
            "tool_version": "2.0.0",
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "url": url,
            "domain": None,
        },
    }

    # Phase 0: Preflight (fail-fast)
    print("[build] === Phase 0: Preflight ===", file=sys.stderr)
    preflight = run_script("preflight.py", [url])
    site_data["preflight"] = preflight

    if not preflight.get("reachable"):
        print("[build] ABORT: Site unreachable", file=sys.stderr)
        site_data["meta"]["domain"] = preflight.get("domain", "unknown")
        site_data_path = os.path.join(output_dir, "site_data.json")
        with open(site_data_path, "w", encoding="utf-8") as f:
            json.dump(site_data, f, indent=2)
        print(f"[build] Partial site_data.json saved: {site_data_path}", file=sys.stderr)
        return site_data

    domain = preflight.get("domain", "unknown")
    cms = preflight.get("cms", "custom")
    site_data["meta"]["domain"] = domain

    # Phase 1: Crawl (sequential, must complete first)
    print("[build] === Phase 1: Crawl ===", file=sys.stderr)
    crawl_result = run_script("crawl_site.py", [
        url, crawl_dir, "--max-pages", str(max_pages),
    ], timeout=600)
    site_data["crawl"] = crawl_result

    # Load crawl manifest for downstream scripts
    manifest_path = os.path.join(crawl_dir, "crawl_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            site_data["crawl"] = json.load(f)

    # Phase 2: Sequential post-crawl (need crawled HTML)
    print("[build] === Phase 2: Post-crawl extraction ===", file=sys.stderr)
    site_data["pages_metadata"] = run_script("extract_metadata.py", [
        crawl_dir, "--cms", cms,
    ])
    site_data["schema"] = run_script("validate_schema.py", [crawl_dir])

    # Save partial site_data.json so NAP extraction can read pages_metadata
    partial_path = os.path.join(output_dir, "site_data.json")
    with open(partial_path, "w", encoding="utf-8") as f:
        json.dump(site_data, f, indent=2)

    # Phase 3: Parallel independent checks
    print("[build] === Phase 3: Parallel checks ===", file=sys.stderr)
    parallel_tasks = {}

    # Sitemap validation
    sitemap_url = None
    if preflight.get("sitemap", {}).get("found"):
        sitemap_url = preflight["sitemap"]["url"]
    elif preflight.get("robots_txt", {}).get("sitemaps"):
        sitemap_url = preflight["robots_txt"]["sitemaps"][0]
    else:
        # Default guess
        import urllib.parse
        sitemap_url = urllib.parse.urljoin(url, "/sitemap.xml")

    parallel_tasks["sitemap"] = ("validate_sitemap.py", [
        sitemap_url, "--crawl-manifest", manifest_path,
    ])

    parallel_tasks["security"] = ("check_security.py", [url])

    # NAP extraction (from crawled HTML + pages_metadata for social links)
    parallel_tasks["nap"] = ("extract_nap.py", [
        crawl_dir, "--site-data", partial_path,
    ])

    if not skip_cwv:
        # Measure CWV on homepage + a sample of pages
        cwv_urls = [url]
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            pages = [p for p in manifest.get("pages", []) if p.get("status") != "error"]
            # Add up to 4 more pages (service pages, about, etc.)
            for p in pages[1:5]:
                cwv_urls.append(p.get("final_url", p["url"]))
        parallel_tasks["cwv"] = ("measure_cwv.py", cwv_urls)

    if not skip_screenshots:
        screenshots_dir = os.path.join(output_dir, "screenshots")
        parallel_tasks["screenshots"] = ("capture_screenshots.py", [url, screenshots_dir])

    # Run parallel tasks
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for key, (script, args) in parallel_tasks.items():
            timeout = 180 if key == "cwv" else 120
            futures[executor.submit(run_script, script, args, timeout)] = key

        for future in as_completed(futures):
            key = futures[future]
            try:
                site_data[key] = future.result()
            except Exception as e:
                site_data[key] = {"status": "error", "error": str(e)}

    # Fill in skipped sections
    if skip_cwv and "cwv" not in site_data:
        site_data["cwv"] = {"status": "skipped"}
    if skip_screenshots and "screenshots" not in site_data:
        site_data["screenshots"] = {"status": "skipped"}

    # Phase 4: External verification (GBP + social profiles)
    # Requires NAP data from Phase 3 for business name and social URLs
    if not skip_external:
        print("[build] === Phase 4: External verification ===", file=sys.stderr)
        nap_data = site_data.get("nap", {})

        # GBP check — use business name + address from NAP extraction
        business_name = nap_data.get("business_name", "")
        primary_address = nap_data.get("nap_consistency", {}).get("primary_address", "")
        if business_name:
            # Build search query from business name + suburb
            parsed_addrs = nap_data.get("addresses_found", [])
            suburb = ""
            state = ""
            if parsed_addrs:
                suburb = parsed_addrs[0].get("parsed", {}).get("suburb", "")
                state = parsed_addrs[0].get("parsed", {}).get("state", "")
            gbp_query = f"{business_name} {suburb} {state}".strip()
            # Clean query — remove title tag noise like "Page Name |"
            if "|" in gbp_query:
                gbp_query = gbp_query.split("|")[-1].strip() + " " + suburb + " " + state
            site_data["gbp"] = run_script("check_gbp.py", [gbp_query], timeout=60)
        else:
            site_data["gbp"] = {"status": "skipped", "reason": "no business name found"}

        # Social media checks — use profile URLs from NAP extraction
        social_profiles = nap_data.get("social_profiles", {})
        social_args = []
        for platform in ("facebook", "instagram", "youtube", "linkedin"):
            urls = social_profiles.get(platform, [])
            if urls:
                social_args.extend([f"--{platform}", urls[0]])

        if social_args:
            site_data["social"] = run_script("check_social.py", social_args, timeout=120)
        else:
            site_data["social"] = {"status": "skipped", "reason": "no social profiles found on site"}
    else:
        site_data["gbp"] = {"status": "skipped"}
        site_data["social"] = {"status": "skipped"}

    # Save site_data.json
    site_data_path = os.path.join(output_dir, "site_data.json")
    with open(site_data_path, "w", encoding="utf-8") as f:
        json.dump(site_data, f, indent=2)

    print(f"\n[build] === Done ===", file=sys.stderr)
    print(f"[build] site_data.json: {site_data_path}", file=sys.stderr)
    sections = [k for k in site_data if k != "meta"]
    print(f"[build] Sections: {', '.join(sections)}", file=sys.stderr)

    return site_data


def main():
    parser = argparse.ArgumentParser(description="Build site_data.json for SEO audit")
    parser.add_argument("url", help="URL to audit")
    parser.add_argument("output_dir", help="Output directory for all data")
    parser.add_argument("--max-pages", type=int, default=500, help="Max pages to crawl (default: 500)")
    parser.add_argument("--skip-cwv", action="store_true", help="Skip CWV measurement")
    parser.add_argument("--skip-screenshots", action="store_true", help="Skip screenshot capture")
    parser.add_argument("--skip-external", action="store_true", help="Skip GBP and social profile checks")
    args = parser.parse_args()

    build_site_data(
        args.url,
        args.output_dir,
        max_pages=args.max_pages,
        skip_cwv=args.skip_cwv,
        skip_screenshots=args.skip_screenshots,
        skip_external=args.skip_external,
    )


if __name__ == "__main__":
    main()
