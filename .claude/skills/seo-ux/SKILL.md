---
name: seo-ux
description: >
  UI/UX analysis covering navigation, visual hierarchy, accessibility,
  conversion optimization, and mobile usability. Use when user says "UX audit",
  "UI check", "user experience", "is my site user friendly", "usability
  review", "accessibility audit", "WCAG check", "conversion optimization",
  "CTA review", "navigation review", "mobile usability", "user friendly",
  "website usability", "UX review", "UI review", "is my website easy to use",
  "check my site's usability", "accessibility check", or "how does my site
  look". Also use when a user reports high bounce rates, low conversions, or
  user complaints about the website.
---

# UX/UI Analysis & Usability Audit

## When to Use

- When a user wants a usability assessment of their website
- When bounce rates or conversion rates suggest UX problems
- When redesigning or improving an existing site
- When checking accessibility compliance
- As part of a comprehensive site audit (delegated from `seo-audit`)

## Prerequisites

Ensure Playwright is available for visual analysis:
```bash
pip install playwright && playwright install chromium
```

## Process

### Step 1: Visual Capture

Capture screenshots at 4 viewports (desktop 1920x1080, laptop 1366x768, tablet 768x1024, mobile 375x812):
- Above-the-fold screenshot (what users see first)
- Full-page screenshot (complete layout)
- Key interaction states (menu open, form focused, modal visible)

### Step 2: Navigation & Information Architecture

Evaluate how easily users can find what they need:

**Check:**
- Main navigation: 5-7 items max with clear, jargon-free labels
- Menu depth: 2 levels maximum for most sites
- Breadcrumbs on interior pages
- Search functionality (if applicable)
- Footer navigation structure
- Mobile hamburger menu accessibility
- Active page indication in nav
- Logical page grouping and hierarchy

**Common issues:**
- Too many nav items overwhelming users
- Unclear or clever labels instead of descriptive ones
- Important pages buried 3+ clicks deep
- No way to navigate back without browser back button

### Step 3: Visual Hierarchy & Layout

Evaluate the visual design's effectiveness at guiding users:

**Check:**
- H1 visible above the fold
- Clear visual hierarchy (size, weight, color guide the eye)
- Adequate white space (not cramped, not wasteful)
- Line length: 60-80 characters for readability
- Font size: 16px+ body text
- Color contrast: 4.5:1 minimum for normal text
- Consistent styling across pages
- Clear visual flow (F-pattern or Z-pattern)

### Step 4: Calls-to-Action & Conversion

Evaluate how effectively the site drives desired actions:

**Check:**
- Primary CTA visible above fold with contrasting color
- Action-oriented CTA text ("Get Free Quote" not "Submit")
- 1 primary CTA per viewport (not competing CTAs)
- Minimum 48x48px touch targets
- Phone number: click-to-call on mobile
- Form length appropriate for conversion stage
- Trust signals near CTAs (reviews, guarantees, badges)
- Clear value proposition before asking for action

**Common issues:**
- No clear CTA above the fold
- Phone number not clickable on mobile
- Forms asking for too much information too early
- CTA buttons that look like disabled elements
- Multiple competing CTAs confusing the user

### Step 5: Accessibility (WCAG 2.2 Level AA)

Check compliance with key accessibility requirements:

**Check:**
- Color contrast ratios (4.5:1 normal, 3:1 large text)
- Keyboard navigation (Tab through all interactive elements)
- Focus indicators visible on all interactive elements
- Alt text on all meaningful images
- Form inputs have associated `<label>` elements (not just placeholders)
- Error messages are clear and specific
- Touch targets: 44x44px minimum with 8px spacing (WCAG 2.2)
- Skip navigation link present
- ARIA landmarks on major sections
- Respects `prefers-reduced-motion`
- Usable at 200% zoom without horizontal scrolling
- Link text is meaningful out of context

### Step 6: Mobile Usability

Test the mobile-specific experience:

**Check:**
- Content reflows without horizontal scrolling
- Touch targets appropriately sized and spaced
- Phone numbers are click-to-call
- Forms use appropriate mobile input types (tel, email)
- Images responsive and properly sized
- Popups/modals easy to dismiss
- Sticky elements useful but not obstructing content
- Key actions within thumb-reach zone
- Text readable without zooming

## Scoring Framework

| Category | Weight | Criteria |
|----------|--------|----------|
| Navigation & IA | 20% | Findability, menu structure, breadcrumbs |
| Visual Hierarchy | 20% | Layout, readability, consistency |
| CTAs & Conversion | 20% | CTA visibility, form UX, trust signals |
| Accessibility | 20% | WCAG 2.2 AA compliance |
| Mobile Usability | 20% | Responsive design, touch UX, mobile-specific |

### Score Interpretation

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | Excellent | Intuitive, accessible, conversion-optimized |
| 75-89 | Good | Minor improvements needed |
| 60-74 | Fair | Noticeable UX issues likely affecting conversions |
| 40-59 | Poor | Significant usability problems |
| 0-39 | Critical | Major barriers to user engagement |

## Cross-Skill Integration

- Complements `seo-visual` (which focuses on SEO visual signals, not UX)
- Feeds into `seo-content` via readability and content structure overlap
- Feeds into `seo-technical` via mobile-friendliness and Core Web Vitals overlap
- Triggered by `seo-audit` when comprehensive analysis is requested
- Accessibility findings feed into E-E-A-T Trustworthiness scoring

## Output

> 🎨 **This skill contributes to Pillar 2 — Content & On-Page** in the
> 3-pillar SEO report. UX quality directly impacts user engagement metrics
> (bounce rate, dwell time, conversion rate) which are indirect ranking signals.

### UX Score: XX/100

### Category Breakdown
| Category | Score | Key Findings |
|----------|-------|-------------|
| Navigation & IA | XX/20 | ... |
| Visual Hierarchy | XX/20 | ... |
| CTAs & Conversion | XX/20 | ... |
| Accessibility | XX/20 | ... |
| Mobile Usability | XX/20 | ... |

### Critical Issues (fix immediately)
- [Accessibility barriers, broken navigation, missing CTAs]

### High Priority (fix soon)
- [Significant UX friction points]

### Quick Wins
- [Easy improvements with high impact]

### Detailed Recommendations
- [Specific, actionable improvements with expected impact]

### Screenshots
- `screenshots/desktop_above_fold.png`
- `screenshots/mobile_above_fold.png`
- [Additional annotated screenshots as needed]
