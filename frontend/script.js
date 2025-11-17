// Check authentication status on page load
window.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
});

// Update UI based on authentication status
function updateAuthUI() {
    const isAuth = isAuthenticated();
    const user = getCurrentUser();
    
    const userName = document.getElementById('userName');
    const dashboardLink = document.getElementById('dashboardLink');
    const loginLink = document.getElementById('loginLink');
    const signupLink = document.getElementById('signupLink');
    const logoutButton = document.getElementById('logoutButton');
    const saveButton = document.getElementById('saveButton');
    const authPrompt = document.getElementById('authPrompt');
    
    if (isAuth && user) {
        // User is logged in
        if (userName) userName.textContent = user.name || user.email;
        if (dashboardLink) dashboardLink.classList.remove('hidden');
        if (loginLink) loginLink.classList.add('hidden');
        if (signupLink) signupLink.classList.add('hidden');
        if (logoutButton) logoutButton.classList.remove('hidden');
        if (saveButton) saveButton.classList.remove('hidden');
        if (authPrompt) authPrompt.classList.add('hidden');
    } else {
        // User is not logged in
        if (userName) userName.textContent = '';
        if (dashboardLink) dashboardLink.classList.add('hidden');
        if (loginLink) loginLink.classList.remove('hidden');
        if (signupLink) signupLink.classList.remove('hidden');
        if (logoutButton) logoutButton.classList.add('hidden');
        if (saveButton) saveButton.classList.add('hidden');
        if (authPrompt) authPrompt.classList.remove('hidden');
    }
}

// Mobile menu toggle
document.getElementById('menu-toggle').addEventListener('click', function () {
    const mobileMenu = document.getElementById('mobile-menu');
    mobileMenu.classList.toggle('hidden');
});

// Resume file upload handling
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('resume-file');
const fileName = document.getElementById('file-name');

fileInput.addEventListener('change', function (e) {
    if (e.target.files.length > 0) {
        fileName.textContent = e.target.files[0].name;
        fileName.classList.remove('hidden');
    }
});

['dragover', 'dragenter'].forEach(eventName => {
    dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        dropzone.classList.add('dragover');
    }, false);
});

['dragleave', 'dragend', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, function (e) {
        e.preventDefault();
        dropzone.classList.remove('dragover');

        if (eventName === 'drop') {
            fileInput.files = e.dataTransfer.files;
            if (e.dataTransfer.files.length > 0) {
                fileName.textContent = e.dataTransfer.files[0].name;
                fileName.classList.remove('hidden');
            }
        }
    }, false);
});

// Extract text from PDF file (client-side)
async function extractPDFText(file) {
    // For now, we'll use the legacy endpoint which handles PDF extraction server-side
    // In a production app, you might want to use pdf.js or similar for client-side extraction
    return null;
}

// Resume analysis function (without saving)
async function analyzeResume() {
    const jd = document.getElementById('jobDescription').value;
    const fileInput = document.getElementById('resume-file');
    const resume = fileInput.files[0];

    if (!jd || !resume) {
        alert("Please enter a job description and upload a PDF resume.");
        return;
    }

    const formData = new FormData();
    formData.append("jd", jd);
    formData.append("resume", resume);

    document.getElementById('results').classList.remove("hidden");
    document.getElementById('results').innerHTML = `
        <div class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-4"></div>
            <p>Analyzing your resume...</p>
        </div>
    `;

    try {
        const response = await fetch("http://localhost:8000/analyze-resume/", {
            method: "POST",
            body: formData
        });

        const result = await response.json();

        if (result.error) {
            document.getElementById('results').innerHTML = `<p class="text-red-600">${result.error}</p>`;
            return;
        }

        const score = result["JD Match"];
        const missing = result["MissingKeywords"];
        const matched = result["MatchedKeywords"];
        const summary = result["Profile Summary"];

        displayResults(score, missing, matched, summary);

    } catch (err) {
        document.getElementById('results').innerHTML = `<p class="text-red-600">Error: ${err.message}</p>`;
    }
}

