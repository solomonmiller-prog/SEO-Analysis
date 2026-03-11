#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
extract_nap.py — Extract business NAP (Name, Address, Phone) data from crawled HTML.

Reads crawl manifest + site_data.json to extract NAP information from multiple
sources: schema markup, contact pages, footers, and social profile links.

Usage:
    python scripts/extract_nap.py <crawl_dir> --site-data <site_data.json>

Output:
    JSON to stdout with consolidated NAP data and consistency analysis.
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ---------------------------------------------------------------------------
# Regex patterns for Australian contact details
# ---------------------------------------------------------------------------

# Phone patterns
RE_LANDLINE = re.compile(
    r'\(0[2-9]\)\s*\d{4}\s*\d{4}'       # (0X) XXXX XXXX
    r'|0[2-9]\s*\d{4}\s*\d{4}'           # 0X XXXX XXXX
    r'|0[2-9]\.\d{4}\.\d{4}'             # 0X.XXXX.XXXX
)
RE_MOBILE = re.compile(
    r'04\d{2}\s*\d{3}\s*\d{3}'           # 04XX XXX XXX
    r'|04\d{2}\s*\d{2}\s*\d{2}\s*\d{2}'  # 04XX XX XX XX
)
RE_1300 = re.compile(
    r'1[38]00\s*\d{3}\s*\d{3}'           # 1300/1800 XXX XXX
    r'|13\s*\d{2}\s*\d{2}'               # 13 XX XX (short 13-numbers)
)
RE_PHONE_ALL = re.compile(
    r'\(0[2-9]\)\s*\d{4}\s*\d{4}'
    r'|0[2-9]\s*\d{4}\s*\d{4}'
    r'|04\d{2}\s*\d{3}\s*\d{3}'
    r'|04\d{2}\s*\d{2}\s*\d{2}\s*\d{2}'
    r'|1[38]00\s*\d{3}\s*\d{3}'
    r'|13\s*\d{2}\s*\d{2}'
)

# Email pattern
RE_EMAIL = re.compile(
    r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
)

# ABN pattern: ABN: XX XXX XXX XXX or ABN XX XXX XXX XXX
RE_ABN = re.compile(
    r'ABN[:\s]+(\d{2}\s*\d{3}\s*\d{3}\s*\d{3})',
    re.IGNORECASE,
)

# Australian address pattern (best-effort)
# Matches: number street-name, suburb STATE postcode
AU_STATES = r'(?:NSW|VIC|QLD|SA|WA|TAS|NT|ACT)'
RE_ADDRESS = re.compile(
    r'(\d{1,5}[A-Za-z]?'              # Street number (possibly with unit letter)
    r'(?:[/\-]\d{1,5})?'               # Optional unit separator e.g. 3/45
    r'\s+[A-Z][A-Za-z\s\'.]+?'         # Street name
    r'(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Boulevard|Blvd|Lane|Ln|'
    r'Place|Pl|Court|Ct|Crescent|Cres|Way|Terrace|Tce|Parade|Pde|'
    r'Circuit|Cct|Highway|Hwy|Close|Cl)[,.\s]+'
    r'[A-Z][A-Za-z\s\'.]+?'            # Suburb
    r'[,\s]+'
    r'' + AU_STATES + r'\s+'
    r'\d{4})',                           # Postcode
    re.IGNORECASE,
)

# Simpler fallback: just state + postcode near text that looks like an address
RE_SUBURB_STATE_POST = re.compile(
    r'([A-Z][A-Za-z\s\'.]{2,30}?)[,\s]+(' + AU_STATES + r')\s+(\d{4})',
)

# Social profile domains
SOCIAL_DOMAINS = {
    "facebook": ["facebook.com"],
    "instagram": ["instagram.com"],
    "youtube": ["youtube.com"],
    "linkedin": ["linkedin.com"],
    "twitter": ["twitter.com", "x.com"],
}


# ---------------------------------------------------------------------------
# HTML text extractor — grabs footer and full body text
# ---------------------------------------------------------------------------

