---
name: seo-audit
description: >
  Full website SEO audit with parallel subagent delegation. Crawls up to 500
  pages, detects business type, delegates to 9 specialists (including fact-
  checking and UX analysis), generates health score, then runs independent
  QA validation before delivery. Use when user says "audit", "full SEO check",
  "full site analysis", "analyze my site", "website health check", "site
  review", "complete SEO review", "website audit", "check my website", or
  "SEO report". Always use this skill when a user provides a URL and asks
  for a comprehensive or full analysis — even if they don't use the word
  "audit" explicitly.
---

# Full Website SEO Audit

## Environment Note — Python

On this system, `python` is not in PATH. Use the full path:
```
PYTHON="/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe"
```
All `PYTHON` references in this skill should be replaced with this path when
executing commands. Example:
```bash
"$PYTHON" scripts/fetch_page.py https://example.com /tmp/out.html
```

## Process

### Pre-Flight Checklist (Step 0)

Before spawning any subagents, verify the following. If any check fails,
stop and report the blocker to the user rather than proceeding with partial data.

1. **Site is fetchable** — run `PYTHON scripts/fetch_page.py <url> /tmp/<domain>_home.html`
   and confirm a 200 response. If 403/timeout, retry with alternate UA (the script
   handles this automatically with 3 retries and UA rotation).
2. **CMS / platform detected** — inspect the homepage HTML for platform signatures:
   - Duda: `class="dmBody"`, `FLAVOR: FLAVOR_FLAVOR_FLAVOR`, `dudaone.com` in scripts
   - WordPress: `wp-content/`, `wp-includes/`, `<meta name="generator" content="WordPress"`
   - Shopify: `cdn.shopify.com`, `Shopify.theme`
   - Wix: `wix.com`, `X-Wix-` headers
   - Squarespace: `squarespace.com`, `<meta name="generator" content="Squarespace"`
   - Custom/Other: no known CMS signatures
3. **robots.txt accessible** — fetch `/robots.txt` and note any `Disallow` rules
   that affect crawling. The crawl script handles this automatically.
4. **Page count estimated** — do a quick link extraction from the homepage to estimate
   site size. For small sites (<20 pages), all pages can be fetched individually.
   For larger sites, the crawler will handle discovery.

If all checks pass, proceed to Step 1.

---

### Phase 1: Data Gathering

1. **Crawl site** — run `PYTHON scripts/crawl_site.py <url> /tmp/crawl_<domain> --max-pages 500`
   This produces:
   - `/tmp/crawl_<domain>/crawl_manifest.json` — structured page inventory
   - `/tmp/crawl_<domain>/pages/*.html` — raw HTML for each page
   - `/tmp/crawl_<domain>/robots.txt` — cached robots.txt

2. **Detect business type** — analyze homepage content, schema, and meta tags to
   classify: local service, e-commerce, SaaS, publisher, agency, professional service, etc.

3. **Delegate to subagents** (parallel where possible):
   - `seo-technical` — robots.txt, sitemaps, canonicals, Core Web Vitals, security headers
   - `seo-content` — E-E-A-T, readability, thin content, AI citation readiness
   - `seo-schema` — detection, validation, generation recommendations
   - `seo-sitemap` — structure analysis, quality gates, missing pages
   - `seo-performance` — LCP, INP, CLS measurements
   - `seo-visual` — screenshots, mobile testing, above-fold analysis
   - `seo-geo` — AI Overviews, ChatGPT/Perplexity visibility, llms.txt, GEO signals
   - `seo-factcheck` — **MANDATORY** — verify factual claims, measurements, statistics
   - `seo-ux` — **MANDATORY** — navigation, visual hierarchy, CTAs, accessibility (WCAG 2.2 AA)

   > **All 9 subagents must run.** Do not skip fact-check or UX analysis even under
   > context pressure. If context is running low, prioritise completing these agents
   > with reduced scope rather than skipping them entirely.

4. **Score** — aggregate findings into SEO Health Score (0-100) using weighted formula.

---

### Phase 2: Report Generation

