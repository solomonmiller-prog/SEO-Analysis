#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
check_social.py — Extract public data from social media profiles using Playwright.

Visits Facebook, Instagram, YouTube, and LinkedIn pages to scrape publicly
visible profile data. Handles login walls gracefully by falling back to
meta tags (og:title, og:description) when the full page is blocked.

Usage:
    python scripts/check_social.py --facebook "https://facebook.com/..." --instagram "https://instagram.com/..."
    python scripts/check_social.py --youtube "https://youtube.com/..." --linkedin "https://linkedin.com/company/..."
    echo '{"facebook": "url", "instagram": "url"}' | python scripts/check_social.py --json -

Output:
    JSON to stdout with per-platform profile data.
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


def get_meta(page, property_name):
    """Extract a meta tag value by property or name attribute."""
    for attr in ["property", "name"]:
        try:
            el = page.query_selector(f'meta[{attr}="{property_name}"]')
            if el:
                val = el.get_attribute("content")
                if val and val.strip():
                    return val.strip()
        except Exception:
            continue
    return None


def parse_count(text):
    """Parse a human-readable count string into an integer.

    Handles formats like '1,234', '12.5K', '1.2M', '3B', plain '456'.
    Returns None if parsing fails.
    """
    if not text:
        return None
    text = text.strip().replace(",", "")
    # Handle K/M/B suffixes
    m = re.match(r'^([\d.]+)\s*([KkMmBb])?$', text)
    if not m:
        return None
    num = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    if suffix in multipliers:
        num *= multipliers[suffix]
    return int(num)


def extract_facebook(page):
    """Extract data from a Facebook page."""
    result = {
        "name": None,
        "category": None,
        "followers": None,
        "likes": None,
        "address": None,
        "phone": None,
        "last_post": None,
        "rating": None,
        "review_count": None,
        "status": "active",
    }

    # Check for not-found / unavailable page
    title = page.title() or ""
    if "page not found" in title.lower() or "content isn" in title.lower():
        result["status"] = "not_found"
        return result

    # --- Meta tag fallbacks (always available, even behind login walls) ---
    og_title = get_meta(page, "og:title")
    og_desc = get_meta(page, "og:description")

    if og_title:
        result["name"] = og_title

    # --- DOM extraction within [role="main"] ---
    main = page.query_selector('[role="main"]')
    scope = main if main else page

    # Page name from h1 or large heading
    if not result["name"]:
        for sel in ["h1", "h2"]:
            try:
                el = scope.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text and len(text) < 200:
                        result["name"] = text
                        break
            except Exception:
                continue

    # Category — often shown under the page name
    try:
        # Facebook puts category in a link or span near the top
        for sel in ['a[href*="/pages/category/"]', 'div[data-pagelet="ProfileTilesFeed"] span',
                    'span:has-text("Restaurant")', 'span:has-text("Service")']:
            el = scope.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if text and len(text) < 100:
                    result["category"] = text
                    break
    except Exception:
        pass

    # Followers / likes from the page body text
    try:
        body_text = scope.inner_text()

        # Followers: "1,234 followers" or "12K followers"
        followers_match = re.search(r'([\d,.]+[KkMmBb]?)\s+follower', body_text, re.IGNORECASE)
        if followers_match:
            result["followers"] = parse_count(followers_match.group(1))

        # Likes: "1,234 likes" or "12K likes"
        likes_match = re.search(r'([\d,.]+[KkMmBb]?)\s+like', body_text, re.IGNORECASE)
        if likes_match:
            result["likes"] = parse_count(likes_match.group(1))

        # Rating: "4.5 out of 5" or "Rating: 4.5"
        rating_match = re.search(r'(\d\.\d)\s*(?:out of\s*5|/\s*5|\s*\()', body_text)
        if rating_match:
            result["rating"] = float(rating_match.group(1))

        # Review count
        review_match = re.search(r'([\d,]+)\s+review', body_text, re.IGNORECASE)
        if review_match:
            result["review_count"] = int(review_match.group(1).replace(",", ""))

    except Exception:
        pass

    # Address — look for map/address sections
    try:
        for sel in ['a[href*="maps"]', 'div[data-pagelet*="address"]',
                    'span:has-text("Located in")', 'div:has-text("Get Directions")']:
            el = scope.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if text and 5 < len(text) < 300 and "map" not in text.lower():
                    result["address"] = text
                    break
    except Exception:
        pass

    # Phone
    try:
        for sel in ['a[href^="tel:"]', 'span:has-text("Call")']:
            el = scope.query_selector(sel)
            if el:
                href = el.get_attribute("href") or ""
                if href.startswith("tel:"):
                    result["phone"] = href.replace("tel:", "").strip()
                    break
                text = el.inner_text().strip()
                phone_match = re.search(r'[\d()+\-\s]{7,}', text)
                if phone_match:
                    result["phone"] = phone_match.group(0).strip()
                    break
    except Exception:
        pass

    # Last post date — look for timestamp elements
    try:
        for sel in ['abbr[data-utime]', 'a[role="link"] span[id]:has-text("ago")',
                    'span:has-text("ago")', 'abbr']:
            el = scope.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                if text and ("ago" in text.lower() or re.search(r'\b\w+\s+\d{1,2}\b', text)):
                    result["last_post"] = text
                    break
    except Exception:
        pass

    # Fallback: parse og:description for follower/like counts
    if og_desc and result["followers"] is None:
        followers_match = re.search(r'([\d,.]+[KkMmBb]?)\s+follower', og_desc, re.IGNORECASE)
        if followers_match:
            result["followers"] = parse_count(followers_match.group(1))
        likes_match = re.search(r'([\d,.]+[KkMmBb]?)\s+like', og_desc, re.IGNORECASE)
        if likes_match:
            result["likes"] = parse_count(likes_match.group(1))

    # Determine activity status
    if result["name"] is None and result["followers"] is None:
        result["status"] = "not_found"

    return result


