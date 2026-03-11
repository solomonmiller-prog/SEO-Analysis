---
name: seo-local
description: >
  Local SEO strategy and audit covering Google Business Profile optimisation,
  local pack ranking factors, citation building, NAP consistency, review
  management, Google Maps ranking, and local schema. Use when user says
  "local SEO", "Google Business Profile", "GBP", "Google Maps ranking",
  "local pack", "3-pack", "map pack", "not showing in local search",
  "local citations", "NAP consistency", "review strategy", "local listings",
  "near me ranking", "local search", "Google My Business", "GMB",
  "service area business", "multi-location SEO", "local keyword research",
  or "how do I rank in my city". Always use this skill for any SEO task
  involving a business that serves customers in specific geographic locations.
---

# Local SEO — Google Business Profile & Local Pack Optimisation

Local SEO is distinct from traditional organic SEO. The local pack (Google Maps
3-pack) is driven by a separate algorithm with different ranking signals.
This skill covers both local pack ranking and organic local landing pages.

## GBP Data Extraction

Google Maps is fully JS-rendered — standard HTTP fetching cannot access review counts, ratings, or listing details. Use the Playwright-based script:

```bash
PYTHON="/c/Users/smiller/AppData/Local/Programs/Python/Python312/python.exe"

# By direct Google Maps place URL (most reliable):
"$PYTHON" scripts/check_gbp.py --url "https://www.google.com/maps/place/..."

# By search query:
"$PYTHON" scripts/check_gbp.py "Business Name Suburb State"
```

**Output:** JSON with `business_name`, `rating`, `review_count`, `address`, `phone`, `website`, `category`, `reviews[]`.

**Tip:** Find the Google Maps place URL first via WebSearch (`"business name" "suburb" site:google.com/maps`), then pass it with `--url` for reliable extraction.

## Local Pack vs Organic: Two Separate Systems

| Factor | Local Pack (Maps) | Local Organic |
|--------|------------------|---------------|
| Primary signals | Relevance, Proximity, Prominence | Standard SEO signals |
| Profile required | Google Business Profile | Optional but helpful |
| Key data source | GBP, citations, reviews | On-page content, links |
| Radius affected by | Searcher location, density | Less location-dependent |
| Tools to track | Local Falcon, BrightLocal | Search Console, Ahrefs |

---

## 1. Google Business Profile Audit

### Profile Completeness Checklist
- [ ] Business name matches legal/signage exactly (no keyword stuffing)
- [ ] Primary category is the most specific available
- [ ] Secondary categories added for all offered services
- [ ] Address: correct, formatted consistently, matches website
- [ ] Service area: specific cities/postcodes only — NOT entire states/countries (June 2025 policy)
- [ ] Hours: accurate and up to date (critical ranking signal — Whitespark 2026)
- [ ] Phone: local number preferred over national 1-800
- [ ] Website URL: points to most relevant landing page
- [ ] Description: 750 character max, includes primary keyword naturally, no URLs
- [ ] Services list: all major services added with descriptions
- [ ] Products: added if applicable
- [ ] Attributes: all relevant attributes ticked (women-led, outdoor seating, etc.)
- [ ] Photos: minimum 10, ideally 25+ (interior, exterior, team, work samples)
- [ ] Videos: at least 1 (30s+, showing business or work)
- [ ] Opening date set

### GBP 2025-2026 Changes
- **Video verification** is now standard — postcard verification largely phased out. Prepare for a short video showing the physical location or service area work.
- **WhatsApp integration** replaced Google Business Chat (deprecated). Connect WhatsApp for messaging if relevant market.
- **Q&A removed from Maps** — replaced by AI-generated answers sourced from GBP description, services, and website FAQ. Ensure these are comprehensive.
- **Review Stories** — Google Maps shows review snippets in a swipeable Stories format on mobile. Encourage detailed reviews with photos.
- **Business hours are now a top-5 local ranking factor** (Whitespark 2026 Local Search Ranking Factors). Keep hours accurate; consider extending hours if feasible and competitive.

