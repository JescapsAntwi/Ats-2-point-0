/**
 * Authentication utility functions
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return localStorage.getItem('token') !== null;
}

/**
 * Get authentication token
 */
function getToken() {
    return localStorage.getItem('token');
}

/**
 * Get current user
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Sign up a new user
 */
async function signup(email, password, name = null) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password,
                name
            })
        });

        // Check if response is ok before parsing JSON
        if (!response.ok) {
            let errorMessage = 'Signup failed';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText || `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        // Handle network errors
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network error: Could not connect to server. Make sure the backend is running on http://localhost:8000');
        }
        throw error;
    }
}

/**
 * Login user
 */
async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                password
            })
        });

        // Check if response is ok before parsing JSON
        if (!response.ok) {
            let errorMessage = 'Login failed';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText || `Server error (${response.status})`;
            }
            throw new Error(errorMessage);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        // Handle network errors
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network error: Could not connect to server. Make sure the backend is running on http://localhost:8000');
        }
        throw error;
    }
}

/**
 * Logout user
 */
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

/**
 * Get authenticated fetch headers
 */
function getAuthHeaders() {
    const token = getToken();
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

/**
 * Make authenticated API request
 */
async function authenticatedFetch(url, options = {}) {
    const token = getToken();
    
    if (!token) {
        // Check if we're on a page that requires auth
        if (window.location.pathname.includes('dashboard') || 
            window.location.pathname.includes('index.html')) {
            // Redirect to login if token is missing
            window.location.href = 'login.html';
        }
        throw new Error('Not authenticated');
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            if (window.location.pathname.includes('dashboard') || 
                window.location.pathname.includes('index.html')) {
                window.location.href = 'login.html';
            }
            throw new Error('Session expired. Please login again.');
        }

        return response;
    } catch (error) {
        // Handle network errors
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network error: Could not connect to server. Make sure the backend is running on http://localhost:8000');
        }
        throw error;
    }
}

