#!/usr/bin/env python3
"""
GTA 6 News Aggregator
Sammelt Nachrichten zu "GTA 6" aus mehreren Quellen (RSS-Feeds) und
schreibt sie dedupliziert + sortiert nach docs/news.json.

Quellen:
- Google News RSS (Query "GTA 6")
- Reddit r/GTA6 RSS
- IGN RSS (Topic: grand-theft-auto-6)
- Rockstar Games Newswire RSS
- PCGamer RSS (gefiltert nach "GTA" im Titel)
- Eurogamer RSS (gefiltert nach "GTA" im Titel)
"""
import json
import hashlib
import datetime as dt
from pathlib import Path

import feedparser
from dateutil import parser as dateparser

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
OUT_FILE = DOCS_DIR / "news.json"
MAX_ITEMS = 150

SOURCES = [
    {
        "name": "Google News",
        "url": "https://news.google.com/rss/search?q=%22GTA%206%22&hl=de&gl=DE&ceid=DE:de",
        "filter": None,
    },
    {
        "name": "Reddit r/GTA6",
        "url": "https://www.reddit.com/r/GTA6/.rss",
        "filter": None,
    },
    {
        "name": "IGN",
        "url": "https://www.ign.com/rss/articles/feed?tag=grand-theft-auto-6",
        "filter": None,
    },
    {
        "name": "Rockstar Newswire",
        "url": "https://www.rockstargames.com/newswire/rss",
        "filter": "gta",
    },
    {
        "name": "PCGamer",
        "url": "https://www.pcgamer.com/rss/",
        "filter": "gta 6",
    },
    {
        "name": "Eurogamer",
        "url": "https://www.eurogamer.net/feed",
        "filter": "gta 6",
    },
    {
        "name": "GameSpot",
        "url": "https://www.gamespot.com/feeds/game/?id=gta-6",
        "filter": None,
    },
]


def item_id(link: str, title: str) -> str:
    return hashlib.sha256((link or title).encode("utf-8")).hexdigest()[:16]


def parse_date(entry) -> str:
    for key in ("published", "updated", "pubDate"):
        val = entry.get(key)
        if val:
            try:
                return dateparser.parse(val).astimezone(dt.timezone.utc).isoformat()
            except Exception:
                pass
    return dt.datetime.now(dt.timezone.utc).isoformat()


def fetch_source(src: dict) -> list[dict]:
    items = []
    try:
        feed = feedparser.parse(src["url"])
    except Exception as e:
        print(f"[WARN] {src['name']}: fetch failed: {e}")
        return items

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue
        if src["filter"] and src["filter"].lower() not in title.lower():
            continue
        summary = entry.get("summary", "")
        items.append(
            {
                "id": item_id(link, title),
                "title": title,
                "link": link,
                "source": src["name"],
                "published": parse_date(entry),
                "summary": summary[:400],
            }
        )
    print(f"[OK] {src['name']}: {len(items)} relevante Einträge")
    return items


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    existing = {}
    if OUT_FILE.exists():
        try:
            data = json.loads(OUT_FILE.read_text())
            for it in data.get("items", []):
                existing[it["id"]] = it
        except Exception:
            pass

    all_items = dict(existing)
    for src in SOURCES:
        for it in fetch_source(src):
            all_items[it["id"]] = it

    sorted_items = sorted(
        all_items.values(), key=lambda x: x["published"], reverse=True
    )[:MAX_ITEMS]

    payload = {
        "updated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "count": len(sorted_items),
        "items": sorted_items,
    }
    OUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"\n{len(sorted_items)} Einträge gespeichert in {OUT_FILE}")


if __name__ == "__main__":
    main()
