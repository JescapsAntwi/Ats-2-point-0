/**
 * Dashboard functionality for managing scans
 */

// API_BASE_URL is already defined in auth.js

// Suppress external errors from browser extensions
(function() {
    const originalConsoleError = console.error;
    console.error = function(...args) {
        try {
            const errorStr = JSON.stringify(args);
            if (errorStr.includes('user role') || 
                errorStr.includes('Failed to fetch user role') ||
                errorStr.includes('"context":"background"')) {
                return;
            }
        } catch (e) {
            // If JSON.stringify fails, just log normally
        }
        originalConsoleError.apply(console, args);
    };

    window.addEventListener('unhandledrejection', function(event) {
        try {
            const errorStr = JSON.stringify(event.reason);
            if (errorStr.includes('user role') || 
                errorStr.includes('Failed to fetch user role') ||
                errorStr.includes('"context":"background"')) {
                event.preventDefault();
                return false;
            }
        } catch (e) {
            // If JSON.stringify fails, let the error through
        }
    });
})();

// Check authentication on page load
window.addEventListener('DOMContentLoaded', async function() {
    console.log('Dashboard page loaded');
    
    if (!isAuthenticated()) {
        console.log('Not authenticated, redirecting to login');
        window.location.href = 'login.html';
        return;
    }

    console.log('User is authenticated');

    // Display user name in nav
    const user = getCurrentUser();
    if (user && user.name) {
        document.getElementById('userName').textContent = user.name;
    } else if (user && user.email) {
        document.getElementById('userName').textContent = user.email;
    }

    // Show welcome banner with animation
    showWelcomeBanner(user);

    // Load scans with timeout
    const loadTimeout = setTimeout(() => {
        console.error('Load timeout - scans taking too long');
        const loadingMessage = document.getElementById('loadingMessage');
        const errorMessage = document.getElementById('errorMessage');
        if (loadingMessage && !loadingMessage.classList.contains('hidden')) {
            loadingMessage.classList.add('hidden');
            errorMessage.textContent = 'Request is taking too long. Please check your connection and try again.';
            errorMessage.classList.remove('hidden');
        }
    }, 30000);

    try {
        await loadScans();
        clearTimeout(loadTimeout);
    } catch (error) {
        clearTimeout(loadTimeout);
        throw error;
    }
});

/**
 * Load all scans for the current user
 */
async function loadScans() {
    const loadingMessage = document.getElementById('loadingMessage');
    const emptyMessage = document.getElementById('emptyMessage');
    const scansContainer = document.getElementById('scansContainer');
    const errorMessage = document.getElementById('errorMessage');

    errorMessage.classList.add('hidden');
    loadingMessage.classList.remove('hidden');

    try {
        console.log('Loading scans...');
        
        const response = await authenticatedFetch(`${API_BASE_URL}/api/scans`);
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
            }
            console.error('API Error:', errorData);
            throw new Error(errorData.detail || `Failed to load scans (${response.status})`);
        }

        const data = await response.json();
        console.log(`Loaded ${data.scans ? data.scans.length : 0} scans`);
        
        loadingMessage.classList.add('hidden');

        if (!data.scans || data.scans.length === 0) {
            emptyMessage.classList.remove('hidden');
            scansContainer.innerHTML = '';
            return;
        }

        emptyMessage.classList.add('hidden');
        scansContainer.innerHTML = '';

        data.scans.forEach(scan => {
            try {
                const scanCard = createScanCard(scan);
                scansContainer.appendChild(scanCard);
            } catch (e) {
                console.error('Error creating scan card:', e, scan);
            }
        });

    } catch (error) {
        console.error('Error loading scans:', error);
        loadingMessage.classList.add('hidden');
        
        let errorText = error.message || 'Failed to load scans. Please try again.';
        
        if (error.message && error.message.includes('Not authenticated')) {
            errorText = 'Your session has expired. Please login again.';
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else if (error.message && error.message.includes('Network error')) {
            errorText = 'Cannot connect to server. Please check your internet connection.';
        }
        
        const errorTextEl = document.getElementById('errorText') || errorMessage;
        if (errorTextEl) {
            errorTextEl.textContent = errorText;
        } else {
            errorMessage.textContent = errorText;
        }
        errorMessage.classList.remove('hidden');
    }
}

/**
 * Create a scan card element
 */
function createScanCard(scan) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition';
    
    const date = new Date(scan.timestamp);
    const formattedDate = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    let scoreColor = 'text-red-600';
    if (scan.ats_score >= 90) {
        scoreColor = 'text-green-600';
    } else if (scan.ats_score >= 80) {
        scoreColor = 'text-blue-600';
    } else if (scan.ats_score >= 70) {
        scoreColor = 'text-yellow-600';
    }

    card.innerHTML = `
        <div class="flex justify-between items-start mb-4">
            <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 mb-1">
                    ${scan.resume_filename || 'Resume Scan'}
                </h3>
                <p class="text-sm text-gray-500">${formattedDate}</p>
            </div>
            <div class="flex items-center space-x-4">
                <div class="text-right">
                    <div class="text-sm text-gray-500">ATS Score</div>
                    <div class="text-2xl font-bold ${scoreColor}">${scan.ats_score}%</div>
                </div>
                <div class="flex space-x-2">
                    <button onclick="viewScan('${scan.id}')" 
                        class="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition">
                        <i class="bi bi-eye text-xl"></i>
                    </button>
                    <button onclick="deleteScan('${scan.id}')" 
                        class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition">
                        <i class="bi bi-trash text-xl"></i>
                    </button>
                </div>
            </div>
        </div>
        <div class="mt-4 pt-4 border-t border-gray-200">
            <div class="flex flex-wrap gap-2">
                <span class="text-xs text-gray-500">Matched Keywords:</span>
                ${scan.matched_keywords.slice(0, 5).map(kw => 
                    `<span class="keyword-tag bg-green-100 text-green-800">${kw}</span>`
                ).join('')}
                ${scan.matched_keywords.length > 5 ? `<span class="text-xs text-gray-500">+${scan.matched_keywords.length - 5} more</span>` : ''}
            </div>
        </div>
    `;

    return card;
}

