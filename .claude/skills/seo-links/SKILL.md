---
name: seo-links
description: >
  Link building strategy, digital PR, backlink profile analysis, toxic link
  identification, and disavow file management. Use when user says "link building",
  "backlinks", "get links", "digital PR", "earn links", "link outreach",
  "toxic links", "disavow", "link audit", "anchor text", "referring domains",
  "link profile", "guest posting", "broken link building", "HARO",
  "link acquisition", "link velocity", "domain authority", "DR", "DA",
  "lost backlinks", "competitor backlinks", "link gap analysis",
  "internal link audit", or "link equity". Also use when a user asks why
  their rankings dropped and backlinks may be a contributing factor.
---

# Link Building & Backlink Profile Analysis

Links remain a top-3 Google ranking signal. This skill covers both offensive
(acquiring new links) and defensive (auditing and cleaning existing profile) workflows.

---

## Part 1: Backlink Profile Audit

### What to Measure

| Metric | Tool | What it tells you |
|--------|------|------------------|
| Total referring domains | Ahrefs / DataForSEO | Overall link footprint |
| Domain Rating / DR | Ahrefs | Relative link authority |
| Spam score | DataForSEO `backlinks_bulk_spam_score` | Toxic link risk |
| Dofollow ratio | DataForSEO `backlinks_summary` | Link equity passing |
| Anchor text distribution | DataForSEO `backlinks_anchors` | Over-optimisation risk |
| Link velocity | DataForSEO `backlinks_timeseries_summary` | Growth pattern naturalness |
| New vs lost links | DataForSEO `backlinks_bulk_new_lost_backlinks` | Link churn rate |
| Top linked pages | DataForSEO `backlinks_domain_pages` | Link equity distribution |

### Anchor Text Distribution — Healthy vs Risky

| Anchor Type | Healthy % | Warning |
|-------------|-----------|---------|
| Branded (company name) | 40-60% | <20% = link scheme risk |
| Naked URL | 15-25% | — |
| Generic ("click here", "website") | 5-15% | — |
| Exact-match keyword | <5% | >10% = over-optimisation risk |
| Partial match keyword | 10-20% | — |
| Image/no anchor | 5-10% | — |

> A natural link profile looks like an organic distribution. Sites that pursued aggressive exact-match anchor campaigns are at penalty risk, especially post-2024 spam updates.

### Toxic Link Signals

Flag links exhibiting 3+ of these:
- Domain spam score >45/100
- Irrelevant niche (no topical connection)
- Foreign language site with no content relevance
- Links from link farm networks (same IP block, identical footer links)
- Exact-match anchor text pointing to a money page
- Link from a hacked or penalised site
- Reciprocal link arrangement
- Sitewide links (footer/sidebar) from unrelated sites

### Link Velocity Analysis

A sudden spike in backlinks can trigger algorithmic scrutiny. Check:
- Was the spike organic (viral content, press coverage, product launch)?
- Or suspicious (bought links, link scheme)?
- Post-penalty or post-algorithm update: look for loss of referring domains

---

## Part 2: Disavow Workflow

Use disavow as a last resort. Google is generally good at ignoring low-quality links. Only disavow if:
- You've received a manual action for unnatural links
- You can identify links from an old paid link scheme
- There's a concentrated cluster of toxic links you cannot remove

### Process
1. Export full backlink list from Ahrefs or DataForSEO
2. Identify toxic links using spam score + manual review
3. Attempt removal first: contact webmaster, use Google's link removal request
4. For links that cannot be removed, add to disavow file
5. Format: one domain per line (`domain:example.com`) or specific URLs
6. Upload via Google Search Console > Legacy tools > Disavow links
7. Allow 2-4 weeks for Google to process

### Disavow File Format
```
# Disavow file for example.com — created 2026-03-01
# Reason: manual action for unnatural links — removed what we can

# Toxic link farm network
domain:spamsite1.com
domain:spamsite2.com

# Specific paid links we couldn't get removed
https://partiallyoksite.com/paid-links-page
```

> **Do NOT over-disavow.** Disavowing legitimate links reduces your authority. When in doubt, leave it out.

---

## Part 3: Competitor Link Gap Analysis

### Process
1. Identify 3-5 direct competitors
2. Use DataForSEO `dataforseo_labs_google_domain_intersection` to find shared backlinks
3. Use `backlinks_domain_intersection` to find sites linking to competitors but not you
4. Prioritise gap domains by: relevance, domain authority, traffic
5. These are your warmest outreach targets — they've already linked to the space

### Scoring Gap Opportunities
| Criteria | Points |
|----------|--------|
| Links to 2+ of your competitors | +3 |
| Topically relevant | +2 |
| Has linked editorially (not paid/sponsored) | +2 |
| DR/DA 30+ | +1 |
| Has active content publication | +1 |

---

## Part 4: Link Building Tactics

### Tier 1 — Editorial Links (Highest Value, Hardest to Get)