### Common GBP Violations to Avoid
| Violation | Risk |
|-----------|------|
| Keyword stuffing in business name | Suspension |
| PO Box or virtual office address | Suspension |
| Multiple listings for same location | Suspension |
| Fake reviews | Suspension + Google penalty |
| Listing for a location without a physical presence | Suspension |
| Service area covering entire states | Listing edited by Google |

---

## 2. Local Pack Ranking Factors (2026)

Based on Whitespark 2026 Local Search Ranking Factors Report:

### Top Proximity & Relevance Signals
1. Physical address proximity to searcher
2. Primary GBP category relevance
3. Business is open at time of search
4. Keyword relevance across GBP (name, categories, services, description)
5. Review quantity and recency

### Top Prominence Signals
6. Overall star rating (aim for 4.0+; 4.3-4.7 is the optimal perceived trust range)
7. Review response rate and quality
8. Number of high-quality photo uploads
9. Presence on curated "best of" lists and directories
10. Domain authority of linked website
11. Citation volume and consistency across directories
12. Google Posts activity (recency and frequency)

### Negative Signals
- Incomplete GBP profile
- Outdated or incorrect hours
- Unresolved negative reviews
- NAP inconsistencies across the web
- No website linked or website has technical errors
- Address in wrong location on Maps (request edit)

---

## 3. NAP Consistency Audit

NAP = Name, Address, Phone. Inconsistencies across directories confuse Google
and reduce local pack ranking confidence.

### Audit Process
1. Record the canonical NAP from the GBP as the source of truth
2. Check top directories: Google, Bing Places, Apple Maps, Yelp, Facebook, Yellow Pages, Foursquare, TripAdvisor (if applicable), industry-specific directories
3. Flag any variations in: business name (abbreviations, old names), address format (St vs Street, Suite vs Ste), phone format
4. Check for duplicate listings — merge or remove

### Priority Citation Sources
| Tier | Sources |
|------|---------|
| Tier 1 (critical) | Google Business Profile, Bing Places, Apple Maps, Facebook Business, Yelp |
| Tier 2 (high value) | Yellow Pages, Foursquare, BBB, Chamber of Commerce, industry associations |
| Tier 3 (supporting) | Data aggregators: Neustar Localeze, Data Axle, Factual/Foursquare (feeds 100s of directories) |
| Industry-specific | TripAdvisor (hospitality), Houzz (home services), Healthgrades (medical), Avvo (legal), Angi/HomeAdvisor (contractors) |

