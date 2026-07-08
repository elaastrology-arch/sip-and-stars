#!/usr/bin/env python3
"""
build_articles.py — generates SEO-indexable standalone pages for every journal
article embedded in index.html, plus sitemap.xml and robots.txt.

Run from the repo root (or anywhere):  python3 tools/build_articles.py
Idempotent: safe to re-run after every new article. The daily-seo-article task
runs this after adding an article so Google can index each note individually.
"""
import re, html, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://elastrology.com"
SRC  = os.path.join(ROOT, "index.html")
OUT  = os.path.join(ROOT, "journal")

src = open(SRC, encoding="utf-8").read()

# ---- extract every article block (EN + ES) from the hidden articles-src ----
blocks = re.findall(r'<div id="(art-\d+(?:-es)?)">(.*?)</div>\s*(?=<div id="art-|\s*</div>\s*<script>)',
                    src, re.S)
articles = {aid: body.strip() for aid, body in blocks}

def meta_of(body):
    t = re.search(r"<h1>(.*?)</h1>", body, re.S)
    d = re.search(r'<p class="dek">(.*?)</p>', body, re.S)
    strip = lambda x: re.sub(r"<[^>]+>", "", x or "").strip()
    return strip(t.group(1) if t else ""), strip(d.group(1) if d else "")

PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | sip &amp; stars journal</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{base}/journal/{slug}.html">
<link rel="alternate" hreflang="en" href="{base}/journal/{en_slug}.html">
<link rel="alternate" hreflang="es" href="{base}/journal/{es_slug}.html">
<link rel="alternate" hreflang="x-default" href="{base}/journal/{en_slug}.html">
<link rel="icon" type="image/png" sizes="32x32" href="../icons/favicon-32.png">
<meta property="og:type" content="article">
<meta property="og:site_name" content="sip &amp; stars">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{base}/journal/{slug}.html">
<meta property="og:image" content="{base}/icons/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":{title_json},
"description":{desc_json},"inLanguage":"{lang}",
"image":"{base}/icons/og-image.jpg",
"mainEntityOfPage":"{base}/journal/{slug}.html",
"author":{{"@type":"Person","name":"MD (Maria Daniela)","url":"{base}/#about"}},
"publisher":{{"@type":"Organization","name":"sip & stars","logo":{{"@type":"ImageObject","url":"{base}/icons/icon-512.png"}}}}}}
</script>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; object-src 'none'; base-uri 'self'">
<link href="../fonts/fonts.css" rel="stylesheet">
<style>
:root{{--cream:#F4EFE3;--cream-2:#FBF8F0;--pink:#F2A8C8;--hot:#E55C9A;--green:#1C6B41;--lime:#CDEF49;--ink:#181712;--ink-soft:#4A473E}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--cream);color:var(--ink);font-family:'Hanken Grotesk',sans-serif;font-size:1.02rem;line-height:1.62}}
.top{{display:flex;justify-content:space-between;align-items:center;padding:18px 22px;border-bottom:2px solid var(--ink);background:var(--cream-2)}}
.mark{{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.25rem;color:var(--green);text-decoration:none}}
.mark .amp{{color:var(--hot);font-style:italic}}
.lang-link{{font-weight:700;font-size:.85rem;color:var(--green);text-decoration:none;border:1.6px solid var(--ink);border-radius:999px;padding:6px 14px;background:var(--cream)}}
main{{max-width:680px;margin:0 auto;padding:48px 22px 30px}}
h1{{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:clamp(1.9rem,5vw,2.7rem);line-height:1.04;letter-spacing:-.02em;color:var(--green);margin-bottom:14px}}
.dek{{font-family:'Caveat',cursive;font-weight:600;font-size:1.45rem;line-height:1.3;color:var(--hot);margin-bottom:26px}}
h2{{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.35rem;letter-spacing:-.01em;color:var(--green);margin:30px 0 10px}}
p{{margin-bottom:14px;color:var(--ink-soft)}}
p strong{{color:var(--ink)}} p em{{color:var(--green)}}
.byline{{font-size:.85rem;font-weight:600;color:var(--ink-soft);margin-bottom:34px}}
.cta{{margin:40px 0 10px;background:var(--cream-2);border:1.8px solid var(--ink);border-radius:16px;padding:24px;box-shadow:5px 6px 0 rgba(28,107,65,.16);text-align:center}}
.cta p{{margin-bottom:14px;color:var(--ink)}}
.btn{{display:inline-block;background:var(--green);color:var(--cream-2);font-weight:700;text-decoration:none;border-radius:999px;padding:12px 26px;border:1.8px solid var(--ink)}}
.btn:hover{{background:var(--hot)}}
footer{{text-align:center;padding:26px;font-size:.85rem;color:var(--ink-soft)}}
footer a{{color:var(--green);font-weight:700}}
</style>
</head>
<body>
<nav class="top"><a class="mark" href="../index.html">sip <span class="amp">&amp;</span> stars</a><a class="lang-link" href="{other_slug}.html">{other_label}</a></nav>
<main>
<article>
{body}
</article>
<div class="cta">
<p>{cta_line}</p>
<a class="btn" href="../index.html#book">{cta_btn}</a>
</div>
</main>
<footer>{foot} · <a href="../index.html#journal">{foot_link}</a></footer>
</body>
</html>
"""

import json as _json
count = 0
urls = []
for aid, body in sorted(articles.items(), key=lambda kv: (int(re.search(r"\d+", kv[0]).group()), kv[0])):
    es = aid.endswith("-es")
    en_slug = aid[:-3] if es else aid
    es_slug = en_slug + "-es"
    if es and en_slug not in articles:   # orphan safety
        continue
    if not es and es_slug not in articles:
        es_slug = en_slug                # no ES version: self-reference
    title, desc = meta_of(body)
    if not title:
        continue
    page = PAGE.format(
        lang="es" if es else "en", title=html.escape(title), desc=html.escape(desc),
        title_json=_json.dumps(title, ensure_ascii=False), desc_json=_json.dumps(desc, ensure_ascii=False),
        base=BASE, slug=aid, en_slug=en_slug, es_slug=es_slug,
        other_slug=(en_slug if es else es_slug),
        other_label=("Read in English" if es else "Leer en español"),
        body=body,
        cta_line=("¿Quieres ver qué dice tu propio cielo? Las lecturas suceden con un café, en Tallin u online."
                  if es else "Curious what your own sky says? Readings happen over a coffee, in Tallinn or online."),
        cta_btn=("Reservar una lectura →" if es else "Book a reading →"),
        foot=("Astrología por MD" if es else "Astrology by MD"),
        foot_link=("Más notas del diario" if es else "More notes from the journal"),
    )
    open(os.path.join(OUT, aid + ".html"), "w", encoding="utf-8").write(page)
    urls.append(f"{BASE}/journal/{aid}.html")
    count += 1

# ---- sitemap.xml ----
today = datetime.date.today().isoformat()
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
      f"<url><loc>{BASE}/</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>"]
for u in urls:
    sm.append(f"<url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>")
sm.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm))

# ---- robots.txt ----
open(os.path.join(ROOT, "robots.txt"), "w").write(
    f"User-agent: *\nAllow: /\nDisallow: /report.html\n\nSitemap: {BASE}/sitemap.xml\n")

print(f"built {count} article pages, sitemap ({len(urls)+1} urls), robots.txt")
