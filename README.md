# 📚 VisionCore Pro - Курсова Робота

Веб-застосунок для пошуку та класифікації товарів за завантаженою фотографією з використанням штучного інтелекту та веб-скрейпингу. Проект демонструє розробку сучасного веб-додатку з аутентифікацією, обробкою зображень та інтеграцією з множинними платформами електронної комерції.

## 📋 Опис Проекту

**VisionCore Pro 2.0** — це веб-платформа, яка дозволяє користувачам:
- 📸 Завантажити фотографію товару
- 🤖 Автоматично класифікувати категорію товару за допомогою машинного навчання
- 🔍 Знайти схожі товари на різних платформах (Amazon, eBay, AliExpress)
- 💰 Порівняти ціни на різних платформах
- 👤 Керувати своїм обліковим записом з забезпеченням JWT-токенами

## 🎯 Основні Функції

### 1️⃣ Аутентифікація та безпека
- Реєстрація нових користувачів
- Вхід в систему з JWT-токенами
- Хеширування паролів за допомогою bcrypt
- Управління сесіями користувачів

### 2️⃣ Завантаження та обробка зображень
- Підтримка форматів: JPG, PNG, WebP, GIF, BMP
- Валідація розміру файлів (максимум 10MB)
- Обробка та оптимізація зображень

### 3️⃣ Класифікація товарів
- Машинне навчання для визначення категорії товару
- Комбінований підхід з аналізу тексту та зображень
- Підтримка українських та англійських назв товарів
- Класифікація товарів за візуальними характеристиками:
  - Взуття (кросівки, черевики, сандалі)
  - Аксесуари (сумки, рюкзаки, шапки, часи)
  - Одяг (куртки, пальто, футболки)
  - Електроніка (смартфони, ноутбуки, навушники, монітори)

### 4️⃣ Пошук та порівняння товарів
- Інтеграція з множинними платформами електронної комерції
- Парсинг результатів пошуку
- Порівняння цін та доступності
- Відображення рейтингів товарів

### 5️⃣ Веб-інтерфейс
- Інтерактивна форма завантаження
- Модальні вікна для входу та реєстрації
- Адаптивний дизайн (мобільний та десктопний)
- Українська локалізація

## 🏗️ Архітектура Проекту

### Структура Директорій

```
VisionCore2.0/
│
├── app/
│   ├── __init__.py                 # Ініціалізація додатку
│   ├── main.py                     # Основна конфігурація FastAPI
│   ├── database.py                 # Конфігурація MongoDB та функції підключення
│   ├── models.py                   # Pydantic моделі (схеми даних)
│   ├── security.py                 # Функції хеширування та JWT-токенів
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Маршрути реєстрації та входу
│   │   ├── upload.py               # Маршрути для завантаження зображень
│   │   └── search.py               # Маршрути пошуку та класифікації товарів
│   │
│   └── services/
│       └── product_classifier.py   # Сервіс класифікації товарів за ШМ
│
├── static/
│   ├── index.html                  # Головна сторінка (фронтенд)
│   ├── app.js                      # Основна логіка JavaScript
│   └── styles.css                  # Стилізація
│
├── uploads/                        # Директорія для збереження завантажених зображень
│
├── run.py                          # Точка входу (запуск сервера)
├── requirements.txt                # Залежності проекту
├── .env                            # Змінні оточення (локально)
└── README.md                       # Цей файл
```

## 🛠️ Технологічний Стек

### Backend
- **FastAPI** (>= 0.104.1) - Сучасний фреймворк для побудови REST API
- **Uvicorn** (>= 0.24.0) - ASGI сервер
- **MongoDB + Motor** - NoSQL база даних та асинхронний драйвер
- **Pydantic** (>= 2.0.0) - Валідація та серіалізація даних
- **PyJWT + bcrypt** - Аутентифікація та шифрування паролів

### Обробка Зображень та Класифікація
- **Pillow** (>= 10.0.0) - Обробка та редагування зображень
- **NumPy** (>= 1.24.0) - Числові обчислення

### Веб-скрейпинг та Пошук
- **BeautifulSoup4** (>= 4.12.0) - Парсинг HTML
- **httpx** (>= 0.25.0) - Асинхронний HTTP-клієнт
- **requests** (>= 2.31.0) - HTTP-запити
- **google-search-results** (>= 2.4.2) - API пошуку Google
- **python-dotenv** - Управління змінними оточення

