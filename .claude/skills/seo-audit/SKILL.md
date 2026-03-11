---
name: seo-audit
description: >
  Full website SEO audit with hybrid scripts + agents pipeline. Scripts handle
  deterministic data collection (preflight, metadata, CWV, schema, sitemap,
  security, screenshots) into site_data.json, then 5 qualitative agents run
  in parallel (content, factcheck, ux, geo, authority). Generates health score, then runs
  independent QA validation before delivery. Use when user says "audit",
  "full SEO check", "full site analysis", "analyze my site", "website health
  check", "site review", "complete SEO review", "website audit", "check my
  website", or "SEO report". Always use this skill when a user provides a URL
  and asks for a comprehensive or full analysis — even if they don't use the
  word "audit" explicitly.
---

# Full Website SEO Audit — Hybrid Pipeline

## Environment Note — Python

On this system, `python` is not in PATH. Use the full path:
```
PYTHON="/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe"
```
All `PYTHON` references in this skill should be replaced with this path when
executing commands. Example:
```bash
"$PYTHON" scripts/build_site_data.py https://example.com reports/example.com
```

## System Dependencies

- **Lighthouse CLI:** `npm install -g lighthouse` (for CWV measurement)
- **Playwright:** `pip install playwright && playwright install chromium` (for screenshots)
- Both are optional — `build_site_data.py` handles missing tools gracefully with `--skip-cwv` and `--skip-screenshots` flags.

## Architecture Overview

```
Phase 0: Pre-flight         → preflight.py (script)
Phase 1A: Data Collection   → build_site_data.py orchestrates 10 scripts → site_data.json
  Steps 1-7: crawl, metadata, schema, cwv, sitemap, security, screenshots
  Step 8: NAP extraction (business name, addresses, phones, social URLs)
  Step 9: GBP check via Playwright (rating, reviews, address, category)
  Step 10: Social media check via Playwright (followers, posts, bio)
Phase 1B: Qualitative       → 5 agents in parallel (content, factcheck, ux, geo, authority)
Phase 2: Report             → Read site_data.json + agent markdowns → HTML → PDF
Phase 3: QA Validation      → seo-validate agent (verifies against site_data.json)
```

---

## Process

### Phase 0: Pre-flight (Step 0)

Run preflight to verify site is reachable and detect CMS:

```bash
"$PYTHON" scripts/preflight.py <url>
```

Check the JSON output:
- `reachable` must be `true` — if false, stop and report the blocker
- `cms` — detected platform (duda, wordpress, shopify, wix, squarespace, custom)
- `robots_txt` — disallow rules and AI crawler access
- `sitemap` — presence and URL count
- `estimated_pages` — rough page count from homepage links

If the site is unreachable, stop and report the error to the user.

---

### Phase 1A: Data Collection (Step 1)

Run the full data collection pipeline:

```bash
"$PYTHON" scripts/build_site_data.py <url> reports/<domain> --max-pages 500
```

This orchestrates all scripts automatically:
1. `preflight.py` — site reachability, CMS detection, robots.txt, llms.txt, sitemap check
2. `crawl_site.py` — crawl up to 500 pages, save HTML files
3. `extract_metadata.py` — extract per-page SEO metadata from crawled HTML
4. `validate_schema.py` — validate JSON-LD + Microdata structured data
5. `measure_cwv.py` — Lighthouse CWV measurement (homepage + sample pages)
6. `validate_sitemap.py` — XML sitemap validation with crawl cross-reference
7. `check_security.py` — HTTPS, SSL, security headers, mixed content
8. `capture_screenshots.py` — 4 viewports × above-fold + full-page
9. `extract_nap.py` — business name, addresses, phones, emails, ABN, social URLs from crawled HTML
10. `check_gbp.py` — Google Business Profile data via Playwright (rating, reviews, address, category)
11. `check_social.py` — social media profiles via Playwright (followers, posts, bio, status)

**Output:** `reports/<domain>/site_data.json` containing all objective measurements.

**Optional flags:**
- `--skip-cwv` — skip Lighthouse if not installed
- `--skip-screenshots` — skip Playwright if not installed
- `--skip-external` — skip GBP and social profile checks (steps 10-11)
- `--max-pages 50` — limit crawl for large sites

---

### Phase 1B: Qualitative Analysis (Step 2)

**Detect business type** — analyze `site_data.json → pages_metadata` and `schema` to
classify: local service, e-commerce, SaaS, publisher, agency, professional service, etc.

