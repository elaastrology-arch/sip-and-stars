# sip & stars — project guide

Bilingual (EN/ES) astrology-readings website for MD (Maria Daniela, IG @mdmundi, TikTok @worldlypenguin, elaastrology@gmail.com). Venezuelan astrologer in Tallinn; readings "over coffee," in person and online.

## Deployment
- **Live at https://elastrology.com** (GitHub Pages, repo `elaastrology-arch/sip-and-stars`, custom domain via CNAME file — never delete it).
- Push to `main` = deploy (~1–2 min). Old github.io URLs 301-redirect automatically.
- Git auth: gh CLI at `/Users/md/.local/bin/gh` (already logged in). If push fails on auth: `/Users/md/.local/bin/gh auth setup-git` and retry.

## Architecture
- **`index.html` is the whole site** — all HTML/CSS/JS/articles inline, no build step, no framework.
- `report.html` — standalone 13-section birth-chart report generator; PDF via html2pdf.js; the unlock code lives in `const FULL_CODE` in report.html. **Never write the code's value in this file or any doc** — GitHub Pages serves every repo file publicly, including this CLAUDE.md.
- `sw.js` — service worker; **bump the cache name** (`sipandstars-vN`) whenever a change must reach clients immediately.
- `tools/build_articles.py` — **run after adding/editing any article**; regenerates `journal/*.html` (one indexable page per article, EN+ES), `sitemap.xml`, `robots.txt`. Commit its output.
- Astro engine: Schlyter low-precision J2000 (verified accurate). Whole-sign houses. Moon computed date-only (no birth time needed); Rising needs time.

## Bilingual system (strict)
- Static text: `data-i18n="key"` attributes; Spanish lives in the single-line JS object `const I18N_ES = {...}` which **must stay valid JSON** — validate after every edit:
  `python3 -c "import re,json;json.loads(re.search(r'const I18N_ES = (\{.*?\});',open('index.html').read(),re.S).group(1))"`
- Dynamic JS output: `L(en, es)` helper + `window.__lang`.
- Spanish voice: warm "tú", neutral Latin American. Reading names stay in English (House Blend, The Refill, Perfect Pairing) — they're menu items.

## Journal articles
- Bodies live in `<div id="articles-src" hidden>`: `<div id="art-N">` (EN) + `<div id="art-N-es">` (ES). N is sequential.
- Card goes in `.journal-grid`; its Read link must be a crawlable anchor:
  `<a class="jread" href="journal/art-N.html" onclick="event.stopPropagation();openArticle('art-N');return false">Read &rarr;</a>`
- Card Spanish: add `art.N.tag/.title/.teaser` keys to I18N_ES.
- Add the article id to the category map (`CAT` in the journal-filter script): basics / moon / love / events / growth.
- Card SVG style: viewBox 0 0 100 100, stroke-width 2.5, currentColor only; solid fills + outlines + one soft halo (opacity .14) + dotted orbit (`stroke-dasharray="1 7"`) + curvy 4-point sparkles. Faces only on outlined shapes.
- Structure: h1 → `<p class="dek">` → intro → 3–5 h2 sections → closing CTA to a reading, ending with ✦.

## Booking & payment
- PayPal pay-to-reserve buttons: `paypal.com/paypalme/Mdmundi/120EUR` (House Blend), `/85EUR` (Refill), `/95EUR` (Pairing). Flow: pay → pick Calendly time.
- Calendly: `calendly.com/elaastrology/90` (both location toggles for now).

## Hard rules (never break)
1. **Never invent testimonials, reviews, client quotes, ratings, or claims** — not even as "placeholder". Only MD adds real ones.
2. **No em-dashes (—) anywhere**, either language. Restructure or use comma/colon/period.
3. No literal `*asterisks*` in prose — use `<em>`/`<strong>`.
4. Before any push: check tag balance (`<section`/`</section>`, `<em>`/`</em>`, `<div>`/`</div>` counts), I18N_ES parses, and no broken onclick ids.
5. Beware regex-wide edits on index.html — a past one deleted commas before dots and silently broke CSS/JS sitewide.
6. Prices/brand/astro math: don't change unless MD asks.
7. **Security**: anything from user input or an external API must go through `esc()` before touching `innerHTML` (helper exists in both index.html and report.html). Both pages ship a `<meta http-equiv="Content-Security-Policy">` — adding a new external script/style/API domain requires updating it or the resource silently fails. External scripts must be version-pinned with an `integrity` (SRI) hash. Fonts are self-hosted in `/fonts` — never reintroduce fonts.googleapis.com links (EU/GDPR). No secrets in any repo file: the public repo AND the live site serve everything, including this CLAUDE.md.

## Voice
Warm, witty, plain-language, lightly literary. Café metaphors woven in, never forced. No jargon. The reader is an astrology-curious millennial/Gen-Z woman.

## Scheduled automation (runs while the Claude app is open)
- `daily-seo-article` (09:01) — writes + publishes one bilingual article/day; instructions at `~/.claude/scheduled-tasks/daily-seo-article/SKILL.md`.
- `daily-site-qa` (19:02) — conservative daily QA; `~/.claude/scheduled-tasks/daily-site-qa/SKILL.md`.

## Local preview
`python3 -m http.server 3000` from the repo root → http://localhost:3000

## Open items (as of July 2026)
- Real testimonials section (waiting on quotes from MD)
- Google Search Console setup (MD's Google login required; submit sitemap.xml)
- Spanish version of report.html; Refill/Pairing report variants
- Formspree endpoint in report.html (`const FORMSPREE = ""`)
- Separate Calendly events per reading type
