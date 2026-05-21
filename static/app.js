// VisionCore Pro - Програма для пошуку товарів по фотографіях

const API_BASE = '/api';
let currentFileId = null;
let currentImageFile = null;
let currentUser = null;
let currentToken = null;

// Підтримувані категорії товарів для демонстрації
const SUPPORTED_CATEGORIES = [
    "ноутбук", "портативний комп'ютер", "лаптоп", "персональний комп'ютер",
    "телефон", "мобільний телефон", "смартфон", "мобільник",
    "навушники", "навушники-бутони", "бездротові навушники", "гарнітура", "слухавки",
    "годинник", "смарт-годинник", "розумний годинник", "електронний годинник",
    "планшет", "портативний планшет", "iPad", "планшетний комп'ютер",
    "монітор", "дисплей", "екран", "монітор комп'ютера",
    "клавіатура", "розкладка клавіш", "програмна клавіатура",
    "мишка", "комп'ютерна мишка", "бездротова мишка", "маніпулятор",
    "веб-камера", "вебкамера", "камера для відеозв'язку",
    "мікрофон", "студійний мікрофон", "конденсаторний мікрофон",
    "динамік", "портативна акустика", "колонка", "аудіосистема",
    "навушники затиснені", "накладні навушники", "повнорозмірні навушники",
    "бездротові навушники", "Bluetooth навушники", "вакуумні навушники",
    "зарядний пристрій", "адаптер", "кабель", "USB кабель",
    "потенційна батарея", "павербанк", "зовнішня батарея", "мобільна батарея",
    "маршрутизатор", "Wi-Fi маршрутизатор", "вай-фай", "роутер",
    "модем", "інтернет модем", "мережевий адаптер",
    "жорсткий диск", "SSD диск", "твердотільний накопичувач", "накопичувач",
    "оперативна пам'ять", "пам'ять RAM", "ОЗУ",
    "відеокарта", "графічна карта", "GPU", "прискорювач",
    "материнська плата", "логіка", "системна плата",
    "блок живлення", "ПБ", "живильник", "трансформатор",
    "корпус комп'ютера", "системний блок", "башня", "ПК корпус",
    "охолодження", "кулер", "система охолодження", "вентилятор",
    "ліцензування", "продукт", "ліцензія", "опція",
    "принтер", "сканер", "багатофункціональний пристрій", "МФУ",
    "проектор", "мультимедійний проектор", "кінопроектор",
    "телевізор", "смарт-ТБ", "розумний телевізор", "екран ТБ",
    "звукова система", "домашній кінотеатр", "акустика", "сабвуфер",
    "гра", "ігрова консоль", "переносна консоль", "портативна консоль",
    "дрон", "безпілотний літальний апарат", "БПЛА", "квадрокоптер",
    "екшн-камера", "камера для екстриму", "спортивна камера", "GoPro",
    "фотоапарат", "цифровий фотоапарат", "дзеркальна камера", "DSLR",
    "відеокамера", "камкордер", "відеорекордер", "відеозйомка",
    "об'єктив", "лінза", "оптика", "скляна оптика",
    "штатив", "монопод", "тримач", "кріплення",
    "рюкзак", "сумка", "портфель", "чохол", "кейс",
    "кабель", "провід", "жила", "електричний провід",
    "роз'єм", "конектор", "штекер", "гніздо",
    "адаптер", "перехідник", "конвертер", "трансформатор сигналу",
    "кросівки", "спортивне взуття", "спортивні кросівки", "гумові кросівки",
    "взуття", "чоловічі ботинки", "жіночі ботинки", "черевики", "туфлі"
];

// DOM елементи інтерфейсу
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const uploadText = document.getElementById('uploadText');
const fileInfo = document.getElementById('fileInfo');
const searchBtn = document.getElementById('searchBtn');
const searchQuery = document.getElementById('searchQuery');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const errorMessage = document.getElementById('errorMessage');
const previewImage = document.getElementById('previewImage');
const categoryDetails = document.getElementById('categoryDetails');
const newSearchBtn = document.getElementById('newSearchBtn');

// Обробники подій для завантаження файлів
uploadBox.addEventListener('click', () => fileInput.click());
uploadBox.addEventListener('dragover', handleDragOver);
uploadBox.addEventListener('dragleave', handleDragLeave);
uploadBox.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
searchBtn.addEventListener('click', performSearch);
newSearchBtn.addEventListener('click', resetSearch);

// Обробники подій для автентифікації
document.getElementById('loginBtn')?.addEventListener('click', openLoginModal);
document.getElementById('registerBtn')?.addEventListener('click', openRegisterModal);
document.getElementById('logoutBtn')?.addEventListener('click', handleLogout);