5. **Generate markdown intermediaries** — before building the HTML report, write:
   - `FULL-AUDIT-REPORT.md` — all findings consolidated by pillar
   - `ACTION-PLAN.md` — prioritised recommendations (Critical > High > Medium > Low)
   - `FACT-CHECK-REPORT.md` — fact-checking results with corrections table
   - `UX-REPORT.md` — UX/UI analysis with accessibility findings

   These intermediaries serve as a checkpoint that survives context compaction.
   If context is compacted during HTML generation, the markdown files can be
   re-read to reconstruct the report.

6. **Generate HTML report** — build the Localsearch-branded HTML report from
   the markdown findings using `_template/SEO-Audit-Template.html` as reference.

---

### Phase 3: Quality Assurance (MANDATORY)

> **This phase is NOT optional.** Every audit must pass QA before delivery.

7. **Run `seo-validate`** — independently re-checks a sample of findings against
   the live site, verifies score calculations, detects contradictions between
   report sections, and confirms recommendations align with actual issues found.

8. **Apply verdict:**
   - **PASS** — report is ready for delivery
   - **PASS WITH CORRECTIONS** — apply listed corrections to the HTML report, then deliver
   - **FAIL** — revise the report to fix identified issues, then re-validate

9. **Write validation report** — save `VALIDATION-REPORT.md` with confidence score
   and all verification results.

---

### Phase 4: Delivery

10. **Generate PDF** — always generate a PDF as the final deliverable via Edge headless:
    ```bash
    "/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
      --headless --disable-gpu \
      --print-to-pdf="OUTPUT.pdf" \
      --print-to-pdf-no-header \
      "file:///PATH/TO/report.html"
    ```

## Platform-Specific Content Extraction

**CRITICAL — Word Count Accuracy:**
When measuring content depth/thin content, you MUST extract ALL visible text patterns
for the CMS platform in use. Different platforms render body text differently:

- **Duda:** Uses BOTH `<span style="display: unset">` (headings/labels) AND
  `<span style="display: initial">` (body paragraphs, FAQ answers). Use grep with
  POSIX-compatible syntax (no `-P` flag — it fails on Git Bash/Windows):
  ```bash
  grep -o '<span[^>]*display: \(unset\|initial\)[^>]*>[^<]*</span>' file.html
  ```
  Failing to include `display: initial` will miss all body content and FAQ text.
- **WordPress:** Extract from `<article>` or `<div class="entry-content">`.
- **Shopify:** Extract from `<div class="rte">` or product containers.

**IMPORTANT — grep Compatibility:**
This toolkit runs on Git Bash (Windows). Do NOT use `grep -P` (PCRE mode) — it
fails with "supports only unibyte and UTF-8 locales". Instead:
- Use basic grep: `grep -o 'pattern'` with `\(alt1\|alt2\)` for alternation
- Use extended grep: `grep -oE 'pattern'` with `(alt1|alt2)` for alternation
- For complex patterns, use `python -c` or `sed` instead of grep -P

**Always remove shared boilerplate LINES, not a flat word count:** Extract text from
3+ different page types, find lines common to ALL using `comm -12` or `grep -vxF`,
then remove those exact lines before counting words. Do NOT use a flat word deduction
— page-specific headings vary per page and must not be stripped.

**Always verify:** Spot-check at least one page by reading the full extracted text
and confirming it matches what a user would see on the rendered page.

## Duda-Specific Notes

Duda sites often have these quirks that affect auditing:
- **`<title>` tags are JS-rendered** — empty in source HTML. Extract `og:title`
  meta property content instead, which is server-rendered.
- **WebFetch tool may get 403s** — Duda's CDN blocks non-browser UAs. Use
  `PYTHON scripts/fetch_page.py` or `curl -sL -A "Mozilla/5.0..."` instead.
- **Schema is embedded in `<script type="application/ld+json">`** on homepage
  only in many Duda sites — inner pages typically have zero structured data.

## Scripts

### `scripts/fetch_page.py`
Fetches a single page with browser-like headers, UA rotation, and retry logic.

```bash
# Fetch to file
PYTHON scripts/fetch_page.py https://example.com /tmp/example_home.html

# Fetch to stdout
PYTHON scripts/fetch_page.py https://example.com

# Custom timeout and retries
PYTHON scripts/fetch_page.py https://example.com /tmp/out.html --timeout 15 --retries 5
```

### `scripts/crawl_site.py`
Crawls a website following internal links. Respects robots.txt, deduplicates
URLs, and produces a structured JSON manifest with page metadata.

