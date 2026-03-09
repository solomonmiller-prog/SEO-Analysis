---
name: seo-migration
description: >
  Site migration planning, execution, and post-migration recovery for SEO.
  Covers domain migrations, URL restructures, HTTPS upgrades, CMS changes,
  subdomain consolidations, and international restructures. Use when user
  says "site migration", "domain migration", "moving domains", "changing URLs",
  "new domain", "rebranding", "URL restructure", "moving to HTTPS",
  "changing CMS", "migrating to WordPress", "migrating to Shopify",
  "subdomain to subfolder", "redesign SEO", "website redesign", "site move",
  "301 redirects", "redirect mapping", "migration checklist",
  "traffic dropped after redesign", "rankings dropped after move",
  "lost rankings after migration", or "website rebuild SEO".
  Always use this skill before a major website change — prevention is
  far easier than recovery.
---

# Site Migration — SEO Planning, Execution & Recovery

Site migrations are the highest-risk SEO event. Done right, they're
transparent to Google. Done wrong, they can wipe out years of rankings.
This skill covers all migration types with pre, during, and post checklists.

---

## Migration Types

| Type | Risk Level | Timeline to Stability |
|------|------------|----------------------|
| HTTPS upgrade (HTTP→HTTPS) | Low | 2-4 weeks |
| CMS change (same URLs) | Low-Medium | 4-8 weeks |
| URL restructure (same domain) | Medium | 6-12 weeks |
| Domain migration (new domain) | High | 3-6 months |
| Subdomain → subfolder consolidation | Medium-High | 8-16 weeks |
| Site merger / acquisition | Very High | 6-12 months |
| International restructure | High | 3-6 months |

> **General principle**: The more URLs that change, the more risk. Maintain as
> many URLs as possible. Every redirect is a small tax on link equity and crawl budget.

---

## Phase 1: Pre-Migration Audit (Do Before Anything)

### Baseline Data Collection — CRITICAL
Document all of this before making any changes. You need a snapshot to compare against.

- [ ] Export all indexed URLs from GSC (Indexing > Pages > Export)
- [ ] Export top 500 pages by organic traffic from GSC (Performance > Pages)
- [ ] Export all ranking keywords for top pages (use DataForSEO `dataforseo_labs_google_ranked_keywords` or Ahrefs)
- [ ] Export all backlinks pointing to the site (DataForSEO `backlinks_backlinks` or Ahrefs)
- [ ] Document current Core Web Vitals scores (GSC Experience report)
- [ ] Screenshot current ranking positions for top 50 keywords
- [ ] Record current organic traffic metrics (monthly average)
- [ ] Crawl the entire current site (Screaming Frog or equivalent) — save the full export

### URL Inventory
From the crawl export, create a spreadsheet with:
- All current URLs
- HTTP status codes
- Page titles and H1s
- Word count
- Inbound internal links count
- Organic traffic (from GSC merge)
- Backlinks (from backlink tool merge)

This becomes the basis for redirect mapping.

### Priority Tier Classification
Classify all URLs before mapping redirects:

| Tier | Criteria | Priority |
|------|----------|----------|
| P1 | Gets organic traffic OR has backlinks | Must redirect, top priority |
| P2 | Has internal links but no traffic/backlinks | Should redirect |
| P3 | Thin/low-value pages | Evaluate: redirect, consolidate, or remove |
| P4 | Duplicate URLs, paginated pages, facets | May not need redirects |

---

## Phase 2: Redirect Mapping

### Rules for Redirect Mapping
- Every P1 and P2 URL must have a redirect destination
- Map to the **most topically relevant** new URL — not just the homepage
- Redirect to homepage only as a last resort (significantly dilutes link equity signal)
- No redirect chains — all redirects must resolve in 1 hop
- 301 for permanent moves, 302 only if truly temporary (rare)
- Validate redirect map before go-live: check every destination URL exists in new site

### Redirect Map Template
```
Old URL | New URL | Redirect Type | Notes
/old-page | /new-page | 301 | Direct equivalent
/old-category/old-product | /new-category/new-product | 301 | Restructured URL
/no-equivalent-page | /closest-topic-page | 301 | Best available destination
/thin-content-page | /parent-page | 301 | Consolidating into parent
```

### Common Redirect Mistakes
| Mistake | Impact |
|---------|--------|
| Redirect to homepage instead of equivalent page | Massive link equity dilution |
| Redirect chains (A→B→C) | Equity lost at each hop; slow crawl |
| 302 instead of 301 | Google may not transfer equity |
| Missing redirects for backlinked URLs | Direct link equity loss |
| Redirecting to 404 destination | Broken redirect — worse than none |
| Forgetting image/asset URLs | Broken images on external sites |

---

## Phase 3: Pre-Launch Technical Checklist

### On Staging (Before Going Live)
- [ ] Verify all redirects work correctly on staging — spot check P1 URLs manually
- [ ] Confirm new site is blocked by robots.txt on staging (`User-agent: * / Disallow: /`)
- [ ] Verify canonical tags are set correctly on all new URLs
- [ ] Check for accidental noindex tags on staging
- [ ] Validate structured data on key page templates (Rich Results Test)
- [ ] Test all critical forms, checkout, login flows
- [ ] Verify meta robots on staging says "noindex" (prevent staging crawl)
- [ ] Test on mobile viewport — all pages responsive
- [ ] Verify hreflang implementation if international site
- [ ] Test XML sitemap loads on staging

### If Domain Migration:
- [ ] Prepare new sitemap with all new URLs
- [ ] Set up Google Search Console for new domain
- [ ] Prepare GSC domain migration tool notification
- [ ] Update Google Analytics property with new domain
- [ ] Prepare to update backlinks to new domain (reach out to major link sources)

