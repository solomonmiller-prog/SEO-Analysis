# Project Memory

## User: smiller (Localsearch)
- Works at Localsearch (digital marketing company, Australia)
- Runs SEO audits for clients
- Projects folder: `C:\Users\smiller\Projects\SEO Audits\`

## SEO Audit PDF Template
- **Location:** `C:\Users\smiller\Projects\SEO Audits\_template\`
- `SEO-Audit-Template.html` - Reusable HTML template with `{{PLACEHOLDER}}` variables
- `README.md` - Design language reference, component docs, PDF generation instructions
- **Design:** Localsearch brand colours (#285aff blue, #40A499 green, #B164FF purple)
- **Font:** Inter (Google Fonts)
- **Layout:** Cover page with large score circle > Executive summary (3 pillar cards + overall last) > Pillar sections > Scoring breakdown > Action plan > Priority matrix
- **PDF generation:** Edge headless: `msedge.exe --headless --disable-gpu --print-to-pdf="OUT.pdf" --print-to-pdf-no-header "file:///PATH/report.html"`
- See `_template/README.md` for full component reference

## Duda Platform Notes
- Duda renders visible text in TWO span style patterns:
  - `display: unset` = headings, nav labels, taglines (small portion of content)
  - `display: initial` = body paragraphs, FAQ answers, descriptions (bulk of content)
- **Must grep for BOTH**: `grep -o '<span[^>]*display: \(unset\|initial\)[^>]*>[^<]*</span>'`
- **Boilerplate removal:** Extract text from 3+ different page types, find common LINES
  via `comm -12`, then remove those exact lines with `grep -vxF` before counting.
  Do NOT use a flat word deduction — page-specific headings vary per page.
  Typical boilerplate: nav links, footer service categories, membership badges, ABN.
- Always spot-check extracted text against rendered page to verify completeness

## Environment
- Windows 11, Git Bash shell
- No Python/Node installed; Java (OpenJDK 25) available
- Microsoft Edge available at `/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`
- WebFetch tool gets 403 from some sites (Localsearch, Duda-hosted); use `curl -A "Mozilla/5.0..."` via Bash instead

## Completed Audits
- `michaelduncanconstructions.com.au` (2026-03-09) - Gold Coast builder, Duda/Localsearch, Score 52/100
- `belmontcarline.com.au` (2026-03-09) - Belmont NSW mechanic/exhausts, Duda, Score 58/100