**Digital PR**
- Create genuinely newsworthy assets: original data, surveys, proprietary research, tools
- Pitch to journalists via: HARO (Help A Reporter Out), Qwoted, Featured, Connectively
- Target: news publishers, industry trade press, major blogs
- Success rate: 2-5% of cold pitches → link
- Timeline: 4-12 weeks per campaign

**Thought Leadership Placement**
- Secure guest author spots on respected industry publications
- Bylined articles, expert commentary, contributed columns
- Do NOT: pay for placements (violates Google's link scheme policies)
- Do NOT: use content mills or link farms disguised as publishers

**Data Studies / Surveys**
- Original research is the most consistently cited content type
- Survey 500-1000 people in your niche, publish findings
- Pitch results to trade press, include free embed badge for the data
- Shelf life: 12-18 months before needing refresh

### Tier 2 — Earned Links (Medium Value, Scalable)

**Broken Link Building**
1. Find resource pages in your niche with dead links (use Ahrefs Content Explorer or Screaming Frog)
2. Identify which of your content could replace the dead resource
3. Email the webmaster: "Hey, you have a broken link on [page] — we have an updated version"
4. Success rate: 5-10% of outreach
5. Best for: tools, guides, statistics pages

**Resource Page Link Building**
- Find pages that curate resources in your space: "best tools for X", "resources for Y"
- Pitch your resource as a worthwhile addition
- Requires genuinely useful content — not just a sales page

**Unlinked Brand Mentions**
- Use DataForSEO `content_analysis_search` or Google Alerts to find brand mentions without links
- Reach out and ask them to add a link — conversion rate is 20-40% (they already like you)

**Competitor Link Reclamation**
- If a competitor has moved or removed content, find their inbound links
- If you have equivalent or better content, pitch as a replacement

### Tier 3 — Foundation Links (Lower Value, Easy to Get)

- Business directory citations (Google, Bing, Apple Maps, industry directories) — primarily for local SEO signals
- Social profiles (LinkedIn company page, Crunchbase, GitHub, etc.) — entity signals
- Industry association memberships
- Press release distribution (not for link value — for distribution only)

> **Never pay for links on established blogs, private blog networks (PBNs), or link insertion services.** These violate Google's link scheme policies and are aggressively targeted by manual action teams.

---

## Part 5: Internal Link Audit

Internal links are the most underutilised link building tactic. They're free, controllable, and move link equity to pages that need it.

### Internal Link Analysis
- Map which pages have the most inbound internal links (these receive the most equity)
- Identify high-value pages with few internal links (equity-starved)
- Check for: broken internal links, orphan pages, redirect chains

### Internal Linking Best Practices
- Link from high-authority pages to pages you want to rank
- Use descriptive anchor text (not "click here")
- 3-5 internal links per 1,000 words of body content
- No more than 100 links per page
- Every page should be reachable within 3 clicks from homepage
- Pillar pages should link to cluster pages and vice versa (hub-spoke model)

### Content Hub / Topical Cluster Structure
```
Pillar Page: "Complete Guide to [Topic]"
  ├── Cluster: "[Sub-topic 1] Guide"
  ├── Cluster: "[Sub-topic 2] Explained"
  ├── Cluster: "How to [Task within topic]"
  └── Cluster: "[Sub-topic 3] Best Practices"

Each cluster links back to pillar. Pillar links to each cluster.
Result: concentrated topical authority signal.
```

---

## Part 6: Link Building KPIs

| Metric | Target | Frequency |
|--------|--------|-----------|
| New referring domains acquired | 5-20/month (size-dependent) | Monthly |
| DR/DA growth | +2-5 per quarter | Quarterly |
| Toxic link ratio | <5% of total | Quarterly |
| Lost link recovery | <20% churn rate | Monthly |
| Anchor text distribution | Branded >40% | Quarterly |
| Link velocity growth | Steady, not spiky | Monthly |

---

## Output

> 🔗 **This skill contributes to Pillar 3 — Authority & Off-Page** in the
> 3-pillar SEO report. Findings feed into Backlink Profile & Link Equity
> (12% of overall Health Score) — the largest single sub-category in Pillar 3.

### Backlink Audit Report
- `BACKLINK-AUDIT.md` — full profile analysis with scores
- `TOXIC-LINKS.csv` — identified toxic links with evidence
- `DISAVOW.txt` — ready-to-upload disavow file (if needed)
- `LINK-GAP-ANALYSIS.md` — competitor comparison and outreach targets

### Link Building Strategy
- `LINK-STRATEGY.md` — prioritised tactics for the specific site type
- `OUTREACH-TARGETS.csv` — scored prospects for broken link / resource outreach

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available:
- `backlinks_summary` — full link profile overview
- `backlinks_backlinks` — individual backlink list with metrics
- `backlinks_anchors` — anchor text distribution analysis
- `backlinks_referring_domains` — referring domain list with authority
- `backlinks_bulk_spam_score` — bulk spam scoring for toxic link detection
- `backlinks_timeseries_summary` — link velocity over time
- `backlinks_domain_intersection` — competitor link gap analysis
- `backlinks_bulk_new_lost_backlinks` — new and lost link tracking
- `content_analysis_search` — find unlinked brand mentions
