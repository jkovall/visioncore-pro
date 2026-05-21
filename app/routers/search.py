"""Product search endpoints"""
import os
import base64
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
import httpx
import requests
from PIL import Image, ImageOps, ImageFilter
from bs4 import BeautifulSoup
import io
import re
import json
import urllib.parse
import numpy as np

from app.services.product_classifier import classify_product_category
from app.database import get_database
from datetime import datetime

router = APIRouter()

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")

# Mock product database for demonstration
MOCK_PRODUCTS = {
    "laptop": [
        {"title": "ASUS VivoBook 15 Ноутбук", "price": "$399.99", "platform": "amazon"},
        {"title": "Dell Inspiron 15 Комп'ютер", "price": "$349.99", "platform": "ebay"},
        {"title": "HP 15 Портативний комп'ютер", "price": "$289.99", "platform": "aliexpress"},
        {"title": "Lenovo IdeaPad 3 Ноутбук", "price": "$429.99", "platform": "amazon"},
        {"title": "ACER Aspire 5 Ноутбук", "price": "$499.99", "platform": "ebay"},
    ],
    "ноутбук": [
        {"title": "ASUS VivoBook 15 Ноутбук", "price": "$399.99", "platform": "amazon"},
        {"title": "Dell Inspiron 15 Комп'ютер", "price": "$349.99", "platform": "ebay"},
        {"title": "HP 15 Портативний комп'ютер", "price": "$289.99", "platform": "aliexpress"},
        {"title": "Lenovo IdeaPad 3 Ноутбук", "price": "$429.99", "platform": "amazon"},
        {"title": "ACER Aspire 5 Ноутбук", "price": "$499.99", "platform": "ebay"},
    ],
    "phone": [
        {"title": "iPhone 15 Pro Max", "price": "$1199.99", "platform": "amazon"},
        {"title": "Samsung Galaxy S24", "price": "$999.99", "platform": "ebay"},
        {"title": "Google Pixel 8 Pro", "price": "$899.99", "platform": "aliexpress"},
        {"title": "OnePlus 12 Смартфон", "price": "$799.99", "platform": "amazon"},
    ],
    "телефон": [
        {"title": "iPhone 15 Pro Max", "price": "$1199.99", "platform": "amazon"},
        {"title": "Samsung Galaxy S24", "price": "$999.99", "platform": "ebay"},
        {"title": "Google Pixel 8 Pro", "price": "$899.99", "platform": "aliexpress"},
        {"title": "OnePlus 12 Смартфон", "price": "$799.99", "platform": "amazon"},
    ],
    "смартфон": [
        {"title": "iPhone 15 Pro Max", "price": "$1199.99", "platform": "amazon"},
        {"title": "Samsung Galaxy S24", "price": "$999.99", "platform": "ebay"},
        {"title": "Google Pixel 8 Pro", "price": "$899.99", "platform": "aliexpress"},
        {"title": "OnePlus 12 Смартфон", "price": "$799.99", "platform": "amazon"},
    ],
    "headphones": [
        {"title": "Sony WH-1000XM5 Навушники", "price": "$399.99", "platform": "amazon"},
        {"title": "Bose QuietComfort 45", "price": "$379.99", "platform": "ebay"},
        {"title": "Apple AirPods Pro", "price": "$249.99", "platform": "aliexpress"},
        {"title": "JBL Live Pro 2", "price": "$199.99", "platform": "amazon"},
    ],
    "навушники": [
        {"title": "Sony WH-1000XM5 Навушники", "price": "$399.99", "platform": "amazon"},
        {"title": "Bose QuietComfort 45", "price": "$379.99", "platform": "ebay"},
        {"title": "Apple AirPods Pro", "price": "$249.99", "platform": "aliexpress"},
        {"title": "JBL Live Pro 2", "price": "$199.99", "platform": "amazon"},
    ],
    "watch": [
        {"title": "Apple Watch Series 9", "price": "$399.99", "platform": "amazon"},
        {"title": "Samsung Galaxy Watch 6", "price": "$299.99", "platform": "ebay"},
        {"title": "Garmin Forerunner 965", "price": "$599.99", "platform": "aliexpress"},
    ],
    "годинник": [
        {"title": "Apple Watch Series 9", "price": "$399.99", "platform": "amazon"},
        {"title": "Samsung Galaxy Watch 6", "price": "$299.99", "platform": "ebay"},
        {"title": "Garmin Forerunner 965", "price": "$599.99", "platform": "aliexpress"},
    ],
    "смарт-годинник": [
        {"title": "Apple Watch Series 9", "price": "$399.99", "platform": "amazon"},
        {"title": "Samsung Galaxy Watch 6", "price": "$299.99", "platform": "ebay"},
        {"title": "Garmin Forerunner 965", "price": "$599.99", "platform": "aliexpress"},
    ],
    "розумний годинник": [
        {"title": "Apple Watch Series 9", "price": "$399.99", "platform": "amazon"},
        {"title": "Samsung Galaxy Watch 6 Розумний", "price": "$299.99", "platform": "ebay"},
    ],
    "планшет": [
        {"title": "iPad Pro 12.9 Планшет", "price": "$1099.99", "platform": "amazon"},
        {"title": "Samsung Galaxy Tab S9", "price": "$799.99", "platform": "ebay"},
        {"title": "iPad Air Планшет", "price": "$599.99", "platform": "aliexpress"},
    ],
    "монітор": [
        {"title": "LG UltraWide 34 Монітор", "price": "$499.99", "platform": "amazon"},
        {"title": "Dell UltraSharp 27 Монітор", "price": "$399.99", "platform": "ebay"},
        {"title": "ASUS ProArt Монітор", "price": "$599.99", "platform": "aliexpress"},
    ],
    "клавіатура": [
        {"title": "Logitech MX Keys Pro", "price": "$99.99", "platform": "amazon"},
        {"title": "Corsair K95 Клавіатура", "price": "$199.99", "platform": "ebay"},
        {"title": "Razer BlackWidow Elite", "price": "$169.99", "platform": "aliexpress"},
    ],
    "мишка": [
        {"title": "Logitech MX Master 3S", "price": "$99.99", "platform": "amazon"},
        {"title": "Corsair Scimitar Pro RGB", "price": "$79.99", "platform": "ebay"},
        {"title": "Razer DeathAdder V3", "price": "$69.99", "platform": "aliexpress"},
    ],
    "мобільний телефон": [
        {"title": "iPhone 15 Pro Max", "price": "$1199.99", "platform": "amazon"},
        {"title": "Samsung Galaxy S24 Мобільний", "price": "$999.99", "platform": "ebay"},
    ],
    "мобільник": [
        {"title": "iPhone 15 Pro Max Мобільник", "price": "$1199.99", "platform": "amazon"},
        {"title": "Samsung Galaxy S24 Мобільник", "price": "$999.99", "platform": "ebay"},
    ],
    "навушники-бутони": [
        {"title": "Apple AirPods Pro", "price": "$249.99", "platform": "amazon"},
        {"title": "Samsung Galaxy Buds2 Бутони", "price": "$149.99", "platform": "ebay"},
        {"title": "Sony WF-C700N Бутони", "price": "$198.00", "platform": "aliexpress"},
    ],
    "бездротові навушники": [
        {"title": "Sony WH-1000XM5 Бездротові", "price": "$399.99", "platform": "amazon"},
        {"title": "Bose QuietComfort 45 Бездротові", "price": "$379.99", "platform": "ebay"},
    ],
    "гарнітура": [
        {"title": "Sony WH-1000XM5 Гарнітура", "price": "$399.99", "platform": "amazon"},
        {"title": "Bose QuietComfort 45 Гарнітура", "price": "$379.99", "platform": "ebay"},
    ],
    "слухавки": [
        {"title": "Sony WH-1000XM5 Слухавки", "price": "$399.99", "platform": "amazon"},
        {"title": "Bose QuietComfort 45 Слухавки", "price": "$379.99", "platform": "ebay"},
    ],
    "портативний комп'ютер": [
        {"title": "ASUS VivoBook 15", "price": "$399.99", "platform": "amazon"},
        {"title": "Dell Inspiron 15 Портативний", "price": "$349.99", "platform": "ebay"},
    ],
    "комп'ютер": [
        {"title": "Desktop PC Custom", "price": "$799.99", "platform": "amazon"},
        {"title": "Gaming Desktop", "price": "$1299.99", "platform": "ebay"},
    ],
    "дисплей": [
        {"title": "LG 27 Дисплей", "price": "$299.99", "platform": "amazon"},
        {"title": "Dell 24 Дисплей", "price": "$249.99", "platform": "ebay"},
    ],
    "екран": [
        {"title": "LG 34 Екран", "price": "$499.99", "platform": "amazon"},
        {"title": "ASUS 27 Екран", "price": "$349.99", "platform": "ebay"},
    ],
    "веб-камера": [
        {"title": "Logitech C922 Веб-камера", "price": "$79.99", "platform": "amazon"},
        {"title": "Corsair Elgato Камера", "price": "$99.99", "platform": "ebay"},
    ],
    "мікрофон": [
        {"title": "Blue Yeti USB Мікрофон", "price": "$99.99", "platform": "amazon"},
        {"title": "Audio-Technica AT2020 Мікрофон", "price": "$99.00", "platform": "ebay"},
    ],
    "портативна колонка": [
        {"title": "JBL Charge 5 Колонка", "price": "$179.99", "platform": "amazon"},
        {"title": "Bose SoundLink Mini Портативна", "price": "$99.99", "platform": "ebay"},
    ],
    "кросівки": [
        {"title": "Nike Air Max 90 Кросівки", "price": "$129.99", "platform": "amazon"},
        {"title": "Adidas Ultraboost 22 Чоловічі", "price": "$139.99", "platform": "ebay"},
        {"title": "New Balance 574 Кросівки", "price": "$89.99", "platform": "aliexpress"},
        {"title": "Skechers Go Walk Comfort", "price": "$69.99", "platform": "amazon"},
        {"title": "Puma RS-X Sneakers", "price": "$74.99", "platform": "ebay"},
    ],
    "взуття": [
        {"title": "Nike Air Max 90 Взуття", "price": "$129.99", "platform": "amazon"},
        {"title": "Adidas Ultraboost Взуття", "price": "$139.99", "platform": "ebay"},
        {"title": "Converse Chuck Taylor Ботинки", "price": "$59.99", "platform": "aliexpress"},
        {"title": "Timberland 6 Inch Boots", "price": "$179.99", "platform": "amazon"},
        {"title": "Dr. Martens Mens Boots", "price": "$149.99", "platform": "ebay"},
    ],
}