class BodyTextExtractor(HTMLParser):
    """Extract body text and track approximate line position for footer heuristic."""

    def __init__(self):
        super().__init__()
        self._in_body = False
        self._skip_depth = 0
        self._skip_tags = {"script", "style", "noscript", "svg"}
        self._text_parts = []       # (text, tag_context)
        self._in_footer = False
        self._footer_depth = 0
        self._footer_parts = []
        self._in_a = False
        self._current_href = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in self._skip_tags:
            self._skip_depth += 1
            return

        if tag == "body":
            self._in_body = True

        # Track footer element
        if tag == "footer":
            self._in_footer = True
            self._footer_depth = 0
        if self._in_footer:
            self._footer_depth += 1

        # Detect footer-like divs by class/id
        if tag in ("div", "section") and not self._in_footer:
            cls = attrs_dict.get("class", "") + " " + attrs_dict.get("id", "")
            if "footer" in cls.lower():
                self._in_footer = True
                self._footer_depth = 0
                self._footer_depth += 1

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._in_footer:
            if tag in ("footer", "div", "section"):
                self._footer_depth -= 1
                if self._footer_depth <= 0:
                    self._in_footer = False

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        text = data.strip()
        if not text:
            return
        if self._in_body:
            self._text_parts.append(text)
        if self._in_footer:
            self._footer_parts.append(text)

    def get_body_text(self):
        return " ".join(self._text_parts)

    def get_footer_text(self):
        return " ".join(self._footer_parts)


# ---------------------------------------------------------------------------
# NAP extraction logic
# ---------------------------------------------------------------------------

def classify_phone(number):
    """Classify a phone number as landline, mobile, or 1300."""
    cleaned = re.sub(r'\s+', '', number)
    if cleaned.startswith("1300") or cleaned.startswith("1800") or cleaned.startswith("13"):
        return "1300"
    if cleaned.startswith("04"):
        return "mobile"
    return "landline"


def normalise_phone(number):
    """Normalise phone to digits only for comparison."""
    return re.sub(r'[^\d]', '', number)


def extract_phones(text, source, page_url):
    """Extract all phone numbers from text."""
    results = []
    seen = set()
    for match in RE_PHONE_ALL.finditer(text):
        raw = match.group(0).strip()
        norm = normalise_phone(raw)
        if norm not in seen and len(norm) >= 8:
            seen.add(norm)
            results.append({
                "source": source,
                "page_url": page_url,
                "number": raw,
                "type": classify_phone(raw),
            })
    return results


def extract_emails(text, source, page_url):
    """Extract email addresses from text."""
    results = []
    seen = set()
    for match in RE_EMAIL.finditer(text):
        email = match.group(0).lower()
        # Filter out common false positives
        if email.endswith((".png", ".jpg", ".gif", ".svg", ".css", ".js")):
            continue
        if email not in seen:
            seen.add(email)
            results.append({
                "source": source,
                "page_url": page_url,
                "email": email,
            })
    return results


STREET_SUFFIXES = re.compile(
    r'(?:Street|St|Road|Rd|Avenue|Ave|Drive|Dr|Boulevard|Blvd|Lane|Ln|'
    r'Place|Pl|Court|Ct|Crescent|Cres|Way|Terrace|Tce|Parade|Pde|'
    r'Circuit|Cct|Highway|Hwy|Close|Cl)\b',
    re.IGNORECASE,
)


def parse_address_parts(raw_text):
    """Attempt to parse an address into components."""
    parts = {"street": "", "suburb": "", "state": "", "postcode": ""}

    # Extract state + postcode
    state_match = re.search(
        r'[,\s]+(' + AU_STATES + r')\s+(\d{4})\s*$', raw_text,
    )
    if not state_match:
        state_match = re.search(
            r'[,\s]+(' + AU_STATES + r')\s+(\d{4})', raw_text,
        )
    if not state_match:
        return parts

    parts["state"] = state_match.group(1).strip()
    parts["postcode"] = state_match.group(2).strip()
    text_before_state = raw_text[:state_match.start()].strip().rstrip(",").strip()

    # Find street suffix to split street from suburb
    suffix_match = STREET_SUFFIXES.search(text_before_state)
    if suffix_match:
        parts["street"] = text_before_state[:suffix_match.end()].strip()
        suburb = text_before_state[suffix_match.end():].strip().lstrip(",").strip()
        parts["suburb"] = suburb if suburb else ""
    else:
        # No street suffix found — put everything as street
        parts["street"] = text_before_state
    return parts


def extract_addresses(text, source, page_url):
    """Extract Australian addresses from text."""
    results = []
    seen = set()

    # Try full address pattern first
    for match in RE_ADDRESS.finditer(text):
        raw = match.group(0).strip()
        norm = re.sub(r'\s+', ' ', raw)
        if norm not in seen:
            seen.add(norm)
            results.append({
                "source": source,
                "page_url": page_url,
                "raw_text": norm,
                "parsed": parse_address_parts(norm),
            })

    return results


