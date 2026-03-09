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

### Page Structure
1. **Cover page** - Blue gradient, large score circle, pillar chip scores, meta cards
2. **Executive summary** - 3 pillar cards + overall card (overall last/right), critical issues + quick wins
3. **Pillar 1** (Technical) - Blue gradient header
4. **Pillar 2** (Content) - Green/teal gradient header
5. **Pillar 3** (Authority) - Purple gradient header
6. **Scoring breakdown** - Weighted table
7. **Action plan** - Priority-grouped action cards (Critical > High > Medium > Low)
8. **Implementation guide** - Step-by-step how-to instructions, code snippets, timeline table, Localsearch CTA

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

### Implementation Guide Items
Three variants for different content types:

**Basic steps:**
```html
<div class="subsection">
  <h3>1. Guide Title (Action #X)</h3>
  <div class="card no-break">
    <div class="card-title mb-sm">Steps in {{PLATFORM}}</div>
    <div class="card-body">
      <ol style="padding-left: 16px; line-height: 1.8;">
        <li>Step one</li>
      </ol>
    </div>
  </div>
</div>
```

**With code block** (schema, robots.txt, technical):
```html
<div class="card no-break">
  <div class="card-body">
    <ol style="padding-left: 16px; line-height: 1.8;">
      <li>Step one</li>
      <li>Paste the following code:</li>
    </ol>
    <pre>Code here</pre>
    <ol start="3" style="padding-left: 16px; line-height: 1.8;">
      <li>Save and publish</li>
    </ol>
  </div>
</div>
```

**With per-page table** (meta descriptions, H1s):
```html
<div class="card no-break">
  <div class="card-body">
    <p class="mt-sm" style="font-weight: 600;">Recommended text:</p>
    <table style="margin-top: 6px;">
      <tr><td style="width: 120px; font-weight: 600;">Page</td><td>Text</td></tr>
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
