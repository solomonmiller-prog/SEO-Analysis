#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
measure_cwv.py — Measure Core Web Vitals using Lighthouse CLI.

Usage:
    python scripts/measure_cwv.py <url> [url2 ...]

Output:
    JSON to stdout with CWV measurements per URL.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

# CWV thresholds (2026)
THRESHOLDS = {
    "LCP": {"good": 2.5, "needs_improvement": 4.0, "unit": "s"},
    "INP": {"good": 200, "needs_improvement": 500, "unit": "ms"},
    "CLS": {"good": 0.1, "needs_improvement": 0.25, "unit": ""},
    "FCP": {"good": 1.8, "needs_improvement": 3.0, "unit": "s"},
    "TTFB": {"good": 0.8, "needs_improvement": 1.8, "unit": "s"},
    "SpeedIndex": {"good": 3.4, "needs_improvement": 5.8, "unit": "s"},
}

EDGE_PATHS = [
    "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "/c/Program Files/Microsoft/Edge/Application/msedge.exe",
    "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
]

CHROME_PATHS = [
    "/c/Program Files/Google/Chrome/Application/chrome.exe",
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
]


def classify_metric(name, value):
    """Classify a metric value as good/needs-improvement/poor."""
    if name not in THRESHOLDS:
        return "unknown"
    t = THRESHOLDS[name]
    if value <= t["good"]:
        return "good"
    elif value <= t["needs_improvement"]:
        return "needs_improvement"
    return "poor"


def find_lighthouse():
    """Find the lighthouse CLI."""
    # Check if lighthouse is available
    lh = shutil.which("lighthouse")
    if lh:
        return lh

    # Check npx
    npx = shutil.which("npx")
    if npx:
        return "npx lighthouse"

    return None


def find_chrome():
    """Find Chrome or Edge executable."""
    # Check Chrome first
    chrome = shutil.which("chrome") or shutil.which("google-chrome")
    if chrome:
        return chrome

    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path

    # Fall back to Edge
    for path in EDGE_PATHS:
        if os.path.exists(path):
            return path

    return None


