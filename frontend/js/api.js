const API_BASE_URL = 'http://localhost:8000/api';

function getToken() {
    return localStorage.getItem('token');
}

function getHeaders() {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: getHeaders()
    };
    
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (response.status === 401) {
            // Unauthorized, redirect to login
            localStorage.removeItem('token');
            window.location.href = 'index.html';
            return null;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function requireAuth() {
    if (!getToken() && !window.location.pathname.endsWith('index.html')) {
        window.location.href = 'index.html';
    }
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = 'index.html';
}
