---
name: seo-gsc
description: >
  Google Search Console analysis, diagnosis, and action planning. Covers
  Search Analytics interpretation, indexing issues, coverage errors, Core
  Web Vitals reports, manual actions, sitemap submissions, and CTR optimisation.
  Use when user says "Google Search Console", "GSC", "Search Console",
  "search performance", "impressions dropping", "clicks dropping",
  "indexed pages", "coverage errors", "crawl errors", "not indexed",
  "manual action", "search appearance", "CTR optimisation", "ranking drop
  diagnosis", "organic traffic dropped", "Search Console data",
  "search analytics", "impressions vs clicks", "page experience report",
  "sitemap submitted", "URL inspection tool", or "Google indexing issues".
  Also use whenever a user shares Search Console screenshots or data
  and wants help interpreting what they mean.
---

# Google Search Console Analysis & Diagnosis

GSC is the primary diagnostic tool for SEO. It provides first-party data
directly from Google on how your site is crawled, indexed, and ranked.

> **Data lag**: GSC data has a 2-3 day processing lag. Recent changes won't
> be visible immediately. Use "Last 3 months" or "Last 16 months" for trend
> analysis; use "Last 7 days" only for very recent monitoring.

---

## 1. Search Performance Report (Search Analytics)

**Location:** Performance > Search results

### Core Metrics

| Metric | Definition | Good Use For |
|--------|------------|-------------|
| Total clicks | Users who clicked your result | Traffic measurement |
| Total impressions | Times your result was shown | Visibility measurement |
| Average CTR | Clicks ÷ impressions | Optimisation opportunity |
| Average position | Mean ranking across queries | Ranking health |

### Critical Analysis Patterns

**Pattern 1: High impressions, low CTR**
- You're ranking but not getting clicked
- Check: title tags and meta descriptions are weak or not compelling
- Benchmark CTR by position: P1=~28%, P2=~15%, P3=~11%, P4-7=~5-6%, P8-10=~3-4%
- Any page with CTR significantly below position benchmark → title/meta rewrite
- Also check: SERP features (featured snippets, ads) eating clicks above you

**Pattern 2: Good CTR, declining clicks**
- Your pages are compelling but ranking is dropping
- Check: algorithm update timeline (correlate with Google algorithm update history)
- Check: E-E-A-T signals, content freshness, competitor content improvements
- Compare position graph with traffic graph — they should move together

**Pattern 3: Impressions stable, clicks dropping**
- Position declining OR SERP layout changing (more ads, AI Overviews, PAA boxes)
- Impressions reflect visibility; clicks reflect whether users choose your result
- Check if AI Overviews are now appearing for your key queries

**Pattern 4: Zero impressions on key pages**
- Page not indexed, canonical issue, or noindex tag
- Run URL Inspection tool immediately (see Section 4)

### Segmentation Workflows

Always segment data before drawing conclusions:

```
By Device:
- Mobile vs Desktop CTR gaps → mobile title/meta optimisation needed
- Mobile impressions >> Desktop → ensure mobile-first experience

By Country:
- Traffic spike/drop in specific country → geo-specific issue or opportunity
- Unintended ranking in irrelevant markets → hreflang fix needed

By Search Type:
- "Web" vs "Image" vs "Video" vs "News" → each has separate optimisation
- Unexpected image traffic → image SEO opportunity
- Missing news traffic (publisher) → Google News inclusion issue

By Date (compare periods):
- Month-over-month: seasonal patterns vs genuine changes
- Pre/post: isolate impact of a specific change or update
```

### CTR Optimisation Workflow
1. Filter to pages with >500 impressions and CTR below position benchmark
2. Sort by "impressions" descending — prioritise by volume
3. For each: read the title tag, meta description, and top 5 queries driving impressions
4. Check live SERP for those queries — what do top results look like?
5. Rewrite title/meta to: match search intent, include primary keyword near start, add a differentiator
6. Re-check in 4-6 weeks for CTR improvement

---

## 2. Coverage / Indexing Report

**Location:** Indexing > Pages

### Status Categories Explained

**Valid (indexed)**
- These pages are in Google's index — all good
- Check: is the count what you'd expect? Unexpectedly high = index bloat