// Analyze and save resume (requires authentication)
async function analyzeAndSaveResume() {
    if (!isAuthenticated()) {
        alert("Please login to save your scan results.");
        window.location.href = 'login.html';
        return;
    }

    const jd = document.getElementById('jobDescription').value;
    const fileInput = document.getElementById('resume-file');
    const resume = fileInput.files[0];

    if (!jd || !resume) {
        alert("Please enter a job description and upload a PDF resume.");
        return;
    }

    const formData = new FormData();
    formData.append("jd", jd);
    formData.append("resume", resume);

    document.getElementById('results').classList.remove("hidden");
    document.getElementById('results').innerHTML = `
        <div class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mb-4"></div>
            <p>Analyzing and saving your resume...</p>
        </div>
    `;

    try {
        // Use the upload endpoint which handles both analysis and saving
        const token = getToken();
        const response = await fetch("http://localhost:8000/api/scans/upload", {
            method: "POST",
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to analyze and save scan');
        }

        const savedScan = await response.json();
        
        // Display results with success message
        displayResults(
            savedScan.ats_score,
            savedScan.missing_keywords,
            savedScan.matched_keywords,
            savedScan.ai_feedback,
            true
        );

    } catch (err) {
        document.getElementById('results').innerHTML = `<p class="text-red-600">Error: ${err.message}</p>`;
    }
}

// Display analysis results
function displayResults(score, missing, matched, summary, saved = false, saveError = null) {
    let scoreColor = 'text-indigo-600';
    if (score >= 90) {
        scoreColor = 'text-green-600';
    } else if (score >= 80) {
        scoreColor = 'text-blue-600';
    } else if (score >= 70) {
        scoreColor = 'text-yellow-600';
    } else {
        scoreColor = 'text-red-600';
    }

    let saveMessage = '';
    if (saved) {
        saveMessage = `
            <div class="mb-4 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
                <i class="bi bi-check-circle mr-2"></i> Scan saved successfully! 
                <a href="dashboard.html" class="underline font-medium">View in Dashboard</a>
            </div>
        `;
    } else if (saveError) {
        saveMessage = `
            <div class="mb-4 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
                <i class="bi bi-exclamation-triangle mr-2"></i> Analysis complete, but failed to save: ${saveError}
            </div>
        `;
    }

    document.getElementById('results').innerHTML = `
        <div class="p-6 bg-gray-50 rounded-lg border border-gray-200">
            <h3 class="text-xl font-semibold mb-6">Analysis Results</h3>
            ${saveMessage}
            <div class="mb-6">
                <div class="flex justify-between mb-2">
                    <div class="font-medium">ATS Compatibility Score:</div>
                    <div class="font-bold ${scoreColor}">${score}%</div>
                </div>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: ${score}%;"></div>
                </div>
            </div>

            <div class="grid md:grid-cols-1 gap-6">
                <div class="bg-white p-4 rounded-lg shadow-sm">
                    <h4 class="font-medium text-red-500 mb-3 flex items-center">
                        <i class="bi bi-exclamation-triangle mr-2"></i> Missing Keywords
                    </h4>
                    <div>${missing.map(k => `<span class="keyword-tag">${k}</span>`).join(' ')}</div>
                </div>
                <div class="bg-white p-4 rounded-lg shadow-sm">
                    <h4 class="font-medium text-green-600 mb-3 flex items-center">
                        <i class="bi bi-check-circle mr-2"></i> Matched Keywords
                    </h4>
                    <div>${matched.map(k => `<span class="keyword-tag bg-green-100 text-green-800">${k}</span>`).join(' ')}</div>
                </div>
                <div class="bg-white p-4 rounded-lg shadow-sm mt-6">
                    <h4 class="font-medium text-indigo-600 mb-3 flex items-center">
                        <i class="bi bi-lightbulb mr-2"></i> Profile Summary
                    </h4>
                    <ul class="list-disc pl-5 text-gray-700">
                        ${summary}
                    </ul>
                </div>
            </div>
        </div>
    `;
}

// Form submission handler
function handleSubmit(event) {
    event.preventDefault();

    // Show success message
    const form = event.target;
    const formContainer = form.parentElement;

    formContainer.innerHTML = `
        <div class="text-center py-8">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-600 mb-4">
                <i class="bi bi-check-lg text-3xl"></i>
            </div>
            <h3 class="text-xl font-semibold mb-2">Message Sent Successfully!</h3>
            <p class="text-gray-600">Thank you for your message. We'll get back to you shortly.</p>
        </div>
    `;
}

// Smooth scroll for navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });

        // Close mobile menu if open
        if (!document.getElementById('mobile-menu').classList.contains('hidden')) {
            document.getElementById('mobile-menu').classList.add('hidden');
        }
    });
});

// Prevent zoom on scroll
document.body.addEventListener('wheel', e => { 
    if (!e.ctrlKey) return; 
    e.preventDefault(); 
    return 
}, { passive: false });

