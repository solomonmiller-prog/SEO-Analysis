#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
capture_screenshots.py — Capture screenshots at multiple viewports using Playwright.

Usage:
    python scripts/capture_screenshots.py <url> <output_dir>

Output:
    PNGs saved to output_dir, JSON summary to stdout.
"""

import argparse
import json
import os
import sys

VIEWPORTS = [
    {"name": "desktop", "width": 1920, "height": 1080},
    {"name": "laptop", "width": 1366, "height": 768},
    {"name": "tablet", "width": 768, "height": 1024},
    {"name": "mobile", "width": 375, "height": 812},
]


def check_playwright():
    """Check if Playwright is installed."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        return False


def capture(url, output_dir):
    """Capture screenshots at all viewports."""
    from playwright.sync_api import sync_playwright

    os.makedirs(output_dir, exist_ok=True)
    results = {"url": url, "output_dir": output_dir, "viewports": []}

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            return {
                "url": url,
                "status": "error",
                "error": f"Failed to launch browser: {e}. Try: playwright install chromium",
            }

        for vp in VIEWPORTS:
            vp_result = {"name": vp["name"], "width": vp["width"], "height": vp["height"]}

            try:
                page = browser.new_page(viewport={"width": vp["width"], "height": vp["height"]})
                page.goto(url, wait_until="networkidle", timeout=30000)

                # Above-fold screenshot
                above_fold_path = os.path.join(output_dir, f"{vp['name']}_above_fold.png")
                page.screenshot(path=above_fold_path, full_page=False)
                vp_result["above_fold"] = above_fold_path

                # Full-page screenshot
                full_path = os.path.join(output_dir, f"{vp['name']}_full.png")
                page.screenshot(path=full_path, full_page=True)
                vp_result["full_page"] = full_path

                # Accessibility tree snapshot
                try:
                    a11y_snapshot = page.accessibility.snapshot()
                    vp_result["accessibility_snapshot"] = a11y_snapshot
                except Exception:
                    vp_result["accessibility_snapshot"] = None

                vp_result["status"] = "success"
                page.close()

            except Exception as e:
                vp_result["status"] = "error"
                vp_result["error"] = str(e)

            results["viewports"].append(vp_result)
            print(f"[screenshots] {vp['name']} ({vp['width']}x{vp['height']}): {vp_result['status']}", file=sys.stderr)

        browser.close()

    results["status"] = "success"
    return results


def main():
    parser = argparse.ArgumentParser(description="Capture screenshots at multiple viewports")
    parser.add_argument("url", help="URL to capture")
    parser.add_argument("output_dir", help="Directory to save screenshots")
    args = parser.parse_args()

    if not check_playwright():
        print("ERROR: Playwright is not installed.", file=sys.stderr)
        print("Install with: pip install playwright && playwright install chromium", file=sys.stderr)
        print(json.dumps({
            "status": "error",
            "error": "Playwright not installed. Install with: pip install playwright && playwright install chromium",
        }))
        sys.exit(1)

    result = capture(args.url, args.output_dir)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