// Ініціалізація користувача при завантаженні сторінки
window.addEventListener('DOMContentLoaded', checkUserSession);

// Обробники перетягування файлів
function handleDragOver(e) {
    e.preventDefault();
    uploadBox.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadBox.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
}

async function handleFile(file) {
    // Перевірка типу файлу
    if (!file.type.startsWith('image/')) {
        showError('Будь ласка, виберіть зображення (JPG, PNG, WebP тощо)');
        return;
    }

    // Перевірка розміру файлу (10MB максимум)
    if (file.size > 10 * 1024 * 1024) {
        showError('Файл занадто великий. Максимальний допустимий розмір: 10 мегабайт');
        return;
    }

    currentImageFile = file;

    // Оновлення користувацького інтерфейсу
    uploadText.textContent = file.name;
    fileInfo.textContent = `Розмір: ${(file.size / 1024).toFixed(2)} КБ`;

    // Завантаження файлу на сервер (після успішного завантаження активуємо кнопку пошуку)
    await uploadFile(file);
}

async function uploadFile(file) {
    try {
        hideError();
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        const text = await response.text();
        if (!response.ok) {
            try {
                const errorData = JSON.parse(text);
                throw new Error(errorData.detail || 'Помилка при завантаженні файлу');
            } catch (e) {
                throw new Error(text || 'Помилка при завантаженні файлу');
            }
        }

        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            throw new Error('Invalid JSON response from server: ' + text);
        }
        currentFileId = data.file_id;

        // Створення попереднього перегляду зображення
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
        };
        reader.readAsDataURL(file);

        // Успішне завантаження — дозволяємо пошук
        searchBtn.disabled = false;

        console.log('Файл успішно завантажено:', data);
    } catch (error) {
        showError(`Помилка завантаження: ${error.message}`);
        searchBtn.disabled = true;
        currentFileId = null;
    }
}

