"""Data loading utilities for product catalog and FAQ."""

import json
import re
from pathlib import Path
from typing import List

from src.vector_store.models import FAQEntry, Product


def load_products(catalog_path: Path) -> List[Product]:
    """Load products from JSON catalog file.

    Args:
        catalog_path: Path to product_catalog.json

    Returns:
        List of Product objects

    Raises:
        FileNotFoundError: If catalog file doesn't exist
        json.JSONDecodeError: If catalog file is invalid JSON
    """
    if not catalog_path.exists():
        raise FileNotFoundError(f"Product catalog not found: {catalog_path}")

    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    products = []
    for item in data:
        product = Product(
            id=item["id"],
            name=item["name"],
            type=item["type"],
            brand=item["brand"],
            price_eur=item["price_eur"],
            frame_material=item["frame_material"],
            suspension=item["suspension"],
            wheel_size=item["wheel_size"],
            gears=item["gears"],
            brakes=item["brakes"],
            weight_kg=item["weight_kg"],
            intended_use=item["intended_use"],
            color=item["color"],
            motor_power_w=item.get("motor_power_w"),
            battery_capacity_wh=item.get("battery_capacity_wh"),
            range_km=item.get("range_km"),
            max_load_kg=item.get("max_load_kg"),
        )
        products.append(product)

    return products


def load_faq(faq_path: Path) -> List[FAQEntry]:
    """Load FAQ entries from text file.

    Parses faq.txt format where entries are numbered like:
    1. Question text?
    Answer text.

    Args:
        faq_path: Path to faq.txt

    Returns:
        List of FAQEntry objects

    Raises:
        FileNotFoundError: If FAQ file doesn't exist
    """
    if not faq_path.exists():
        raise FileNotFoundError(f"FAQ file not found: {faq_path}")

    with open(faq_path, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    # Split by numbered entries (e.g., "1. ", "2. ", etc.)
    sections = re.split(r"\n\d+\.\s+", content)

    # Skip the first section (header text before first question)
    for idx, section in enumerate(sections[1:], start=1):
        if not section.strip():
            continue

        # Split into question and answer (question ends with ?)
        lines = section.strip().split("\n")
        question = lines[0].strip()

        # Join remaining lines as answer
        answer = " ".join(line.strip() for line in lines[1:] if line.strip())

        if question and answer:
            entries.append(FAQEntry(id=idx, question=question, answer=answer))

    return entries
