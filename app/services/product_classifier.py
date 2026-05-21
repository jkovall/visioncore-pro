from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageFilter, UnidentifiedImageError

_TEXT_HINTS: dict[str, str] = {
    "кроси": "кросівки",
    "кросівки": "кросівки",
    "кроссовки": "кросівки",
    "кеди": "кросівки",
    "sneaker": "кросівки",
    "sneakers": "кросівки",
    "shoes": "взуття",
    "shoe": "взуття",
    "boots": "черевики",
    "boot": "черевики",
    "sandals": "сандалі",
    "bag": "сумка",
    "backpack": "рюкзак",
    "jacket": "куртка",
    "coat": "пальто",
    "t-shirt": "футболка",
    "shirt": "футболка",
    "cap": "кепка",
    "hat": "кепка",
    "watch": "годинник",
    "smartwatch": "смарт-годинник",
    "phone": "смартфон",
    "mobile": "смартфон",
    "tablet": "планшет",
    "laptop": "ноутбук",
    "notebook": "ноутбук",
    "monitor": "монітор",
    "headphone": "навушники",
    "headphones": "навушники",
}

_IMAGE_ONLY_RULES: list[tuple[str, str]] = [
    ("кросівки", "shoe-like dark textured object"),
    ("навушники", "compact dark high-detail object"),
    ("смартфон", "portrait rectangular object"),
    ("монітор", "wide flat display-like object"),
    ("ноутбук", "wide rectangular object"),
]


def classify_product_category(image_bytes: bytes, query: str | None = None, filename: str | None = None) -> dict[str, Any]:
    """Classify a product photo using text hints first, then image heuristics."""
    query_text = _normalize_text(" ".join(part for part in [query or "", _stem_from_filename(filename)] if part))
    image_info = _analyze_image(image_bytes)

    for token, category in _TEXT_HINTS.items():
        if token in query_text:
            return {
                "detected_type": category,
                "search_query": category,
                "detected_categories": [category],
                "detection_source": "text_hint",
                "confidence": 0.97,
                **image_info,
            }

    image_category, confidence = _classify_by_image_features(image_info)
    if image_category != "невідомо":
        return {
            "detected_type": image_category,
            "search_query": image_category,
            "detected_categories": [image_category],
            "detection_source": "image_heuristic",
            "confidence": confidence,
            **image_info,
        }

    return {
        "detected_type": "невідомо",
        "search_query": query_text or "товари",
        "detected_categories": ["невідомо"],
        "detection_source": "ambiguous",
        "confidence": 0.25,
        **image_info,
    }


def _analyze_image(image_bytes: bytes) -> dict[str, Any]:
    try:
        image = Image.open(io.BytesIO(image_bytes))
    except UnidentifiedImageError:
        return {
            "error": "uploaded file is not a supported image",
            "image_size": {"width": 0, "height": 0},
            "aspect_ratio": 0.0,
            "analysis": {},
        }

    image_rgb = image.convert("RGB")
    width, height = image.size
    aspect_ratio = round(width / height, 2) if height else 0.0
    image_array = np.array(image_rgb)

    pixels = image_array.reshape(-1, 3)
    unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
    dominant_color = unique_colors[np.argmax(counts)]

    brightness = float(np.mean(image_array))
    contrast = float(np.std(image_array))

    gray = image_rgb.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edge_array = np.array(edges)
    edge_density = float(np.sum(edge_array > 50) / (width * height)) if width and height else 0.0

    return {
        "image_size": {"width": width, "height": height},
        "aspect_ratio": aspect_ratio,
        "analysis": {
            "brightness": round(brightness, 2),
            "contrast": round(contrast, 2),
            "edge_density": round(edge_density, 4),
            "dominant_color_rgb": [int(dominant_color[0]), int(dominant_color[1]), int(dominant_color[2])],
        },
    }


def _classify_by_image_features(image_info: dict[str, Any]) -> tuple[str, float]:
    analysis = image_info.get("analysis", {})
    aspect_ratio = float(image_info.get("aspect_ratio", 0.0) or 0.0)
    brightness = float(analysis.get("brightness", 0.0) or 0.0)
    contrast = float(analysis.get("contrast", 0.0) or 0.0)
    edge_density = float(analysis.get("edge_density", 0.0) or 0.0)
    dominant = analysis.get("dominant_color_rgb", [0, 0, 0])

    if len(dominant) != 3:
        dominant = [0, 0, 0]
    r, g, b = dominant

    is_dark = brightness < 100
    is_black = r < 50 and g < 50 and b < 50
    is_colorful = max(abs(int(r) - int(g)), abs(int(g) - int(b)), abs(int(r) - int(b))) > 60
    high_contrast = contrast > 50
    high_edge = edge_density > 0.15
    medium_edge = edge_density > 0.08
    is_landscape = aspect_ratio > 1.2
    is_portrait = aspect_ratio < 0.85
    is_square = 0.85 <= aspect_ratio <= 1.2

    if is_dark and high_edge and medium_edge and not is_colorful:
        if contrast > 40 or (is_black and edge_density > 0.12):
            return "взуття", 0.72

    if is_black and high_edge and contrast > 50 and edge_density > 0.10 and 0.9 < aspect_ratio < 1.3:
        return "кросівки", 0.76

    if is_dark or is_black:
        if edge_density > 0.15 and contrast > 40 and (is_square or is_landscape):
            return "навушники", 0.6

    if is_portrait and brightness > 80 and brightness < 180:
        return "смартфон", 0.62

    if is_portrait and (high_contrast or high_edge):
        return "телефон", 0.58

    if is_landscape and brightness > 120 and (not high_edge or edge_density < 0.05):
        return "монітор", 0.57

    if is_landscape and 1.3 < aspect_ratio < 1.7 and brightness > 80 and not (is_dark and high_edge):
        return "ноутбук", 0.55

    if is_landscape and contrast < 40 and brightness > 100:
        return "ноутбук", 0.5

    if is_square and brightness > 100:
        return "невідомо", 0.2

    return "невідомо", 0.15


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _stem_from_filename(filename: str | None) -> str:
    if not filename:
        return ""
    stem = Path(filename).stem.replace("_", " ").replace("-", " ")
    return _normalize_text(stem)