---

## Phase 4: Go-Live Checklist

### Immediately After Launch
- [ ] Verify all 301 redirects are live — spot check top 20 P1 URLs
- [ ] Confirm staging robots.txt block is removed from production
- [ ] Confirm no noindex tags accidentally deployed on production
- [ ] Submit new sitemap in GSC
- [ ] For domain migrations: use GSC "Change of Address" tool (Settings > Change of Address)
- [ ] Fetch and render homepage in GSC URL Inspection — verify Googlebot can render
- [ ] Check server response times under load (migration often involves infrastructure changes)
- [ ] Monitor 404 errors in real-time via server logs or Cloudflare
- [ ] Verify SSL certificate is valid if HTTPS change
- [ ] Test payment flows and critical conversion paths

### Change of Address Tool (Domain Migrations Only)
GSC has a dedicated Change of Address tool that signals to Google your domain has moved.
- Set up the new domain in GSC first and verify ownership
- Use the tool from the OLD domain's GSC property
- This accelerates Google's recognition of the migration
- Must have proper 301 redirects in place first

---

## Phase 5: Post-Migration Monitoring

### Week 1-2
- Check GSC Coverage report daily for new errors
- Monitor 404 rate in server logs or Cloudflare analytics
- Check crawl rate — should increase as Google recrawls redirects
- Monitor organic traffic daily — expect some volatility, not a cliff

### Week 3-8
- Compare ranking positions to pre-migration baseline (weekly)
- GSC Performance: impressions and clicks should stabilise and recover
- Coverage report: indexed count should stabilise close to pre-migration levels
- Check for redirect chains (if any were created accidentally)

### Month 3-6 (Domain Migrations)
- Full link equity transfer typically takes 3-6 months for Google to recalibrate
- Monitor backlink acquisition to new domain — major sources may not auto-redirect their links
- Proactively reach out to top 20 backlink sources to update their links to new domain

### What's Normal vs Concerning

| Observation | Normal | Concerning |
|-------------|--------|------------|
| Traffic dip first 2 weeks | 10-20% | >40% |
| Ranking volatility first 4 weeks | Yes | Persistent decline beyond 6 weeks |
| Indexed pages drop initially | 5-15% | >30% |
| New 404 errors in GSC | Some | Hundreds of P1 URLs returning 404 |
| Recovery timeline (URL restructure) | 6-12 weeks | Not recovering after 16 weeks |
| Recovery timeline (domain migration) | 3-6 months | Not recovering after 6 months |

---

## Phase 6: Traffic Recovery

If traffic hasn't recovered within expected timeline:

### Diagnosis Tree

```
Traffic not recovering →

Is it all pages or specific pages?
  → All pages: Technical issue (check robots.txt, noindex, GSC Coverage)
  → Specific pages: Content or redirect mapping issue

Are the affected pages indexed?
  → Not indexed: URL Inspection → find the block
  → Indexed: Ranking issue, not indexing issue

Are rankings lower on the same keywords?
  → Yes: Content quality or E-E-A-T issue (or competitor improved)
  → No impressions: Keyword mapping changed, or topic not targeted by new content

Do the old URLs redirect correctly?
  → No: Fix redirects immediately
  → Yes: Check redirect destination relevance
```

### Common Recovery Fixes
1. **Missed redirects on P1 URLs** — add immediately, submit URLs for recrawl
2. **Redirect to homepage** — remap to topically relevant page
3. **New site has thinner content** — redesigns often strip content; add it back
4. **Structured data not transferred** — re-implement schema on new templates
5. **New CMS changed canonical URLs** — audit and fix canonical tags
6. **Internal link structure degraded** — redesigns often break internal linking; audit and rebuild

---

## Quick Reference: Migration Checklist Card

```
PRE-LAUNCH
□ Baseline data captured (GSC export, rankings, backlinks)
□ Full site crawl completed and saved
□ All P1 URLs identified (traffic + backlinks)
□ Redirect map created and validated
□ Staging verified: correct redirects, robots.txt blocking

GO-LIVE
□ Redirects live and tested
□ Staging block removed
□ New sitemap submitted
□ Change of address tool used (domain migrations)
□ Monitoring dashboards active

POST-LAUNCH MONITORING
□ Day 1: 404 errors, redirect spot checks
□ Week 1: GSC Coverage daily
□ Week 2-4: Rankings vs baseline weekly
□ Month 2-3: Full recovery assessment
```

---

## Output

> 🔧 **This skill contributes to Pillar 1 — Technical Foundation** in the
> 3-pillar SEO report. Migration health directly impacts Crawlability &
> Indexability. A clean migration preserves existing scores; a bad migration
> can collapse all three pillars simultaneously.

### Pre-Migration
- `MIGRATION-PLAN.md` — full plan with timeline and responsibilities
- `REDIRECT-MAP.csv` — complete URL mapping spreadsheet
- `PRE-MIGRATION-BASELINE.md` — documented snapshot for comparison

### Post-Migration
- `MIGRATION-HEALTH-REPORT.md` — status across all monitoring dimensions
- `404-REPORT.csv` — unresolved 404s with fix recommendations
- `RECOVERY-PLAN.md` — if traffic hasn't recovered, root cause and fixes

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available:
- `dataforseo_labs_google_ranked_keywords` — pre-migration keyword baseline
- `backlinks_backlinks` — identify P1 URLs by backlink count
- `backlinks_bulk_new_lost_backlinks` — monitor link equity transfer post-migration
- `on_page_instant_pages` — crawl new site post-migration for technical validation
- `serp_organic_live_advanced` — verify ranking positions for key terms post-migration