/**
 * View scan details in modal
 */
async function viewScan(scanId) {
    const modal = document.getElementById('scanModal');
    const modalContent = document.getElementById('modalContent');

    modalContent.innerHTML = `
        <div class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-4"></div>
            <p>Loading scan details...</p>
        </div>
    `;
    modal.classList.remove('hidden');

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/api/scans/${scanId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load scan details');
        }

        const scan = await response.json();
        
        const date = new Date(scan.timestamp);
        const formattedDate = date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        let scoreColor = 'text-red-600';
        if (scan.ats_score >= 90) {
            scoreColor = 'text-green-600';
        } else if (scan.ats_score >= 80) {
            scoreColor = 'text-blue-600';
        } else if (scan.ats_score >= 70) {
            scoreColor = 'text-yellow-600';
        }

        modalContent.innerHTML = `
            <div class="space-y-6">
                <div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Scan Information</h3>
                    <div class="bg-gray-50 p-4 rounded-lg">
                        <p class="text-sm text-gray-600 mb-1"><strong>Date:</strong> ${formattedDate}</p>
                        ${scan.resume_filename ? `<p class="text-sm text-gray-600 mb-1"><strong>File:</strong> ${scan.resume_filename}</p>` : ''}
                        <p class="text-sm text-gray-600"><strong>ATS Score:</strong> <span class="${scoreColor} font-bold">${scan.ats_score}%</span></p>
                    </div>
                </div>

                <div>
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Job Description</h3>
                    <div class="bg-gray-50 p-4 rounded-lg max-h-40 overflow-y-auto">
                        <p class="text-sm text-gray-700 whitespace-pre-wrap">${scan.job_description}</p>
                    </div>
                </div>

                <div class="grid md:grid-cols-2 gap-4">
                    <div>
                        <h4 class="font-medium text-red-500 mb-3 flex items-center">
                            <i class="bi bi-exclamation-triangle mr-2"></i> Missing Keywords
                        </h4>
                        <div class="bg-white p-4 rounded-lg border border-gray-200">
                            ${scan.missing_keywords.length > 0 
                                ? scan.missing_keywords.map(k => `<span class="keyword-tag">${k}</span>`).join(' ')
                                : '<p class="text-sm text-gray-500">None</p>'
                            }
                        </div>
                    </div>
                    <div>
                        <h4 class="font-medium text-green-600 mb-3 flex items-center">
                            <i class="bi bi-check-circle mr-2"></i> Matched Keywords
                        </h4>
                        <div class="bg-white p-4 rounded-lg border border-gray-200">
                            ${scan.matched_keywords.map(k => `<span class="keyword-tag bg-green-100 text-green-800">${k}</span>`).join(' ')}
                        </div>
                    </div>
                </div>

                <div>
                    <h4 class="font-medium text-indigo-600 mb-3 flex items-center">
                        <i class="bi bi-lightbulb mr-2"></i> Profile Summary & Suggestions
                    </h4>
                    <div class="bg-white p-4 rounded-lg border border-gray-200">
                        <p class="text-gray-700 whitespace-pre-wrap">${scan.ai_feedback}</p>
                    </div>
                </div>
            </div>
        `;
    } catch (error) {
        modalContent.innerHTML = `
            <div class="text-center py-8">
                <p class="text-red-600">${error.message || 'Failed to load scan details'}</p>
            </div>
        `;
    }
}

/**
 * Close modal
 */
function closeModal() {
    document.getElementById('scanModal').classList.add('hidden');
}

/**
 * Delete a scan
 */
async function deleteScan(scanId) {
    if (!confirm('Are you sure you want to delete this scan?')) {
        return;
    }

    try {
        const response = await authenticatedFetch(`${API_BASE_URL}/api/scans/${scanId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            throw new Error('Failed to delete scan');
        }

        await loadScans();
    } catch (error) {
        alert(error.message || 'Failed to delete scan');
    }
}

/**
 * Show welcome banner with user's name
 */
function showWelcomeBanner(user) {
    const banner = document.getElementById('welcomeBanner');
    const welcomeMessage = document.getElementById('welcomeMessage');
    
    if (!banner || !welcomeMessage) {
        return;
    }
    
    if (sessionStorage.getItem('welcomeDismissed') === 'true') {
        return;
    }

    const userName = user?.name || user?.email?.split('@')[0] || 'there';
    
    const hour = new Date().getHours();
    let greeting;
    
    if (hour < 12) {
        greeting = `Good morning, ${userName}! ☀️`;
    } else if (hour < 18) {
        greeting = `Good afternoon, ${userName}! 👋`;
    } else {
        greeting = `Good evening, ${userName}! 🌙`;
    }
    
    welcomeMessage.textContent = greeting;
    
    setTimeout(() => {
        banner.style.opacity = '1';
        banner.style.transform = 'translateY(0)';
    }, 300);
    
    setTimeout(() => {
        dismissWelcome();
    }, 8000);
}

/**
 * Dismiss welcome banner
 */
function dismissWelcome() {
    const banner = document.getElementById('welcomeBanner');
    if (!banner) return;
    
    banner.style.opacity = '0';
    banner.style.transform = 'translateY(-20px)';
    sessionStorage.setItem('welcomeDismissed', 'true');
    
    setTimeout(() => {
        banner.style.display = 'none';
    }, 500);
}