def extract_nap_from_schema(jsonld_blocks, page_url):
    """Extract NAP from JSON-LD schema blocks."""
    phones = []
    emails = []
    addresses = []
    business_name = None

    def process_block(block):
        nonlocal business_name
        if not isinstance(block, dict):
            return
        block_type = block.get("@type", "")
        if isinstance(block_type, list):
            block_type = " ".join(block_type)

        is_org = any(t in block_type for t in (
            "Organization", "LocalBusiness", "Corporation", "Store",
            "Restaurant", "MedicalBusiness", "LegalService",
            "FinancialService", "RealEstateAgent", "Dentist",
            "AutoRepair", "HomeAndConstructionBusiness",
            "ProfessionalService",
        ))

        if is_org:
            name = block.get("name", "")
            if name and not business_name:
                business_name = name

            # Telephone
            tel = block.get("telephone", "")
            if tel:
                phones.extend(extract_phones(tel, "schema", page_url))

            # Email
            email = block.get("email", "")
            if email:
                emails.extend(extract_emails(email, "schema", page_url))

            # Address
            addr = block.get("address", {})
            if isinstance(addr, dict):
                parts = {
                    "street": addr.get("streetAddress", ""),
                    "suburb": addr.get("addressLocality", ""),
                    "state": addr.get("addressRegion", ""),
                    "postcode": addr.get("postalCode", ""),
                }
                raw = ", ".join(v for v in [
                    parts["street"], parts["suburb"],
                    parts["state"], parts["postcode"],
                ] if v)
                if raw.strip():
                    addresses.append({
                        "source": "schema",
                        "page_url": page_url,
                        "raw_text": raw,
                        "parsed": parts,
                    })
            elif isinstance(addr, str) and addr.strip():
                addresses.append({
                    "source": "schema",
                    "page_url": page_url,
                    "raw_text": addr.strip(),
                    "parsed": parse_address_parts(addr),
                })

        # Recurse into @graph
        if "@graph" in block:
            for item in block["@graph"]:
                process_block(item)

    for block in jsonld_blocks:
        try:
            process_block(block)
        except Exception:
            pass

    return business_name, phones, emails, addresses


def extract_social_profiles(pages_metadata):
    """Collect social profile URLs from external_links across all pages."""
    profiles = {k: set() for k in SOCIAL_DOMAINS}

    for page in pages_metadata:
        for link in page.get("external_links", []):
            href = link.get("href", "").lower()
            for platform, domains in SOCIAL_DOMAINS.items():
                for domain in domains:
                    if domain in href:
                        # Clean up — take the original-case URL
                        profiles[platform].add(link["href"])

    # Convert sets to sorted lists
    return {k: sorted(v) for k, v in profiles.items()}


def get_business_name(pages_metadata):
    """Infer business name from og:site_name or title brand portion."""
    # Try og:site_name first
    for page in pages_metadata:
        og = page.get("og_tags", {})
        site_name = og.get("og:site_name", "")
        if site_name:
            return site_name

    # Fall back to title — take the portion after | or - or : (brand typically last)
    for page in pages_metadata:
        title = page.get("title", "")
        if not title:
            continue
        for sep in [" | ", " - ", " – ", " — ", " : "]:
            if sep in title:
                parts = title.split(sep)
                # Brand is usually the last part
                brand = parts[-1].strip()
                if 3 <= len(brand) <= 60:
                    return brand
        # If no separator, use the whole title for the home page
        url = page.get("url", "")
        path = url.rstrip("/").split("/")[-1] if url else ""
        if not path or path == url.split("//")[-1].split("/")[0]:
            return title

    return None


def analyse_consistency(addresses, phones):
    """Analyse NAP consistency across sources."""
    issues = []

    # Normalise addresses for comparison
    addr_variants = set()
    for a in addresses:
        norm = re.sub(r'[\s,]+', ' ', a["raw_text"].lower()).strip()
        addr_variants.add(norm)

    if len(addr_variants) > 1:
        issues.append("Address varies between sources/pages")

    # Normalise phones
    phone_variants = set()
    for p in phones:
        phone_variants.add(normalise_phone(p["number"]))

    # Multiple different phone numbers is not necessarily an issue
    # (could have landline + mobile), but flag if same type differs
    by_type = {}
    for p in phones:
        t = p["type"]
        norm = normalise_phone(p["number"])
        by_type.setdefault(t, set()).add(norm)
    for t, nums in by_type.items():
        if len(nums) > 1:
            issues.append(f"Multiple different {t} numbers found")

    primary_address = addresses[0]["raw_text"] if addresses else None
    primary_phone = phones[0]["number"] if phones else None

    return {
        "primary_address": primary_address,
        "primary_phone": primary_phone,
        "variations_found": len(issues) > 0,
        "issues": issues,
    }


def is_contact_page(url):
    """Check if URL is likely a contact page."""
    path = url.lower().rstrip("/").split("/")[-1] if url else ""
    return "contact" in path


