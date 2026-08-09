#!/usr/bin/env python3
"""
gen_site_pages.py — Ummanitarian Insight
Membangun: (1) grid terpotong index.html + pagination, (2) halaman arsip page-2..N,
(3) search-index.json untuk pencarian client-side.

Idempotent: kartu dibaca dari index.html + halaman page-N yang sudah ada,
di-dedupe per href (urutan index.html menang), urutan editorial dipertahankan,
lalu di-chunk PER_PAGE per halaman. Aman dijalankan ulang setelah publish.

Aturan keras: TIDAK mengubah hero, ticker, about band, footer, style, atau isi
artikel — hanya blok grid, pagination, kotak search, dan <head> halaman arsip.

Usage: python3 scripts/gen_site_pages.py [--per-page N] [--dry-run]
"""
import argparse, glob, json, os, re, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, "index.html")
PER_PAGE = 10

# ---------- anchors ----------
GRID_OPEN = '<div class="articles-grid">'
GRID_END = "<!-- ARTICLE GRID END -->"
HERO_BLOCK = re.compile(r"<!-- HERO START -->[\s\S]*?<!-- HERO END -->")
CARD_RE = re.compile(r"(<!--[^>]*-->\s*)?<article class=\"article-card\"[\s\S]*?</article>", re.S)
HEADER_TOP = '<div class="header-top">'
HEADER_END = '<div class="header-tagline">Humanitarian knowledge, plainly told.</div>\n  </div>'
STYLE_END = "</style>"
BODY_END = "</body>"
TITLE_RE = re.compile(r"<title>.*?</title>")
CANONICAL_RE = re.compile(r'<link rel="canonical"[^>]*>')
INLINE_SCRIPT_RE = re.compile(r"<script>(.*?)</script>", re.S)

SEARCH_HTML = """    <div class="header-search" role="search">
      <input id="search-input" type="search" placeholder="Search insights…" aria-label="Search insights" autocomplete="off">
      <div id="search-results"></div>
    </div>
"""

SEARCH_CSS = """
  /* ===== SEARCH (generated) ===== */
  .header-search { position: relative; margin-left: 0; margin-right: 1.5rem; }
  .header-top { gap: 1.5rem; position: relative; z-index: 20; }
  .header-tagline { margin-right: auto; }
  #search-input { font-family: 'DM Sans', sans-serif; font-size: 0.82rem; padding: 0.42rem 1rem; border: 1px solid var(--rule); border-radius: 999px; background: var(--cream-dark); color: var(--ink); width: 210px; outline: none; transition: border-color .15s, background .15s; }
  #search-input:focus { border-color: var(--red); background: var(--cream); }
  #search-results { display: none; position: absolute; top: calc(100% + 8px); right: 0; width: min(430px, 88vw); background: var(--cream); border: 1px solid var(--rule); border-radius: 10px; box-shadow: 0 10px 30px rgba(26,20,16,.14); max-height: 70vh; overflow-y: auto; z-index: 99; }
  #search-results.open { display: block; }
  .search-result { display: block; padding: .7rem .95rem; border-bottom: 1px solid var(--rule); text-decoration: none; color: inherit; }
  .search-result:last-child { border-bottom: none; }
  .search-result:hover { background: var(--cream-dark); }
  .sr-cat { font-family: 'DM Sans', sans-serif; font-size: .58rem; font-weight: 500; letter-spacing: .16em; text-transform: uppercase; color: var(--red); }
  .sr-title { font-weight: 600; font-size: .92rem; line-height: 1.35; margin-top: .2rem; }
  .sr-deck { font-size: .78rem; line-height: 1.5; color: var(--ink-light); margin-top: .25rem; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  .search-empty { padding: .85rem .95rem; color: var(--ink-light); font-size: .85rem; }
  /* ===== PAGINATION (generated) ===== */
  .pagination { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1.4rem 0 0; margin: 3rem 0 4rem; border-top: 1px solid var(--rule); }
  .page-numbers { display: flex; gap: .35rem; flex-wrap: wrap; }
  .page-num { min-width: 2.1rem; height: 2.1rem; display: inline-flex; align-items: center; justify-content: center; border: 1px solid var(--rule); border-radius: 6px; font-size: .85rem; text-decoration: none; color: var(--ink); font-family: 'DM Sans', sans-serif; }
  .page-num.active { background: var(--red); border-color: var(--red); color: #fff; }
  .page-num:hover:not(.active) { border-color: var(--ink); }
  .page-link { font-size: .85rem; text-decoration: none; color: var(--ink); white-space: nowrap; font-family: 'DM Sans', sans-serif; }
  .page-link.disabled { opacity: .35; pointer-events: none; }
  .sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
  @media (max-width: 860px) {
    .header-tagline { display: none; }
    #search-input { width: 118px; }
    .header-search { margin-right: .8rem; }
    .pagination { flex-wrap: wrap; justify-content: center; }
  }
"""

