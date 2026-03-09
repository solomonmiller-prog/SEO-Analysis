---
name: seo-audit
description: >
  Full website SEO audit with parallel subagent delegation. Crawls up to 500
  pages, detects business type, delegates to 7 specialists, generates health
  score. Use when user says "audit", "full SEO check", "full site analysis",
  "analyze my site", "website health check", "site review", "complete SEO
  review", "website audit", "check my website", or "SEO report". Always use
  this skill when a user provides a URL and asks for a comprehensive or full
  analysis — even if they don't use the word "audit" explicitly.
---

# Full Website SEO Audit

## Process

1. **Fetch homepage** — use `scripts/fetch_page.py` to retrieve HTML
2. **Detect business type** — analyze homepage signals per seo orchestrator
3. **Crawl site** — follow internal links up to 500 pages, respect robots.txt
4. **Delegate to subagents** (if available, otherwise run inline sequentially):
   - `seo-technical` — robots.txt, sitemaps, canonicals, Core Web Vitals, security headers
   - `seo-content` — E-E-A-T, readability, thin content, AI citation readiness
   - `seo-schema` — detection, validation, generation recommendations
   - `seo-sitemap` — structure analysis, quality gates, missing pages
   - `seo-performance` — LCP, INP, CLS measurements
   - `seo-visual` — screenshots, mobile testing, above-fold analysis
   - `seo-geo` — AI Overviews, ChatGPT/Perplexity visibility, llms.txt, GEO signals
5. **Score** — aggregate into SEO Health Score (0-100)
6. **Report** — generate prioritized action plan

## Platform-Specific Content Extraction

**CRITICAL — Word Count Accuracy:**
When measuring content depth/thin content, you MUST extract ALL visible text patterns
for the CMS platform in use. Different platforms render body text differently:

- **Duda:** Uses BOTH `<span style="display: unset">` (headings/labels) AND
  `<span style="display: initial">` (body paragraphs, FAQ answers). Grep for both:
  `grep -o '<span[^>]*display: \(unset\|initial\)[^>]*>[^<]*</span>'`
  Failing to include `display: initial` will miss all body content and FAQ text.
- **WordPress:** Extract from `<article>` or `<div class="entry-content">`.
- **Shopify:** Extract from `<div class="rte">` or product containers.

**Always remove shared boilerplate LINES, not a flat word count:** Extract text from
3+ different page types, find lines common to ALL using `comm -12` or `grep -vxF`,
then remove those exact lines before counting words. Do NOT use a flat word deduction
— page-specific headings vary per page and must not be stripped.

**Always verify:** Spot-check at least one page by reading the full extracted text
and confirming it matches what a user would see on the rendered page.

## Crawl Configuration

```
Max pages: 500
Respect robots.txt: Yes
Follow redirects: Yes (max 3 hops)
Timeout per page: 30 seconds
Concurrent requests: 5
Delay between requests: 1 second
```

## Output Files

- `FULL-AUDIT-REPORT.md` — Comprehensive findings
- `ACTION-PLAN.md` — Prioritized recommendations (Critical → High → Medium → Low)
- `screenshots/` — Desktop + mobile captures (if Playwright available)

## Scoring Weights

Reports use a **3-pillar structure**. Each pillar has a section score; the overall
SEO Health Score is their weighted aggregate.

| Pillar | Sub-category | Weight | Pillar Total |
|--------|-------------|--------|-------------|
| **1 — Technical Foundation** | Crawlability & Indexability | 15% | **35%** |
| | Performance (Core Web Vitals) | 10% | |
| | Mobile & JavaScript Rendering | 10% | |
| **2 — Content & On-Page** | Content Quality & E-E-A-T | 15% | **40%** |
| | On-Page SEO | 10% | |
| | Schema & Structured Data | 8% | |
| | Images & Media | 7% | |
| **3 — Authority & Off-Page** | Backlink Profile & Link Equity | 12% | **25%** |
| | AI Search / GEO Visibility | 8% | |
| | Local & Brand Signals | 5% | |

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

### Action Plan

All issues from all three pillars combined and re-sorted by business impact:

**Critical** (fix immediately — blocks indexing or causes penalties)
**High** (fix within 1 week — significantly impacts rankings)
**Medium** (fix within 1 month — optimisation opportunity)
**Low** (backlog — nice to have)

Each issue tagged with its pillar (🔧 Technical / 📝 Content / 🔗 Authority)
and owner (Dev / Content / Marketing) for easy team distribution.

## Priority Definitions

- **Critical**: Blocks indexing or causes penalties (fix immediately)
- **High**: Significantly impacts rankings (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available, spawn the `seo-dataforseo` agent alongside existing subagents to enrich the audit with live data: real SERP positions, backlink profiles with spam scores, on-page analysis (Lighthouse), business listings, and AI visibility checks (ChatGPT scraper, LLM mentions).
