---
name: seo-page
description: >
  Deep single-page SEO analysis covering on-page elements, content quality,
  technical meta tags, schema, images, and performance. Use when user says
  "analyze this page", "check page SEO", "on-page SEO", "page audit",
  "page analysis", "check my page", "meta tags", "title tag", "meta description",
  "check this URL", "review this page", "optimize this page", "page score",
  "single page check", or provides a single URL and asks what's wrong or
  how to improve it. Use this skill for any single-URL SEO review task.
---

# Single Page Analysis

## What to Analyze

### On-Page SEO
- Title tag: 50-60 characters, includes primary keyword, unique
- Meta description: 150-160 characters, compelling, includes keyword
- H1: exactly one, matches page intent, includes keyword
- H2-H6: logical hierarchy (no skipped levels), descriptive
- URL: short, descriptive, hyphenated, no parameters
- Internal links: sufficient, relevant anchor text, no orphan pages
- External links: to authoritative sources, reasonable count

### Content Quality
- Word count vs page type minimums (see quality-gates.md)
- Readability: Flesch Reading Ease score, grade level
- Keyword density: natural (1-3%), semantic variations present
- E-E-A-T signals: author bio, credentials, first-hand experience markers
- Content freshness: publication date, last updated date

### Technical Elements
- Canonical tag: present, self-referencing or correct
- Meta robots: index/follow unless intentionally blocked
- Open Graph: og:title, og:description, og:image, og:url
- Twitter Card: twitter:card, twitter:title, twitter:description
- Hreflang: if multi-language, correct implementation

### Schema Markup
- Detect all types (JSON-LD preferred)
- Validate required properties
- Identify missing opportunities
- NEVER recommend HowTo (deprecated) or FAQ (restricted to gov/health)

### Images
- Alt text: present, descriptive, includes keywords where natural
- File size: flag >200KB (warning), >500KB (critical)
- Format: recommend WebP/AVIF over JPEG/PNG
- Dimensions: width/height set for CLS prevention
- Lazy loading: loading="lazy" on below-fold images

### Core Web Vitals (reference only — not measurable from HTML alone)
- Flag potential LCP issues (huge hero images, render-blocking resources)
- Flag potential INP issues (heavy JS, no async/defer)
- Flag potential CLS issues (missing image dimensions, injected content)

### GEO / AI Citation Readiness
- Does the page have a clear, quotable definition or answer in the first 60 words?
- Are there self-contained answer blocks of 134-167 words?
- Does the page have question-based H2/H3 headings?
- Are statistics cited with sources?
- Is the author identified with credentials?
- Is server-side rendering used (content visible in raw HTML)?
- See `seo-geo` skill for full GEO analysis workflow.

## Output

### Page Score Card

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Overall Page Score: XX/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  🔧 TECHNICAL FOUNDATION         XX/100
  ────────────────────────────────────────
  Crawlability / Indexability    XX/100  ████████░░
  Performance (CWV flags)        XX/100  ██████░░░░
  Mobile & JS Rendering          XX/100  █████████░

  📝 CONTENT & ON-PAGE            XX/100
  ────────────────────────────────────────
  Content Quality & E-E-A-T      XX/100  ████████░░
  On-Page SEO                    XX/100  ███████░░░
  Schema & Structured Data       XX/100  █████░░░░░
  Images & Media                 XX/100  ████████░░
  AI Citation Readiness          XX/100  ██████░░░░

  🔗 AUTHORITY SIGNALS            XX/100
  ────────────────────────────────────────
  (On-page visible signals only)
  Backlink indicators            XX/100  ███░░░░░░░
  GEO / AI citation signals      XX/100  ████░░░░░░

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

> **Note:** Authority score reflects only on-page visible signals (schema entity
> links, author attribution, outbound citations). Full backlink and off-page
> authority assessment requires the `seo-links` and `seo-geo` skills.

### Issues Found
Organised by priority — each tagged with pillar:
🔧 Technical / 📝 Content / 🔗 Authority

**Critical** → **High** → **Medium** → **Low**

### Recommendations
Specific, actionable improvements with expected impact and owner (Dev / Content / Marketing)

### Schema Suggestions
Ready-to-use JSON-LD code for detected opportunities

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available, use `serp_organic_live_advanced` for real SERP positions and `backlinks_summary` for backlink data and spam scores.