def extract_instagram(page):
    """Extract data from an Instagram profile."""
    result = {
        "username": None,
        "display_name": None,
        "bio": None,
        "followers": None,
        "following": None,
        "posts": None,
        "website": None,
        "is_business": False,
        "status": "active",
    }

    title = page.title() or ""
    if "page not found" in title.lower() or "sorry" in title.lower():
        result["status"] = "not_found"
        return result

    # --- Meta tags are the most reliable source for Instagram ---
    # og:description often has: "X Followers, X Following, X Posts - See Instagram photos and videos from Display Name (@handle)"
    og_desc = get_meta(page, "og:description") or ""
    og_title = get_meta(page, "og:title")

    # Parse og:description for counts
    if og_desc:
        # Pattern: "1,234 Followers, 567 Following, 89 Posts"
        followers_match = re.search(r'([\d,.]+[KkMmBb]?)\s+Follower', og_desc, re.IGNORECASE)
        following_match = re.search(r'([\d,.]+[KkMmBb]?)\s+Following', og_desc, re.IGNORECASE)
        posts_match = re.search(r'([\d,.]+[KkMmBb]?)\s+Post', og_desc, re.IGNORECASE)

        if followers_match:
            result["followers"] = parse_count(followers_match.group(1))
        if following_match:
            result["following"] = parse_count(following_match.group(1))
        if posts_match:
            result["posts"] = parse_count(posts_match.group(1))

        # Display name and username from description
        # Pattern: "... from Display Name (@username)"
        name_match = re.search(r'from\s+(.+?)\s*\(@(\w+)\)', og_desc)
        if name_match:
            result["display_name"] = name_match.group(1).strip()
            result["username"] = name_match.group(2)

    # og:title often has: "Display Name (@username) * Instagram photos and videos"
    if og_title:
        title_match = re.search(r'^(.+?)\s*\(@(\w+)\)', og_title)
        if title_match:
            if not result["display_name"]:
                result["display_name"] = title_match.group(1).strip()
            if not result["username"]:
                result["username"] = title_match.group(2)
        elif not result["display_name"]:
            result["display_name"] = og_title.split("|")[0].split("*")[0].strip()

    # --- DOM extraction (may be blocked by login wall) ---
    login_wall = page.query_selector('div[role="dialog"] a[href*="accounts/login"]')
    is_blocked = login_wall is not None

    if not is_blocked:
        # Username from URL or header
        try:
            url = page.url
            url_match = re.search(r'instagram\.com/([^/?#]+)', url)
            if url_match and not result["username"]:
                candidate = url_match.group(1)
                if candidate not in ("p", "explore", "accounts", "stories", "reel"):
                    result["username"] = candidate
        except Exception:
            pass

        # Bio text
        try:
            for sel in ['div.-vDIg span', 'meta[name="description"]',
                        'section main header section > div:nth-child(3)']:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text().strip() if el.inner_text else (el.get_attribute("content") or "").strip()
                    if text and len(text) > 2 and len(text) < 500 and "Follower" not in text:
                        result["bio"] = text
                        break
        except Exception:
            pass

        # Website in bio
        try:
            for sel in ['a[rel="me nofollow noopener noreferrer"]', 'a[href*="l.instagram.com"]',
                        'header a[target="_blank"]']:
                el = page.query_selector(sel)
                if el:
                    href = el.get_attribute("href") or ""
                    text = el.inner_text().strip()
                    if href and "instagram.com" not in href:
                        result["website"] = text or href
                        break
        except Exception:
            pass

        # Business account indicators
        try:
            # Business/professional accounts have contact buttons and category text
            contact_btn = page.query_selector('a[href*="tel:"], a[href*="mailto:"], button:has-text("Contact")')
            category_el = page.query_selector('div._aa_c, header div[style] > div:last-child')
            if contact_btn or category_el:
                result["is_business"] = True
        except Exception:
            pass

        # Try DOM-based count extraction if meta tags failed
        if result["followers"] is None:
            try:
                body_text = page.inner_text("header") if page.query_selector("header") else ""
                if body_text:
                    f_match = re.search(r'([\d,.]+[KkMmBb]?)\s+follower', body_text, re.IGNORECASE)
                    if f_match:
                        result["followers"] = parse_count(f_match.group(1))
                    fw_match = re.search(r'([\d,.]+[KkMmBb]?)\s+following', body_text, re.IGNORECASE)
                    if fw_match:
                        result["following"] = parse_count(fw_match.group(1))
                    p_match = re.search(r'([\d,.]+[KkMmBb]?)\s+post', body_text, re.IGNORECASE)
                    if p_match:
                        result["posts"] = parse_count(p_match.group(1))
            except Exception:
                pass

    # Extract username from URL as last resort
    if not result["username"]:
        try:
            url_match = re.search(r'instagram\.com/([^/?#]+)', page.url)
            if url_match:
                candidate = url_match.group(1)
                if candidate not in ("p", "explore", "accounts", "stories", "reel"):
                    result["username"] = candidate
        except Exception:
            pass

    # Determine status
    if result["display_name"] is None and result["followers"] is None and result["username"] is None:
        result["status"] = "not_found"

    return result


