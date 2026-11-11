"""
Compose a PECS-style card: symbol image on top, printed word in a label
band below — from a plain symbol image + its text label.

Why this exists instead of a "database with words already on the images":
every open symbol set (ARASAAC, Sclera, Mulberry, OpenSymbols) intentionally
ships the image and the label as *separate* fields, so the same picture can
be relabeled in any language. Baking text into the pixel data is something
the *consuming app* does at render/print time — this module is that step.

Usage:
    from render_card import CardRenderer

    renderer = CardRenderer()
    renderer.render_from_url(
        image_url="https://static.arasaac.org/pictograms/2368/2368_500.png",
        label="water",
        output_path="cards/water.png",
    )
"""

import io
import logging
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("render_card")

FONT_DIR = Path(__file__).parent / "fonts"
FONT_REGULAR = FONT_DIR / "AtkinsonHyperlegible-Regular.ttf"
FONT_BOLD = FONT_DIR / "AtkinsonHyperlegible-Bold.ttf"


class CardRenderer:
    """
    Composites a symbol image onto a standard PECS-style card layout:
    a white card, the pictogram filling the top ~78%, a bold word label
    centered in a band at the bottom, and a thin outer border. The picture
    and label band have no divider between them.

    Card proportions default to a 4:5 aspect ratio (common physical PECS
    card size, e.g. 8cm x 10cm) so printed sheets stay consistent.
    """

    def __init__(
        self,
        card_width=480,
        card_height=600,
        label_band_ratio=0.22,
        border_color=(30, 30, 30),
        border_width=4,
        background_color=(255, 255, 255),
        label_color=(20, 20, 20),
        max_font_size=64,
        min_font_size=22,
        padding=18,
    ):
        self.card_width = card_width
        self.card_height = card_height
        self.label_band_ratio = label_band_ratio
        self.border_color = border_color
        self.border_width = border_width
        self.background_color = background_color
        self.label_color = label_color
        self.max_font_size = max_font_size
        self.min_font_size = min_font_size
        self.padding = padding

        if not FONT_BOLD.exists():
            raise FileNotFoundError(
                f"Font not found at {FONT_BOLD}. Expected the Atkinson "
                f"Hyperlegible TTF files to already be in {FONT_DIR}."
            )

    def _fit_font(self, draw, text, max_width, max_height):
        """Binary-search the largest font size where `text` fits max_width."""
        lo, hi = self.min_font_size, self.max_font_size
        best = ImageFont.truetype(str(FONT_BOLD), lo)
        while lo <= hi:
            mid = (lo + hi) // 2
            font = ImageFont.truetype(str(FONT_BOLD), mid)
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            if w <= max_width and h <= max_height:
                best = font
                lo = mid + 1
            else:
                hi = mid - 1
        return best

    def render(self, symbol_image: Image.Image, label: str) -> Image.Image:
        """Compose a single card image in memory; returns a PIL Image."""
        card = Image.new("RGB", (self.card_width, self.card_height), self.background_color)
        draw = ImageDraw.Draw(card)

        label_band_height = int(self.card_height * self.label_band_ratio)
        image_area_height = self.card_height - label_band_height - self.padding * 2

        # --- Fit and paste the symbol image, preserving aspect ratio ---
        symbol_image = symbol_image.convert("RGBA")
        available_w = self.card_width - self.padding * 2
        available_h = image_area_height
        scale = min(available_w / symbol_image.width, available_h / symbol_image.height)
        new_size = (max(1, int(symbol_image.width * scale)), max(1, int(symbol_image.height * scale)))
        resized = symbol_image.resize(new_size, Image.LANCZOS)

        paste_x = (self.card_width - new_size[0]) // 2
        paste_y = self.padding + (available_h - new_size[1]) // 2
        card.paste(resized, (paste_x, paste_y), resized)

        # --- Label band (no divider line between the picture and label) ---
        band_top = self.card_height - label_band_height
        font = self._fit_font(
            draw, label.upper(),
            max_width=self.card_width - self.padding * 2,
            max_height=label_band_height - self.padding,
        )
        bbox = draw.textbbox((0, 0), label.upper(), font=font)
        text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        text_x = (self.card_width - text_w) // 2
        text_y = band_top + (label_band_height - text_h) // 2 - bbox[1]
        draw.text((text_x, text_y), label.upper(), font=font, fill=self.label_color)

        # --- Card border ---
        draw.rectangle(
            [0, 0, self.card_width - 1, self.card_height - 1],
            outline=self.border_color, width=self.border_width,
        )

        return card

    def render_from_bytes(self, image_bytes: bytes, label: str) -> Image.Image:
        symbol_image = Image.open(io.BytesIO(image_bytes))
        return self.render(symbol_image, label)

    def render_from_url(self, image_url: str, label: str, output_path: str, timeout=8):
        resp = requests.get(image_url, timeout=timeout)
        resp.raise_for_status()
        card = self.render_from_bytes(resp.content, label)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        card.save(output_path)
        logger.info("Rendered card: %s -> %s", label, output_path)
        return output_path

    def render_from_path(self, image_path: str, label: str, output_path: str):
        symbol_image = Image.open(image_path)
        card = self.render(symbol_image, label)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        card.save(output_path)
        logger.info("Rendered card: %s -> %s", label, output_path)
        return output_path
