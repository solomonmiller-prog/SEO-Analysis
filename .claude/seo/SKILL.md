---
name: seo
description: >
  Comprehensive SEO analysis for any website or business type. Performs full site
  audits, single-page deep analysis, technical SEO checks (crawlability, indexability,
  Core Web Vitals with INP), schema markup detection/validation/generation, content
  quality assessment (E-E-A-T framework per Dec 2025 update extending to ALL competitive
  queries), image optimization, sitemap analysis, hreflang/international SEO, programmatic
  SEO, competitor comparison pages, and Generative Engine Optimization (GEO) for AI
  Overviews, ChatGPT, and Perplexity citations. Analyzes AI crawler accessibility
  (GPTBot, ClaudeBot, PerplexityBot), llms.txt compliance, brand mention signals,
  and passage-level citability. Industry detection for SaaS, e-commerce, local business,
  publishers, agencies. Triggers on: "SEO", "audit", "schema", "Core Web Vitals",
  "sitemap", "E-E-A-T", "AI Overviews", "GEO", "technical SEO", "content quality",
  "page speed", "structured data", "hreflang", "international SEO", "programmatic SEO",
  "comparison page", "vs page", "alternatives page", "robots.txt", "canonicals",
  "indexing", "crawl", "keyword strategy", "SEO plan", "SEO roadmap", "image SEO",
  "alt text", "rich results", "JSON-LD", "LCP", "INP", "CLS", "AI search",
  "ChatGPT visibility", "Perplexity", "llms.txt", "website health check".
  Use this skill for ANY request that touches search engine visibility, rankings,
  organic traffic, or website discoverability — even if the user doesn't say "SEO".
---

# SEO — Universal SEO Analysis Skill

