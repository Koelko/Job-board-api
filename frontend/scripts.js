document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('stat-vacancies')) {
        loadStats();
        loadRecentVacancies();
    }
    if (document.getElementById('vacancies-list-full')) {
        loadVacanciesFull();
    }
    if (document.getElementById('vacancy-detail')) {
        loadVacancyDetail();
    }
});

async function loadStats() {
    try {
        const [vacanciesRes, employersRes] = await Promise.all([
            fetch('http://127.0.0.1:8000/vacancies?page=1&page_size=1'),
            fetch('http://127.0.0.1:8000/employers?page=1&page_size=1')
        ]);
        
        const vacanciesData = await vacanciesRes.json();
        const employersData = await employersRes.json();
        
        document.getElementById('stat-vacancies').textContent = vacanciesData.total;
        document.getElementById('stat-companies').textContent = employersData.total;
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
        document.getElementById('stat-vacancies').textContent = '—';
        document.getElementById('stat-companies').textContent = '—';
    }
}

async function loadRecentVacancies() {
    try {
        const response = await fetch('http://127.0.0.1:8000/vacancies?page=1&page_size=5&sort=publication_date&order=desc');
        const data = await response.json();
        
        const list = document.getElementById('vacancies-list');
        if (!list) return;
        
        if (data.items.length === 0) {
            list.innerHTML = '<p>Пока нет вакансий</p>';
            return;
        }
        
        list.innerHTML = data.items.map(vacancy => `
            <div class="vacancy-card">
                <h3>${vacancy.specialty}</h3>
                <div class="vacancy-meta">
                    <p><strong>Город:</strong> ${vacancy.city || 'Не указано'}</p>
                    <p><strong>Зарплата:</strong> ${vacancy.salary ? vacancy.salary + ' ₽' : 'Не указана'}</p>
                </div>
                <div style="margin-top: 15px;">
                    <a href="vacancy.html?id=${vacancy.id}" class="btn btn-primary">Подробнее</a>
                </div>
            </div>
        `).join('');
    } catch (error) {
        const list = document.getElementById('vacancies-list');
        if (list) list.innerHTML = '<p>Ошибка загрузки вакансий</p>';
        console.error(error);
    }
}

function searchVacancies() {
    const query = document.getElementById('search-input')?.value;
    if (query) {
        window.location.href = `vacancies.html?search=${encodeURIComponent(query)}`;
    }
}

async function loadVacanciesFull() {
    const params = new URLSearchParams(window.location.search);
    const search = params.get('search');
    
    let url = 'http://127.0.0.1:8000/vacancies?page=1&page_size=10';
    if (search) url += `&skills=${encodeURIComponent(search)}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        displayVacanciesFull(data);
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

function displayVacanciesFull(data) {
    const list = document.getElementById('vacancies-list-full');
    if (!list) return;
    
    list.innerHTML = data.items.map(vacancy => `
        <div class="vacancy-card">
            <h3>${vacancy.specialty}</h3>
            <p><strong>Компания:</strong> ${vacancy.company || 'Не указано'}</p>
            <p><strong>Город:</strong> ${vacancy.city || 'Не указано'}</p>
            <p><strong>Зарплата:</strong> ${vacancy.salary ? vacancy.salary + ' ₽' : 'Не указана'}</p>
            <p><strong>Опыт:</strong> ${vacancy.experience || 'Не указан'}</p>
            <a href="vacancy.html?id=${vacancy.id}" class="btn btn-primary">Подробнее</a>
        </div>
    `).join('');
}

async function loadVacancyDetail() {
    const params = new URLSearchParams(window.location.search);
    const id = params.get('id');
    
    if (!id) {
        document.getElementById('vacancy-detail').innerHTML = '<p>Вакансия не указана</p>';
        return;
    }
    
    try {
        const response = await fetch(`http://127.0.0.1:8000/vacancies/${id}`);
        const vacancy = await response.json();
        
        document.getElementById('vacancy-detail').innerHTML = `
            <h1>${vacancy.specialty}</h1>
            <p><strong>Компания:</strong> ${vacancy.company || 'Не указано'}</p>
            <p><strong>Город:</strong> ${vacancy.city || 'Не указано'}</p>
            <p><strong>Зарплата:</strong> ${vacancy.salary ? vacancy.salary + ' ₽' : 'Не указана'}</p>
            <p><strong>Опыт:</strong> ${vacancy.experience || 'Не указан'}</p>
            <p><strong>Навыки:</strong> ${vacancy.key_skills || 'Не указаны'}</p>
            <a href="vacancies.html" class="btn btn-secondary">← Назад</a>
        `;
    } catch (error) {
        document.getElementById('vacancy-detail').innerHTML = '<p>Ошибка загрузки вакансии</p>';
        console.error(error);
    }
}
 document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('register') === '1') {
        toggleForms();
    }
});
function toggleForms() {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const formTitle = document.getElementById('form-title');
    const switchText = document.getElementById('switch-text');
            
    if (loginForm.classList.contains('hidden')) {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
        formTitle.textContent = 'Вход';
        switchText.innerHTML = 'Нет аккаунта? <a onclick="toggleForms()">Зарегистрироваться</a>';
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
        formTitle.textContent = 'Регистрация';
        switchText.innerHTML = 'Уже есть аккаунт? <a onclick="toggleForms()">Войти</a>';
    }
    clearMessages();
}

