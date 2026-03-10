# Localsearch SEO Audit Report Template

## Design Language (Localsearch Brand)

### Colours
| Token | Hex | Usage |
|-------|-----|-------|
| `--ls-blue` | `#285aff` | Primary brand, links, headings, Technical pillar |
| `--ls-blue-light` | `#EAEFFF` | Light backgrounds, info badges |
| `--ls-blue-mid` | `#6793EE` | Gradients |
| `--ls-green` | `#40A499` | Content pillar, pass badges |
| `--ls-purple` | `#B164FF` | Authority pillar |
| `--ls-red` | `#f16159` | Errors, high priority |
| `--ls-yellow` | `#ffc414` | Warnings, medium priority |
| `--ls-text` | `#4a4a4a` | Primary text |
| `--ls-text-secondary` | `#757575` | Secondary text |
| `--ls-border` | `#ececec` | Borders, dividers |
| `--ls-bg-light` | `#f8f8f8` | Light backgrounds |

### Typography
- **Font:** Inter (Google Fonts), fallback: -apple-system, BlinkMacSystemFont, sans-serif
- **Body:** 11px (10px print)
- **Headings:** 800 weight for scores, 700 for section headers
- **Line-height:** 1.5

### Design Patterns
- **Border-radius:** 12px (cards/sections), 100px (badges/pills), 8px (code blocks)
- **Shadows:** None (flat design)
- **Gradients:** 135deg linear gradients on headers
- **Cards:** 1px solid #ececec border, 12px radius, 16px padding
- **Badges:** Pill-shaped (100px radius), 9px uppercase text, 600 weight
- **Action items:** Left border accent (4px) colour-coded by priority
- **Note cards:** Yellow left border (4px solid `--ls-yellow`) for contextual observations
- **Green cards:** `card-green` (#e8f5e9 bg) for positive findings and projected outcomes
- **Strengths/Weaknesses:** `flex-row` with two `flex-col` columns, green/red `h4` headers, `check-list` items
- **Pillar headers:** Gradient rounded bar with icon box, nested `pillar-info` (h3 + p subtitle), score right-aligned

### Report Sections (No Implementation Guide)
The report does NOT include a detailed implementation guide — this keeps the PDF concise.
The implementation guide can be generated separately if needed.

### Page Structure
1. **Cover page** - Blue gradient, large score circle, pillar chip scores, meta cards
2. **Executive summary** - 3 pillar cards + overall card (overall last/right), critical issues + quick wins (matching card format), site overview table
3. **Pillar 1** (Technical) - Blue gradient header
4. **Pillar 2** (Content) - Green/teal gradient header
5. **Pillar 3** (Authority) - Purple gradient header
6. **Scoring breakdown** - Weighted table
7. **Action plan** - Priority-grouped action cards (Critical > High > Medium > Low)
8. **Implementation timeline** - Phased roadmap, projected outcome card, Localsearch CTA

## Template Placeholders
Replace `{{PLACEHOLDER}}` values:
- `{{CLIENT_NAME}}`, `{{CLIENT_NAME_LINE1}}`, `{{CLIENT_NAME_LINE2}}`
- `{{DOMAIN}}`, `{{AUDIT_DATE}}`, `{{PAGES_COUNT}}`
- `{{OVERALL_SCORE}}`, `{{TECHNICAL_SCORE}}`, `{{CONTENT_SCORE}}`, `{{AUTHORITY_SCORE}}`
- `{{BUSINESS_TYPE}}`, `{{LOCATION}}`, `{{PLATFORM}}`
- `{{PHONE}}`, `{{EMAIL}}`
- `{{ISSUE_1}}` to `{{ISSUE_5}}`, `{{WIN_1}}` to `{{WIN_5}}`

## Generating PDF
Use Microsoft Edge headless:
```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --headless --disable-gpu \
  --print-to-pdf="OUTPUT.pdf" \
  --print-to-pdf-no-header \
  "file:///PATH/TO/report.html"
```

## Component Reference

### Status Badges
```html
<span class="badge badge-pass">PASS</span>
<span class="badge badge-warn">WARN</span>
<span class="badge badge-fail">FAIL</span>
<span class="badge badge-info">INFO</span>
```

### Priority Badges
```html
<span class="badge badge-critical">CRITICAL</span>
<span class="badge badge-high">HIGH</span>
<span class="badge badge-medium">MEDIUM</span>
<span class="badge badge-low">LOW</span>
```

### Checklist Items
```html
<ul class="check-list">
  <li class="pass">Passed check</li>
  <li class="fail">Failed check</li>
  <li class="warn">Warning check</li>
</ul>
```

### Action Items
```html
<div class="action-item critical no-break">  <!-- or: high, medium, low -->
  <div class="action-header">
    <div class="action-title">1. Title</div>
    <div class="action-meta">
      <span class="badge badge-info">Pillar</span>
      <span class="badge" style="background: var(--ls-bg-light);">Owner</span>
    </div>
  </div>
  <div class="action-body">Description.</div>
</div>
```

### Side-by-Side Columns
```html
<div class="flex-row">
  <div class="flex-col">Left column</div>
  <div class="flex-col">Right column</div>
</div>
```

### Pillar Headers
```html
<div class="pillar-header tech">    <!-- tech (blue), content (green), authority (purple) -->
  <div class="pillar-icon">&#9881;</div>
  <div class="pillar-info">
    <h3>Pillar Title</h3>
    <p>Subtitle</p>
  </div>
  <div class="pillar-score">XX<span>/100</span></div>
</div>
```

### Priority Tags (Implementation Guide)
Used inline within implementation guide cards to show action priority.
```html
<span class="priority-tag priority-critical">CRITICAL</span>
<span class="priority-tag priority-high">HIGH</span>
<span class="priority-tag priority-medium">MEDIUM</span>
<span class="priority-tag priority-low">LOW</span>
```

CSS:
```css
.priority-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 100px;
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.4px;
}
.priority-critical { background: #c62828; color: white; }
.priority-high { background: var(--ls-red); color: white; }
.priority-medium { background: var(--ls-yellow); color: #4a4a4a; }
.priority-low { background: var(--ls-blue-light); color: var(--ls-blue); }
```

### Card Variants
```css
.card       { background: var(--ls-white); border: 1px solid var(--ls-border); border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.card-blue  { background: var(--ls-blue-light); border-color: #d0d9ff; }   /* Implementation guide items */
.card-green { background: #e8f5e9; border-color: #c8e6c9; }               /* Positive outcomes, verification */
```

### Implementation Guide Items
Each action gets a `card card-blue` with priority tag, category/owner badges, h4 sub-headings, and content.

**Standard structure:**
```html
<div class="card card-blue mb-md no-break">
  <div class="card-title">Action #1 &mdash; Title Here</div>
  <div class="card-body mt-sm">
    <p>
      <span class="priority-tag priority-critical" style="margin-right:6px;">CRITICAL</span>
      <span class="badge badge-info">TECHNICAL</span>
      <span class="badge" style="background:#f1f5f9;">DEV</span>
    </p>

    <h4>Background</h4>
    <p>Why this matters...</p>

    <h4>Steps</h4>
    <ol style="padding-left: 16px; line-height: 1.8;">
      <li>Step one</li>
      <li>Step two</li>
    </ol>
  </div>
</div>
```

**With code block** (schema, robots.txt, technical):
```html
<div class="card card-blue mb-md no-break">
  <div class="card-title">Action #3 &mdash; Fix Schema Errors</div>
  <div class="card-body mt-sm">
    <p><span class="priority-tag priority-critical" style="margin-right:6px;">CRITICAL</span> ...</p>
    <h4>Current Issues</h4>
    <ul style="padding-left: 16px; line-height: 1.8;"><li>Issue description</li></ul>
    <h4>Corrected Code</h4>
    <pre>{
  "@context": "https://schema.org",
  "@type": "Organization"
}</pre>
  </div>
</div>
```

**With per-page table** (meta descriptions, H1s):
```html
<div class="card card-blue mb-md no-break">
  <div class="card-title">Action #5 &mdash; Add Meta Descriptions</div>
  <div class="card-body mt-sm">
    <p><span class="priority-tag priority-high" style="margin-right:6px;">HIGH</span> ...</p>
    <h4>Steps</h4>
    <ol style="padding-left: 16px; line-height: 1.8;">
      <li>Open the CMS and navigate to the page</li>
      <li>Add the meta description from the table below</li>
    </ol>
    <p class="mt-sm" style="font-weight: 600;">Recommended text:</p>
    <table style="margin-top: 6px;">
      <tr><td style="width: 120px; font-weight: 600;">Page</td><td>Meta Description</td></tr>
    </table>
  </div>
</div>
```

### Verification Checklist
Placed at the end of the implementation guide section. Uses `card-green`.
```html
<div class="card card-green mb-md no-break">
  <div class="card-title" style="color: #2e7d32;">Post-Implementation Verification Checklist</div>
  <div class="card-body mt-sm">
    <table>
      <thead><tr><th>#</th><th>Check</th><th>Command / Method</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>Check description</td><td><code>curl command or manual method</code></td></tr>
      </tbody>
    </table>
  </div>
</div>
```

### Implementation Timeline
```html
<table>
  <thead>
    <tr><th style="width: 100px;">Timeline</th><th>Tasks</th><th style="width: 90px;">Expected Score</th></tr>
  </thead>
  <tbody>
    <tr>
      <td style="font-weight: 700;">Week 1</td>
      <td>Critical fixes</td>
      <td style="font-weight: 700; color: var(--ls-blue); font-size: 14px;">XX&ndash;XX</td>
    </tr>
  </tbody>
</table>
```

### Need Help CTA
```html
<div class="card no-break" style="border-left: 4px solid var(--ls-blue); margin-top: 16px;">
  <div class="card-title mb-sm" style="color: var(--ls-blue);">Need Help Implementing These Changes?</div>
  <div class="card-body" style="line-height: 1.8;">
    Localsearch can handle the full implementation...
  </div>
</div>
```