def extract_youtube(page):
    """Extract data from a YouTube channel page."""
    result = {
        "name": None,
        "subscribers": None,
        "videos": None,
        "last_upload": None,
        "description": None,
        "custom_url": None,
        "status": "active",
    }

    title = page.title() or ""
    if "404" in title or "not found" in title.lower():
        result["status"] = "not_found"
        return result

    # --- Meta tags ---
    og_title = get_meta(page, "og:title")
    og_desc = get_meta(page, "og:description")
    og_url = get_meta(page, "og:url")

    if og_title:
        # Remove " - YouTube" suffix
        result["name"] = re.sub(r'\s*-\s*YouTube\s*$', '', og_title).strip()

    if og_desc:
        result["description"] = og_desc[:300]

    if og_url:
        # Custom URL: youtube.com/@handle
        url_match = re.search(r'youtube\.com/@([\w.-]+)', og_url)
        if url_match:
            result["custom_url"] = f"@{url_match.group(1)}"

    # --- DOM extraction ---

    # Channel name
    if not result["name"]:
        for sel in ['#channel-name yt-formatted-string', '#channel-header #text',
                    'yt-formatted-string#text', 'h1 yt-formatted-string', 'c3-banner-title']:
            try:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text and len(text) < 200:
                        result["name"] = text
                        break
            except Exception:
                continue

    # Subscriber count — shown as "X subscribers" in the channel header
    try:
        for sel in ['#subscriber-count', 'yt-formatted-string#subscriber-count',
                    '#channel-header-container #subscriber-count',
                    'span:has-text("subscriber")']:
            el = page.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                sub_match = re.search(r'([\d,.]+[KkMmBb]?)\s+subscriber', text, re.IGNORECASE)
                if sub_match:
                    result["subscribers"] = sub_match.group(1)
                    break
                elif text and "subscriber" not in text.lower():
                    # Might just be the number
                    result["subscribers"] = text
                    break
    except Exception:
        pass

    # Video count
    try:
        for sel in ['#videos-count', 'span:has-text("video")', 'yt-formatted-string:has-text("video")']:
            el = page.query_selector(sel)
            if el:
                text = el.inner_text().strip()
                vid_match = re.search(r'([\d,.]+)\s+video', text, re.IGNORECASE)
                if vid_match:
                    result["videos"] = int(vid_match.group(1).replace(",", ""))
                    break
    except Exception:
        pass

    # Try to get video count and last upload from the Videos tab or page body
    try:
        body_text = page.inner_text("body")

        # Subscribers from body text if not found
        if not result["subscribers"]:
            sub_match = re.search(r'([\d,.]+[KkMmBb]?)\s+subscriber', body_text, re.IGNORECASE)
            if sub_match:
                result["subscribers"] = sub_match.group(1)

        # Video count from body text
        if result["videos"] is None:
            vid_match = re.search(r'([\d,.]+)\s+video', body_text, re.IGNORECASE)
            if vid_match:
                result["videos"] = int(vid_match.group(1).replace(",", ""))

        # Last upload — look for relative time markers near video entries
        time_patterns = [
            r'(\d+\s+(?:hour|day|week|month|year)s?\s+ago)',
            r'(Streamed\s+\d+\s+\w+\s+ago)',
        ]
        for pat in time_patterns:
            m = re.search(pat, body_text, re.IGNORECASE)
            if m:
                result["last_upload"] = m.group(1)
                break

    except Exception:
        pass

    # Custom URL from page URL
    if not result["custom_url"]:
        try:
            url_match = re.search(r'youtube\.com/@([\w.-]+)', page.url)
            if url_match:
                result["custom_url"] = f"@{url_match.group(1)}"
        except Exception:
            pass

    # Channel description from about section (if not already from meta)
    if not result["description"]:
        try:
            desc_el = page.query_selector('#description-container, #channel-tagline, #about-description')
            if desc_el:
                text = desc_el.inner_text().strip()
                if text:
                    result["description"] = text[:300]
        except Exception:
            pass

    if result["name"] is None and result["subscribers"] is None:
        result["status"] = "not_found"

    return result


