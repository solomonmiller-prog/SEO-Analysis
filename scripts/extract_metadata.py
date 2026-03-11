#!/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe
"""
extract_metadata.py — Extract detailed SEO metadata from crawled HTML files.

Reads HTML files from a crawl directory (does NOT re-fetch). Extends the
LinkExtractor pattern from crawl_site.py with full metadata extraction.

Usage:
    python scripts/extract_metadata.py <crawl_dir> --cms <type>

Output:
    JSON array to stdout with per-page metadata.
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class MetadataExtractor(HTMLParser):
    """Extract comprehensive SEO metadata from HTML."""

    def __init__(self, cms="custom"):
        super().__init__()
        self.cms = cms

        # Title
        self.title = ""
        self.og_title = ""
        self._in_title = False
        self._title_parts = []

        # Headings
        self.h1s = []
        self.headings = []  # All H1-H6 with level
        self._current_heading = None
        self._heading_parts = []

        # Meta tags
        self.meta_description = ""
        self.meta_robots = ""
        self.canonical = ""
        self.og_tags = {}
        self.hreflang_tags = []

        # Images
        self.images = []

        # Embeds (iframes, video, object/embed)
        self.iframes = []
        self.videos = []

        # Links
        self.internal_links = []
        self.external_links = []
        self._current_link = None
        self._link_parts = []

        # JSON-LD
        self.jsonld_blocks = []
        self._in_jsonld = False
        self._jsonld_parts = []

        # Content extraction
        self._in_body = False
        self._text_parts = []
        self._skip_tags = {"script", "style", "noscript", "svg"}
        self._skip_depth = 0

        # Duda-specific content spans
        self._duda_content_parts = []
        self._in_duda_span = False

        # WordPress-specific
        self._in_wp_content = False
        self._wp_content_parts = []
        self._wp_depth = 0

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Skip script/style content
        if tag in self._skip_tags:
            self._skip_depth += 1
            # But handle JSON-LD scripts
            if tag == "script" and attrs_dict.get("type") == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_parts = []
            return

        # Track body
        if tag == "body":
            self._in_body = True

        # Title (only the real <title> in <head>, not SVG <title> elements)
        if tag == "title" and self._skip_depth == 0:
            self._in_title = True
            self._title_parts = []

        # Headings H1-H6
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(tag[1])
            self._current_heading = level
            self._heading_parts = []

        # Meta tags
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            content = attrs_dict.get("content", "")

            if name == "description":
                self.meta_description = content
            elif name == "robots":
                self.meta_robots = content
            elif prop.startswith("og:"):
                self.og_tags[prop] = content
                if prop == "og:title":
                    self.og_title = content

        # Canonical
        if tag == "link":
            rel = attrs_dict.get("rel", "")
            if rel == "canonical":
                self.canonical = attrs_dict.get("href", "")
            elif rel == "alternate":
                hreflang = attrs_dict.get("hreflang", "")
                if hreflang:
                    self.hreflang_tags.append({
                        "hreflang": hreflang,
                        "href": attrs_dict.get("href", ""),
                    })

        # Images
        if tag == "img":
            self.images.append({
                "src": attrs_dict.get("src", ""),
                "alt": attrs_dict.get("alt", ""),
                "width": attrs_dict.get("width", ""),
                "height": attrs_dict.get("height", ""),
                "loading": attrs_dict.get("loading", ""),
            })

        # Iframes (YouTube embeds, Google Maps, etc.)
        if tag == "iframe":
            src = attrs_dict.get("src", "") or attrs_dict.get("data-src", "")
            iframe_type = "other"
            if "youtube.com" in src or "youtu.be" in src:
                iframe_type = "youtube"
            elif "google.com/maps" in src or "maps.google" in src:
                iframe_type = "google_map"
            elif "vimeo.com" in src:
                iframe_type = "vimeo"
            elif "facebook.com" in src:
                iframe_type = "facebook"
            self.iframes.append({
                "src": src,
                "type": iframe_type,
                "title": attrs_dict.get("title", ""),
                "width": attrs_dict.get("width", ""),
                "height": attrs_dict.get("height", ""),
                "loading": attrs_dict.get("loading", ""),
            })

        # Video elements
        if tag == "video":
            self.videos.append({
                "src": attrs_dict.get("src", ""),
                "poster": attrs_dict.get("poster", ""),
                "autoplay": "autoplay" in attrs_dict,
                "controls": "controls" in attrs_dict,
            })

        # Source inside video (handled separately since video src can be in child <source>)
        if tag == "source" and self.videos:
            src = attrs_dict.get("src", "")
            if src and not self.videos[-1].get("src"):
                self.videos[-1]["src"] = src

        # Links
        if tag == "a" and "href" in attrs_dict:
            self._current_link = attrs_dict["href"]
            self._link_parts = []

        # Duda content spans
        if self.cms == "duda" and tag == "span":
            style = attrs_dict.get("style", "")
            if "display: unset" in style or "display: initial" in style:
                self._in_duda_span = True

        # WordPress content container
        if self.cms == "wordpress" and tag in ("article", "div"):
            cls = attrs_dict.get("class", "")
            if "entry-content" in cls or tag == "article":
                self._in_wp_content = True
                self._wp_depth = 0
            if self._in_wp_content:
                self._wp_depth += 1

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            if self._in_jsonld and tag == "script":
                self._in_jsonld = False
                raw = "".join(self._jsonld_parts).strip()
                if raw:
                    try:
                        parsed = json.loads(raw)
                        self.jsonld_blocks.append(parsed)
                    except json.JSONDecodeError:
                        self.jsonld_blocks.append({"_raw": raw, "_parse_error": True})
            self._skip_depth = max(0, self._skip_depth - 1)
            return

        # Title (only process if we're actually tracking a real title)
        if tag == "title" and self._in_title and self._skip_depth == 0:
            self._in_title = False
            self.title = " ".join(self._title_parts).strip()

        # Headings
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._current_heading:
            text = " ".join(self._heading_parts).strip()
            level = self._current_heading
            self.headings.append({"level": level, "text": text})
            if level == 1:
                self.h1s.append(text)
            self._current_heading = None

        # Links
        if tag == "a" and self._current_link is not None:
            anchor_text = " ".join(self._link_parts).strip()
            self._current_link = None
            # Classification happens later when we have the base URL

        # Duda spans
        if self.cms == "duda" and tag == "span" and self._in_duda_span:
            self._in_duda_span = False

        # WordPress content
        if self.cms == "wordpress" and self._in_wp_content:
            if tag in ("article", "div"):
                self._wp_depth -= 1
                if self._wp_depth <= 0:
                    self._in_wp_content = False

    def handle_data(self, data):
        if self._skip_depth > 0:
            if self._in_jsonld:
                self._jsonld_parts.append(data)
            return

        text = data.strip()
        if not text:
            return

        # Title
        if self._in_title:
            self._title_parts.append(text)

        # Headings
        if self._current_heading is not None:
            self._heading_parts.append(text)

        # Links
        if self._current_link is not None:
            self._link_parts.append(text)

        # Body text
        if self._in_body:
            self._text_parts.append(text)

        # Duda content
        if self._in_duda_span:
            self._duda_content_parts.append(text)

        # WordPress content
        if self._in_wp_content:
            self._wp_content_parts.append(text)

    def get_word_count(self):
        """Get platform-aware word count."""
        if self.cms == "duda" and self._duda_content_parts:
            text = " ".join(self._duda_content_parts)
        elif self.cms == "wordpress" and self._wp_content_parts:
            text = " ".join(self._wp_content_parts)
        else:
            text = " ".join(self._text_parts)
        return len(text.split())

    def get_content_text(self):
        """Get the extracted content text for the platform."""
        if self.cms == "duda" and self._duda_content_parts:
            return " ".join(self._duda_content_parts)
        elif self.cms == "wordpress" and self._wp_content_parts:
            return " ".join(self._wp_content_parts)
        return " ".join(self._text_parts)


def classify_links(links, base_url):
    """Classify links as internal or external."""
    import urllib.parse
    base_parsed = urllib.parse.urlparse(base_url)
    base_domain = base_parsed.netloc.lower().lstrip("www.")

    internal = []
    external = []

    for href, anchor in links:
        if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        resolved = urllib.parse.urljoin(base_url, href)
        parsed = urllib.parse.urlparse(resolved)
        domain = parsed.netloc.lower().lstrip("www.")

        entry = {"href": resolved, "anchor_text": anchor}
        if domain == base_domain:
            internal.append(entry)
        else:
            external.append(entry)

    return internal, external


def extract_page_metadata(html_path, page_url, cms="custom"):
    """Extract metadata from a single HTML file."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return {"url": page_url, "error": str(e)}

    extractor = MetadataExtractor(cms=cms)
    try:
        extractor.feed(html)
    except Exception:
        pass  # Best-effort parsing

    # Effective title (Duda og:title fallback)
    title = extractor.title
    if cms == "duda" and (not title or len(title) < 10):
        title = extractor.og_title or title

    # Classify links by collecting them during a second pass
    # (simpler than tracking in the main parser)
    import urllib.parse

    class LinkCollector(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self._current_href = None
            self._parts = []

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                attrs_dict = dict(attrs)
                if "href" in attrs_dict:
                    self._current_href = attrs_dict["href"]
                    self._parts = []

        def handle_endtag(self, tag):
            if tag == "a" and self._current_href is not None:
                anchor = " ".join(self._parts).strip()
                self.links.append((self._current_href, anchor))
                self._current_href = None

        def handle_data(self, data):
            if self._current_href is not None:
                self._parts.append(data.strip())

    lc = LinkCollector()
    try:
        lc.feed(html)
    except Exception:
        pass

    internal_links, external_links = classify_links(lc.links, page_url)

    return {
        "url": page_url,
        "file": html_path,
        "title": title,
        "h1s": extractor.h1s,
        "headings": extractor.headings,
        "meta_description": extractor.meta_description,
        "meta_robots": extractor.meta_robots,
        "canonical": extractor.canonical,
        "og_tags": extractor.og_tags,
        "hreflang_tags": extractor.hreflang_tags,
        "images": extractor.images,
        "internal_links": internal_links,
        "external_links": external_links,
        "jsonld_blocks": extractor.jsonld_blocks,
        "iframes": extractor.iframes,
        "videos": extractor.videos,
        "word_count": extractor.get_word_count(),
    }


def main():
    parser = argparse.ArgumentParser(description="Extract SEO metadata from crawled HTML")
    parser.add_argument("crawl_dir", help="Directory containing crawl output")
    parser.add_argument("--cms", default="custom", choices=["duda", "wordpress", "shopify", "wix", "squarespace", "custom"],
                        help="CMS type for platform-aware extraction")
    args = parser.parse_args()

    # Read crawl manifest
    manifest_path = os.path.join(args.crawl_dir, "crawl_manifest.json")
    if not os.path.exists(manifest_path):
        print(f"ERROR: Crawl manifest not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    pages = manifest.get("pages", [])
    results = []

    print(f"[extract_metadata] Processing {len(pages)} pages (CMS: {args.cms})...", file=sys.stderr)

    for i, page in enumerate(pages):
        if page.get("status") == "error":
            results.append({"url": page["url"], "error": page.get("error", "crawl error")})
            continue

        html_path = page.get("file", "")
        if not os.path.exists(html_path):
            results.append({"url": page["url"], "error": f"HTML file not found: {html_path}"})
            continue

        page_url = page.get("final_url", page["url"])
        metadata = extract_page_metadata(html_path, page_url, cms=args.cms)
        results.append(metadata)

        if (i + 1) % 50 == 0:
            print(f"[extract_metadata] Processed {i + 1}/{len(pages)} pages...", file=sys.stderr)

    print(f"[extract_metadata] Done: {len(results)} pages processed", file=sys.stderr)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