### Frontend
- **HTML5** - Структура сторінки
- **CSS3** - Стилізація та адаптивний дизайн
- **JavaScript (Vanilla)** - Клієнтська логіка

## 📦 Встановлення та Запуск

### 1️⃣ Передумови
- Python >= 3.10
- MongoDB (локально або у хмарі)
- pip або conda

### 2️⃣ Клонування репозиторію
```bash
git clone <URL-репозиторію>
cd VisionCore2.0-200526
```

### 3️⃣ Створення віртуального оточення
```bash
# На Windows
python -m venv .venv
.venv\Scripts\activate

# На macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 4️⃣ Встановлення залежностей
```bash
pip install -r requirements.txt
```

### 5️⃣ Конфігурація середовища
Створіть файл `.env` у кореневій директорії проекту:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=visioncore_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
VISIONCORE_HOST=0.0.0.0
VISIONCORE_PORT=8501
VISIONCORE_RELOAD=true

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB

# API Keys (якщо використовуєте externe сервіси)
GOOGLE_API_KEY=your-api-key
```

### 6️⃣ Запуск сервера

```bash
python run.py
```

Сервер запуститься за адресою: `http://localhost:8501`

Або запустіть напряму через uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8501
```

## 🚀 Як запустити проєкт локально

### Швидкий старт

1. **Встановіть залежності:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Запустіть MongoDB:**
   ```bash
   # Якщо встановлено локально
   mongod
   ```

3. **Запустіть сервер:**
   ```bash
   python run.py
   ```

4. **Відкрийте браузер:**
   ```
   http://localhost:8501
   ```

## 📡 API Документація

### Базовий URL
```
http://localhost:8501/api
```

### 🔐 Маршрути Аутентифікації (`/auth`)

#### 1. Реєстрація користувача
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123",
  "full_name": "John Doe"
}
```

**Відповідь (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe",
    "created_at": "2024-05-21T10:30:00",
    "is_active": true
  }
}
```

#### 2. Вхід користувача
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Відповідь (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 📸 Маршрути Завантаження (`/upload`)

#### 1. Завантаження зображення
```http
POST /api/upload
Content-Type: multipart/form-data

file: <image_file>
```

**Відповідь (200 OK):**
```json
{
  "file_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
  "filename": "product_photo.jpg",
  "size": 245678,
  "format": "JPEG",
  "upload_time": "2024-05-21T10:35:00"
}
```

### 🔍 Маршрути Пошуку (`/search`)

#### 1. Класифікація та пошук товару
```http
POST /api/search/classify-and-find
Content-Type: multipart/form-data

file: <image_file>
query: "смартфон" (необов'язково)
```

**Відповідь (200 OK):**
```json
{
  "category": "смартфон",
  "confidence": 0.92,
  "products": [
    {
      "title": "iPhone 15 Pro Max",
      "price": "$1199.99",
      "platform": "amazon",
      "rating": 4.8,
      "reviews": 2345
    },
    {
      "title": "Samsung Galaxy S24",
      "price": "$999.99",
      "platform": "ebay",
      "rating": 4.7,
      "reviews": 1890
    }
  ]
}
```

#### 2. Пошук за описом
```http
POST /api/search/find
Content-Type: application/json

{
  "query": "ноутбук ASUS",
  "platform": "amazon" (необов'язково)
}
```

## 💾 Моделі Даних

### User (Користувач)
```json
{
  "_id": "ObjectId",
  "username": "john_doe",
  "email": "john@example.com",
  "password_hash": "bcrypt_hash",
  "full_name": "John Doe",
  "created_at": "2024-05-21T10:30:00",
  "updated_at": "2024-05-21T10:30:00",
  "is_active": true
}
```

### UploadedImage (Завантажене зображення)
```json
{
  "_id": "ObjectId",
  "file_id": "uuid",
  "user_id": "ObjectId",
  "filename": "product_photo.jpg",
  "filepath": "/uploads/product_photo_uuid.jpg",
  "size": 245678,
  "format": "JPEG",
  "upload_time": "2024-05-21T10:35:00",
  "search_results": [...]
}
```

### Product (Товар)
```json
{
  "_id": "ObjectId",
  "title": "iPhone 15 Pro Max",
  "category": "смартфон",
  "price": "$1199.99",
  "platform": "amazon",
  "url": "https://amazon.com/...",
  "rating": 4.8,
  "reviews": 2345,
  "in_stock": true,
  "thumbnail": "image_url",
  "scraped_at": "2024-05-21T10:40:00"
}
```

## 🔄 Робочий Процес Додатку

```
┌─────────────────────────────────┐
│   1. Користувач завантажує      │
│      фотографію товару          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   2. Обробка та валідація       │
│      зображення (Pillow)        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   3. Класифікація товару        │
│      (product_classifier.py)    │
│      - Аналіз візуальних        │
│        ознак                    │
│      - Аналіз тексту (якщо є)   │
│      - Визначення категорії     │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   4. Пошук схожих товарів       │
│      - Amazon                   │
│      - eBay                     │
│      - AliExpress               │
│      - Google Search            │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   5. Парсинг результатів        │
│      - Витяг назв товарів       │
│      - Витяг цін               │
│      - Витяг рейтингів         │
│      - Витяг посилань          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   6. Збереження в MongoDB       │
│      - Зберіганню дані про      │
│        користувача              │
│      - Результати пошуку        │
│      - Історія запитів          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   7. Повернення результатів     │
│      користувачу                │
└─────────────────────────────────┘
```

## 🧪 Тестування API

### Через cURL

#### Реєстрація
```bash
curl -X POST "http://localhost:8501/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPassword123",
    "full_name": "Test User"
  }'
```

#### Вхід
```bash
curl -X POST "http://localhost:8501/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123"
  }'