def extract_nap_from_html(html_path, page_url, source_hint="page"):
    """Extract NAP data from an HTML file's body/footer text."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
    except (OSError, UnicodeDecodeError):
        return [], [], [], None

    extractor = BodyTextExtractor()
    try:
        extractor.feed(html)
    except Exception:
        pass  # Best-effort parsing

    phones = []
    emails = []
    addresses = []
    abn = None

    # Determine which text blocks to scan and with which source label
    blocks = []
    footer_text = extractor.get_footer_text()
    body_text = extractor.get_body_text()

    if footer_text:
        blocks.append((footer_text, "footer"))

    if is_contact_page(page_url):
        blocks.append((body_text, "contact_page"))

    # Fallback: if no footer detected, use last ~2000 chars of body as proxy
    if not footer_text and body_text:
        tail = body_text[-2000:]
        blocks.append((tail, "footer"))

    for text, source in blocks:
        phones.extend(extract_phones(text, source, page_url))
        emails.extend(extract_emails(text, source, page_url))
        addresses.extend(extract_addresses(text, source, page_url))
        m = RE_ABN.search(text)
        if m and abn is None:
            abn = re.sub(r'\s+', ' ', m.group(1).strip())

    return phones, emails, addresses, abn


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract NAP data from crawled HTML")
    parser.add_argument("crawl_dir", help="Directory containing crawl output")
    parser.add_argument("--site-data", required=True, help="Path to site_data.json")
    args = parser.parse_args()

    # Read crawl manifest
    manifest_path = os.path.join(args.crawl_dir, "crawl_manifest.json")
    if not os.path.exists(manifest_path):
        print(f"ERROR: Crawl manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Read site_data.json
    if not os.path.exists(args.site_data):
        print(f"ERROR: site_data.json not found: {args.site_data}", file=sys.stderr)
        sys.exit(1)

    with open(args.site_data, "r", encoding="utf-8") as f:
        site_data = json.load(f)

    pages_metadata = site_data.get("pages_metadata", [])
    pages = manifest.get("pages", [])

    print(f"[extract_nap] Processing {len(pages)} crawled pages...", file=sys.stderr)

    all_phones = []
    all_emails = []
    all_addresses = []
    abn = None
    schema_business_name = None

    # --- Source 1: Schema markup from site_data.json ---
    for page_meta in pages_metadata:
        jsonld = page_meta.get("jsonld_blocks", [])
        if not jsonld:
            continue
        page_url = page_meta.get("url", "")
        name, phones, emails, addrs = extract_nap_from_schema(jsonld, page_url)
        if name and not schema_business_name:
            schema_business_name = name
        all_phones.extend(phones)
        all_emails.extend(emails)
        all_addresses.extend(addrs)

    # --- Source 2 & 3: Contact pages and footers from crawled HTML ---
    for page in pages:
        if page.get("status") == "error":
            continue
        html_path = page.get("file", "")
        if not html_path or not os.path.exists(html_path):
            continue
        page_url = page.get("final_url", page.get("url", ""))

        phones, emails, addrs, page_abn = extract_nap_from_html(
            html_path, page_url,
        )
        all_phones.extend(phones)
        all_emails.extend(emails)
        all_addresses.extend(addrs)
        if page_abn and abn is None:
            abn = page_abn

    # --- Source 4: Social profiles from external_links ---
    social_profiles = extract_social_profiles(pages_metadata)

    # --- Business name ---
    business_name = schema_business_name or get_business_name(pages_metadata)

    # --- Deduplicate ---
    def dedup_phones(phones):
        seen = set()
        out = []
        for p in phones:
            key = normalise_phone(p["number"])
            if key not in seen:
                seen.add(key)
                out.append(p)
        return out

    def dedup_emails(emails):
        seen = set()
        out = []
        for e in emails:
            key = e["email"].lower()
            if key not in seen:
                seen.add(key)
                out.append(e)
        return out

    def dedup_addresses(addresses):
        seen = set()
        out = []
        for a in addresses:
            key = re.sub(r'[\s,]+', ' ', a["raw_text"].lower()).strip()
            if key not in seen:
                seen.add(key)
                out.append(a)
        return out

    all_phones = dedup_phones(all_phones)
    all_emails = dedup_emails(all_emails)
    all_addresses = dedup_addresses(all_addresses)

    # --- Consistency analysis ---
    nap_consistency = analyse_consistency(all_addresses, all_phones)

    # --- Build output ---
    result = {
        "business_name": business_name,
        "addresses_found": all_addresses,
        "phones_found": all_phones,
        "emails_found": all_emails,
        "abn": abn,
        "social_profiles": social_profiles,
        "nap_consistency": nap_consistency,
    }

    print(f"[extract_nap] Done: {len(all_addresses)} addresses, "
          f"{len(all_phones)} phones, {len(all_emails)} emails, "
          f"{len([v for v in social_profiles.values() if v])} social platforms",
          file=sys.stderr)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
