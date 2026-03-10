---
name: seo-validate
description: >
  Independent validation of SEO audit reports. Re-checks a sample of findings
  against the live site, verifies score calculations, detects contradictions
  between sections, and confirms recommendations align with issues found.
  Use when user says "validate report", "check the report", "verify audit",
  "is this report accurate", "quality check", "QA the report", "review the
  audit", "double check findings", "validate findings", "report QA",
  "verify the audit", "cross-check report", "independent review", or
  "sanity check the report". Always use this skill after completing a full
  audit before delivering to a client.
---

# Independent Report Validation

## Purpose

This skill acts as an **independent quality gate** between audit completion and
client delivery. It assumes the report may contain errors and systematically
verifies accuracy, consistency, and completeness.

**Key principle:** The validator is NOT the original auditor. It approaches the
report with fresh eyes and healthy skepticism.

## When to Use

- After completing a full `seo-audit` — run before delivering to client
- When a user questions specific findings in a report
- When reviewing a report generated in a previous session
- As a quality gate in any multi-step audit workflow

## Process

### Step 1: Report Intake

Read the complete audit report and extract:
- All findings (issues identified, with their severity ratings)
- All scores (overall, per-category, per-pillar)
- All recommendations (with their priority ratings)
- The target URL and pages audited
- The stated methodology and scoring weights

### Step 2: Finding Verification (30% of validation score)

Re-test a representative sample of findings against the live site:

**Sampling strategy:**
- ALL critical-severity findings (100% coverage)
- Random 30% of high-severity findings
- Random 10% of medium/low-severity findings
- At least 1-2 findings from every report section

**For each sampled finding:**
1. Re-fetch the relevant URL
2. Re-run the specific check that produced the finding
3. Compare the result against what the report states
4. Record verdict: ✅ Confirmed | ❌ Incorrect | ⚠️ Partially correct | 🔄 Changed

**Common verification checks:**
- Re-fetch URLs to confirm HTTP status codes
- Re-check HTML source for meta tags, schema, heading structure
- Re-test page speed with a fresh measurement
- Re-check mobile rendering at 375px viewport
- Re-count words on content pages
- Re-trace redirect chains
- Re-validate schema markup

### Step 3: Score Validation (25% of validation score)

Verify that scores are mathematically correct and logically consistent:

**Mathematical checks:**
- Do category scores add up to the overall score using stated weights?
- Are all scores within valid ranges (0-100)?
- Do percentage weights sum to 100%?

**Logical checks:**
- A section with 5 critical issues shouldn't score 80+
- A section with no issues shouldn't score below 70
- Similar issues should be scored consistently across pages
- If content is flagged as "thin" in content section, content score should reflect it
- Mobile score should align with mobile-specific findings

**Severity-score alignment guide:**
| Critical Issues | Expected Max Score |
|----------------|-------------------|
| 0 | 100 |
| 1-2 | 75 |
| 3-5 | 60 |
| 6+ | 40 |

### Step 4: Contradiction Detection (20% of validation score)

Scan for internal contradictions:

**Types to check:**
- **Score vs. findings:** "Excellent" score but multiple critical issues listed
- **Section vs. section:** Different sections making conflicting claims
- **Summary vs. detail:** Executive summary not reflecting detailed findings
- **Recommendation vs. finding:** Recommending fixes for non-existent issues
- **Priority vs. severity:** Critical issues listed as low priority
- **Data conflicts:** Different numbers for the same metric in different sections
- **Status conflicts:** Same page listed as both indexed and not-indexed

### Step 5: Recommendation Alignment (15% of validation score)

Check that recommendations are:
- **Relevant:** Each recommendation addresses an actual finding in the report
- **Complete:** Every critical and high-severity issue has a recommendation
- **Actionable:** Specific enough for the client to implement
- **Prioritized correctly:** Order reflects actual impact
- **Technically sound:** Recommended fixes would actually solve the stated problem
- **No phantoms:** No recommendations for issues not found in the audit

### Step 6: Completeness Check (10% of validation score)

Verify the audit covered all expected areas:

**Standard audit areas that should be present:**
- [ ] Technical SEO (crawlability, indexability, robots.txt, sitemap)
- [ ] On-page SEO (titles, meta descriptions, headings, content)
- [ ] Content quality (word count, E-E-A-T, readability)
- [ ] Schema markup (JSON-LD validation)
- [ ] Performance (Core Web Vitals, page speed)
- [ ] Mobile usability
- [ ] Security (HTTPS, headers)
- [ ] Internal linking
- [ ] Image optimization

**Page coverage:**
- Were all key page types audited? (homepage, service pages, contact, about)
- Were high-traffic pages included?
- Were pages from the sitemap cross-referenced?

## Validation Scoring

### Report Confidence Score (0-100)

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | High confidence | Findings verified, scores consistent, no contradictions |
| 75-89 | Good confidence | Minor discrepancies, mostly accurate |
| 60-74 | Moderate confidence | Some findings unverifiable or scores seem off |
| 40-59 | Low confidence | Significant errors or contradictions — needs revision |
| 0-39 | Very low confidence | Major issues — report should not be delivered as-is |

## Cross-Skill Integration

- Runs AFTER `seo-audit` completes all subagent delegation
- Can invoke `seo-factcheck` for content accuracy verification
- May re-run individual checks from `seo-technical`, `seo-content`, `seo-schema`
- Acts as the final quality gate before client delivery

## Output

> 🔍 **Quality Assurance** — This skill does not contribute to the SEO Health
> Score directly. It validates the accuracy of the score and all findings.

### Report Confidence Score: XX/100

### Validation Summary
| Category | Score | Status |
|----------|-------|--------|
| Finding Verification | XX/30 | X of Y re-checked |
| Score Validation | XX/25 | [consistent / issues found] |
| Contradiction Detection | XX/20 | [X contradictions found] |
| Recommendation Alignment | XX/15 | [aligned / gaps found] |
| Completeness | XX/10 | [complete / gaps found] |

### Findings Re-checked
| # | Original Finding | Section | Verdict | Notes |
|---|-----------------|---------|---------|-------|
| 1 | "..." | ... | ✅/❌/⚠️ | ... |

### Issues Found in Report
#### Contradictions
- [List any contradictions between sections]

#### Scoring Errors
- [Mathematical or logical scoring issues]

#### Incorrect Findings
- [Findings that failed re-verification]

#### Missing Coverage
- [Audit areas or pages that were skipped]

### Verdict
- [ ] ✅ **PASS** — Report is ready for delivery
- [ ] ⚠️ **PASS WITH CORRECTIONS** — Minor fixes needed (listed above)
- [ ] ❌ **FAIL** — Significant revisions required before delivery

### Required Corrections
- [Specific changes to make before delivering the report]