def extract_linkedin(page):
    """Extract data from a LinkedIn company page."""
    result = {
        "name": None,
        "followers": None,
        "employees": None,
        "industry": None,
        "headquarters": None,
        "status": "active",
    }

    title = page.title() or ""
    if "page not found" in title.lower() or "404" in title:
        result["status"] = "not_found"
        return result

    # --- Meta tags (often the only data available without login) ---
    og_title = get_meta(page, "og:title")
    og_desc = get_meta(page, "og:description")

    if og_title:
        # Remove "| LinkedIn" suffix
        result["name"] = re.sub(r'\s*\|\s*LinkedIn\s*$', '', og_title).strip()

    if og_desc:
        desc = og_desc

        # Follower count: "X followers on LinkedIn"
        followers_match = re.search(r'([\d,.]+[KkMmBb]?)\s+follower', desc, re.IGNORECASE)
        if followers_match:
            result["followers"] = parse_count(followers_match.group(1))

        # Employee count: "11-50 employees" or "1,001-5,000 employees"
        emp_match = re.search(r'([\d,]+-[\d,]+|[\d,.]+[KkMmBb]?\+?)\s+employee', desc, re.IGNORECASE)
        if emp_match:
            result["employees"] = emp_match.group(1)

        # Industry — often in the description text
        # LinkedIn descriptions often follow: "Company Name | X followers on LinkedIn. Tagline | Industry text..."
        parts = desc.split("|")
        if len(parts) >= 2:
            # Last part often contains industry/description
            for part in parts[1:]:
                part = part.strip()
                if "follower" not in part.lower() and "employee" not in part.lower() and len(part) > 3:
                    if not result["industry"]:
                        result["industry"] = part[:100]
                    break

    # --- DOM extraction (may be blocked by login wall) ---
    login_wall = page.query_selector('a[href*="login"], div[class*="auth-wall"]')
    is_blocked = login_wall is not None and page.query_selector('main section') is None

    if not is_blocked:
        # Company name
        if not result["name"]:
            for sel in ['h1 span', 'h1', '.top-card-layout__title', '.org-top-card-summary__title']:
                try:
                    el = page.query_selector(sel)
                    if el:
                        text = el.inner_text().strip()
                        if text and len(text) < 200:
                            result["name"] = text
                            break
                except Exception:
                    continue

        # Followers from DOM
        if result["followers"] is None:
            try:
                body_text = page.inner_text("body")
                f_match = re.search(r'([\d,.]+[KkMmBb]?)\s+follower', body_text, re.IGNORECASE)
                if f_match:
                    result["followers"] = parse_count(f_match.group(1))
            except Exception:
                pass

        # Employee count from DOM
        if not result["employees"]:
            try:
                for sel in ['a[href*="people"] span', 'div:has-text("employees")']:
                    el = page.query_selector(sel)
                    if el:
                        text = el.inner_text().strip()
                        emp_match = re.search(r'([\d,]+-[\d,]+|[\d,.]+[KkMmBb]?\+?)\s+employee', text, re.IGNORECASE)
                        if emp_match:
                            result["employees"] = emp_match.group(1)
                            break
            except Exception:
                pass

        # Industry from DOM
        if not result["industry"]:
            try:
                for sel in ['.org-top-card-summary-info-list__info-item',
                            '.top-card-layout__first-subline', 'dd.org-page-details__definition']:
                    el = page.query_selector(sel)
                    if el:
                        text = el.inner_text().strip()
                        if text and len(text) < 100:
                            result["industry"] = text
                            break
            except Exception:
                pass

        # Headquarters from DOM
        try:
            for sel in ['div:has-text("Headquarters") + div', 'dd:has-text(",")']:
                el = page.query_selector(sel)
                if el:
                    text = el.inner_text().strip()
                    if text and "," in text and len(text) < 200:
                        result["headquarters"] = text
                        break
        except Exception:
            pass

    if result["name"] is None and result["followers"] is None:
        result["status"] = "not_found"

    return result


