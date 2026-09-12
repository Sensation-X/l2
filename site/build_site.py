#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_site.py — собирает статический сайт «Хурмыч» из markdown-файлов.
Только стандартная библиотека Python. На выходе папка site/dist/ — готовая
статика, которую можно залить на любой хостинг (FTP/rsync/nginx).

Запуск:  python3 site/build_site.py
Структура:
  site/content/articles/*.md   статьи (frontmatter: title, date, tags, version, desc)
  site/content/pages/*.md      служебовые страницы (start.md, about.md)
  site/assets/                 style.css, site.js
  brand/                       эмблема и превью (копируются в dist/assets/img/)

Что генерируется: index.html, guides.html, updates.html, статьи, страницы,
rss.xml, sitemap.xml, robots.txt.
"""
import os
import re
import html
import shutil
import datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # папка проекта
SITE = os.path.join(ROOT, "site")
CONTENT = os.path.join(SITE, "content")
DIST = os.path.join(SITE, "dist")
ASSETS = os.path.join(SITE, "assets")

SITE_URL = "https://hurmych.ru"          # домен зарегистрирован 12.09.2026
TG_URL = "https://t.me/hurmych"
YT_URL = "https://www.youtube.com/@hurmych"
REF_LINK = "#REF#"                        # вставь реферальную ссылку, когда её выдаст партнёрка

MAINT = {"dow": 2, "h": 10, "m": 0}       # среда 10:00 МСК — еженедельная профилактика
UPDATES = [                                # проверено по официальным анонсам 11.09.2026
    ("2026-10-14", "Replica", "Lineage 2 Main"),
    ("2026-10-21", "Forged in Battle", "Lineage 2 Essence и Special Project"),
    ("2026-10-28", "Cruma Tower", "Lineage 2 Legacy (Classic)"),
]

CSS = "assets/style.css"
JS = "assets/site.js"


# ---------------------------------------------------------------- markdown
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', t)
    return t


def md_to_html(src):
    out, lines = [], src.split("\n")
    i, n = 0, len(lines)
    while i < n:
        ln = lines[i]
        if ln.startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
            continue
        if ln.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<div class=tablewrap><table><thead><tr>" +
                       "".join(f"<th>{inline(c)}</th>" for c in head) +
                       "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows) +
                       "</tbody></table></div>")
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lv = len(m.group(1))
            out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>")
            i += 1
            continue
        if ln.startswith("> "):
            buf = []
            while i < n and lines[i].startswith("> "):
                buf.append(lines[i][2:]); i += 1
            out.append("<blockquote>" + inline(" ".join(buf)) + "</blockquote>")
            continue
        if re.match(r"^[-*] ", ln):
            buf = []
            while i < n and re.match(r"^[-*] ", lines[i]):
                buf.append("<li>" + inline(lines[i][2:]) + "</li>"); i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue
        if re.match(r"^\d+\. ", ln):
            buf = []
            while i < n and re.match(r"^\d+\. ", lines[i]):
                buf.append("<li>" + inline(re.sub(r"^\d+\. ", "", lines[i])) + "</li>"); i += 1
            out.append("<ol>" + "".join(buf) + "</ol>")
            continue
        if ln.strip() in ("---", "***"):
            out.append("<hr>"); i += 1; continue
        if not ln.strip():
            i += 1; continue
        buf = [ln]
        i += 1
        while i < n and lines[i].strip() and not re.match(r"^(#|\||>|-|\d+\.|```)", lines[i]):
            buf.append(lines[i]); i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")
    return "\n".join(out)


def parse_doc(path):
    txt = open(path, encoding="utf-8").read()
    meta = {}
    if txt.startswith("---"):
        end = txt.index("---", 3)
        for line in txt[3:end].strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        txt = txt[end + 3:]
    return meta, txt


# ---------------------------------------------------------------- шаблон
def page(title, desc, body, canonical, og="assets/img/og_1200x630.png"):
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE_URL}/{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="{SITE_URL}/{og}">
<meta property="og:type" content="article">
<link rel="icon" type="image/png" href="assets/img/tg_avatar_512.png">
<link rel="alternate" type="application/rss+xml" title="Хурмыч" href="{SITE_URL}/rss.xml">
<link rel="stylesheet" href="{CSS}">
</head>
<body>
<header class="top">
  <a class="logo" href="index.html"><img src="assets/img/tg_avatar_512.png" alt=""><span>ХУРМЫЧ</span></a>
  <nav>
    <a href="guides.html">Гайды</a>
    <a href="updates.html">Обновления</a>
    <a href="start.html">Начать играть</a>
    <a href="about.html">О проекте</a>
    <a class="tg" href="{TG_URL}" rel="noopener">Telegram</a>
  </nav>
</header>
<main>{body}</main>
<footer>
  <div class="fgrid">
    <div>
      <strong>Хурмыч</strong> — фанатский медиапроект о Lineage 2 на платформе Фогейм.
      Не является официальным ресурсом. Lineage® — товарный знак NC Corporation;
      лицензиат в РФ и СНГ — ООО «Мир Хобби».
    </div>
    <div>
      <a href="{TG_URL}">Telegram</a> · <a href="{YT_URL}">YouTube</a> · <a href="rss.xml">RSS</a><br>
      Реклама и сотрудничество: {TG_URL.replace('https://t.me/','@')}
    </div>
    <div class="fine">Все материалы датированы и привязаны к номеру обновления.
      Данные проверяются по официальным источникам перед публикацией.</div>
  </div>
</footer>
<script src="{JS}"></script>
</body>
</html>"""


ARTICLES, PAGES = [], []


def build():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(os.path.join(DIST, "assets", "img"), exist_ok=True)
    os.makedirs(os.path.join(DIST, "a"), exist_ok=True)
    shutil.copy(os.path.join(ASSETS, "style.css"), os.path.join(DIST, "assets", "style.css"))
    shutil.copy(os.path.join(ASSETS, "site.js"), os.path.join(DIST, "assets", "site.js"))
    for src, dst in [("emblem_hurmych.png", "tg_avatar_512.png"),
                     ("banner_2560x1440.png", "banner.png"),
                     ("og_1200x630.png", "og_1200x630.png")]:
        shutil.copy(os.path.join(ROOT, "brand", src), os.path.join(DIST, "assets", "img", dst))

    adir = os.path.join(CONTENT, "articles")
    for fn in sorted(os.listdir(adir)):
        if not fn.endswith(".md"):
            continue
        meta, txt = parse_doc(os.path.join(adir, fn))
        meta["slug"] = fn[:-3]
        ARTICLES.append((meta, txt))
    ARTICLES.sort(key=lambda x: x[0].get("date", ""), reverse=True)

    for meta, txt in ARTICLES:
        body = article_body(meta, txt)
        write(f"a/{meta['slug']}.html",
              page(meta["title"], meta.get("desc", ""), body, f"a/{meta['slug']}.html"))

    pdir = os.path.join(CONTENT, "pages")
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".md"):
            continue
        meta, txt = parse_doc(os.path.join(pdir, fn))
        slug = fn[:-3]
        body = f'<article class="doc"><h1>{inline(meta["title"])}</h1>{md_to_html(txt)}</article>'
        if slug == "start":
            body = cta_ref() + body
        write(f"{slug}.html", page(meta["title"], meta.get("desc", ""), body, f"{slug}.html"))

    write("index.html", page("Хурмыч — Lineage 2 Essence и Main: гайды, патчи, экономика",
                             "Разборы обновлений в день выхода, классы, экономика и фарм в Lineage 2 на Фогейме. Без воды: цифры, даты, номера патчей.",
                             home_body(), "index.html"))
    write("guides.html", page("Гайды по Lineage 2 — Хурмыч", "Все гайды и разборы: классы, серверы, прокачка, экономика, промокоды.",
                              guides_body(), "guides.html"))
    write("updates.html", page("Календарь обновлений Lineage 2 — Хурмыч",
                               "Даты обновлений и еженедельных профилактик Lineage 2 на Фогейме с таймерами.",
                               updates_body(), "updates.html"))

    # rss
    items = []
    for meta, txt in ARTICLES[:20]:
        link = f"{SITE_URL}/a/{meta['slug']}.html"
        items.append(f"<item><title>{html.escape(meta['title'])}</title><link>{link}</link>"
                     f"<guid>{link}</guid><pubDate>{meta.get('date','')}</pubDate>"
                     f"<description>{html.escape(meta.get('desc',''))}</description></item>")
    write("rss.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
          f"<title>Хурмыч</title><link>{SITE_URL}</link>"
          "<description>Lineage 2 Essence и Main: гайды, патчи, экономика</description>"
          + "".join(items) + "</channel></rss>", raw=True)

    # sitemap
    urls = ["index.html", "guides.html", "updates.html", "start.html", "about.html"] + \
           [f"a/{m['slug']}.html" for m, _ in ARTICLES]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
          + "".join(f"<url><loc>{SITE_URL}/{u}</loc></url>" for u in urls) + "</urlset>", raw=True)
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", raw=True)
    print(f"Сайт собран: {DIST} — страниц: {len(urls)}")


def write(name, content, raw=False):
    p = os.path.join(DIST, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(content)


def cta_ref():
    return (f'<section class="cta"><h3>Начать играть с бонусами</h3>'
            f'<p>Регистрация по партнёрской ссылке канала даёт стартовые бонусы в игре и поддерживает проект.</p>'
            f'<a class="btn" href="{REF_LINK}" rel="noopener nofollow">Создать аккаунт и забрать бонусы</a>'
            f'<p class="fine">Бонусы начисляются только новым аккаунтам и вернувшимся после 90 дней отсутствия.</p></section>')


def home_body():
    cards = "".join(card(m) for m, _ in ARTICLES[:6])
    feats = """
    <section class="feats">
      <div><h3>⚡ Патчи в день выхода</h3><p>Разбор обновления в течение часа: что изменилось и что делать игроку.</p></div>
      <div><h3>🗓 Календарь и таймеры</h3><p>Даты обновлений и еженедельной профилактики с обратным отсчётом.</p></div>
      <div><h3>⚔️ Классы и билды</h3><p>Кого брать под твой стиль игры: соло, группа, PvP, фарм с автобоем.</p></div>
      <div><h3>💰 Экономика</h3><p>Еженедельный срез рынка: что фармить, что продавать, что подорожало.</p></div>
      <div><h3>🎁 Ивенты и промокоды</h3><p>Что можно забрать прямо сейчас и как это активировать.</p></div>
      <div><h3>🔎 Всё с датой и патчем</h3><p>Каждый материал помечен датой актуальности — устаревшее не маскируется под свежее.</p></div>
    </section>"""
    return f"""
<section class="hero">
  <h1>ХУРМЫЧ</h1>
  <p class="tag">Lineage 2 на Фогейме: Essence и Main. Гайды, патчи, экономика — без воды.</p>
  <div class="counters">
    <div class="cd" data-maint><span class="cdv">—</span><span class="cdl">до профилактики (ср 10:00 МСК)</span></div>
    <div class="cd" data-date="2026-10-14T10:00"><span class="cdv">—</span><span class="cdl">до обновления Replica (Main)</span></div>
    <div class="cd" data-date="2026-10-21T10:00"><span class="cdv">—</span><span class="cdl">до Forged in Battle (Essence)</span></div>
  </div>
  <div class="heroactions">
    <a class="btn" href="start.html">Начать играть</a>
    <a class="btn ghost" href="{TG_URL}" rel="noopener">Читать в Telegram</a>
  </div>
</section>
{cta_ref()}
<section class="latest"><h2>Свежие материалы</h2><div class="grid">{cards}</div>
<p class="more"><a href="guides.html">Все гайды и разборы →</a></p></section>
{feats}"""


def card(meta):
    tags = meta.get("tags", "")
    return (f'<a class="card" href="a/{meta["slug"]}.html">'
            f'<span class="meta">{meta.get("date","")} · {meta.get("version","")}</span>'
            f'<h3>{inline(meta["title"])}</h3><p>{inline(meta.get("desc",""))}</p>'
            f'<span class="tags">{tags}</span></a>')


def guides_body():
    cards = "".join(card(m) for m, _ in ARTICLES)
    return (f'<section class="doc"><h1>Гайды и разборы</h1>'
            f'<input id="q" class="search" placeholder="Поиск по гайдам: класс, сервер, прокачка…">'
            f'<div class="grid" id="cards">{cards}</div></section>')


def updates_body():
    rows = "".join(f"<tr><td>{d}</td><td><strong>{n}</strong></td><td>{v}</td>"
                   f"<td><span class='cd' data-date='{d}T10:00'><span class='cdv'>—</span></span></td></tr>"
                   for d, n, v in UPDATES)
    return f"""<section class="doc"><h1>Календарь обновлений и профилактик</h1>
<p>Даты официальных осенних обновлений для российских серверов. В состав войдут все патчи,
вышедшие в Корее с 4 июня по 26 августа 2026 включительно. Полные патчноуты публикуются ближе к релизу —
разбор каждого выйдет в день выхода.</p>
<div class="tablewrap"><table><thead><tr><th>Дата</th><th>Обновление</th><th>Версия</th><th>Осталось</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<h2>Еженедельная профилактика</h2>
<p>Серверы недоступны каждую <strong>среду с 10:00 до 12:00 МСК</strong>. В это окно выходят мелкие правки и
хотфиксы — их разбор публикуется в Telegram в день профилактики.</p>
<div class="cd big" data-maint><span class="cdv">—</span><span class="cdl">до ближайшей профилактики</span></div>
<h2>Что уже вышло в 2026</h2>
<ul>
<li><strong>Celestial Destiny</strong> (29.07.2026, Essence) — улучшение классов и Битва серверов</li>
<li><strong>Throne</strong> (16.07.2026, Main)</li>
<li><strong>Antharas Rising</strong> (24.07.2026, Legacy)</li>
<li>Обновление Essence от 09.09.2026 — чёрные купоны, бонус +100% опыта, изменения Цитадели Кельбима</li>
</ul>
<p class="fine">Даты и состав обновлений уточняются официальными анонсами. Страница обновляется после каждого патча.</p>
</section>"""


def article_body(meta, txt):
    nxt = ""
    for i, (m, _) in enumerate(ARTICLES):
        if m["slug"] == meta["slug"] and i + 1 < len(ARTICLES):
            n = ARTICLES[i + 1][0]
            nxt = f'<p class="more"><a href="{n["slug"]}.html">← {inline(n["title"])}</a></p>'
    return (f'<article class="doc"><header class="ahead">'
            f'<span class="meta">{meta.get("date","")} · {meta.get("version","")} · {meta.get("tags","")}</span>'
            f'<h1>{inline(meta["title"])}</h1>'
            f'<p class="desc">{inline(meta.get("desc",""))}</p></header>'
            f'{md_to_html(txt)}'
            f'<p class="fine">Данные актуальны на {meta.get("date","")}. Источник: официальные материалы Фогейма и база знаний Lineage 2.</p>'
            f'{cta_ref()}{nxt}</article>')


if __name__ == "__main__":
    build()