**Valid with warnings**
- Common: "Indexed, though blocked by robots.txt" — Google found the page via links but your robots.txt tries to block it. Decision: allow or noindex properly?
- "Submitted in sitemap but indexed as a different URL" → canonical or redirect issue

**Excluded (not indexed — these need investigation)**

| Reason | What it means | What to do |
|--------|--------------|------------|
| Crawled - currently not indexed | Google crawled it but chose not to index | Improve content quality; check thin/duplicate content |
| Discovered - currently not indexed | In queue but not yet crawled | Improve internal links and submit URL |
| Duplicate without canonical | Google detected a duplicate and chose a different URL | Add canonical tags |
| Canonical URL set by user | Your canonical tag points elsewhere (intentional or bug?) | Verify canonical logic |
| Redirect | Page is a redirect (correct if intentional) | Ensure redirect chain isn't causing issues |
| Not found (404) | Page returns 404 — Google found a link but no page | Fix or redirect |
| Soft 404 | Returns 200 but content appears to be a 404 | Fix the page or return proper 404 |
| Blocked by robots.txt | robots.txt disallows Googlebot | Is this intentional? |
| Noindex | noindex tag present | Is this intentional? |
| Page with redirect | Google found the URL but it redirects | Check destination is appropriate |

### Crawl Budget Considerations

For large sites (>10,000 pages), crawl budget matters:
- High volume of "Discovered - not indexed" = Google not crawling fast enough
- Fix: improve internal linking, reduce noindexed URLs, speed up server, submit sitemap
- Remove low-value pages (thin content, old promos, duplicate variants) from index

---

## 3. Core Web Vitals Report

**Location:** Experience > Core Web Vitals

### Reading the Report
- Separate reports for Mobile and Desktop
- Status: Good (green) / Needs Improvement (orange) / Poor (red)
- Google uses field data (CrUX) — real user measurements, not lab simulations
- Threshold: 75% of page visits must meet "Good" threshold per metric

### Grouping Logic
GSC groups pages with similar URL patterns (e.g., all `/blog/` URLs grouped).
A single slow page template can flag thousands of pages. To diagnose:
1. Click into a failing group
2. Open example URLs
3. Run those specific URLs in PageSpeed Insights for detailed breakdown

### Common CWV Failure Patterns

**LCP failures on all pages:** Usually server TTFB or render-blocking resources — fix affects the whole site
**LCP failures on specific templates:** Usually that template has an unoptimised hero image
**CLS failures on mobile only:** Usually ads/embeds without reserved space or injected banners
**INP failures:** Usually heavy JavaScript — often third-party scripts (chat widgets, tag managers)

Cross-reference `seo/references/cwv-thresholds.md` for full threshold values and fix recommendations.

---

## 4. URL Inspection Tool

**Location:** Search > URL Inspection (or enter any URL in the top search bar)

### When to Use
- A page isn't appearing in search despite being live
- You've made an important change and want Google to recrawl
- You suspect a noindex, canonical, or robots.txt issue

### What to Check
1. **Indexing status** — "URL is on Google" or not
2. **Last crawl date** — if >30 days ago, internal linking or crawl budget issue
3. **Crawled as** — should show Googlebot Smartphone (mobile-first indexing)
4. **Referring page** — how Google found the URL (useful for orphan detection)
5. **Canonical** — "User-declared" vs "Google-selected" — if they differ, Google disagrees with your canonical
6. **Page fetch** — can Google render the page? If not, JS rendering issue

### Request Indexing
- After fixing a critical page, use "Request Indexing" to prioritise recrawl
- Has a daily quota — don't use for bulk submissions; use sitemap for that
- Not a guarantee — Google still decides whether to index

---

## 5. Manual Actions Report

**Location:** Security & Manual Actions > Manual Actions

### If You Have a Manual Action
This is serious — a Google employee has reviewed your site and penalised it.

