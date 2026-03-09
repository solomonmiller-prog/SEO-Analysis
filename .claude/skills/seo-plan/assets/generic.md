<!-- Updated: 2026-03-09 -->
# Generic Business SEO Strategy Template

## Overview

This template applies to businesses that don't fit neatly into SaaS, local service,
e-commerce, publisher, or agency categories — including B2B manufacturers, professional
services firms, non-profits, consultancies, and general small businesses.

## Industry Characteristics

- Moderate transaction value with considered purchase decisions
- Trust and credibility are central to conversion
- Content serves multiple funnel stages simultaneously
- Mix of informational and commercial search intent
- May have both B2B and B2C audiences

## Recommended Site Architecture

```
/
├── Home
├── /products (or /services)
│   ├── /product-1
│   ├── /product-2
│   └── ...
├── /solutions (if applicable)
│   ├── /solution-by-problem
│   └── /solution-by-industry
├── /about
│   ├── /team
│   ├── /story
│   └── /values
├── /resources
│   ├── /blog
│   ├── /guides
│   ├── /case-studies
│   ├── /faq
│   └── /glossary
├── /contact
├── /support (if applicable)
└── /legal
    ├── /privacy
    └── /terms
```

## Schema Recommendations

| Page Type | Schema Types |
|-----------|-------------|
| Homepage | Organization, WebSite (with SearchAction) |
| About | Organization, AboutPage |
| Team Member | Person, ProfilePage |
| Contact | ContactPage |
| Service Page | Service, Organization |
| Product Page | Product, Offer |
| Blog Post | Article, BlogPosting, Person (author) |
| Case Study | Article |

### Organization Schema (required on all sites)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Business Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "description": "What the business does in 1-2 sentences",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-555-555-5555",
    "contactType": "customer service"
  },
  "sameAs": [
    "https://www.linkedin.com/company/...",
    "https://www.facebook.com/..."
  ]
}
```

## Content Requirements

### Minimum Word Counts
| Page Type | Min Words | Notes |
|-----------|-----------|-------|
| Homepage | 500 | Clear value proposition above fold |
| Product/Service | 800 | Specific, detailed, no marketing fluff |
| Blog Post | 1,500 | Comprehensive topical coverage |
| About Page | 400 | Genuine story, real team members |
| Landing Page | 600 | Focused on single conversion goal |
| Case Study | 800 | Problem → approach → outcome with metrics |
| Glossary Term | 300 | Accurate definition with context |

### E-E-A-T Essentials

**Experience:** Case studies with real outcomes and metrics. Before/after examples. Original photos of work, products, team.

**Expertise:** Named authors on all content with bios. Team page with credentials. Industry certifications displayed.

**Authoritativeness:** External press mentions. Industry awards. Client logos (with permission). Speaking engagements.

**Trustworthiness:** Complete contact info including physical address. Privacy policy and terms linked from footer. SSL. Customer testimonials with full names.

## Technical Foundations

### Must-Haves
- [ ] HTTPS enabled with valid SSL
- [ ] Mobile-responsive design (16px+ base font)
- [ ] robots.txt correctly configured
- [ ] XML sitemap submitted to Google Search Console
- [ ] GSC verified and active
- [ ] Core Web Vitals passing (LCP <2.5s, INP <200ms, CLS <0.1)
- [ ] 404 error page with navigation

### Should-Haves
- [ ] Organization schema on homepage
- [ ] Internal linking strategy documented
- [ ] No redirect chains (1 hop max)
- [ ] Images: WebP, alt text, lazy loading, width/height set
- [ ] Open Graph tags for social sharing
- [ ] Canonical tags on all pages

## Content Priorities & Phases

### Phase 1 — Foundation (Weeks 1-4)
1. Homepage with clear value proposition and primary CTA
2. Core product/service pages (one per offering)
3. About page with real team, story, credentials
4. Contact page with all contact methods
5. Organization + WebSite schema

### Phase 2 — Expansion (Weeks 5-12)
1. Blog launch: 2-4 posts/month, targeting bottom-of-funnel first
2. FAQ page addressing top customer questions
3. 1-2 detailed case studies with real metrics
4. Internal linking audit
5. Backlink outreach begins

### Phase 3 — Growth (Weeks 13-24)
1. Content cluster development (pillar + supporting articles)
2. Comparison/alternative pages if applicable
3. Glossary or resource hub for topical authority
4. Digital PR campaign for editorial links
5. GEO optimisation pass

### Phase 4 — Authority (Months 7-12)
1. Original research or survey (unique, citable data)
2. Advanced schema across all page types
3. PR and media mentions strategy
4. Video content (YouTube — highest correlation with AI citations)
5. Entity building: LinkedIn, Wikipedia if warranted, Wikidata

## Keyword Strategy

| Content Type | Intent | Example |
|-------------|--------|---------|
| Product/service pages | Commercial/transactional | "[service] for [audience]" |
| Blog how-to posts | Informational | "how to [problem your service solves]" |
| Comparison content | Commercial | "[your product] vs [alternative]" |
| Glossary | Informational | "what is [industry term]" |
| Case studies | Commercial | "[outcome] for [industry]" |

**Content Cluster Model:** Build one pillar page (2,000+ words) per core topic. Support with 5-10 cluster articles (800-1,500 words). Bidirectional internal links between pillar and clusters. This concentrates topical authority.

## Key Metrics to Track

- Organic sessions (GSC / GA) — weekly
- Non-branded keyword impressions (GSC) — monthly
- Indexed pages (GSC Coverage) — monthly
- Core Web Vitals (GSC Experience) — monthly
- Referring domains (DataForSEO / Ahrefs) — quarterly

## Generative Engine Optimization (GEO) Checklist

- [ ] Clear, quotable facts and statistics AI systems can extract and cite
- [ ] Organization schema with complete sameAs entity links
- [ ] Named authors with credentials and Person + ProfilePage schema
- [ ] Original data, research, or case study outcomes only found on your site
- [ ] `/llms.txt` file at site root with key pages and facts
- [ ] AI crawlers allowed in robots.txt: GPTBot, ClaudeBot, PerplexityBot
- [ ] Brand presence on: LinkedIn, YouTube, industry directories
- [ ] Content structured with clear definitions ("X is...") and headings
- [ ] Monitor AI citation across Google AI Overviews, ChatGPT, Perplexity
