---
name: seo-factcheck
description: >
  Content fact-checking and contextual accuracy verification. Extracts verifiable
  claims from page content, cross-references against authoritative sources, and
  flags inaccuracies with corrections. Use when user says "fact check", "verify
  claims", "check accuracy", "is this correct", "content accuracy", "verify
  facts", "check the facts", "are these claims true", "fact-check my content",
  "verify statistics", "check measurements", "content verification", or
  "accuracy check". Also use when a user suspects specific content may contain
  errors or when reviewing content before publication.
---

# Content Fact-Checking & Contextual Accuracy

## When to Use

- Before publishing new content (pre-publication review)
- After generating content with AI tools
- When auditing existing site content for credibility
- When a user flags specific claims as potentially wrong
- As part of a full site audit (delegated from `seo-audit`)

## Process

### Step 1: Content Extraction

Fetch the target URL(s) and extract all visible text content:
- Headings, body text, FAQ answers
- Image alt text and captions
- Testimonial text
- Footer claims (awards, certifications, years in business)
- Meta description (shown in search results — errors here are highly visible)

### Step 2: Claim Extraction

Parse extracted content and identify every verifiable claim:
- **Numbers & measurements** — sizes, weights, distances, quantities, percentages
- **Dates & timelines** — founding years, "X years of experience", event dates
- **Scientific/technical facts** — species info, chemical properties, medical claims
- **Regulatory references** — standards numbers, legal requirements, certifications
- **Comparative/superlative claims** — "best", "#1", "fastest", "most affordable"
- **Process descriptions** — "takes X days", "lasts X years", "X steps"

### Step 3: Prioritize by Risk

| Priority | Claim Types |
|----------|-------------|
| CRITICAL | YMYL claims (health, safety, legal, financial), regulatory references |
| HIGH | Measurements, statistics, certification claims, comparative claims |
| MEDIUM | Dates, timelines, process descriptions, geographic facts |
| LOW | General industry knowledge, widely accepted facts |

### Step 4: Verify

Use web search to verify each HIGH and CRITICAL claim against authoritative sources:
- Government websites (.gov, .gov.au)
- Scientific databases and journals
- Industry body publications
- Manufacturer specifications
- Standards organizations (Standards Australia, ISO)

For each claim, determine:
- ✅ **Correct** — verified by 2+ authoritative sources
- ❌ **Incorrect** — contradicted by authoritative sources (provide correct value)
- ⚠️ **Unverifiable** — cannot confirm or deny with available sources
- 🟡 **Outdated** — was correct but information has since changed
- 🔵 **Misleading** — technically true but presented in a deceptive context

### Step 5: Contextual Relevance

Evaluate whether the content makes sense in context:
- Does the content match the page's stated purpose?
- Is industry terminology used correctly?
- Are claims appropriate for the business type and location?
- Does the content appear to be template-generated with incorrect details?
- Are there copy-paste artifacts from other businesses or locations?

## Cross-Skill Integration

- Feeds into `seo-content` E-E-A-T assessment (factual accuracy is core to Expertise and Trustworthiness)
- Feeds into `seo-validate` as an independent verification layer
- Triggered by `seo-audit` when content analysis is delegated

## Common Errors by Industry

### Pest Control
- Insect/pest sizes (mm vs cm confusion)
- Chemical safety claims vs actual SDS data
- Treatment warranty periods vs actual product lifespan
- Regulatory requirements by state/territory

### Construction / Trades
- Building code references (NCC/BCA version)
- Material specifications and tolerances
- Licensing requirements (varies by state)
- Warranty periods vs statutory guarantees

### Health & Wellness
- Treatment effectiveness claims (must be evidence-based)
- Qualification claims (verify registrations)
- "Approved by" claims (verify with the approving body)
- Therapeutic goods claims (TGA regulated in Australia)

### Legal / Financial
- Regulatory body names and jurisdictions
- Fee structures and legal requirements
- Statute of limitations and legal timeframes
- Insurance and liability claims

## Output

> 📝 **This skill contributes to Pillar 2 — Content & On-Page** in the
> 3-pillar SEO report. Factual accuracy directly impacts E-E-A-T scoring
> (Expertise and Trustworthiness dimensions).

### Factual Accuracy Score: XX/100
### Contextual Relevance Score: XX/100

### Claims Verified: X total (X correct, X incorrect, X unverifiable)

### Errors by Severity
- 🔴 **CRITICAL:** [list]
- 🟠 **HIGH:** [list]
- 🟡 **MEDIUM:** [list]

### Corrections Table
| Claim | Location | Current (Wrong) | Correct Value | Source |
|-------|----------|-----------------|---------------|--------|

### Contextual Issues
- [Content-page mismatch issues]
- [Template artifacts]
- [Terminology misuse]

### Recommendations
- Specific corrections with sources
- Claims needing citations added
- Content requiring subject-matter expert review