def run_lighthouse(url, lighthouse_cmd, chrome_path=None):
    """Run Lighthouse for a single URL and return parsed results."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        output_path = f.name

    try:
        cmd_parts = lighthouse_cmd.split()
        cmd = cmd_parts + [
            url,
            f"--output-path={output_path}",
            "--output=json",
            '--chrome-flags="--headless --no-sandbox --disable-gpu"',
            "--only-categories=performance",
            "--quiet",
        ]

        if chrome_path:
            cmd.append(f"--chrome-path={chrome_path}")

        print(f"[cwv] Running Lighthouse for {url}...", file=sys.stderr)

        result = subprocess.run(
            " ".join(cmd),
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {
                "url": url,
                "status": "error",
                "error": f"Lighthouse produced no output. stderr: {result.stderr[:500]}",
            }

        with open(output_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        return parse_lighthouse_report(url, report)

    except subprocess.TimeoutExpired:
        return {"url": url, "status": "error", "error": "Lighthouse timed out after 120s"}
    except json.JSONDecodeError as e:
        return {"url": url, "status": "error", "error": f"Invalid Lighthouse JSON: {e}"}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def parse_lighthouse_report(url, report):
    """Parse Lighthouse JSON report and extract CWV metrics."""
    try:
        categories = report.get("categories", {})
        audits = report.get("audits", {})

        performance_score = None
        perf = categories.get("performance", {})
        if perf and perf.get("score") is not None:
            performance_score = round(perf["score"] * 100)

        metrics = {}

        # LCP
        lcp_audit = audits.get("largest-contentful-paint", {})
        if lcp_audit.get("numericValue") is not None:
            value = lcp_audit["numericValue"] / 1000  # ms to seconds
            metrics["LCP"] = {
                "value": round(value, 2),
                "unit": "s",
                "rating": classify_metric("LCP", value),
            }

        # CLS
        cls_audit = audits.get("cumulative-layout-shift", {})
        if cls_audit.get("numericValue") is not None:
            value = cls_audit["numericValue"]
            metrics["CLS"] = {
                "value": round(value, 3),
                "unit": "",
                "rating": classify_metric("CLS", value),
            }

        # FCP
        fcp_audit = audits.get("first-contentful-paint", {})
        if fcp_audit.get("numericValue") is not None:
            value = fcp_audit["numericValue"] / 1000
            metrics["FCP"] = {
                "value": round(value, 2),
                "unit": "s",
                "rating": classify_metric("FCP", value),
            }

        # TTFB (server-response-time)
        ttfb_audit = audits.get("server-response-time", {})
        if ttfb_audit.get("numericValue") is not None:
            value = ttfb_audit["numericValue"] / 1000
            metrics["TTFB"] = {
                "value": round(value, 2),
                "unit": "s",
                "rating": classify_metric("TTFB", value),
            }

        # Speed Index
        si_audit = audits.get("speed-index", {})
        if si_audit.get("numericValue") is not None:
            value = si_audit["numericValue"] / 1000
            metrics["SpeedIndex"] = {
                "value": round(value, 2),
                "unit": "s",
                "rating": classify_metric("SpeedIndex", value),
            }

        # INP — Lighthouse lab doesn't directly measure INP (it's a field metric),
        # but Total Blocking Time is the lab proxy
        tbt_audit = audits.get("total-blocking-time", {})
        if tbt_audit.get("numericValue") is not None:
            metrics["TBT"] = {
                "value": round(tbt_audit["numericValue"]),
                "unit": "ms",
                "note": "Lab proxy for INP — TBT > 200ms suggests poor INP",
                "rating": "good" if tbt_audit["numericValue"] <= 200 else ("needs_improvement" if tbt_audit["numericValue"] <= 600 else "poor"),
            }

        return {
            "url": url,
            "status": "success",
            "performance_score": performance_score,
            "metrics": metrics,
        }

    except Exception as e:
        return {"url": url, "status": "error", "error": f"Parse error: {e}"}


def check_playwright():
    """Check if Playwright is available as fallback."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def run_playwright_perf(url):
    """Fallback: measure performance timing via Playwright when Lighthouse is unavailable."""
    from playwright.sync_api import sync_playwright

    print(f"[cwv] Running Playwright perf measurement for {url}...", file=sys.stderr)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(url, wait_until="networkidle", timeout=30000)

            # Extract Navigation Timing API data
            timing = page.evaluate("""() => {
                const nav = performance.getEntriesByType('navigation')[0];
                const paint = performance.getEntriesByType('paint');
                const fcp = paint.find(e => e.name === 'first-contentful-paint');
                const lcp = new Promise(resolve => {
                    new PerformanceObserver(list => {
                        const entries = list.getEntries();
                        resolve(entries[entries.length - 1]?.startTime || null);
                    }).observe({type: 'largest-contentful-paint', buffered: true});
                    setTimeout(() => resolve(null), 3000);
                });
                return {
                    ttfb: nav ? nav.responseStart - nav.requestStart : null,
                    fcp: fcp ? fcp.startTime : null,
                    domContentLoaded: nav ? nav.domContentLoadedEventEnd - nav.startTime : null,
                    loadComplete: nav ? nav.loadEventEnd - nav.startTime : null,
                    transferSize: nav ? nav.transferSize : null,
                    encodedBodySize: nav ? nav.encodedBodySize : null,
                    decodedBodySize: nav ? nav.decodedBodySize : null,
                };
            }""")

            # Try to get LCP with a short wait
            import time
            time.sleep(2)
            lcp_value = page.evaluate("""() => {
                return new Promise(resolve => {
                    let lcp = null;
                    try {
                        new PerformanceObserver(list => {
                            const entries = list.getEntries();
                            if (entries.length > 0) lcp = entries[entries.length - 1].startTime;
                        }).observe({type: 'largest-contentful-paint', buffered: true});
                    } catch(e) {}
                    setTimeout(() => resolve(lcp), 1000);
                });
            }""")

            # Get CLS
            cls_value = page.evaluate("""() => {
                return new Promise(resolve => {
                    let cls = 0;
                    try {
                        new PerformanceObserver(list => {
                            for (const entry of list.getEntries()) {
                                if (!entry.hadRecentInput) cls += entry.value;
                            }
                        }).observe({type: 'layout-shift', buffered: true});
                    } catch(e) {}
                    setTimeout(() => resolve(cls), 500);
                });
            }""")

            # Get DOM stats
            dom_stats = page.evaluate("""() => {
                return {
                    domElements: document.querySelectorAll('*').length,
                    scripts: document.querySelectorAll('script[src]').length,
                    stylesheets: document.querySelectorAll('link[rel=stylesheet]').length,
                    images: document.querySelectorAll('img').length,
                };
            }""")

            browser.close()

            metrics = {}

            if timing.get("ttfb") is not None:
                value = timing["ttfb"] / 1000
                metrics["TTFB"] = {
                    "value": round(value, 2),
                    "unit": "s",
                    "rating": classify_metric("TTFB", value),
                }

            if timing.get("fcp") is not None:
                value = timing["fcp"] / 1000
                metrics["FCP"] = {
                    "value": round(value, 2),
                    "unit": "s",
                    "rating": classify_metric("FCP", value),
                }

            if lcp_value is not None:
                value = lcp_value / 1000
                metrics["LCP"] = {
                    "value": round(value, 2),
                    "unit": "s",
                    "rating": classify_metric("LCP", value),
                }

            if cls_value is not None:
                metrics["CLS"] = {
                    "value": round(cls_value, 3),
                    "unit": "",
                    "rating": classify_metric("CLS", cls_value),
                }

            if timing.get("domContentLoaded") is not None:
                metrics["DOMContentLoaded"] = {
                    "value": round(timing["domContentLoaded"] / 1000, 2),
                    "unit": "s",
                }

            if timing.get("loadComplete") is not None:
                metrics["LoadComplete"] = {
                    "value": round(timing["loadComplete"] / 1000, 2),
                    "unit": "s",
                }

            return {
                "url": url,
                "status": "success",
                "method": "playwright",
                "note": "Playwright Navigation Timing fallback — less accurate than Lighthouse lab data",
                "performance_score": None,
                "metrics": metrics,
                "dom_stats": dom_stats,
                "transfer_size_bytes": timing.get("transferSize"),
            }

    except Exception as e:
        return {"url": url, "status": "error", "method": "playwright", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Measure Core Web Vitals via Lighthouse")
    parser.add_argument("urls", nargs="+", help="URLs to measure")
    args = parser.parse_args()

    # Check prerequisites — try Lighthouse first, fall back to Playwright
    lighthouse_cmd = find_lighthouse()
    use_playwright = False

    if not lighthouse_cmd:
        if check_playwright():
            print("[cwv] Lighthouse not found, falling back to Playwright perf timing", file=sys.stderr)
            use_playwright = True
        else:
            print("ERROR: Neither Lighthouse nor Playwright available.", file=sys.stderr)
            print("Install Lighthouse: npm install -g lighthouse", file=sys.stderr)
            print("Or install Playwright: pip install playwright && playwright install chromium", file=sys.stderr)
            print(json.dumps({
                "status": "error",
                "error": "Neither Lighthouse nor Playwright available",
            }))
            sys.exit(1)

    chrome_path = None
    if not use_playwright:
        chrome_path = find_chrome()
        if not chrome_path:
            print("WARNING: Chrome/Edge not found. Lighthouse may fail.", file=sys.stderr)
        print(f"[cwv] Lighthouse: {lighthouse_cmd}", file=sys.stderr)
        if chrome_path:
            print(f"[cwv] Chrome/Edge: {chrome_path}", file=sys.stderr)

    results = []
    for url in args.urls:
        if use_playwright:
            result = run_playwright_perf(url)
        else:
            result = run_lighthouse(url, lighthouse_cmd, chrome_path)
        results.append(result)
        score = result.get('performance_score', 'N/A')
        method = result.get('method', 'lighthouse')
        print(f"[cwv] {url}: score={score} ({method})", file=sys.stderr)

    output = {
        "method": "playwright" if use_playwright else "lighthouse",
        "lighthouse_cmd": lighthouse_cmd,
        "chrome_path": chrome_path,
        "results": results,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
