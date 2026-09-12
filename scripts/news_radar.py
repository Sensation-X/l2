#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
news_radar.py — ежедневный радар новостей и патчноутов по Lineage 2 (Фогейм).

Что делает:
  1. Обходит список источников (официальные новости/гайды/патчноуты 4game,
     новостной портал lineage2.cc).
  2. Достаёт ссылки и заголовки материалов.
  3. Сравнивает с сохранённым состоянием (seen.json) и выводит ТОЛЬКО новое.
  4. Пишет дайджест в digest/ГГГГ-ММ-ДД.md — его можно скормить ИИ как сырьё.

Запуск:
  python3 scripts/news_radar.py            # показать новое и записать дайджест
  python3 scripts/news_radar.py --reset    # обнулить состояние (первый запуск:
                                           #   всё считается "новым", прогони
                                           #   один раз, чтобы заполнить базу)

Требования: только стандартная библиотека Python 3.8+. Интернет нужен.
Состояние и дайджесты хранятся рядом со скриптом в папке scripts/state/ и digest/.
"""

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
DIGEST_DIR = os.path.join(os.path.dirname(BASE_DIR), "digest")
STATE_FILE = os.path.join(STATE_DIR, "seen.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

# Источники: (название, URL, базовый домен для склейки относительных ссылок)
SOURCES = [
    ("4game: новости", "https://ru.4game.ru/articles/news/", "https://ru.4game.ru"),
    ("4game: гайды", "https://ru.4game.ru/articles/guides/", "https://ru.4game.ru"),
    ("4game: патчноуты Essence", "https://ru.4game.ru/patchnotes/lineage2essence/", "https://ru.4game.ru"),
    ("4game: календарь событий", "https://ru.4game.ru/event-calendar/", "https://ru.4game.ru"),
    ("lineage2.cc: новости", "https://lineage2.cc/news/", "https://lineage2.cc"),
]

# Мусорные фрагменты ссылок, которые не являются материалами
SKIP_PATTERNS = (
    "/legal/", "/webshop/", "#", "javascript:", "mailto:", "/partners/",
    "/install", "vk.com/", "t.me/", "youtube.com/", "/tags/", "/search",
    "cookie", "/user/", "/profile", "support.", "/forum/", "actionpay",
)

# Мусорные заголовки
SKIP_TITLES = (
    "страница не найдена", "не загрузилась", "показать все", "подробнее",
    "читать далее", "все новости", "назад", "вперёд", "меню", "войти",
    "регистрация", "согласен", "принять", "хорошо",
)

LINK_RE = re.compile(
    r"""<a[^>]+href=["']([^"']+)["'][^>]*>(.*?)</a>""", re.I | re.S
)
TAG_RE = re.compile(r"<[^>]+>")


def fetch(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def absolutize(href: str, base_domain: str, page_url: str) -> str:
    href = href.strip()
    if href.startswith("//"):
        return "https:" + href
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base_domain + href
    # относительный путь от текущей страницы
    return page_url.rsplit("/", 1)[0] + "/" + href


def clean_title(raw_html: str) -> str:
    text = TAG_RE.sub(" ", raw_html)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s*\|\s*4game.*$", "", text, flags=re.I)
    return text


def parse_links(page_html: str, page_url: str, base_domain: str):
    items = []
    for href, inner in LINK_RE.findall(page_html):
        href_low = href.lower()
        if any(p in href_low for p in SKIP_PATTERNS):
            continue
        title = clean_title(inner)
        if len(title) < 18 or len(title) > 160:
            continue
        if title.lower() in SKIP_TITLES or any(t in title.lower() for t in SKIP_TITLES):
            continue
        url = absolutize(href, base_domain, page_url)
        if not url.startswith("http"):
            continue
        items.append({"title": title, "url": url, "source": None})
    # дедупликация по URL с сохранением порядка
    seen, out = set(), []
    for it in items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        out.append(it)
    return out


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"seen": {}, "last_run": None}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("seen", {})
        data.setdefault("last_run", None)
        return data
    except (json.JSONDecodeError, OSError):
        return {"seen": {}, "last_run": None}


def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)


def main() -> int:
    ap = argparse.ArgumentParser(description="Радар новостей Lineage 2 / Фогейм")
    ap.add_argument("--reset", action="store_true", help="обнулить состояние")
    ap.add_argument("--no-digest", action="store_true", help="не писать файл дайджеста")
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()

    if args.reset:
        save_state({"seen": {}, "last_run": None})
        print("Состояние сброшено. Следующий запуск поместит все материалы как новые.")
        return 0

    state = load_state()
    seen = state["seen"]
    now = dt.datetime.now()
    fresh, errors, total = [], [], 0

    for name, url, base in SOURCES:
        try:
            page = fetch(url, args.timeout)
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, TimeoutError) as e:
            errors.append(f"{name}: {type(e).__name__} {e}")
            continue
        items = parse_links(page, url, base)
        total += len(items)
        for it in items:
            it["source"] = name
            if it["url"] in seen:
                continue
            seen[it["url"]] = {
                "title": it["title"],
                "first_seen": now.strftime("%Y-%m-%d %H:%M"),
                "source": name,
            }
            fresh.append(it)

    state["last_run"] = now.strftime("%Y-%m-%d %H:%M:%S")
    # держим состояние компактным: максимум 4000 записей
    if len(seen) > 4000:
        for k in list(seen.keys())[: len(seen) - 4000]:
            seen.pop(k, None)
    save_state(state)

    print("=" * 72)
    print(f"Радар новостей L2 — {now.strftime('%d.%m.%Y %H:%M')}")
    print(f"Источников: {len(SOURCES)} | материалов найдено: {total} | новых: {len(fresh)}")
    if errors:
        print("Ошибки доступа:")
        for e in errors:
            print("  !", e)
    print("=" * 72)

    if not fresh:
        print("Нового нет. Проверь источники или запусти с --reset после изменений в списке.")
        return 0

    by_source = {}
    for it in fresh:
        by_source.setdefault(it["source"], []).append(it)

    lines = [
        f"# Дайджест новых материалов — {now.strftime('%d.%m.%Y %H:%M')}",
        "",
        f"Новых материалов: **{len(fresh)}**. Корми этот файл ИИ как сырьё для новостей.",
        "",
    ]
    for src, items in by_source.items():
        print(f"\n--- {src} ({len(items)}) ---")
        lines += [f"## {src}", ""]
        for it in items:
            title = it["title"][:150]
            print(f"  • {title}")
            print(f"    {it['url']}")
            lines += [f"- [{title}]({it['url']})", ""]
        lines += [""]

    if not args.no_digest:
        os.makedirs(DIGEST_DIR, exist_ok=True)
        path = os.path.join(DIGEST_DIR, now.strftime("%Y-%m-%d") + ".md")
        mode = "a" if os.path.exists(path) else "w"
        with open(path, mode, encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print(f"\nДайджест сохранён: {path}")

    print(
        "\nСледующий шаг: скопируй нужные заголовки в промпт «Патч-реакция» "
        "(см. 02_ПРОМПТЫ_ИИ.md) и открой ссылки, чтобы собрать факты."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