**Spawn 5 agents in parallel**, each given the path to `site_data.json` and `reports/<domain>/`:

1. **`seo-content`** — E-E-A-T, readability, thin content, AI citation readiness
   - Reads word counts, headings, meta tags from `site_data.json`
   - Reads crawled HTML for qualitative content analysis

2. **`seo-factcheck`** — **MANDATORY** — verify factual claims, measurements, statistics
   - Reads page inventory from `site_data.json`
   - Uses WebSearch/WebFetch for source verification

3. **`seo-ux`** — **MANDATORY** — navigation, visual hierarchy, CTAs, accessibility (WCAG 2.2 AA)
   - Reads pre-captured screenshots from `reports/<domain>/screenshots/`
   - Reads accessibility snapshot from `site_data.json`

4. **`seo-geo`** — AI Overviews, ChatGPT/Perplexity visibility, llms.txt, GEO signals
   - Reads AI crawler status from `site_data.json → preflight.robots_txt.ai_crawlers`
   - Reads llms.txt from `site_data.json → preflight.llms_txt`

5. **`seo-authority`** — **MANDATORY** — external presence research (GBP, Facebook, YouTube, LinkedIn, directories, reviews)
   - Reads embedded content (iframes, videos) from `site_data.json → pages_metadata[].iframes`
   - Reads external links from `site_data.json → pages_metadata[].external_links`
   - Uses WebSearch/WebFetch to research presence on Google Business Profile, Facebook, YouTube, LinkedIn, Instagram, industry directories, and review platforms
   - Checks NAP consistency across all platforms found
   - Outputs `AUTHORITY-REPORT.md`

> **All 5 agents must run.** Do not skip fact-check, UX, or authority analysis even under
> context pressure. If context is running low, prioritise completing these agents
> with reduced scope rather than skipping them entirely.

---

### Phase 2: Report Generation (Step 3)

5. **Score** — aggregate findings from `site_data.json` (objective) + agent markdowns
   (qualitative) into SEO Health Score (0-100) using weighted formula.

6. **Generate markdown intermediaries** — before building the HTML report, write:
   - `FULL-AUDIT-REPORT.md` — all findings consolidated by pillar
   - `ACTION-PLAN.md` — prioritised recommendations (Critical > High > Medium > Low)
   - `FACT-CHECK-REPORT.md` — fact-checking results with corrections table
   - `UX-REPORT.md` — UX/UI analysis with accessibility findings
   - `GEO-ANALYSIS.md` — GEO visibility analysis

   These intermediaries serve as a checkpoint that survives context compaction.
   If context is compacted during HTML generation, the markdown files can be
   re-read to reconstruct the report.

7. **Generate HTML report** — build the Localsearch-branded HTML report from
   the markdown findings using `_template/SEO-Audit-Template.html` as reference.

---

### Phase 3: Quality Assurance (MANDATORY) (Step 4)

> **This phase is NOT optional.** Every audit must pass QA before delivery.

8. **Run `seo-validate`** — independently cross-references findings against
   `site_data.json` objective measurements, verifies score calculations, detects
   contradictions between report sections, and confirms recommendations align
   with actual issues found.

9. **Apply verdict:**
   - **PASS** — report is ready for delivery
   - **PASS WITH CORRECTIONS** — apply listed corrections to the HTML report, then deliver
   - **FAIL** — revise the report to fix identified issues, then re-validate

10. **Write validation report** — save `VALIDATION-REPORT.md` with confidence score
    and all verification results.

---

### Phase 4: Delivery (Step 5)

11. **Generate PDF** — always generate a PDF as the final deliverable via Edge headless:
    ```bash
    "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
      --headless --disable-gpu \
      --print-to-pdf="OUTPUT.pdf" \
      --print-to-pdf-no-header \
      "file:///PATH/TO/report.html"
    ```

---

## Platform-Specific Content Extraction

**CRITICAL — Word Count Accuracy:**
The `extract_metadata.py` script handles platform-aware word counting automatically:

- **Duda:** Extracts from `<span style="display: unset">` and `<span style="display: initial">` spans
- **WordPress:** Extracts from `<article>` or `<div class="entry-content">`
- **Other:** Falls back to full body text

The CMS type is auto-detected by `preflight.py` and passed to `extract_metadata.py`.

**Always verify:** Spot-check at least one page's word count from `site_data.json → pages_metadata[].word_count` against the rendered page.

## Duda-Specific Notes