def generate_amazon_search_link(query: str, product_data: dict = None) -> dict:
    """Generate Amazon search link with mock product data"""
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.amazon.com/s?k={encoded_query}"
    
    # Find matching products from mock database
    products = []
    query_lower = query.lower()
    
    # Try both Ukrainian and English versions
    for key, items in MOCK_PRODUCTS.items():
        if key in query_lower or query_lower in key:
            for item in items[:3]:
                if item["platform"] == "amazon":
                    products.append({
                        "title": item["title"],
                        "price": item["price"],
                        "url": f"{search_url}&ref=sr_pg_1",
                        "source": "Amazon",
                        "platform": "amazon"
                    })
    
    # Add generic Amazon link if no products found
    if not products:
        products.append({
            "title": f"Результати пошуку за запитом: {query}",
            "price": "Різні ціни",
            "url": search_url,
            "source": "Amazon",
            "platform": "amazon"
        })
    
    return products

def generate_ebay_search_link(query: str) -> list:
    """Generate eBay search link with mock product data"""
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_query}"
    
    products = []
    query_lower = query.lower()
    
    for key, items in MOCK_PRODUCTS.items():
        if key in query_lower or query_lower in key:
            for item in items[:3]:
                if item["platform"] == "ebay":
                    products.append({
                        "title": item["title"],
                        "price": item["price"],
                        "url": f"{search_url}&LH_PrefLoc=3",
                        "source": "eBay",
                        "platform": "ebay"
                    })
    
    if not products:
        products.append({
            "title": f"Результати пошуку за запитом: {query}",
            "price": "Різні ціни",
            "url": search_url,
            "source": "eBay",
            "platform": "ebay"
        })
    
    return products

