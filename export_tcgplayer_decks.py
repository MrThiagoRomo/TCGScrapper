#!/usr/bin/env python3
"""
export_tcgplayer_decks.py
-------------------------

Bulk‑export every MTG deck owned by <PLAYER> on decks.tcgplayer.com.

• crawls all search‑result pages
• opens each deck, waits for card rows to render
• writes   ./<player>/<deck title>.txt   with lines like  '2 Sol Ring'

Tested on Steam Deck (Arch Linux) with Playwright 1.44.
"""

import asyncio, os, pathlib, re, sys
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PwTimeout

PLAYER   = os.getenv("TCG_PLAYER", "the-commander-s-quarters")   
BASE_URL = f"https://decks.tcgplayer.com/magic/deck/search?player={PLAYER}"

OUTROOT  = pathlib.Path(PLAYER)
OUTROOT.mkdir(exist_ok=True)

SEARCH_ANCHOR      = "table.dataTable a[href^='/magic/']"  
CARD_SELECTOR_QTY  = ".subdeck-group__card-qty"
CARD_SELECTOR_NAME = ".subdeck-group__card-name"


def slug(text: str) -> str:
    """Return a filesystem‑safe version of *text* (max 80 chars)."""
    return re.sub(r"[^\w\-. ]+", "", text).strip()[:80]


async def scrape():
    async with async_playwright() as pw:

        browser = await pw.chromium.launch(headless=False, slow_mo=200)
        page    = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.set_default_timeout(60_000) 

        deck_urls, page_no = set(), 1

        while True:
            url = f"{BASE_URL}&page={page_no}"
            print(f"[search] {url}")
            await page.goto(url)

            try:
                await page.wait_for_selector("table.dataTable tbody tr", timeout=15_000)
            except PwTimeout:
                print("   ⚠  results grid never appeared (timeout/Captcha?)")
                break

            soup  = BeautifulSoup(await page.content(), "html.parser")
            links = [
                a["href"] for a in soup.select(SEARCH_ANCHOR)
                if f"/{PLAYER}/" in a["href"] and re.search(r"/\d+$", a["href"])
            ]
            print(f"   …found {len(links)} deck links on page {page_no}")

            for href in links:
                deck_urls.add("https://decks.tcgplayer.com" + href)

            if not soup.select_one("a.nextPage"):
                break
            page_no += 1

        total = len(deck_urls)
        print(f"\nCollected {total} deck URLs – fetching decks …\n")

        for idx, deck_url in enumerate(sorted(deck_urls), 1):
            print(f"[{idx:>4}/{total}] {deck_url}")
            try:
                await page.goto(deck_url, wait_until="domcontentloaded")
                await page.wait_for_selector(CARD_SELECTOR_QTY, timeout=20_000)
            except PwTimeout:
                print("     ⚠  deck page too slow – skipped")
                continue

            dsoup = BeautifulSoup(await page.content(), "html.parser")
            header = dsoup.select_one(".viewDeckHeader h1")
            if not header:
                print("     !  deck title missing – skipped")
                continue

            title_slug = slug(header.get_text(strip=True))
            qtys  = [q.get_text()           for q in dsoup.select(CARD_SELECTOR_QTY)]
            names = [n.get_text(strip=True) for n in dsoup.select(CARD_SELECTOR_NAME)]
            if len(qtys) != len(names):
                print("     !  mismatch qty/name – skipped")
                continue

            outfile = OUTROOT / f"{title_slug}.txt"
            outfile.write_text(
                "\n".join(f"{q} {n}" for q, n in zip(qtys, names)),
                encoding="utf‑8",
            )
            print(f"     ✓ saved {outfile}")

        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(scrape())
    except KeyboardInterrupt:
        sys.exit(0)