### Schema for NAP Consistency
Every location page must include LocalBusiness schema with:
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Exact business name as it appears in GBP",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "City",
    "addressRegion": "QLD",
    "postalCode": "4000",
    "addressCountry": "AU"
  },
  "telephone": "+61-7-XXXX-XXXX",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "-27.4698",
    "longitude": "153.0251"
  },
  "openingHoursSpecification": [...],
  "url": "https://example.com",
  "sameAs": [
    "https://www.google.com/maps/place/...",
    "https://www.facebook.com/businesspage",
    "https://www.yelp.com/biz/..."
  ]
}
```

---

## 4. Review Strategy

### Review Velocity Guidelines
- Aim for consistent review acquisition over time (not bursts — triggers spam filters)
- Google flags sudden spikes in reviews as suspicious
- Target: 2-4 genuine reviews per month for small businesses, more for high-volume businesses

### Getting Reviews (Compliant Practices)
✅ Ask customers verbally after service delivery
✅ Follow-up email/SMS with direct GBP review link
✅ QR code at point of sale or on receipts
✅ Add review request to email signature

❌ Never offer incentives for reviews (violates Google policies)
❌ Never use review gating (showing review form only to happy customers)
❌ Never buy reviews

### Responding to Reviews
- Respond to ALL reviews — positive and negative
- Response time target: within 24-48 hours
- Negative review response formula: Acknowledge → Apologise → Take offline → Resolve
- Keyword-naturally mention your service and location in responses (secondary ranking signal)

### Removing Fake/Spam Reviews
1. Flag review in GBP for policy violation
2. If no action within 7 days, escalate via Google Business Profile support
3. As last resort, respond publicly to dispute false claims professionally

---

## 5. Local Keyword Research

### Search Intent Patterns for Local
| Pattern | Example | Priority |
|---------|---------|----------|
| `[service] [city]` | "plumber Brisbane" | Highest |
| `[service] near me` | "plumber near me" | Highest (mobile) |
| `[service] in [suburb]` | "plumber in Fortitude Valley" | High |
| `best [service] [city]` | "best plumber Brisbane" | High |
| `[service] [city] [qualifier]` | "emergency plumber Brisbane" | High |
| `[service] [city] [year]` | "plumber Brisbane 2026" | Medium |
| `how much does [service] cost [city]` | "how much does plumber cost Brisbane" | Medium |

### City vs Suburb Targeting
- Homepage: target primary city (e.g., "Brisbane plumber")
- Service area pages: target individual suburbs/areas (e.g., "plumber Fortitude Valley")
- Blog: target long-tail informational queries (e.g., "why is my hot water not working Brisbane")

---

## 6. Local Landing Pages

For multi-location businesses or service area businesses, each location
needs its own SEO-optimised landing page.

### Required Elements per Location Page
- [ ] Unique H1 with service + location
- [ ] Unique body content (60%+ unique — not just city name swapped)
- [ ] Embedded Google Map
- [ ] Location-specific phone number (if possible)
- [ ] LocalBusiness schema with full address and geo
- [ ] Local photos (not stock images)
- [ ] Local testimonials from that area
- [ ] Mention of local landmarks, suburbs served, or community ties
- [ ] Internal links to main service pages
- [ ] Link from main location directory page

### Quality Gates (enforce strictly)
- ⚠️ WARNING at 30+ location pages — require 60%+ unique content
- 🛑 HARD STOP at 50+ location pages — require justification and content audit

---

## 7. AI Visibility for Local (2025-2026)

AI Overviews appear for only ~0.14% of local keywords (March 2025 data) — local SEO faces significantly less AI disruption than other verticals. However, ChatGPT and Perplexity are increasingly used for local recommendations.

### Top AI Local Citation Signals (Whitespark 2026)
1. Presence on curated "best of" lists (e.g., "Best Plumbers in Brisbane" articles)
2. Consistent NAP across platforms (entity clarity for AI systems)
3. Genuine review volume and quality
4. Complete LocalBusiness schema with all properties
5. Wikipedia or Wikidata entity for established businesses

---

## Output

> 🔗 **This skill primarily contributes to Pillar 3 — Authority & Off-Page**
> (Local & Brand Signals, 5% of overall Health Score). Location landing page
> quality also feeds into Pillar 2 — Content & On-Page.
>
> Local SEO straddles both pillars: GBP optimisation and landing page content
> are Pillar 2; citation building, reviews, and brand signals are Pillar 3.

### Local SEO Audit Report
- GBP completeness score (0-100)
- Local pack ranking assessment
- NAP consistency issues (directory by directory)
- Review profile summary
- Citation gap analysis
- Location page quality assessment
- Top 10 priority recommendations

### Deliverables
- `LOCAL-SEO-AUDIT.md` — full audit findings
- `NAP-CONSISTENCY-REPORT.md` — all citation discrepancies
- `REVIEW-STRATEGY.md` — tailored review acquisition plan
- LocalBusiness JSON-LD schema for each location

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available:
- `business_data_business_listings_search` — audit competitor GBP profiles and citation presence
- `serp_organic_live_advanced` with local location codes — check actual local pack results
- `dataforseo_labs_google_ranked_keywords` — identify which local keywords a competitor ranks for
- `kw_data_google_ads_search_volume` with location targeting — local keyword volume data