def generate_aliexpress_search_link(query: str) -> list:
    """Generate AliExpress search link with mock product data"""
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.aliexpress.com/wholesale?SearchText={encoded_query}"
    
    products = []
    query_lower = query.lower()
    
    for key, items in MOCK_PRODUCTS.items():
        if key in query_lower or query_lower in key:
            for item in items[:3]:
                if item["platform"] == "aliexpress":
                    products.append({
                        "title": item["title"],
                        "price": item["price"],
                        "url": search_url,
                        "source": "AliExpress",
                        "platform": "aliexpress"
                    })
    
    if not products:
        products.append({
            "title": f"Результати пошуку за запитом: {query}",
            "price": "Різні ціни",
            "url": search_url,
            "source": "AliExpress",
            "platform": "aliexpress"
        })
    
    return products

async def search_amazon_products(query: str) -> dict:
    """Search Amazon for products with prices"""
    try:
        products = generate_amazon_search_link(query)
        return {
            "provider": "amazon",
            "query": query,
            "status": "success" if products else "no_results",
            "products": products
        }
    except Exception as e:
        return {"provider": "amazon", "status": "error", "error": str(e), "products": []}

async def search_ebay_products(query: str) -> dict:
    """Search eBay for products with prices"""
    try:
        products = generate_ebay_search_link(query)
        return {
            "provider": "ebay",
            "query": query,
            "status": "success" if products else "no_results",
            "products": products
        }
    except Exception as e:
        return {"provider": "ebay", "status": "error", "error": str(e), "products": []}

