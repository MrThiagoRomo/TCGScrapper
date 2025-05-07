# TCGplayer Deck Bulk‑Exporter

Export every Magic: The Gathering deck that belongs to a specific author on [https://decks.tcgplayer.com](https://decks.tcgplayer.com) to individual, plain‑text lists that you can paste into Archidekt, Moxfield, or any other deck‑builder.

---

## Features

* Crawls **all** paginated search‑result pages for the chosen player.
* Opens each deck in a real Chromium window (easy to watch & solve CAPTCHAs).
* Waits for the JavaScript‑rendered card list, then saves a file named:

```
./<player>/<Deck Title>.txt      →   "2 Sol Ring" style lines
```

* Skips (with a warning) any deck that takes longer than 20 s to load.

---

## Requirements

| Tool            | Version | Notes                           |
| --------------- | ------- | ------------------------------- |
| Python          | 3.9 +   | Tested on Steam OS (Arch)       |
| Playwright      | 1.44.0  | Bundles its own Chromium/driver |
| BeautifulSoup 4 | latest  | HTML parsing                    |

> **Linux only?** The script is cross‑platform; the visible‑browser version was tuned on a Steam Deck but works on macOS/Windows with Python ≥ 3.9.

---

## Quick start

```bash
# 1 · clone / copy this repo

# 2 · (option) create a venv
python -m venv venv
source venv/bin/activate

# 3 · install dependencies
pip install playwright==1.44.0 beautifulsoup4
playwright install chromium

# 4 · run! (opens a window you can watch)
python export_tcgplayer_decks.py
```

### Export a different player

```bash
TCG_PLAYER="wizards-of-the-coast" python export_tcgplayer_decks.py
```

### Headless / faster mode

Edit the two lines at the top of the script:

```python
browser = await pw.chromium.launch(headless=True, slow_mo=0)
page.set_default_timeout(30_000)        # optional: shorten timeouts
```

---

## Output structure

```
./the-commander-s-quarters/
  Adeliz the Cinder Wind  The Commanders Quarters.txt
  Slimefoot the Stowaway  The Commanders Quarters.txt
  …
```

Each file contains one card per line, in the common `"<qty> <card name>"` format accepted by Mass Entry boxes and deck importers.

---

## Troubleshooting

| Symptom                                     | Fix                                                                                                                                    |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Timeout while loading a deck**            | The script prints `⚠ deck page too slow – skipped`.  Re‑run later, increase the per‑deck timeout, or enable headless `slow_mo=0`.      |
| **Cloudflare "checking your browser" loop** | Run with the visible window, solve the CAPTCHA once.  Consider lowering the crawl rate (`slow_mo`) or exporting in smaller batches.    |
| **Mismatch qty/name**                       | TCGplayer changed their CSS classes – inspect a deck, then adjust `CARD_SELECTOR_QTY` / `CARD_SELECTOR_NAME` at the top of the script. |

---

## Respecting TCGplayer’s Terms

This exporter is intended for **personal backup and analysis only**.  Automated extraction for commercial or public redistribution likely violates TCGplayer’s TOS – read their rules and stay polite with request rates.

---

## License

MIT – see `LICENSE` in this repo.  No warranty; use at your own risk.

---

## Contributing

Issues, PRs, or selector updates for layout changes are welcome.  Open an issue, describe the breakage, and include a sample deck URL (mask the final digits if it’s private).