| Action Type | Common Cause | Recovery |
|-------------|-------------|---------|
| Unnatural links to your site | Purchased or scheme links | Disavow + reconsideration request |
| Unnatural links from your site | Outbound paid links | Remove links + reconsideration |
| Thin content | Scraped, AI-generated, or very thin pages | Improve or remove content |
| Cloaking / sneaky redirects | Showing different content to Google vs users | Fix and reconsideration |
| Spammy structured data | Schema markup misrepresenting content | Fix markup |
| Site reputation abuse | Third-party content on high-authority domain | Remove or isolate content |

### Reconsideration Request Process
1. Fix ALL instances of the issue — not just some
2. Document what you found and what you did
3. Submit reconsideration request in GSC
4. Response time: 2-8 weeks
5. If rejected: the message will explain what's still unresolved

---

## 6. Sitemaps Report

**Location:** Indexing > Sitemaps

### What to Check
- Is your sitemap submitted?
- Is the submitted URL returning a 200 status?
- Submitted count vs indexed count: large gap = indexing issues (not unusual — Google won't index all pages)
- Errors: XML format issues, URLs returning non-200 status, blocked by robots.txt

### Sitemap Best Practices
- Update `<lastmod>` dates accurately — don't set all pages to today's date (GSC ignores this signal if identical)
- Remove noindexed URLs from sitemap
- Remove 301-redirected URLs from sitemap (include final destination URL instead)
- Split at 50,000 URLs per file; use sitemap index for larger sites
- Re-submit sitemap after major content updates

---

## 7. Ranking Drop Diagnosis Workflow

When organic traffic or rankings drop, follow this sequence:

### Step 1: Quantify the Drop
- GSC Performance report: compare affected period vs prior period
- Which queries lost impressions? Which pages lost clicks?
- Is the drop broad (site-wide) or narrow (specific pages/topic)?

### Step 2: Correlate with External Events
- Check Google algorithm update timeline (Google Search Status Dashboard)
- Did the drop coincide with an update? Which type?
- Core update → E-E-A-T and content quality issues
- Spam update → link profile or policy violations
- HCU-style signals → content helpfulness

### Step 3: Check Technical Issues
- Coverage report: any new "Excluded" pages?
- Was robots.txt changed recently? (check version history in your CMS/repo)
- Did any canonical tags change?
- Was a noindex accidentally deployed?
- URL Inspection on top affected pages

### Step 4: Check External Factors
- Did competitors improve their content on affected topics?
- Did Google add SERP features (AI Overviews, shopping ads) that reduce CTR?
- Seasonality? (compare to same period last year)

### Step 5: Identify Root Cause and Prioritise Fix
| Finding | Action |
|---------|--------|
| Technical issue (noindex, robots.txt) | Fix immediately, re-submit URLs |
| Content quality decline | E-E-A-T audit, content refresh |
| Core update (content quality) | Review affected pages vs QRG standards |
| Spam update (links) | Backlink audit, disavow if needed |
| SERP feature cannibalism | Optimise for featured snippet/AI Overview or accept lower CTR |
| Competitor content improvement | Identify gaps, refresh and deepen content |

---

## 8. 2025-2026 GSC Updates

- **Hourly data in API** (December 2025) — real-time monitoring now possible via API
- **Branded vs non-branded filter** (December 2025) — split branded queries from non-branded to get a cleaner view of organic acquisition health
- **Custom chart annotations** (December 2025) — mark algorithm updates, site changes on performance charts
- **Social channels tracking** (December 2025) — track referral traffic from social platforms in GSC
- **AI-powered configuration suggestions** (December 2025) — automated recommendations for site setup issues

---

## Output

> 🔧 **This skill primarily contributes to Pillar 1 — Technical Foundation**
> in the 3-pillar SEO report. GSC data informs Crawlability & Indexability
> and Performance sub-categories. CTR optimisation findings also feed into
> Pillar 2 — Content & On-Page (On-Page SEO sub-category).

### GSC Health Report
- `GSC-ANALYSIS.md` — full findings across all report sections
- **Performance summary**: top opportunities by CTR gap, impression volume
- **Indexing summary**: breakdown of excluded pages with priority actions
- **CWV summary**: failing groups with fix recommendations
- **Manual actions**: status and remediation plan if applicable
- **Priority action list**: top 10 recommendations sorted by estimated impact