# ── Platform dispatcher ──────────────────────────────────────────────

PLATFORMS = {
    "facebook": extract_facebook,
    "instagram": extract_instagram,
    "youtube": extract_youtube,
    "linkedin": extract_linkedin,
}


def check_social(urls):
    """Check all provided social URLs using a shared Playwright browser.

    Args:
        urls: dict mapping platform name to URL string.

    Returns:
        dict mapping platform name to extracted data dict.
    """
    from playwright.sync_api import sync_playwright

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-AU",
            timezone_id="Australia/Brisbane",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )

        for platform, url in urls.items():
            if not url or platform not in PLATFORMS:
                continue

            print(f"[check_social] Checking {platform}: {url}", file=sys.stderr)
            page = context.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=15000)
                time.sleep(3)

                # Save debug screenshot
                screenshot_path = f"/tmp/social_debug_{platform}.png"
                try:
                    page.screenshot(path=screenshot_path)
                    print(f"[check_social] Debug screenshot: {screenshot_path}", file=sys.stderr)
                except Exception:
                    pass

                # Dismiss cookie/consent banners common across platforms
                for consent_sel in [
                    'button[data-cookiebanner="accept_button"]',   # Facebook
                    'button:has-text("Accept All")',
                    'button:has-text("Accept all")',
                    'button:has-text("Allow all cookies")',
                    'button:has-text("Allow essential and optional cookies")',
                    'button[aria-label*="Accept"]',
                    'button:has-text("Reject")',
                ]:
                    try:
                        btn = page.query_selector(consent_sel)
                        if btn and btn.is_visible():
                            btn.click()
                            time.sleep(1)
                            break
                    except Exception:
                        continue

                # Run platform-specific extraction
                extractor = PLATFORMS[platform]
                data = extractor(page)
                data["url"] = url

                results[platform] = data

            except Exception as e:
                print(f"[check_social] Error on {platform}: {e}", file=sys.stderr)
                results[platform] = {
                    "url": url,
                    "status": "error",
                    "error": str(e),
                }
            finally:
                try:
                    page.close()
                except Exception:
                    pass

        browser.close()

    return results


def main():
    parser = argparse.ArgumentParser(description="Extract social media profile data via Playwright")
    parser.add_argument("--facebook", help="Facebook page URL")
    parser.add_argument("--instagram", help="Instagram profile URL")
    parser.add_argument("--youtube", help="YouTube channel URL")
    parser.add_argument("--linkedin", help="LinkedIn company page URL")
    parser.add_argument("--json", dest="json_input", metavar="FILE",
                        help="Read URLs from JSON file (use '-' for stdin)")
    args = parser.parse_args()

    if not check_playwright():
        sys.exit(1)

    # Build URL map from arguments
    urls = {}

    # If --json provided, read from file or stdin
    if args.json_input:
        try:
            if args.json_input == "-":
                raw = sys.stdin.read()
            else:
                with open(args.json_input, "r", encoding="utf-8") as f:
                    raw = f.read()
            urls = json.loads(raw)
        except Exception as e:
            print(f"ERROR: Failed to read JSON input: {e}", file=sys.stderr)
            sys.exit(1)

    # CLI flags override / supplement JSON input
    if args.facebook:
        urls["facebook"] = args.facebook
    if args.instagram:
        urls["instagram"] = args.instagram
    if args.youtube:
        urls["youtube"] = args.youtube
    if args.linkedin:
        urls["linkedin"] = args.linkedin

    # Filter to only known platforms with non-empty URLs
    urls = {k: v for k, v in urls.items() if k in PLATFORMS and v}

    if not urls:
        print("ERROR: No social profile URLs provided. Use --facebook, --instagram, --youtube, --linkedin, or --json", file=sys.stderr)
        sys.exit(1)

    results = check_social(urls)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