Comprehensive SEO analysis across all industries (SaaS, local services,
e-commerce, publishers, agencies). Orchestrates 12 specialized sub-skills
and 7 subagents (+ optional extension sub-skills).

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/seo audit <url>` | Full website audit with parallel subagent delegation |
| `/seo page <url>` | Deep single-page analysis |
| `/seo sitemap <url or generate>` | Analyze or generate XML sitemaps |
| `/seo schema <url>` | Detect, validate, and generate Schema.org markup |
| `/seo images <url>` | Image optimization analysis |
| `/seo technical <url>` | Technical SEO audit (9 categories incl. IndexNow) |
| `/seo content <url>` | E-E-A-T and content quality analysis |
| `/seo geo <url>` | AI Overviews / Generative Engine Optimization |
| `/seo plan <business-type>` | Strategic SEO planning |
| `/seo programmatic [url\|plan]` | Programmatic SEO analysis and planning |
| `/seo competitor-pages [url\|generate]` | Competitor comparison page generation |
| `/seo hreflang [url]` | Hreflang/i18n SEO audit and generation |
| `/seo local [url\|gbp]` | Google Business Profile, local pack, citations, reviews |
| `/seo links [domain]` | Backlink audit, link building strategy, disavow |
| `/seo gsc [url]` | Google Search Console analysis and diagnosis |
| `/seo migration [url]` | Site migration planning, execution, and recovery |
| `/seo dataforseo [command]` | Live SEO data via DataForSEO (extension) |

## Orchestration Logic

When the user invokes `/seo audit`, delegate to subagents in parallel:
1. Detect business type (SaaS, local, ecommerce, publisher, agency, other)
2. Spawn subagents: seo-technical, seo-content, seo-schema, seo-sitemap, seo-performance, seo-visual, seo-geo
3. Collect results and generate unified report with SEO Health Score (0-100)
4. Create prioritized action plan (Critical → High → Medium → Low)

For individual commands, load the relevant sub-skill directly.

## Industry Detection

Detect business type from homepage signals:
- **SaaS**: pricing page, /features, /integrations, /docs, "free trial", "sign up"
- **Local Service**: phone number, address, service area, "serving [city]", Google Maps embed
- **E-commerce**: /products, /collections, /cart, "add to cart", product schema
- **Publisher**: /blog, /articles, /topics, article schema, author pages, publication dates
- **Agency**: /case-studies, /portfolio, /industries, "our work", client logos

## Quality Gates

Read `references/quality-gates.md` for thin content thresholds per page type.
Hard rules:
- ⚠️ WARNING at 30+ location pages (enforce 60%+ unique content)
- 🛑 HARD STOP at 50+ location pages (require user justification)
- Never recommend HowTo schema (deprecated Sept 2023)
- FAQ schema only for government and healthcare sites
- All Core Web Vitals references use INP, never FID
- Mobile-first indexing is 100% complete (July 5, 2024) — always assess mobile version

## Reference Files

Load these on-demand as needed — do NOT load all at startup:
- `references/cwv-thresholds.md` — Current Core Web Vitals thresholds and measurement details
- `references/schema-types.md` — All supported schema types with deprecation status
- `references/eeat-framework.md` — E-E-A-T evaluation criteria (Sept 2025 + Dec 2025 update)
- `references/quality-gates.md` — Content length minimums, uniqueness thresholds, title/meta rules

## Scoring Methodology

### SEO Health Score (0-100)

Reports are structured into **three pillars**, each with a section score and
contributing sub-category scores. The overall Health Score is a weighted aggregate.

```
┌─────────────────────────────────────────────────────────────────┐
│  PILLAR 1 — TECHNICAL FOUNDATION               35% of total     │
│  The plumbing. Without this, nothing else matters.              │
├─────────────────────────────────────────────────────────────────┤
│  Crawlability & Indexability          15%                        │
│  Performance (Core Web Vitals)        10%                        │
│  Mobile & JavaScript Rendering        10%                        │
├─────────────────────────────────────────────────────────────────┤
│  PILLAR 2 — CONTENT & ON-PAGE                  40% of total     │
│  What the site says and how well it says it.                    │
├─────────────────────────────────────────────────────────────────┤
│  Content Quality & E-E-A-T            15%                        │
│  On-Page SEO (titles, meta, headings, internal links)  10%      │
│  Schema & Structured Data              8%                        │
│  Images & Media                        7%                        │
├─────────────────────────────────────────────────────────────────┤
│  PILLAR 3 — AUTHORITY & OFF-PAGE               25% of total     │
│  How the rest of the web perceives the site. The long game.     │
├─────────────────────────────────────────────────────────────────┤
│  Backlink Profile & Link Equity       12%                        │
│  AI Search / GEO Visibility            8%                        │
│  Local & Brand Signals                 5%                        │
└─────────────────────────────────────────────────────────────────┘
```

**Why this structure?**
- Technical issues are always highest priority — a miscrawled site with great content still ranks nowhere. Separating it from content gives technical problems the urgency they deserve.
- Content & On-Page is the largest surface area — most sites have the most room to improve here, and it's fully within the site owner's control.
- Authority is honest at 25% — backlinks and brand signals matter enormously but require external action and months to move.

### Skill-to-Pillar Mapping

| Pillar | Primary Skills | Agent |
|--------|---------------|-------|
| Technical Foundation | seo-technical, seo-sitemap, seo-gsc, seo-migration | seo-technical |
| Content & On-Page | seo-content, seo-page, seo-schema, seo-images | seo-content, seo-schema |
| Authority & Off-Page | seo-links, seo-geo, seo-local, seo-competitor-pages | seo-geo |

### Priority Levels
- **Critical**: Blocks indexing or causes penalties (immediate fix required)
- **High**: Significantly impacts rankings (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## Sub-Skills

This skill orchestrates 16 specialized sub-skills (+ 1 extension):

1. **seo-audit** — Full website audit with parallel delegation
2. **seo-page** — Deep single-page analysis
3. **seo-technical** — Technical SEO (9 categories incl. IndexNow)
4. **seo-content** — E-E-A-T and content quality
5. **seo-schema** — Schema markup detection and generation
6. **seo-images** — Image optimization
7. **seo-sitemap** — Sitemap analysis and generation
8. **seo-geo** — AI Overviews / GEO optimization
9. **seo-plan** — Strategic planning with industry templates
10. **seo-programmatic** — Programmatic SEO analysis and planning
11. **seo-competitor-pages** — Competitor comparison page generation
12. **seo-hreflang** — Hreflang/i18n SEO audit and generation
13. **seo-local** — Local SEO, Google Business Profile, citations, reviews
14. **seo-links** — Backlink audit, link building strategy, disavow workflow
15. **seo-gsc** — Google Search Console analysis and diagnosis
16. **seo-migration** — Site migration planning, execution, and recovery
17. **seo-dataforseo** — Live SEO data via DataForSEO MCP (extension)

## Subagents

For parallel analysis during audits:
- `seo-technical` — Crawlability, indexability, security, CWV, IndexNow
- `seo-content` — E-E-A-T, readability, thin content, GEO citation readiness
- `seo-schema` — Detection, validation, generation
- `seo-sitemap` — Structure, coverage, quality gates
- `seo-performance` — Core Web Vitals measurement
- `seo-visual` — Screenshots, mobile testing, above-fold
- `seo-geo` — AI Overviews, ChatGPT/Perplexity visibility, llms.txt, brand signals
- `seo-dataforseo` — Live SERP, keyword, backlink, local SEO data (extension, optional)

## Additional Skills (Available on Demand)

These skills are not part of the standard audit delegation but are invoked directly:
- `seo-local` — Google Business Profile optimisation, local pack, citations, reviews
- `seo-links` — Backlink profile audit, link building strategy, disavow workflow
- `seo-gsc` — Google Search Console analysis, diagnosis, CTR optimisation
- `seo-migration` — Site migration planning, redirect mapping, post-migration monitoring