Duda sites often have these quirks that affect auditing:
- **`<title>` tags are JS-rendered** — `extract_metadata.py` automatically falls back to `og:title`
- **CDN blocks non-browser UAs** — `fetch_page.py` handles this with UA rotation
- **Schema is homepage-only** — `validate_schema.py` detects this and flags inner pages

---

## Scripts Reference

### `scripts/build_site_data.py` (main orchestrator)
```bash
"$PYTHON" scripts/build_site_data.py <url> <output_dir> [--max-pages 500] [--skip-cwv] [--skip-screenshots]
```

### `scripts/preflight.py`
```bash
"$PYTHON" scripts/preflight.py <url>
```

### `scripts/fetch_page.py`
```bash
"$PYTHON" scripts/fetch_page.py <url> [output_path] [--timeout 30] [--retries 3]
```

### `scripts/crawl_site.py`
```bash
"$PYTHON" scripts/crawl_site.py <url> <output_dir> [--max-pages 500] [--delay 1.0]
```

### `scripts/extract_metadata.py`
```bash
"$PYTHON" scripts/extract_metadata.py <crawl_dir> --cms <type>
```

### `scripts/validate_schema.py`
```bash
"$PYTHON" scripts/validate_schema.py <crawl_dir>
```

### `scripts/measure_cwv.py`
```bash
"$PYTHON" scripts/measure_cwv.py <url> [url2 ...]
```

### `scripts/validate_sitemap.py`
```bash
"$PYTHON" scripts/validate_sitemap.py <sitemap_url> [--crawl-manifest <path>]
```

### `scripts/check_security.py`
```bash
"$PYTHON" scripts/check_security.py <url>
```

### `scripts/capture_screenshots.py`
```bash
"$PYTHON" scripts/capture_screenshots.py <url> <output_dir>
```

### `scripts/check_gbp.py`
```bash
# By search query:
"$PYTHON" scripts/check_gbp.py "Business Name Suburb State"
# By direct Google Maps URL (most reliable):
"$PYTHON" scripts/check_gbp.py --url "https://www.google.com/maps/place/..."
# By CID:
"$PYTHON" scripts/check_gbp.py --cid 1234567890
```
Uses Playwright to load Google Maps and extract GBP data (rating, review count, address, phone, category, individual reviews). Now called automatically by `build_site_data.py` in Phase 4.

### `scripts/extract_nap.py`
```bash
"$PYTHON" scripts/extract_nap.py <crawl_dir> --site-data <site_data.json>
```
Extracts business NAP (Name, Address, Phone), emails, ABN, and social profile URLs from crawled HTML files. Parses contact pages, footers, schema markup, and external links. Called automatically by `build_site_data.py` in Phase 3.

### `scripts/check_social.py`
```bash
"$PYTHON" scripts/check_social.py --facebook "URL" --instagram "URL" --youtube "URL" --linkedin "URL"
```
Uses Playwright to visit social media profiles and extract public data (followers, posts, bio, address, rating). Handles login walls by falling back to meta tags. Called automatically by `build_site_data.py` in Phase 4.

---

## `site_data.json` Schema

```json
{
  "meta": {"tool_version": "2.0.0", "generated_at": "ISO8601", "url": "...", "domain": "..."},
  "preflight": {
    "reachable": true, "cms": "duda", "status_code": 200, "final_url": "...",
    "robots_txt": {"found": true, "disallow_rules": [...], "ai_crawlers": {...}, "sitemaps": [...]},
    "llms_txt": {"found": false, "url": "..."},
    "sitemap": {"found": true, "url": "...", "url_count": 15},
    "estimated_pages": 12
  },
  "crawl": {"domain": "...", "pages_crawled": 15, "pages": [...]},
  "pages_metadata": [
    {"url": "...", "title": "...", "h1s": [...], "headings": [...], "meta_description": "...",
     "images": [...], "internal_links": [...], "external_links": [...],
     "iframes": [{"src": "...", "type": "youtube|google_map|vimeo|facebook|other", "title": "..."}],
     "videos": [{"src": "...", "poster": "...", "autoplay": false, "controls": true}],
     "jsonld_blocks": [...], "word_count": 450}
  ],
  "schema": {"total_pages": 15, "pages_with_schema": 3, "types_found": {...}, "issues": [...]},
  "sitemap": {"total_urls": 15, "spot_check": [...], "cross_reference": {...}},
  "cwv": {"results": [{"url": "...", "performance_score": 72, "metrics": {...}}]},
  "security": {"https_redirect": {...}, "ssl_certificate": {...}, "security_headers": {...}},
  "screenshots": {"viewports": [...]},
  "nap": {
    "business_name": "...", "addresses_found": [...], "phones_found": [...],
    "emails_found": [...], "abn": "...", "social_profiles": {"facebook": [...], "instagram": [...]},
    "nap_consistency": {"primary_address": "...", "primary_phone": "...", "variations_found": false}
  },
  "gbp": {
    "business_name": "...", "rating": 4.6, "review_count": 104, "address": "...",
    "phone": "...", "category": "...", "reviews": [...]
  },
  "social": {
    "facebook": {"name": "...", "followers": 77, "likes": 32, "status": "active"},
    "instagram": {"username": "...", "followers": 39, "posts": 47, "bio": "...", "status": "active"}
  }
}
```

