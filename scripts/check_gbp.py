#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
check_gbp.py — Extract Google Business Profile data using Playwright.

Google Maps is fully JS-rendered, so we use a headless browser to load the
listing and extract review count, rating, business details, and individual
reviews.

Usage:
    python scripts/check_gbp.py "<business name>" "<suburb, state>"
    python scripts/check_gbp.py --cid <cid_number>
    python scripts/check_gbp.py --url "<google maps url>"

Output:
    JSON to stdout with GBP data.
"""

import argparse
import json
import re
import sys
import time


def check_playwright():
    """Check if playwright is available."""
    try:
        from playwright.sync_api import sync_playwright
        return True
    except ImportError:
        print("ERROR: playwright not installed. Run: pip install playwright && playwright install chromium", file=sys.stderr)
        return False


def extract_gbp_data(page):
    """Extract GBP data from a loaded Google Maps page."""
    result = {
        "business_name": None,
        "address": None,
        "phone": None,
        "website": None,
        "category": None,
        "rating": None,
        "review_count": 0,
        "hours": None,
        "photos_count": None,
        "reviews": [],
    }

    # Wait for the main content to load
    try:
        page.wait_for_selector('[data-attrid="title"], h1.DUwDvf, div.tAiQdd', timeout=10000)
    except Exception:
        pass  # May not always match, continue anyway

    # Give extra time for dynamic content
    time.sleep(3)

    # Business name
    for selector in ['h1.DUwDvf', 'div.tAiQdd h1', '[data-attrid="title"]', 'h1']:
        try:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                if text and len(text) < 200:
                    result["business_name"] = text
                    break
        except Exception:
            continue

    # Rating and review count from the main panel
    # Google Maps shows rating like "4.5" and reviews like "(123)"
    try:
        # Try the rating span
        for selector in ['div.F7nice span[aria-hidden="true"]', 'span.ceNzKf', 'div.F7nice span']:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                try:
                    result["rating"] = float(text)
                    break
                except ValueError:
                    continue
    except Exception:
        pass

    # Review count extraction — scoped to the business side panel only.
    # IMPORTANT: Google Maps shows nearby businesses on the map with their own
    # aria-labels (e.g. "5.0 stars 16 Reviews" for a gym next door). We must
    # restrict selectors to the place info panel, not the map area.
    #
    # The side panel is typically inside div[role="main"] > div (first child).
    # We use panel-scoped selectors to avoid picking up map marker labels.
    PANEL_SCOPE = 'div[role="main"]'

    try:
        # Method 1: aria-label on the reviews button/link in the panel
        for selector in [
            f'{PANEL_SCOPE} button[aria-label*="review" i]',
            f'{PANEL_SCOPE} a[aria-label*="review" i]',
        ]:
            el = page.query_selector(selector)
            if el:
                label = el.get_attribute('aria-label') or ''
                # Only accept if it also mentions stars (confirms it's a rating summary)
                review_match = re.search(r'([\d,]+)\s*review', label, re.IGNORECASE)
                star_match = re.search(r'([\d.]+)\s*star', label, re.IGNORECASE)
                if review_match and star_match:
                    api_rating = float(star_match.group(1))
                    # Cross-check: if we already have a rating from DOM, only accept
                    # if the aria-label rating matches (avoids nearby business data)
                    if result["rating"] is None or abs(api_rating - result["rating"]) < 0.2:
                        result["review_count"] = int(review_match.group(1).replace(',', ''))
                        if result["rating"] is None:
                            result["rating"] = api_rating
                        print(f"[check_gbp] Reviews from panel aria-label: {label}", file=sys.stderr)
                        break
                    else:
                        print(f"[check_gbp] Skipping mismatched aria-label: {label} (DOM rating={result['rating']})", file=sys.stderr)
    except Exception:
        pass

    # Method 2: text-based extraction from known panel elements
    if result["review_count"] == 0:
        try:
            for selector in [
                f'{PANEL_SCOPE} div.F7nice span:last-child',
                f'{PANEL_SCOPE} span.RDApEe',
                f'{PANEL_SCOPE} button[jsaction*="review"] span',
            ]:
                el = page.query_selector(selector)
                if el:
                    text = el.inner_text().strip()
                    # Match "(104)" or "104 reviews" but NOT single digits (rating fragments)
                    match = re.search(r'\((\d[\d,]*)\)', text)
                    if not match:
                        match = re.search(r'(\d[\d,]+)\s*review', text, re.IGNORECASE)
                    if not match and len(text) > 1:
                        match = re.search(r'(\d{2,}[\d,]*)', text)
                    if match:
                        result["review_count"] = int(match.group(1).replace(',', ''))
                        print(f"[check_gbp] Reviews from panel text: '{text}'", file=sys.stderr)
                        break
        except Exception:
            pass

    # Method 3: panel-scoped aria-label scan (broader)
    if result["rating"] is None or result["review_count"] == 0:
        try:
            elements = page.query_selector_all(f'{PANEL_SCOPE} [aria-label*="star"], {PANEL_SCOPE} [aria-label*="review"]')
            for el in elements:
                label = el.get_attribute('aria-label') or ''
                star_match = re.search(r'([\d.]+)\s*star', label, re.IGNORECASE)
                review_match = re.search(r'([\d,]+)\s*review', label, re.IGNORECASE)
                if star_match and review_match:
                    api_rating = float(star_match.group(1))
                    if result["rating"] is None or abs(api_rating - result["rating"]) < 0.2:
                        if result["rating"] is None:
                            result["rating"] = api_rating
                        if review_match and result["review_count"] == 0:
                            result["review_count"] = int(review_match.group(1).replace(',', ''))
                elif star_match and result["rating"] is None:
                    result["rating"] = float(star_match.group(1))
        except Exception:
            pass

    # Address
    try:
        for selector in ['button[data-item-id="address"] div.fontBodyMedium',
                         'button[data-tooltip="Copy address"] div',
                         '[data-item-id="address"]']:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                if text and len(text) > 5:
                    result["address"] = text
                    break
    except Exception:
        pass

    # Phone
    try:
        for selector in ['button[data-item-id*="phone"] div.fontBodyMedium',
                         'button[data-tooltip="Copy phone number"] div',
                         '[data-item-id*="phone"]']:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                if text:
                    result["phone"] = text
                    break
    except Exception:
        pass

    # Website
    try:
        for selector in ['a[data-item-id="authority"]',
                         'a[data-tooltip="Open website"]',
                         '[data-item-id="authority"] a']:
            el = page.query_selector(selector)
            if el:
                href = el.get_attribute('href') or ''
                if href:
                    result["website"] = href
                    break
    except Exception:
        pass

    # Category
    try:
        for selector in ['button[jsaction*="category"] span',
                         'span.DkEaL',
                         '.fontBodyMedium span[jstcache]']:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                if text and len(text) < 100 and not text.startswith('http'):
                    result["category"] = text
                    break
    except Exception:
        pass

    # Hours
    try:
        hours_el = page.query_selector('[aria-label*="hour" i], [data-item-id*="hour"]')
        if hours_el:
            label = hours_el.get_attribute('aria-label') or hours_el.inner_text()
            result["hours"] = label.strip()[:500]
    except Exception:
        pass

    # Try to extract individual reviews
    try:
        # Click on the reviews tab/section if available
        reviews_tab = page.query_selector('button[aria-label*="Reviews"], button[data-tab-id="reviews"]')
        if reviews_tab:
            reviews_tab.click()
            time.sleep(3)

        # Extract individual reviews
        review_elements = page.query_selector_all('div[data-review-id], div.jftiEf')
        for rev_el in review_elements[:20]:  # Cap at 20
            review = {}
            try:
                # Reviewer name
                name_el = rev_el.query_selector('div.d4r55, button.WEBjve div')
                if name_el:
                    review["name"] = name_el.inner_text().strip()

                # Star rating
                star_el = rev_el.query_selector('span[role="img"], span.kvMYJc')
                if star_el:
                    label = star_el.get_attribute('aria-label') or ''
                    star_match = re.search(r'(\d)', label)
                    if star_match:
                        review["rating"] = int(star_match.group(1))

                # Review text
                text_el = rev_el.query_selector('span.wiI7pd, div.MyEned span')
                if text_el:
                    review["text"] = text_el.inner_text().strip()

                # Date
                date_el = rev_el.query_selector('span.rsqaWe, span.dehysf')
                if date_el:
                    review["date"] = date_el.inner_text().strip()

                if review.get("name") or review.get("text"):
                    result["reviews"].append(review)
            except Exception:
                continue
    except Exception:
        pass

    # Fallback: try to get review data from the page's full text
    if result["rating"] is None and result["review_count"] == 0:
        try:
            full_text = page.inner_text('body')
            # Look for rating patterns
            rating_match = re.search(r'(\d\.\d)\s*(?:\(\d)', full_text)
            if rating_match:
                result["rating"] = float(rating_match.group(1))
            count_match = re.search(r'\((\d[\d,]*)\s*(?:review|Google)', full_text, re.IGNORECASE)
            if count_match:
                result["review_count"] = int(count_match.group(1).replace(',', ''))
        except Exception:
            pass

    return result


def extract_from_preview_api(data):
    """Extract rating and review count from /maps/preview/place API response.

    Google Maps loads business data via an internal API that returns a deeply
    nested JSON array. The rating and review count are at known positions.
    This is more reliable than DOM scraping since Google frequently changes
    CSS classes but rarely changes the API format.
    """
    import json as _json

    # Strip Google's XSSI prefix: )]}'\n
    for prefix in [")]}'\\n", ")]}'", ")]}'\n"]:
        if data.startswith(prefix):
            data = data[len(prefix):]
            break

    try:
        parsed = _json.loads(data)
    except _json.JSONDecodeError:
        return None, None

    rating = None
    review_count = None

    # Walk the parsed data to find floats that look like ratings (1.0-5.0)
    # and integers nearby that could be review counts
    def search(obj, path=""):
        nonlocal rating, review_count
        if isinstance(obj, list):
            for i, item in enumerate(obj):
                search(item, f"{path}[{i}]")
                # When we find the rating, look for review count in adjacent indices
                if isinstance(item, float) and 1.0 <= item <= 5.0 and rating is None:
                    # Check if next element is an integer (review count)
                    if i + 1 < len(obj) and isinstance(obj[i + 1], int) and obj[i + 1] > 0:
                        rating = item
                        review_count = obj[i + 1]
                        return

    search(parsed)
    return rating, review_count


def run_gbp_check(search_query=None, cid=None, url=None):
    """Run GBP check using Playwright."""
    from playwright.sync_api import sync_playwright

    if url:
        target_url = url
    elif cid:
        target_url = f"https://www.google.com/maps?cid={cid}"
    else:
        target_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

    print(f"[check_gbp] Loading: {target_url}", file=sys.stderr)

    # Capture API responses for more reliable data extraction
    preview_responses = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        def capture_preview(response):
            if "/maps/preview/place" in response.url:
                try:
                    preview_responses.append(response.text())
                except Exception:
                    pass

        page.on("response", capture_preview)

        try:
            # Navigate and handle consent dialogs
            page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # Dismiss Google consent/cookie banners if present
            for consent_selector in [
                'button[aria-label*="Accept"]',
                'button:has-text("Accept all")',
                'form[action*="consent"] button',
                'button:has-text("Reject all")',
            ]:
                try:
                    btn = page.query_selector(consent_selector)
                    if btn and btn.is_visible():
                        btn.click()
                        time.sleep(1)
                        break
                except Exception:
                    continue

            # Wait for maps content
            time.sleep(3)

            # Take a debug screenshot
            page.screenshot(path="/tmp/gbp_debug.png")
            print("[check_gbp] Debug screenshot saved to /tmp/gbp_debug.png", file=sys.stderr)

            # Extract data from DOM
            result = extract_gbp_data(page)

            # Enrich with API response data (more reliable for rating/review count)
            for resp_body in preview_responses:
                api_rating, api_review_count = extract_from_preview_api(resp_body)
                if api_rating is not None:
                    if result["rating"] is None or result["rating"] != api_rating:
                        print(f"[check_gbp] API rating: {api_rating} (DOM: {result['rating']})", file=sys.stderr)
                    result["rating"] = api_rating
                if api_review_count is not None and api_review_count > result["review_count"]:
                    print(f"[check_gbp] API review_count: {api_review_count} (DOM: {result['review_count']})", file=sys.stderr)
                    result["review_count"] = api_review_count

            result["source_url"] = page.url
            result["search_query"] = search_query
            result["cid"] = cid

            # Also grab the page title as fallback context
            result["page_title"] = page.title()

        except Exception as e:
            result = {"error": str(e), "source_url": target_url}
        finally:
            browser.close()

    return result


def main():
    parser = argparse.ArgumentParser(description="Extract Google Business Profile data via Playwright")
    parser.add_argument("query", nargs="*", help="Search query (e.g. 'Holland Plastics Molendinar QLD')")
    parser.add_argument("--cid", help="Google Maps CID number")
    parser.add_argument("--url", help="Direct Google Maps URL")
    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    search_query = " ".join(args.query) if args.query else None

    if not search_query and not args.cid and not args.url:
        print("ERROR: Provide a search query, --cid, or --url", file=sys.stderr)
        sys.exit(1)

    result = run_gbp_check(search_query=search_query, cid=args.cid, url=args.url)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