ARCHIVE_SCRIPT = """<script>
(function(){
  var navLinks = document.querySelectorAll('nav a[data-filter]');
  var miniCards = document.querySelectorAll('.mini-card[data-category]');
  var articleCards = document.querySelectorAll('.articles-grid .article-card[data-category]');
  function filterAll(cat){
    miniCards.forEach(function(c){ c.style.display = (cat==='all'||c.dataset.category===cat)?'':'none'; });
    articleCards.forEach(function(c){ c.style.display = (cat==='all'||c.dataset.category===cat)?'':'none'; });
    navLinks.forEach(function(a){ a.classList.remove('active'); });
    var t = document.querySelector('nav a[data-filter="'+cat+'"]'); if (t) t.classList.add('active');
  }
  navLinks.forEach(function(link){
    link.addEventListener('click', function(e){ e.preventDefault(); filterAll(this.dataset.filter); });
  });
})();
</script>"""


def strip_tags(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def extract_cards(html_text):
    """Ambil kartu + komentar pendahulunya, dedupe per href, urutan dipertahankan."""
    cards, seen = [], set()
    for m in CARD_RE.finditer(html_text):
        block = m.group(0)
        href_m = re.search(r'href="([^"]+)"', block)
        key = href_m.group(1) if href_m else block[:80]
        if key in seen:
            continue
        seen.add(key)
        cards.append(block)
    return cards


def card_to_index_entry(card):
    href_m = re.search(r'href="([^"]+)"', card)
    title_m = re.search(r'<h2 class="card-headline"[^>]*>(.*?)</h2>', card, re.S)
    deck_m = re.search(r'<p class="card-deck"[^>]*>(.*?)</p>', card, re.S)
    cat_m = re.search(r'<span class="card-category"[^>]*>(.*?)</span>', card, re.S)
    meta_m = re.search(r'<div class="card-meta"[^>]*>(.*?)</div>', card, re.S)
    date = ""
    if meta_m:
        raw = strip_tags(meta_m.group(1))
        date = raw.split("·")[0].split("Source:")[0].strip()
    return {
        "url": href_m.group(1) if href_m else "",
        "title": strip_tags(title_m.group(1)) if title_m else "",
        "deck": strip_tags(deck_m.group(1)) if deck_m else "",
        "category": strip_tags(cat_m.group(1)) if cat_m else "",
        "date": date,
    }


def pagination_nav(current, total):
    if total <= 1:
        return ""
    prev_html = f'<a class="page-link prev" href="{"/" if current==2 else f"/page-{current-1}/"}" aria-label="Newer articles">&larr; Newer</a>' if current > 1 else '<span class="page-link prev disabled" aria-disabled="true">&larr; Newer</span>'
    next_html = f'<a class="page-link next" href="/page-{current+1}/" aria-label="Older articles">Older &rarr;</a>' if current < total else '<span class="page-link next disabled" aria-disabled="true">Older &rarr;</span>'
    nums = []
    for n in range(1, total + 1):
        href = "/" if n == 1 else f"/page-{n}/"
        cls = ' class="page-num active"' if n == current else ' class="page-num"'
        nums.append(f'<a{cls} href="{href}">{n}</a>')
    return (
        '<nav class="pagination" aria-label="Pagination">\n'
        f"  {prev_html}\n"
        '  <div class="page-numbers">\n    '
        + "\n    ".join(nums)
        + f'\n  </div>\n  {next_html}\n'
        "</nav>"
    )


def assert_anchor(html_text, anchor, label):
    if anchor not in html_text:
        sys.exit(f"[FAIL] anchor tidak ditemukan: {label}")


def inject_common(html_text):
    """Injeksi yang berlaku di SEMUA halaman: kotak search, CSS, script search.js.
    Idempotent — aman dijalankan berulang pada file yang sudah ter-injeksi."""
    if 'header-search' not in html_text:
        html_text, n = re.subn(re.escape(HEADER_END), HEADER_END + "\n" + SEARCH_HTML, html_text, count=1)
        assert n == 1, "sisip search gagal"
    if '/* ===== SEARCH (generated) ===== */' not in html_text:
        html_text, n = re.subn(re.escape(STYLE_END), SEARCH_CSS + "\n" + STYLE_END, html_text, count=1)
        assert n == 1, "sisip CSS gagal"
    if '<script src="/search.js"></script>' not in html_text:
        html_text, n = re.subn(re.escape(BODY_END), '<script src="/search.js"></script>\n' + BODY_END, html_text, count=1)
        assert n == 1, "sisip script gagal"
    return html_text


def main():
    global PER_PAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-page", type=int, default=10)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    PER_PAGE = args.per_page

    index = open(INDEX, encoding="utf-8").read()
    assert_anchor(index, GRID_OPEN, "grid open")
    assert_anchor(index, GRID_END, "grid end")
    assert_anchor(index, HEADER_TOP, "header-top")
    assert_anchor(index, STYLE_END, "style end")
    assert_anchor(index, BODY_END, "body end")

    # 1) kumpulkan semua kartu: index.html dulu, lalu page-N yang sudah ada
    cards = extract_cards(index)
    seen_hrefs = set()
    for c in cards:
        m = re.search(r'href="([^"]+)"', c)
        if m:
            seen_hrefs.add(m.group(1))
    for p in sorted(glob.glob(os.path.join(REPO, "page-*", "index.html"))):
        for c in extract_cards(open(p, encoding="utf-8").read()):
            m = re.search(r'href="([^"]+)"', c)
            if m and m.group(1) not in seen_hrefs:
                seen_hrefs.add(m.group(1))
                cards.append(c)

    total_cards = len(cards)
    total_pages = max(1, -(-total_cards // PER_PAGE))
    print(f"kartu: {total_cards} | per halaman: {PER_PAGE} | total halaman: {total_pages}")

    # 2) search-index.json
    search_index = [card_to_index_entry(c) for c in cards]
    search_index = [e for e in search_index if e["url"] and e["title"]]
    si_path = os.path.join(REPO, "search-index.json")
    with open(si_path, "w", encoding="utf-8") as f:
        json.dump(search_index, f, ensure_ascii=False, indent=1)
    print(f"search-index.json: {len(search_index)} entri")

    if args.dry_run:
        for n in range(1, total_pages + 1):
            chunk = cards[(n - 1) * PER_PAGE : n * PER_PAGE]
            print(f"  [dry] page {n}: {len(chunk)} kartu")
        return

    grid_re = re.compile(r'(<div class="articles-grid">).*?(\s*</div>\s*<!-- ARTICLE GRID END -->)', re.S)

    def build_grid(chunk):
        return GRID_OPEN + "\n    " + "\n    ".join(chunk).replace("\n", "\n    ") + "\n  </div>\n  " + GRID_END

    def insert_pagination(html_text, current, total):
        pag = pagination_nav(current, total)
        if not pag:
            return html_text
        # buang pagination lama dulu (idempotent), lalu sisip yang baru
        html_text, _ = re.subn(r"<!-- PAGINATION -->[\s\S]*?</nav>", "", html_text, count=1)
        html_text, n = re.subn(r"(" + re.escape(GRID_END) + r")", r"\1\n\n  <!-- PAGINATION -->\n" + pag, html_text, count=1)
        assert n == 1, f"sisip pagination page {current} gagal"
        return html_text

    # 3) susun ulang index.html (halaman 1) — dari index ASLI
    new_index = inject_common(index)
    new_grid = build_grid(cards[:PER_PAGE])
    new_index, n1 = grid_re.subn(lambda m: new_grid, new_index, count=1)
    assert n1 == 1, "ganti grid index.html gagal"
    new_index = insert_pagination(new_index, 1, total_pages)
    open(INDEX, "w", encoding="utf-8").write(new_index)
    print("index.html: grid terpangkas + pagination + search OK")

    # 4) halaman arsip page-2..N — basis: index ASLI + injeksi search
    existing = sorted(
        glob.glob(os.path.join(REPO, "page-*")),
        key=lambda p: int((m := re.search(r"page-(\d+)", p)) and m.group(1) or 0),
    )
    for n in range(2, total_pages + 1):
        chunk = cards[(n - 1) * PER_PAGE : n * PER_PAGE]
        page = inject_common(index)
        page, _ = HERO_BLOCK.subn("  <!-- HERO (archive page) -->\n", page, count=1)
        page, _ = TITLE_RE.subn(f"<title>Insights — Page {n} · Ummanitarian Insight</title>", page, count=1)
        page, _ = CANONICAL_RE.subn(f'<link rel="canonical" href="https://insight.ummanitarian.org/page-{n}/">', page, count=1)
        page, cnt = grid_re.subn(lambda m: build_grid(chunk), page, count=1)
        assert cnt == 1, f"ganti grid page-{n} gagal"
        page = insert_pagination(page, n, total_pages)
        page, cnt = re.subn(r'(<div class="articles-grid">)', f'  <h1 class="sr-only">Ummanitarian Insights — Page {n}</h1>\n  \\1', page, count=1)
        assert cnt == 1, f"sisip h1 page-{n} gagal"
        page, cnt = INLINE_SCRIPT_RE.subn(ARCHIVE_SCRIPT, page, count=1)
        assert cnt == 1, f"ganti script page-{n} gagal"
        pdir = os.path.join(REPO, f"page-{n}")
        os.makedirs(pdir, exist_ok=True)
        open(os.path.join(pdir, "index.html"), "w", encoding="utf-8").write(page)
        print(f"page-{n}: {len(chunk)} kartu OK")

    # 5) hapus halaman yang tidak terpakai
    keep = {os.path.join(REPO, f"page-{n}") for n in range(2, total_pages + 1)}
    for p in existing:
        if p not in keep:
            import shutil
            shutil.rmtree(p)
            print(f"hapus {os.path.basename(p)} (stale)")


if __name__ == "__main__":
    main()