```

#### Завантаження зображення
```bash
curl -X POST "http://localhost:8501/api/upload" \
  -F "file=@/path/to/image.jpg"
```

### Через Swagger UI
FastAPI автоматично генерує інтерактивну документацію:
```
http://localhost:8501/docs
```

## 🐛 Можливі Помилки та Рішення

### 1. Помилка підключення до MongoDB
```
pymongo.errors.ServerSelectionTimeoutError
```
**Рішення:** Переконайтеся, що MongoDB запущена та доступна за адресою в `.env`

### 2. CORS помилки при завантаженні
```
Access to XMLHttpRequest blocked by CORS policy
```
**Рішення:** CORS вже налаштований в `main.py`, проверьте браузерну консоль

### 3. Помилка при завантаженні файла
```
413 Payload Too Large
```
**Рішення:** Файл більше за 10MB. Збільшіть `MAX_UPLOAD_SIZE` в `.env`

## 📊 Статистика Проекту

- **Кількість файлів Python:** 8 основних модулів
- **Кількість API маршрутів:** 6+ основних ендпоїнтів
- **Поддержувані категорії товарів:** 20+ типів
- **Платформи інтеграції:** 3 (Amazon, eBay, AliExpress)
- **Мови інтерфейсу:** Українська, можливо англійська

## 🎓 Навчальні Цілі

Цей проект демонструє:

✅ **Backend розробка:**
- Побудова REST API з FastAPI
- Асинхронне програмування (async/await)
- Робота з NoSQL базами даних (MongoDB)
- JWT аутентифікація та безпека

✅ **Frontend розробка:**
- Ванільний JavaScript без фреймворків
- Асинхронні запити (Fetch API)
- Модальні вікна та обробка подій
- Адаптивний дизайн

✅ **Машинне навчання та обробка даних:**
- Класифікація зображень
- Обробка зображень (Pillow, NumPy)
- Аналіз текстових даних
- Комбінований підхід до класифікації

✅ **Веб-скрейпинг та інтеграція:**
- Парсинг HTML з BeautifulSoup
- Асинхронні HTTP-запити
- Інтеграція з зовнішніми сервісами

✅ **Практики розробки:**
- Модульна архітектура
- Обробка помилок
- Документування кода
- Конфігурація через змінні оточення

## 👨‍💻 Розробник

- **Роль:** Студент курсової роботи
- **Дисципліна:** Веб-розробка / Штучний інтелект / Програмування
- **Дата:** травень 2024

## 📝 Ліцензія

Цей проект розроблено як навчальна курсова робота. Вільне використання в навчальних цілях.

## 🔗 Посилання та Ресурси

- [FastAPI Документація](https://fastapi.tiangolo.com/)
- [MongoDB Документація](https://docs.mongodb.com/)
- [JWT Аутентифікація](https://tools.ietf.org/html/rfc7519)
- [Pillow Документація](https://pillow.readthedocs.io/)
- [BeautifulSoup4 Документація](https://www.crummy.com/software/BeautifulSoup/)

---

**Вдалого використання VisionCore Pro 2.0! 🚀**
