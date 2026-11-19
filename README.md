# hm_gta6_news

Aggregiert aktuelle **GTA 6**-News aus mehreren Plattformen (Google News, Reddit r/GTA6,
IGN, Rockstar Newswire, PCGamer, Eurogamer, GameSpot) und veröffentlicht sie als
statische, automatisch aktualisierte Website via GitHub Pages.

## Wie es funktioniert

1. `scripts/fetch_news.py` liest alle RSS-Feeds aus, dedupliziert Einträge per Hash
   und schreibt das Ergebnis nach `docs/news.json`.
2. `docs/index.html` lädt `news.json` im Browser und rendert eine einfache Timeline.
3. Eine GitHub Action (`.github/workflows/update-news.yml`) führt das Skript alle
   3 Stunden aus und committed Änderungen automatisch.
4. GitHub Pages served `docs/` als Live-Website.

## Lokal ausführen

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python scripts/fetch_news.py
```

Ergebnis liegt danach in `docs/news.json`.

## Quellen erweitern

Neue Quelle in `scripts/fetch_news.py` im `SOURCES`-Dict ergänzen (RSS-URL +
optionaler Titel-Filter).