function toggleRegisterFields() {
    const role = document.getElementById('register-role').value;
    const seekerFields = document.getElementById('seeker-fields');
    const employerFields = document.getElementById('employer-fields');
            
    if (role === 'seeker') {
        seekerFields.classList.remove('hidden');
        employerFields.classList.add('hidden');
    } else {
        seekerFields.classList.add('hidden');
        employerFields.classList.remove('hidden');
    }
}
function showError(msg) {
    const el = document.getElementById('error-msg');
    el.textContent = msg;
    el.style.display = 'block';
    document.getElementById('success-msg').style.display = 'none';
}
function showSuccess(msg) {
    const el = document.getElementById('success-msg');
    el.textContent = msg;
    el.style.display = 'block';
    document.getElementById('error-msg').style.display = 'none';
}
 function clearMessages() {
    document.getElementById('error-msg').style.display = 'none';
    document.getElementById('success-msg').style.display = 'none';
}

const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();
            
    const role = document.getElementById('login-role').value;
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
                        
    try {
        const response = await fetch('http://127.0.0.1:8000/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },  
            body: JSON.stringify({
                email: email,
                password: password,
                user_type: role 
            })
        });   
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка входа');
        }
                
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user_role', role);
                
        showSuccess('Успешный вход! Перенаправление...');                
        setTimeout(() => {
            window.location.href = role === 'employer' ? 'profile.html' : 'index.html';
        }, 1000);
                
    } catch (error) {
        showError(error.message || 'Не удалось войти. Проверьте данные.');
        console.error('Login error:', error);
    }
})
};

