#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
validate_schema.py — Validate structured data from crawled HTML files.

Detects both JSON-LD (<script type="application/ld+json">) and Microdata
(itemscope/itemtype/itemprop attributes) schema formats.

Usage:
    python scripts/validate_schema.py <crawl_dir>

Output:
    JSON to stdout with schema validation results.
"""

import argparse
import json
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


DEPRECATED_TYPES = {
    "HowTo": "Rich results removed September 2023",
    "SpecialAnnouncement": "Deprecated July 31, 2025",
    "CourseInfo": "Retired June 2025",
    "EstimatedSalary": "Retired June 2025",
    "LearningVideo": "Retired June 2025",
    "ClaimReview": "Retired from rich results June 2025",
    "VehicleListing": "Retired from rich results June 2025",
    "PracticeProblem": "Retired late 2025",
    "Dataset": "Retired from rich results late 2025",
}

RESTRICTED_TYPES = {
    "FAQPage": "Restricted to government and healthcare authority sites since August 2023",
}

REQUIRED_PROPERTIES = {
    "Organization": ["name", "url"],
    "LocalBusiness": ["name", "address", "url"],
    "Product": ["name"],
    "Article": ["headline", "author", "datePublished"],
    "BlogPosting": ["headline", "author", "datePublished"],
    "NewsArticle": ["headline", "author", "datePublished"],
    "BreadcrumbList": ["itemListElement"],
    "WebSite": ["name", "url"],
    "WebPage": ["name"],
    "Event": ["name", "startDate", "location"],
    "JobPosting": ["title", "description", "datePosted"],
    "VideoObject": ["name", "uploadDate", "thumbnailUrl"],
    "Person": ["name"],
    "Review": ["reviewRating", "author"],
    "AggregateRating": ["ratingValue", "reviewCount"],
    "Service": ["name"],
    "Offer": ["price", "priceCurrency"],
    "MerchantReturnPolicy": ["returnPolicyCountry"],
}

# Page type to recommended schema mapping
PAGE_SCHEMA_OPPORTUNITIES = {
    "homepage": ["Organization", "WebSite", "BreadcrumbList"],
    "about": ["Organization", "Person", "BreadcrumbList"],
    "service": ["Service", "BreadcrumbList", "Organization"],
    "product": ["Product", "Offer", "BreadcrumbList"],
    "blog": ["Article", "BlogPosting", "BreadcrumbList"],
    "contact": ["LocalBusiness", "Organization", "BreadcrumbList"],
    "faq": ["BreadcrumbList"],  # FAQPage restricted
    "location": ["LocalBusiness", "BreadcrumbList"],
}


class JsonLdExtractor(HTMLParser):
    """Extract JSON-LD blocks from HTML."""

    def __init__(self):
        super().__init__()
        self.blocks = []
        self._in_jsonld = False
        self._parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            attrs_dict = dict(attrs)
            if attrs_dict.get("type") == "application/ld+json":
                self._in_jsonld = True
                self._parts = []

    def handle_endtag(self, tag):
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
            raw = "".join(self._parts).strip()
            if raw:
                try:
                    parsed = json.loads(raw)
                    self.blocks.append(parsed)
                except json.JSONDecodeError as e:
                    self.blocks.append({"_raw": raw[:500], "_parse_error": str(e)})

    def handle_data(self, data):
        if self._in_jsonld:
            self._parts.append(data)


class MicrodataExtractor(HTMLParser):
    """Extract Microdata (itemscope/itemtype/itemprop) from HTML."""

    def __init__(self):
        super().__init__()
        self.items = []        # Top-level items (with itemscope + itemtype)
        self._stack = []       # Stack of nested itemscope elements
        self._skip_depth = 0
        self._skip_tags = {"script", "style"}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in self._skip_tags:
            self._skip_depth += 1
            return

        if self._skip_depth > 0:
            return

        has_itemscope = "itemscope" in attrs_dict
        itemtype = attrs_dict.get("itemtype", "")
        itemprop = attrs_dict.get("itemprop", "")

        if has_itemscope:
            # Extract short type name from full URL
            # e.g. "https://schema.org/Question" → "Question"
            type_name = ""
            if itemtype:
                type_name = itemtype.rsplit("/", 1)[-1] if "/" in itemtype else itemtype

            item = {
                "@type": type_name,
                "_tag": tag,
                "_props": {},
                "_children": [],
            }

            if self._stack and itemprop:
                # Nested itemscope — attach as child property
                parent = self._stack[-1]
                parent["_props"].setdefault(itemprop, []).append(item)
                parent["_children"].append(item)
            else:
                # Top-level itemscope
                self.items.append(item)

            self._stack.append(item)
        elif itemprop and self._stack:
            # Simple property on current item
            current = self._stack[-1]
            # Extract value from common attributes
            value = ""
            if tag == "meta":
                value = attrs_dict.get("content", "")
            elif tag in ("a", "link"):
                value = attrs_dict.get("href", "")
            elif tag == "img":
                value = attrs_dict.get("src", "")
            elif tag == "time":
                value = attrs_dict.get("datetime", "")
            # Text content handled in handle_data via _pending_prop
            if value:
                current["_props"][itemprop] = value
            else:
                # Will be filled by handle_data
                current["_pending_prop"] = itemprop

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip_depth = max(0, self._skip_depth - 1)
            return

        if self._skip_depth > 0:
            return

        # Pop itemscope when its tag closes
        if self._stack and self._stack[-1]["_tag"] == tag:
            item = self._stack[-1]
            item.pop("_pending_prop", None)
            self._stack.pop()

    def handle_data(self, data):
        if self._skip_depth > 0 or not self._stack:
            return
        text = data.strip()
        if text:
            current = self._stack[-1]
            prop = current.pop("_pending_prop", None)
            if prop:
                current["_props"][prop] = text

    def get_schema_types(self):
        """Return list of schema type names found."""
        types = []
        def _collect(items):
            for item in items:
                t = item.get("@type", "")
                if t:
                    types.append(t)
                for prop_val in item.get("_props", {}).values():
                    if isinstance(prop_val, list):
                        _collect([v for v in prop_val if isinstance(v, dict)])
        _collect(self.items)
        return types

    def get_summary(self):
        """Return a clean summary of microdata found."""
        summary = []
        def _summarize(item, depth=0):
            t = item.get("@type", "unknown")
            props = {k: v for k, v in item.get("_props", {}).items()
                     if not isinstance(v, list)}
            nested = {k: v for k, v in item.get("_props", {}).items()
                      if isinstance(v, list)}
            entry = {"@type": t, "properties": props}
            if nested:
                entry["nested"] = {}
                for k, items_list in nested.items():
                    entry["nested"][k] = [_summarize(i, depth+1) for i in items_list
                                          if isinstance(i, dict)]
            return entry
        for item in self.items:
            summary.append(_summarize(item))
        return summary


def flatten_schema(schema):
    """Flatten a schema that might have @graph or be a list."""
    items = []
    if isinstance(schema, list):
        for item in schema:
            items.extend(flatten_schema(item))
    elif isinstance(schema, dict):
        if "@graph" in schema:
            for item in schema["@graph"]:
                items.extend(flatten_schema(item))
        elif "@type" in schema:
            items.append(schema)
    return items


def validate_schema_block(schema):
    """Validate a single schema block. Returns list of issues."""
    issues = []

    if not isinstance(schema, dict):
        return [{"type": "invalid_format", "message": "Schema is not a dict"}]

    if "_parse_error" in schema:
        return [{"type": "parse_error", "message": schema["_parse_error"]}]

    # Check @context
    context = schema.get("@context", "")
    if context and context != "https://schema.org" and "schema.org" in str(context):
        if context == "http://schema.org":
            issues.append({
                "type": "http_context",
                "message": "Use https://schema.org instead of http://schema.org",
            })

    # Flatten and validate each item
    items = flatten_schema(schema)
    for item in items:
        schema_type = item.get("@type", "")

        # Handle list of types
        if isinstance(schema_type, list):
            types = schema_type
        else:
            types = [schema_type]

        for t in types:
            # Check deprecated
            if t in DEPRECATED_TYPES:
                issues.append({
                    "type": "deprecated_type",
                    "schema_type": t,
                    "message": DEPRECATED_TYPES[t],
                })

            # Check restricted
            if t in RESTRICTED_TYPES:
                issues.append({
                    "type": "restricted_type",
                    "schema_type": t,
                    "message": RESTRICTED_TYPES[t],
                })

            # Check required properties
            if t in REQUIRED_PROPERTIES:
                for prop in REQUIRED_PROPERTIES[t]:
                    if prop not in item or not item[prop]:
                        issues.append({
                            "type": "missing_property",
                            "schema_type": t,
                            "property": prop,
                        })

        # Check for placeholder text
        for key, value in item.items():
            if isinstance(value, str):
                if re.search(r"\[.*?\]", value) and key not in ("@context", "@type", "@id"):
                    issues.append({
                        "type": "placeholder_text",
                        "property": key,
                        "value": value[:100],
                    })

        # Check for relative URLs
        for key in ("url", "image", "logo", "sameAs", "mainEntityOfPage"):
            value = item.get(key)
            if isinstance(value, str) and value and not value.startswith(("http://", "https://", "//")):
                if not value.startswith("#") and not value.startswith("mailto:"):
                    issues.append({
                        "type": "relative_url",
                        "property": key,
                        "value": value[:100],
                    })
            elif isinstance(value, dict) and "@id" in value:
                id_val = value["@id"]
                if isinstance(id_val, str) and not id_val.startswith(("http://", "https://")):
                    issues.append({
                        "type": "relative_url",
                        "property": f"{key}.@id",
                        "value": id_val[:100],
                    })

        # Check date formats (ISO 8601)
        for key in ("datePublished", "dateModified", "dateCreated", "startDate", "endDate", "datePosted"):
            value = item.get(key)
            if isinstance(value, str) and value:
                if not re.match(r"\d{4}-\d{2}-\d{2}", value):
                    issues.append({
                        "type": "invalid_date_format",
                        "property": key,
                        "value": value,
                        "message": "Expected ISO 8601 format (YYYY-MM-DD)",
                    })

    return issues


def guess_page_type(url, title="", h1s=None):
    """Guess page type from URL and title for schema opportunity detection."""
    path = urllib.parse.urlparse(url).path.lower() if "://" in url else url.lower()
    title_lower = title.lower()

    if path in ("/", "") or "homepage" in path:
        return "homepage"
    if any(w in path for w in ("/about", "/team", "/our-story")):
        return "about"
    if any(w in path for w in ("/contact", "/get-in-touch")):
        return "contact"
    if any(w in path for w in ("/blog", "/news", "/article", "/post")):
        return "blog"
    if any(w in path for w in ("/product", "/shop", "/store", "/item")):
        return "product"
    if any(w in path for w in ("/service", "/what-we-do", "/our-services")):
        return "service"
    if any(w in path for w in ("/faq", "/frequently-asked")):
        return "faq"
    if any(w in path for w in ("/location", "/suburb", "/area", "/service-area")):
        return "location"
    return None


def identify_missing_opportunities(url, existing_types, title=""):
    """Identify missing schema opportunities based on page type."""
    page_type = guess_page_type(url, title)
    if not page_type or page_type not in PAGE_SCHEMA_OPPORTUNITIES:
        return []

    recommended = PAGE_SCHEMA_OPPORTUNITIES[page_type]
    missing = [t for t in recommended if t not in existing_types]
    if missing:
        return [{"page_type": page_type, "missing_types": missing}]
    return []


def validate_crawl_dir(crawl_dir):
    """Validate all schema in crawled HTML files."""
    manifest_path = os.path.join(crawl_dir, "crawl_manifest.json")
    if not os.path.exists(manifest_path):
        print(f"ERROR: Crawl manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    pages = manifest.get("pages", [])
    results = {
        "total_pages": len(pages),
        "pages_with_schema": 0,
        "pages_without_schema": 0,
        "total_schema_blocks": 0,
        "types_found": {},
        "microdata_types_found": {},
        "issues": [],
        "pages": [],
        "missing_opportunities": [],
    }

    for page in pages:
        if page.get("status") == "error":
            continue

        html_path = page.get("file", "")
        if not os.path.exists(html_path):
            continue

        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()
        except (OSError, UnicodeDecodeError):
            continue

        # Extract JSON-LD
        jsonld_extractor = JsonLdExtractor()
        try:
            jsonld_extractor.feed(html)
        except Exception:
            pass

        # Extract Microdata
        microdata_extractor = MicrodataExtractor()
        try:
            microdata_extractor.feed(html)
        except Exception:
            pass

        url = page.get("final_url", page.get("url", ""))
        title = page.get("title", "")
        microdata_types = microdata_extractor.get_schema_types()

        page_result = {
            "url": url,
            "schema_blocks": len(jsonld_extractor.blocks),
            "microdata_items": len(microdata_extractor.items),
            "types": [],
            "microdata_types": [],
            "issues": [],
        }

        has_any_schema = bool(jsonld_extractor.blocks) or bool(microdata_extractor.items)
        existing_types = set()

        # Process JSON-LD
        if jsonld_extractor.blocks:
            results["total_schema_blocks"] += len(jsonld_extractor.blocks)

            for block in jsonld_extractor.blocks:
                block_issues = validate_schema_block(block)
                page_result["issues"].extend(block_issues)

                # Collect types
                items = flatten_schema(block)
                for item in items:
                    t = item.get("@type", "unknown")
                    if isinstance(t, list):
                        for tt in t:
                            existing_types.add(tt)
                            results["types_found"][tt] = results["types_found"].get(tt, 0) + 1
                    else:
                        existing_types.add(t)
                        results["types_found"][t] = results["types_found"].get(t, 0) + 1

        # Process Microdata
        if microdata_extractor.items:
            page_result["microdata_types"] = list(set(microdata_types))
            page_result["microdata_summary"] = microdata_extractor.get_summary()
            for t in microdata_types:
                existing_types.add(t)
                results["microdata_types_found"][t] = results["microdata_types_found"].get(t, 0) + 1

                # Check restricted/deprecated for microdata types too
                if t in DEPRECATED_TYPES:
                    page_result["issues"].append({
                        "type": "deprecated_type",
                        "schema_type": t,
                        "format": "microdata",
                        "message": DEPRECATED_TYPES[t],
                    })
                if t in RESTRICTED_TYPES:
                    page_result["issues"].append({
                        "type": "restricted_type",
                        "schema_type": t,
                        "format": "microdata",
                        "message": RESTRICTED_TYPES[t],
                    })

        if has_any_schema:
            results["pages_with_schema"] += 1
            page_result["types"] = list(existing_types)

            # Missing opportunities (considers both formats)
            opportunities = identify_missing_opportunities(url, existing_types, title)
            if opportunities:
                for opp in opportunities:
                    opp["url"] = url
                results["missing_opportunities"].extend(opportunities)
        else:
            results["pages_without_schema"] += 1
            # Check for missing schema on pages that should have it
            opportunities = identify_missing_opportunities(url, set(), title)
            if opportunities:
                for opp in opportunities:
                    opp["url"] = url
                results["missing_opportunities"].extend(opportunities)

        if page_result["issues"]:
            results["issues"].extend([{**issue, "url": url} for issue in page_result["issues"]])

        results["pages"].append(page_result)

    microdata_count = sum(1 for p in results["pages"] if p.get("microdata_items", 0) > 0)
    jsonld_count = sum(1 for p in results["pages"] if p.get("schema_blocks", 0) > 0)
    print(f"[schema] {results['pages_with_schema']}/{results['total_pages']} pages have schema "
          f"(JSON-LD: {jsonld_count}, Microdata: {microdata_count})", file=sys.stderr)
    return results


def main():
    parser = argparse.ArgumentParser(description="Validate structured data (JSON-LD + Microdata)")
    parser.add_argument("crawl_dir", help="Directory containing crawl output")
    args = parser.parse_args()

    result = validate_crawl_dir(args.crawl_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
