"""Ingest the seed AAC vocabulary from ARASAAC into the app's symbols table.

Run from the project root with the project's configured DATABASE_URL:

    python scripts/ingest_seed_symbols.py

The script uses ARASAAC's English best-search endpoint, downloads each chosen
pictogram, renders a labeled card without an image/label divider, and stores the
card path and attribution in
the existing Symbol table. Existing rows are matched by ARASAAC source ID, then
by seed word, so the demo catalog can be upgraded in place and user references
remain intact.
"""

from __future__ import annotations

import logging
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote

import requests
from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data_manager import SessionLocal  # noqa: E402
import data_models as dm  # noqa: E402
from scripts.render_card import CardRenderer  # noqa: E402
from scripts.seed_vocabulary import iter_seed_words  # noqa: E402

API_BASE = "https://api.arasaac.org/api"
IMAGE_DIR = PROJECT_ROOT / "static" / "symbols"
IMAGE_REFERENCE_PREFIX = "static/symbols"
LANGUAGE = "en"
IMAGE_RESOLUTION = 500
REQUEST_TIMEOUT_SECONDS = 20
REQUEST_DELAY_SECONDS = 0.3
ARASAAC_AUTHOR = "Sergio Palao"
ARASAAC_LICENSE = "CC BY-NC-SA 4.0"
ARASAAC_ATTRIBUTION = (
    "Author: Sergio Palao; source: ARASAAC (https://arasaac.org); "
    "license: CC BY-NC-SA 4.0"
)

WORD_CLASS_BY_CATEGORY = {
    "food_drink": "noun",
    "action_request": "verb",
    "emotion": "adjective",
    "greeting_social": "social",
    "person": "noun",
    "place": "noun",
    "toy_activity": "noun",
    "descriptor": "adjective",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("seed_symbol_ingest")


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return value or "symbol"


def get_best_pictogram(word: str, http: requests.Session) -> dict | None:
    url = f"{API_BASE}/pictograms/{LANGUAGE}/bestsearch/{quote(word, safe='')}"
    response = http.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    results = response.json()
    if not isinstance(results, list) or not results:
        return None

    pictogram = results[0]
    if not isinstance(pictogram, dict) or pictogram.get("_id") is None:
        return None
    return pictogram


def download_card(
    pictogram_id: int,
    word: str,
    renderer: CardRenderer,
    http: requests.Session,
) -> str:
    image_url = f"{API_BASE}/pictograms/{pictogram_id}"
    response = http.get(
        image_url,
        params={"resolution": IMAGE_RESOLUTION},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()

    stem = f"arasaac_{pictogram_id}_{slugify(word)}"
    raw_path = IMAGE_DIR / f"{stem}_symbol.png"
    output_path = IMAGE_DIR / f"{stem}_card.png"
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(response.content)
    card = renderer.render_from_bytes(response.content, word)
    card.save(output_path, format="PNG")
    return f"{IMAGE_REFERENCE_PREFIX}/{output_path.name}"


def find_existing_symbol(db, pictogram_id: int, word: str):
    by_source_id = db.scalar(
        select(dm.Symbol).where(
            dm.Symbol.source == "ARASAAC",
            dm.Symbol.source_id == str(pictogram_id),
        )
    )
    if by_source_id is not None:
        return by_source_id

    return db.scalar(
        select(dm.Symbol).where(dm.Symbol.word.ilike(word))
    )


def main() -> int:
    renderer = CardRenderer()
    http = requests.Session()
    missing: list[str] = []
    ingested = 0

    with SessionLocal() as db:
        try:
            for word, category, _default_phase in iter_seed_words():
                try:
                    pictogram = get_best_pictogram(word, http)
                    if pictogram is None:
                        logger.warning("No ARASAAC pictogram found for %r", word)
                        missing.append(word)
                        continue

                    pictogram_id = int(pictogram["_id"])
                    image_reference = download_card(pictogram_id, word, renderer, http)
                    symbol = find_existing_symbol(db, pictogram_id, word)
                    if symbol is None:
                        symbol = dm.Symbol()
                        db.add(symbol)

                    symbol.word = word
                    symbol.word_class = WORD_CLASS_BY_CATEGORY.get(category, "noun")
                    symbol.source = "ARASAAC"
                    symbol.source_id = str(pictogram_id)
                    symbol.image_reference = image_reference
                    symbol.author = ARASAAC_AUTHOR
                    symbol.license = ARASAAC_LICENSE
                    symbol.attribution = ARASAAC_ATTRIBUTION
                    ingested += 1
                    logger.info(
                        "%s | %s | pictogram_id=%s | %s",
                        category,
                        word,
                        pictogram_id,
                        image_reference,
                    )
                except (requests.RequestException, ValueError, OSError):
                    logger.exception("Failed to ingest %r", word)
                    missing.append(word)
                finally:
                    time.sleep(REQUEST_DELAY_SECONDS)

            if ingested == 0:
                db.rollback()
                logger.error("No symbols were ingested; database was not changed.")
                return 1

            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            http.close()

    logger.info("Ingest complete: %d symbols added or updated", ingested)
    if missing:
        logger.warning("Not ingested (%d): %s", len(missing), ", ".join(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