async def search_aliexpress_products(query: str) -> dict:
    """Search AliExpress for products with prices"""
    try:
        products = generate_aliexpress_search_link(query)
        return {
            "provider": "aliexpress",
            "query": query,
            "status": "success" if products else "no_results",
            "products": products
        }
    except Exception as e:
        return {"provider": "aliexpress", "status": "error", "error": str(e), "products": []}

async def detect_product_category(image_bytes: bytes, query: str = "", filename: str | None = None) -> dict:
    """Детальний аналіз фотографії для визначення типу товару."""
    try:
        return classify_product_category(image_bytes=image_bytes, query=query, filename=filename)
    except Exception as e:
        return {
            "error": str(e),
            "detected_type": "невідомо",
            "search_query": query or "товари",
            "detected_categories": ["невідомо"],
        }

def detect_product_type_by_features(dominant_color, brightness, contrast, 
                                   edge_density, aspect_ratio, r_channel, 
                                   g_channel, b_channel) -> str:
    """
    Визначає тип товару на основі аналізу характеристик зображення
    """
    
    # Розпаковування домінуючого кольору
    r, g, b = dominant_color[0], dominant_color[1], dominant_color[2]
    
    # Обчислення параметрів кольору
    is_dark = brightness < 100
    is_black = r < 50 and g < 50 and b < 50
    is_grey = abs(int(r) - int(g)) < 20 and abs(int(g) - int(b)) < 20
    is_colorful = max(abs(int(r) - int(g)), abs(int(g) - int(b)), abs(int(r) - int(b))) > 60
    
    # Аналіз текстури та контрастності
    high_contrast = contrast > 50
    high_edge = edge_density > 0.15
    medium_edge = edge_density > 0.08
    
    # Аналіз пропорцій
    is_landscape = aspect_ratio > 1.2
    is_portrait = aspect_ratio < 0.85
    is_square = 0.85 <= aspect_ratio <= 1.2
    
    # ===== КРОСІВКИ / ВЗУТТЯ =====
    if is_dark and high_edge and medium_edge and not is_colorful:
        if contrast > 40 or (is_black and edge_density > 0.12):
            return "взуття"
    
    if is_black and high_edge and contrast > 50 and edge_density > 0.10:
        if aspect_ratio > 0.9 and aspect_ratio < 1.3:
            return "кросівки"
    
    # ===== НАВУШНИКИ =====
    if is_dark or is_black:
        if edge_density > 0.15 and contrast > 40:
            if is_square or is_landscape:
                return "навушники"
    
    if high_edge and edge_density > 0.12 and (brightness < 110 or (is_black and contrast > 50)):
        return "навушники"
    
    # ===== СМАРТФОН / ТЕЛЕФОН =====
    if is_portrait:  # Портретна орієнтація
        if brightness > 80 and brightness < 180:
            return "смартфон"
    
    if is_portrait and (high_contrast or high_edge):
        return "телефон"
    
    # ===== ПЛАНШЕТ =====
    if is_landscape and brightness > 70 and brightness < 200:
        if not high_edge:
            return "планшет"
    
    if is_square and brightness > 100:
        return "планшет"
    
    # ===== МОНІТОР / ЕКРАН =====
    if is_landscape and brightness > 120:
        if not high_edge or edge_density < 0.05:
            return "монітор"
    
    # ===== НОУТБУК =====
    if is_landscape and 1.3 < aspect_ratio < 1.7:
        if brightness > 80 and not (is_dark and high_edge):
            return "ноутбук"
    
    if is_landscape and contrast < 40:
        return "ноутбук"
    
    # ===== КОЛОНКА / ДИНАМІК =====
    if is_dark and is_square:
        if edge_density > 0.15 and high_contrast:
            return "портативна колонка"
    
    # ===== ГОДИННИК =====
    if is_square or is_landscape:
        if brightness < 100 and edge_density > 0.12:
            if contrast > 45:
                return "годинник"
    
    # ===== КАМЕРА / ВЕККАМЕРА =====
    if brightness > 100 and brightness < 160:
        if not high_edge and not is_colorful:
            if is_square or is_landscape:
                return "веб-камера"
    
    # Стандартний варіант
    return "невідомо"