---

## Crawl Configuration

```
Max pages: 500
Respect robots.txt: Yes
Follow redirects: Yes (max 3 hops, handled by urllib)
Timeout per page: 30 seconds
Concurrent requests: 1 (sequential with delay)
Delay between requests: 1 second
Retries per page: 3 (with UA rotation on 403)
```

## Output Files

All output goes to `reports/<domain>/`:

**Phase 1A — Data collection:**
- `site_data.json` — all objective measurements
- `crawl/` — crawl manifest and HTML files
- `screenshots/` — desktop + mobile captures

**Phase 1B — Agent output (markdown intermediaries):**
- `FULL-AUDIT-REPORT.md` — Comprehensive findings by pillar
- `ACTION-PLAN.md` — Prioritised recommendations (Critical → High → Medium → Low)
- `FACT-CHECK-REPORT.md` — Fact-checking results with corrections table
- `UX-REPORT.md` — UX/UI analysis with accessibility findings
- `GEO-ANALYSIS.md` — GEO visibility analysis
- `AUTHORITY-REPORT.md` — External presence research (GBP, social, directories, reviews)

**Phase 3 — QA output:**
- `VALIDATION-REPORT.md` — Independent QA results with confidence score and verdict

**Phase 4 — Final deliverables:**
- `SEO-Audit-Report.html` — Localsearch-branded HTML report
- `SEO-Audit-Report.pdf` — PDF version

## Scoring Weights

Reports use a **3-pillar structure**. Each pillar has a section score; the overall
SEO Health Score is their weighted aggregate.

| Pillar | Sub-category | Weight | Pillar Total |
|--------|-------------|--------|-------------|
| **1 — Technical Foundation** | Crawlability & Indexability | 15% | **35%** |
| | Performance (Core Web Vitals) | 10% | |
| | Mobile & JavaScript Rendering | 10% | |
| **2 — Content & On-Page** | Content Quality & E-E-A-T | 12% | **40%** |
| | Factual Accuracy & Contextual Relevance | 5% | |
| | On-Page SEO | 8% | |
| | Schema & Structured Data | 6% | |
| | Images & Media | 5% | |
| | UX & Usability | 4% | |
| **3 — Authority & Off-Page** | Backlink Profile & Link Equity | 12% | **25%** |
| | AI Search / GEO Visibility | 8% | |
| | Local & Brand Signals | 5% | |
| **QA (not scored)** | Report Validation | — | — |

> **Note:** Factual Accuracy and UX scores feed into Pillar 2. The Report
> Validation step does not contribute to the Health Score — it validates
> the score itself.

## Report Structure

### Executive Summary
- **Overall SEO Health Score: XX/100**
- Business type detected
- Pillar scores at a glance:
  ```
  Technical Foundation:   XX/100  ████████░░
  Content & On-Page:      XX/100  ██████░░░░
  Authority & Off-Page:   XX/100  █████░░░░░
  ```
- Top 5 critical issues (across all pillars)
- Top 5 quick wins (highest impact / lowest effort)
- Who owns what: Technical (dev team) / Content (writers) / Authority (marketing/outreach)

---

### PILLAR 1 — Technical Foundation

**Pillar Score: XX/100**

#### Crawlability & Indexability
- robots.txt: correct, not blocking key resources
- XML sitemap: valid, submitted, no noindexed/redirected URLs *(from `site_data.json → sitemap`)*
- Indexing status: intended pages indexed, no index bloat
- Canonical tags: self-referencing or correctly pointing *(from `site_data.json → pages_metadata`)*
- Duplicate content: detected and handled
- Redirect health: no chains, 301 vs 302 correct

#### Performance (Core Web Vitals)
*(Direct from `site_data.json → cwv`)*
- LCP: XX.Xs (Good / Needs Improvement / Poor)
- INP: XXXms (estimated from TBT lab proxy)
- CLS: X.XX
- Performance score: XX/100
- Top bottlenecks identified