async function performSearch() {
    if (!currentFileId) {
        showError('Немає завантаженої фотографії. Будь ласка, завантажте зображення.');
        return;
    }

    try {
        hideError();
        showLoading(true);

        let query = searchQuery.value.trim();
        
        // Якщо пошуковий запит порожній, використовуємо першу категорію
        if (!query) {
            query = SUPPORTED_CATEGORIES[0];
            searchQuery.value = query;
        }

        const response = await fetch(
            `${API_BASE}/search/by-file-id?file_id=${currentFileId}&query=${encodeURIComponent(query)}`,
            { method: 'POST' }
        );
        const text = await response.text();
        if (!response.ok) {
            try {
                const errorData = JSON.parse(text);
                throw new Error(errorData.detail || 'Помилка при пошуку товарів');
            } catch (e) {
                throw new Error(text || 'Помилка при пошуку товарів');
            }
        }

        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            throw new Error('Invalid JSON response from server: ' + text);
        }
        displayResults(data);
    } catch (error) {
        showError(`Помилка пошуку: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

function displayResults(data) {
    // Відображення інформації про категорію та визначений тип товару
    if (data.category_info && !data.category_info.error) {
        const detectedType = data.detected_product_type || data.category_info.detected_type || "невідомо";
        const analysis = data.category_info.analysis || {};
        
        const categoryHtml = `
            <div class="detail-item" style="background: #e3f2fd; border-left: 4px solid #2196F3; padding: 15px; border-radius: 4px; margin-bottom: 10px;">
                <div class="detail-label" style="color: #1976D2; font-weight: bold;">🎯 Визначений тип товару</div>
                <div class="detail-value" style="color: #1565C0; font-size: 1.1em; font-weight: 600; text-transform: capitalize;">${detectedType}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">📏 Розміри фотографії</div>
                <div class="detail-value">${data.category_info.image_size.width} × ${data.category_info.image_size.height} пікселів</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">📐 Пропорція сторін</div>
                <div class="detail-value">${data.category_info.aspect_ratio}:1</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">🔍 Пошуковий запит</div>
                <div class="detail-value">"${data.search_query}"</div>
            </div>
            ${analysis.brightness ? `
            <div class="detail-item" style="border-top: 1px solid #eee; padding-top: 10px; margin-top: 10px;">
                <div class="detail-label" style="font-size: 0.85rem; color: #666;">📊 Аналіз зображення</div>
                <div class="analysis-stats" style="font-size: 0.9rem; color: #666; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px;">
                    <div>Яскравість: ${analysis.brightness}</div>
                    <div>Контрастність: ${analysis.contrast}</div>
                    <div>Щільність ребер: ${(analysis.edge_density * 100).toFixed(1)}%</div>
                    <div>Колір RGB: (${analysis.dominant_color_rgb.join(', ')})</div>
                </div>
            </div>
            ` : ''}
        `;
        categoryDetails.innerHTML = categoryHtml;
    }

    // Відображення товарів з цінами та посиланнями
    let resultsHtml = '';
    
    if (data.products && data.products.length > 0) {
        data.products.forEach(product => {
            const platformEmoji = {
                'amazon': '🛍️',
                'ebay': '🏷️',
                'aliexpress': '🌐'
            };
            const emoji = platformEmoji[product.platform] || '📦';
            
            resultsHtml += `
                <div class="result-card">
                    <div class="result-header">
                        <span class="result-platform">${emoji} ${product.source}</span>
                    </div>
                    <div class="result-info">
                        <div class="result-title">${product.title}</div>
                        <div class="result-price">💰 ${product.price}</div>
                        <a href="${product.url}" target="_blank" class="result-link btn-buy">
                            Переглянути на ${product.source} →
                        </a>
                    </div>
                </div>
            `;
        });
    } else {
        resultsHtml = `<div class="no-results">На жаль, товари не знайдено. Спробуйте ввести іншу назву або перейти за посиланням безпосередньо.</div>`;
    }

    // Додавання корисних порад
    if (data.products.some(p => p.title.includes("Результати пошуку за запитом"))) {
        resultsHtml += `
            <div class="suggestions-box">
                <h4>💡 Корисна порада для кращого пошуку</h4>
                <p>Система працює найкраще з наступними категоріями товарів. Спробуйте ввести одну з них:</p>
                <div class="suggestion-tags">
                    ${SUPPORTED_CATEGORIES.slice(0, 12).map(cat => `<span class="tag">${cat}</span>`).join('')}
                </div>
            </div>
        `;
    }

    resultsGrid.innerHTML = resultsHtml;
    // Feedback UI
    const feedbackHtml = `
        <div class="detail-item" style="grid-column: 1 / -1; display:flex; align-items:center; gap:10px;">
            <div style="flex:1">Чи правильно визначено тип товару? <strong>${data.detected_product_type || (data.category_info && data.category_info.detected_type) || 'невідомо'}</strong></div>
            <select id="feedbackCategory" style="padding:8px; border-radius:6px; border:1px solid #ddd;">
                ${SUPPORTED_CATEGORIES.map(c => `<option value="${c}">${c}</option>`).join('')}
            </select>
            <label style="display:flex; align-items:center; gap:6px; font-size:13px;">
                <input type="checkbox" id="applyGlobalCorrection" style="width:16px; height:16px;" /> Застосувати для всіх подібних
            </label>
            <button id="sendFeedbackBtn" class="btn-small btn-primary" data-detected="${(data.detected_product_type || (data.category_info && data.category_info.detected_type) || 'невідомо')}">Ні, це інше</button>
        </div>
    `;
    // Insert feedback block at top of results
    resultsGrid.insertAdjacentHTML('afterbegin', feedbackHtml);
    document.getElementById('sendFeedbackBtn').addEventListener('click', async (ev) => {
        const selected = document.getElementById('feedbackCategory').value;
        const detected = ev.currentTarget.dataset.detected || 'невідомо';
        const applyGlobal = document.getElementById('applyGlobalCorrection').checked;
        await sendFeedback(currentFileId, selected, detected, applyGlobal);
    });
    resultsSection.style.display = 'block';
    document.querySelector('.upload-section').style.display = 'none';

    // Прокрутка до результатів
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

function resetSearch() {
    uploadBox.classList.remove('dragover');
    fileInput.value = '';
    uploadText.textContent = 'Натисніть тут або перетягніть зображення товару';
    fileInfo.textContent = '';
    searchQuery.value = '';
    searchBtn.disabled = true;
    currentFileId = null;
    currentImageFile = null;
    resultsSection.style.display = 'none';
    document.querySelector('.upload-section').style.display = 'block';
    hideError();
    
    // Прокрутка у верх сторінки
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showLoading(show) {
    loadingIndicator.style.display = show ? 'block' : 'none';
    searchBtn.disabled = show;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function hideError() {
    errorMessage.style.display = 'none';
}

// ============ AUTHENTICATION FUNCTIONS ============

function checkUserSession() {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        currentToken = token;
        currentUser = JSON.parse(user);
        updateAuthUI();
    }
}

function updateAuthUI() {
    const authButtons = document.getElementById('authButtonsContainer');
    const userInfo = document.getElementById('userInfoContainer');
    
    if (currentUser && currentToken) {
        authButtons.style.display = 'none';
        userInfo.style.display = 'flex';
        document.getElementById('userDisplay').textContent = `👤 ${currentUser.full_name || currentUser.username}`;
    } else {
        authButtons.style.display = 'flex';
        userInfo.style.display = 'none';
    }
}

function openLoginModal() {
    document.getElementById('loginModal').style.display = 'flex';
    document.getElementById('loginForm').reset();
    document.getElementById('loginError').style.display = 'none';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

function openRegisterModal() {
    document.getElementById('registerModal').style.display = 'flex';
    document.getElementById('registerForm').reset();
    document.getElementById('registerError').style.display = 'none';
}

function closeRegisterModal() {
    document.getElementById('registerModal').style.display = 'none';
}

function switchToRegister() {
    closeLoginModal();
    openRegisterModal();
}

function switchToLogin() {
    closeRegisterModal();
    openLoginModal();
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');
    
    try {
        errorDiv.style.display = 'none';
        
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        });
        
        const text = await response.text();
        if (!response.ok) {
            try {
                const errorData = JSON.parse(text);
                throw new Error(errorData.detail || 'Помилка входу');
            } catch (e) {
                throw new Error(text || 'Помилка входу');
            }
        }

        let data;
        try { data = JSON.parse(text); } catch (e) { throw new Error('Invalid JSON response from server: ' + text); }
        
        // Збереження токена та користувача
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        currentToken = data.access_token;
        currentUser = data.user;
        
        closeLoginModal();
        updateAuthUI();
        showError(`✓ Ласкаво просимо, ${data.user.full_name || data.user.username}!`);
        setTimeout(() => hideError(), 3000);
        
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const full_name = document.getElementById('registerFullName').value;
    const password = document.getElementById('registerPassword').value;
    const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
    const errorDiv = document.getElementById('registerError');
    
    try {
        errorDiv.style.display = 'none';
        
        // Перевірка паролей
        if (password !== passwordConfirm) {
            throw new Error('Паролі не збігаються');
        }
        
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                email: email,
                full_name: full_name || null,
                password: password
            })
        });
        
        const text = await response.text();
        if (!response.ok) {
            try {
                const errorData = JSON.parse(text);
                throw new Error(errorData.detail || 'Помилка реєстрації');
            } catch (e) {
                throw new Error(text || 'Помилка реєстрації');
            }
        }

        let data;
        try { data = JSON.parse(text); } catch (e) { throw new Error('Invalid JSON response from server: ' + text); }
        
        // Збереження токена та користувача
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        currentToken = data.access_token;
        currentUser = data.user;
        
        closeRegisterModal();
        updateAuthUI();
        showError(`✓ Реєстрація успішна! Ласкаво просимо, ${data.user.username}!`);
        setTimeout(() => hideError(), 3000);
        
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

function handleLogout() {
    // Видалення даних з localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    currentToken = null;
    currentUser = null;
    
    updateAuthUI();
    showError('✓ Ви вийшли з облікового запису');
    setTimeout(() => hideError(), 3000);
    
    resetSearch();
}

async function sendFeedback(fileId, correctCategory, detectedType = null, applyGlobally = false) {
    try {
        const payload = { file_id: fileId, correct_category: correctCategory };
        if (detectedType) payload.detected_type = detectedType;
        if (applyGlobally) payload.apply_globally = true;

        const response = await fetch(`${API_BASE}/search/feedback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const text = await response.text();
        if (!response.ok) {
            try { const err = JSON.parse(text); throw new Error(err.detail || 'Помилка при надсиланні відгуку'); }
            catch (e) { throw new Error(text || 'Помилка при надсиланні відгуку'); }
        }

        try { JSON.parse(text); }
        catch (e) { throw new Error('Invalid JSON response from server: ' + text); }

        showError(`✓ Дякуємо! Виправлення збережено: ${correctCategory}` + (applyGlobally ? ' (застосовано глобально)' : ''));
        setTimeout(() => hideError(), 3000);
    } catch (error) {
        showError(error.message || 'Помилка відправки відгуку');
    }
}

// Закриття модалей при кліку поза ними
window.addEventListener('click', function(event) {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    
    if (event.target === loginModal) {
        closeLoginModal();
    }
    if (event.target === registerModal) {
        closeRegisterModal();
    }
});

// Ініціалізація програми
console.log('VisionCore Pro ініціалізована з категоріями:', SUPPORTED_CATEGORIES);