const registerForm = document.getElementById('register-form');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearMessages();            
    const role = document.getElementById('register-role').value;
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const phone = document.getElementById('register-phone')?.value || null;
                       
    const payload = {        
        email: email,
        password: password,
        user_type: role,
        phone : phone,
        name: name,
    };        
    if (role === 'seeker') {
        payload.city = document.getElementById('register-city').value || null;
    } else {
        payload.company_name = document.getElementById('register-company-name').value;
        payload.industry = document.getElementById('register-industry').value || null;
    }
            
    try {
        const response = await fetch(`http://127.0.0.1:8000/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });                
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка регистрации');
        }                
        showSuccess('Регистрация успешна! Теперь войдите в систему.');
        setTimeout(() => {
            toggleForms();                    
            document.getElementById('login-email').value = email;
        }, 2000);                
    } catch (error) {
        showError(error.message || 'Не удалось зарегистрироваться.');
        console.error('Register error:', error);
    }
})
};

document.addEventListener('DOMContentLoaded', () => {
    if (!window.location.pathname.includes('profile.html')) {
        return;
    }
    
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('user_role');
    
    console.log('🔹 Проверка авторизации на profile.html');
    console.log('  Token:', token ? 'есть' : 'нет');
    console.log('  Role:', role);
    
    if (!token || !role) {
        console.log('Нет токена, редирект на login.html');
        window.location.href = 'login.html';
        return;
    }
    console.log('Токен есть, загружаем профиль');
    loadProfile(role, token);
    const tabApplications = document.getElementById('tab-applications');
    const tabVacancies = document.getElementById('tab-vacancies');
    const createAction = document.getElementById('create-action');
    
    if (role === 'seeker') {
        if (tabApplications) tabApplications.style.display = 'block';
        if (tabVacancies) tabVacancies.style.display = 'none';
        if (createAction) createAction.innerHTML = 
            '<a href="resume-form.html" class="btn btn-primary">Создать резюме</a>';
    } else {
        if (tabApplications) tabApplications.style.display = 'none';
        if (tabVacancies) tabVacancies.style.display = 'block';
        if (createAction) createAction.innerHTML = 
            '<a href="vacancy-form.html" class="btn btn-primary">Создать вакансию</a>';
    }
});
async function loadProfile(role, token) {
    const endpoint = role === 'seeker' ? '/seekers/my' : '/employer/my';      
    try {
        const response = await fetch(`http://127.0.0.1:8000${endpoint}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });                
        if (!response.ok) throw new Error('Не удалось загрузить профиль');                
        const profile = await response.json();
        const name = profile.name || profile.full_name || profile.company_name || 'Без имени';
        document.getElementById('profile-name').textContent = name;
        document.getElementById('profile-email').textContent = profile.email;
        document.getElementById('profile-role').textContent = role === 'seeker' ? 'Соискатель' : 'Работодатель';
        let details = `<p><strong>Email:</strong> ${profile.email}</p>`;
        if (profile.city) details += `<p><strong>Город:</strong> ${profile.city}</p>`;
        if (profile.phone) details += `<p><strong>Телефон:</strong> ${profile.phone}</p>`;
        if (profile.industry) details += `<p><strong>Сфера:</strong> ${profile.industry}</p>`;                
        document.getElementById('profile-details').innerHTML = details;
        if (role === 'seeker') {
            loadApplications(token);
        } else {
            loadEmployerVacancies(token);
        }                
    } catch (error) {
        console.error('Ошибка загрузки профиля:', error);
        document.getElementById('profile-details').innerHTML = '<p>Ошибка загрузки</p>';
    }
}
async function loadApplications(token) {
    try {
        const response = await fetch('http://127.0.0.1:8000/applications/my', {
            headers: { 'Authorization': `Bearer ${token}` }
        });                
    if (!response.ok) throw new Error('Не удалось загрузить отклики');
        const data = await response.json();
        const list = document.getElementById('applications-list');                
        if (data.items.length === 0) {
            list.innerHTML = '<div class="empty-state">У вас пока нет откликов</div>';
            return;
        }                
        list.innerHTML = data.items.map(app => `
            <div class="item-card">
                <h4>${app.vacancy_specialty || 'Вакансия'}</h4>
                <div class="item-meta">
                    <p><strong>Компания:</strong> ${app.vacancy_company || 'Не указано'}</p>
                    <p><strong>Дата отклика:</strong> ${new Date(app.application_date).toLocaleDateString('ru-RU')}</p>
                    <span class="status-badge status-${app.status}">${app.status}</span>
                </div>
            </div>
        `).join('');                
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('applications-list').innerHTML = '<p>Ошибка загрузки</p>';
    }
}
async function loadEmployerVacancies(token) {
    document.getElementById('vacancies-list').innerHTML = 
        '<div class="empty-state">Функция в разработке</div>';
}
function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));            
    document.getElementById(`tab-${tabName}`).classList.add('active');
    event.target.classList.add('active');
}
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_role');
    indow.location.href = 'index.html';
}