#### Security
*(Direct from `site_data.json → security`)*
- HTTPS redirect: working/missing
- SSL certificate: valid/expired/issues
- Security headers: HSTS, CSP, X-Frame-Options, etc.

#### Mobile & JavaScript Rendering
- Mobile-first indexing compliance
- Touch targets, font sizes, viewport *(from UX agent)*
- SSR vs CSR: critical SEO elements in initial HTML
- JS rendering blockers: canonical, noindex, schema

---

### PILLAR 2 — Content & On-Page

**Pillar Score: XX/100**

#### Content Quality & E-E-A-T *(from `seo-content` agent)*
- E-E-A-T breakdown: Experience / Expertise / Authoritativeness / Trustworthiness
- Thin content pages (below minimums) *(word counts from `site_data.json`)*
- AI content quality signals
- Content freshness
- AI Citation Readiness score

#### On-Page SEO *(from `site_data.json → pages_metadata`)*
- Title tag issues (length, uniqueness, keyword placement)
- Meta description issues
- Heading structure (H1 count, hierarchy)
- Internal linking gaps and anchor text
- URL structure

#### Schema & Structured Data *(from `site_data.json → schema`)*
- Current implementation detected
- Validation errors
- Missing opportunities by page type
- Deprecated schema in use

#### Images & Media *(from `site_data.json → pages_metadata`)*
- Missing alt text count
- Images without dimensions (CLS risk)
- Lazy loading compliance

#### Factual Accuracy & Contextual Relevance *(from `seo-factcheck` agent)*
- Claims verified: X total (X correct, X incorrect, X unverifiable)
- Critical errors (measurements, statistics, regulatory references)
- Contextual issues (content-page mismatch, template artifacts, terminology misuse)
- Corrections table with sources

#### UX & Usability *(from `seo-ux` agent)*
- Navigation & information architecture assessment
- Visual hierarchy & layout effectiveness
- CTA visibility and conversion path analysis
- Accessibility compliance (WCAG 2.2 Level AA)
- Mobile usability (touch targets, thumb zones, responsive layout)
- UX Score: XX/100

---

### PILLAR 3 — Authority & Off-Page

**Pillar Score: XX/100**

#### Backlink Profile & Link Equity
- Total referring domains
- Domain Rating / authority estimate
- Spam score assessment
- Anchor text distribution
- Link velocity trend
- Top opportunities from competitor gap analysis

#### AI Search / GEO Visibility *(from `seo-geo` agent + `site_data.json`)*
- GEO Readiness Score
- Google AI Overviews citation status
- ChatGPT / Perplexity visibility
- llms.txt presence *(from `site_data.json → preflight.llms_txt`)*
- AI crawler access *(from `site_data.json → preflight.robots_txt.ai_crawlers`)*
- Brand mention signals

#### Local & Brand Signals
- GBP completeness (if local business)
- NAP consistency across directories
- Review profile summary
- Entity presence (Wikipedia, LinkedIn, YouTube)

---

### QUALITY ASSURANCE — Report Validation

> This section is generated by `seo-validate` AFTER the audit is complete.
> It does not contribute to the Health Score — it validates the score.

**Report Confidence Score: XX/100**

| Validation Check | Result |
|-----------------|--------|
| Findings re-verified against site_data.json | X of Y confirmed |
| Score calculations | Consistent / Issues found |
| Contradictions detected | X found |
| Recommendations aligned | Yes / Gaps found |
| Completeness | All areas covered / Gaps found |

**Verdict:** PASS / PASS WITH CORRECTIONS / FAIL

*If corrections were applied, they are noted here.*

---

### Action Plan

All issues from all three pillars combined and re-sorted by business impact:

**Critical** (fix immediately — blocks indexing or causes penalties)
**High** (fix within 1 week — significantly impacts rankings)
**Medium** (fix within 1 month — optimisation opportunity)
**Low** (backlog — nice to have)

Each issue tagged with its pillar (Technical / Content / Authority)
and owner (Dev / Content / Marketing) for easy team distribution.

## Priority Definitions

- **Critical**: Blocks indexing or causes penalties (fix immediately)
- **High**: Significantly impacts rankings (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available, spawn the `seo-dataforseo` agent alongside existing subagents to enrich the audit with live data: real SERP positions, backlink profiles with spam scores, on-page analysis (Lighthouse), business listings, and AI visibility checks (ChatGPT scraper, LLM mentions).