@router.post("/search/by-file-id")
async def search_by_file_id(file_id: str, query: str = ""):
    """
    Пошук схожих товарів за завантаженим зображенням.
    Повертає реальні товари з цінами та посиланнями для покупки.
    
    Args:
        file_id: Унікальний ідентифікатор завантаженого зображення
        query: Необов'язковий пошуковий запит для уточнення результатів
    
    Returns:
        Список товарів на Amazon, eBay, AliExpress з цінами та посиланнями
    """
    try:
        # Пошук завантаженого файлу
        uploaded_file = None
        if os.path.exists(UPLOADS_DIR):
            for filename in os.listdir(UPLOADS_DIR):
                if filename.startswith(file_id):
                    uploaded_file = os.path.join(UPLOADS_DIR, filename)
                    break
        
        if not uploaded_file or not os.path.exists(uploaded_file):
            raise HTTPException(status_code=404, detail=f"Файл зображення не знайдено: {file_id}")
        
        # Читання зображення
        with open(uploaded_file, "rb") as f:
            image_bytes = f.read()
        
        # Аналіз зображення для визначення типу товару
        category_info = await detect_product_category(image_bytes, query=query, filename=os.path.basename(uploaded_file))

        # Check for user feedback override in the database
        try:
            db = get_database()
            feedback = await db["feedback"].find_one({"file_id": file_id})
            if feedback and feedback.get("correct_category"):
                # Override detected type and search query
                category_info["detected_type"] = feedback.get("correct_category")
                category_info["note"] = "overridden_by_feedback"
        except Exception:
            # If DB not available or other error, ignore feedback
            pass

        # Check for global corrections mapping (e.g., map common mislabels like "ноутбук"->"монітор")
        try:
            db = get_database()
            detected = category_info.get("detected_type")
            if detected:
                gc = await db["global_corrections"].find_one({"from": detected.lower()})
                if gc and gc.get("to"):
                    category_info["detected_type"] = gc.get("to")
                    category_info["note"] = "overridden_by_global_correction"
        except Exception:
            # ignore global correction failures
            pass
        
        # Використання результатів аналізу або введеного запиту
        search_query = category_info.get("search_query") or query or category_info.get("detected_type", "невідомо")
        if search_query == "невідомо":
            search_query = query or "товари"
        
        # Пошук на кількох платформах
        amazon_results = await search_amazon_products(search_query)
        ebay_results = await search_ebay_products(search_query)
        aliexpress_results = await search_aliexpress_products(search_query)
        
        # Комбінування всіх результатів
        all_products = []
        all_products.extend(amazon_results.get("products", []))
        all_products.extend(ebay_results.get("products", []))
        all_products.extend(aliexpress_results.get("products", []))
        
        # Якщо результатів не знайдено
        if not all_products:
            all_products = [
                {
                    "title": f"Результати пошуку за запитом: {search_query}",
                    "price": "Різні ціни",
                    "url": f"https://www.amazon.com/s?k={search_query}",
                    "source": "Amazon",
                    "platform": "amazon"
                }
            ]
        
        return JSONResponse({
            "success": True,
            "file_id": file_id,
            "category_info": category_info,
            "search_query": search_query,
            "detected_product_type": category_info.get("detected_type", "невідомо"),
            "total_results": len(all_products),
            "products": all_products,
            "search_results": {
                "amazon": amazon_results,
                "ebay": ebay_results,
                "aliexpress": aliexpress_results
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Помилка при пошуку: {str(e)}")

@router.get("/search/categories")
async def get_categories():
    """Get list of supported product categories"""
    categories = [
        "smartphones",
        "clothing",
        "shoes",
        "electronics",
        "furniture",
        "accessories",
        "books",
        "sports",
        "beauty",
        "food",
        "auto-detect"
    ]
    return JSONResponse({"categories": categories})

@router.post("/search/test")
async def test_search(query: str = "laptop"):
    """Test search functionality without uploading an image"""
    try:
        amazon_result = await search_amazon_products(query)
        ebay_result = await search_ebay_products(query)
        aliexpress_result = await search_aliexpress_products(query)
        
        all_products = []
        all_products.extend(amazon_result.get("products", []))
        all_products.extend(ebay_result.get("products", []))
        all_products.extend(aliexpress_result.get("products", []))
        
        return JSONResponse({
            "success": True,
            "test_query": query,
            "total_results": len(all_products),
            "products": all_products,
            "results": {
                "amazon": amazon_result,
                "ebay": ebay_result,
                "aliexpress": aliexpress_result
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/feedback")
async def submit_feedback(request: Request):
    """Store user feedback (correction) for an uploaded image.

    If `apply_globally` is True and `detected_type` is provided, create/update a global correction
    mapping so future detections with the same detected_type are overridden automatically.
    """
    try:
        payload = await request.json()
        file_id = payload.get("file_id")
        correct_category = payload.get("correct_category")
        detected_type = payload.get("detected_type")
        apply_globally = bool(payload.get("apply_globally", False))

        if not file_id or not correct_category:
            raise HTTPException(status_code=400, detail="file_id and correct_category are required")

        db = get_database()
        entry = {
            "file_id": file_id,
            "detected_type": detected_type,
            "correct_category": correct_category,
            "timestamp": datetime.utcnow()
        }
        await db["feedback"].insert_one(entry)

        # If user requests global correction, upsert mapping from detected_type -> correct_category
        if apply_globally and detected_type:
            try:
                filter_q = {"from": detected_type.lower()}
                update_q = {"$set": {"from": detected_type.lower(), "to": correct_category, "updated_at": datetime.utcnow()}}
                await db["global_corrections"].update_one(filter_q, update_q, upsert=True)
            except Exception:
                # ignore global correction failures but keep individual feedback
                pass

        return JSONResponse({"success": True, "message": "Feedback saved"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