```bash
# Full crawl (up to 500 pages)
PYTHON scripts/crawl_site.py https://example.com /tmp/crawl_example

# Limited crawl
PYTHON scripts/crawl_site.py https://example.com /tmp/crawl_example --max-pages 50

# Slower crawl (polite mode)
PYTHON scripts/crawl_site.py https://example.com /tmp/crawl_example --delay 2
```

**Output structure:**
```
/tmp/crawl_example/
├── crawl_manifest.json    # Page inventory with metadata
├── robots.txt             # Cached robots.txt
└── pages/
    ├── homepage.html
    ├── about.html
    ├── services.html
    └── ...
```

**Manifest format:**
```json
{
  "domain": "example.com",
  "start_url": "https://example.com",
  "pages_crawled": 15,
  "pages_in_queue": 0,
  "timestamp": "2026-03-10T14:30:00+1100",
  "pages": [
    {
      "url": "https://example.com",
      "final_url": "https://example.com",
      "status": 200,
      "slug": "homepage",
      "file": "/tmp/crawl_example/pages/homepage.html",
      "title": "Example Business",
      "meta_description": "...",
      "h1": ["Welcome to Example"],
      "word_count": 1250,
      "internal_links_found": 12
    }
  ]
}
```

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

**Phase 1 — Markdown intermediaries (checkpoint files):**
- `FULL-AUDIT-REPORT.md` — Comprehensive findings by pillar
- `ACTION-PLAN.md` — Prioritised recommendations (Critical → High → Medium → Low)
- `FACT-CHECK-REPORT.md` — Fact-checking results with corrections table
- `UX-REPORT.md` — UX/UI analysis with accessibility findings
- `GEO-ANALYSIS.md` — GEO visibility analysis
- `visual-analysis.md` — Visual/screenshot analysis
- `screenshots/` — Desktop + mobile captures

**Phase 3 — QA output:**
- `VALIDATION-REPORT.md` — Independent QA results with confidence score and verdict

**Phase 4 — Final deliverables:**
- `SEO-Audit-Report.html` — Localsearch-branded HTML report
- `SEO-Audit-Report.pdf` — PDF version (if requested)

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
- XML sitemap: valid, submitted, no noindexed/redirected URLs
- Indexing status: intended pages indexed, no index bloat
- Canonical tags: self-referencing or correctly pointing
- Duplicate content: detected and handled
- Redirect health: no chains, 301 vs 302 correct

#### Performance (Core Web Vitals)
- LCP: XX.Xs (Good / Needs Improvement / Poor)
- INP: XXXms
- CLS: X.XX
- 75th percentile field data (CrUX)
- Top bottlenecks identified

#### Mobile & JavaScript Rendering
- Mobile-first indexing compliance
- Touch targets, font sizes, viewport
- SSR vs CSR: critical SEO elements in initial HTML
- JS rendering blockers: canonical, noindex, schema

---

### PILLAR 2 — Content & On-Page

**Pillar Score: XX/100**

#### Content Quality & E-E-A-T
- E-E-A-T breakdown: Experience / Expertise / Authoritativeness / Trustworthiness
- Thin content pages (below minimums)
- AI content quality signals
- Content freshness
- AI Citation Readiness score

#### On-Page SEO
- Title tag issues (length, uniqueness, keyword placement)
- Meta description issues
- Heading structure (H1 count, hierarchy)
- Internal linking gaps and anchor text
- URL structure

#### Schema & Structured Data
- Current implementation detected
- Validation errors
- Missing opportunities by page type
- Deprecated schema in use

#### Images & Media
- Missing alt text count
- Oversized images
- Format opportunities (WebP/AVIF)
- CLS-causing images (no dimensions)
- Lazy loading compliance

#### Factual Accuracy & Contextual Relevance
- Claims verified: X total (X correct, X incorrect, X unverifiable)
- Critical errors (measurements, statistics, regulatory references)
- Contextual issues (content-page mismatch, template artifacts, terminology misuse)
- Corrections table with sources

#### UX & Usability
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

#### AI Search / GEO Visibility
- GEO Readiness Score
- Google AI Overviews citation status
- ChatGPT / Perplexity visibility
- llms.txt presence
- AI crawler access in robots.txt
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
| Findings re-verified | X of Y confirmed |
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
