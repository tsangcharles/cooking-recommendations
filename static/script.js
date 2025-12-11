// Load default configuration on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadDefaultConfig();
    checkForExistingResults();
    startStatusPolling();
});

// Load default config from backend
async function loadDefaultConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        document.getElementById('postalCode').value = config.postal_code;
        document.getElementById('numPeople').value = config.num_people;
        document.getElementById('numMeals').value = config.num_meals;
        document.getElementById('cuisine').value = config.cuisine;
        
        // Pre-fill Discord webhook if available
        if (config.discord_webhook_url) {
            document.getElementById('webhookUrl').value = config.discord_webhook_url;
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Check if there are existing results
async function checkForExistingResults() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        if (status.has_results) {
            await displayRecommendations();
            setDiscordBtnDisabled(false);
        }
    } catch (error) {
        console.error('Error checking results:', error);
    }
}

// Helper to safely enable/disable the (now optional) Discord button
function setDiscordBtnDisabled(state) {
    const btn = document.getElementById('discordBtn');
    if (btn) btn.disabled = state;
}

// General helper to safely set `disabled` on an element or element id
function safeSetDisabled(elOrId, state) {
    let el = null;
    if (!elOrId) return;
    if (typeof elOrId === 'string') {
        el = document.getElementById(elOrId);
    } else {
        el = elOrId;
    }
    if (el) el.disabled = state;
}

// Generate recommendations
const generateBtn = document.getElementById('generateBtn');
if (generateBtn) {
    generateBtn.addEventListener('click', async () => {
    const form = document.getElementById('configForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const postalCode = document.getElementById('postalCode');
    const numPeople = document.getElementById('numPeople');
    const numMeals = document.getElementById('numMeals');
    const cuisine = document.getElementById('cuisine');
    
    if (!postalCode || !numPeople || !numMeals || !cuisine) {
        showError('Form elements not found');
        return;
    }
    
    const request = {
        postal_code: postalCode.value.trim(),
        num_people: parseInt(numPeople.value),
        num_meals: parseInt(numMeals.value),
        cuisine: cuisine.value.trim(),
        headless: true,
        auto_send_discord: true
    };
    
    try {
    safeSetDisabled(generateBtn, true);
    setDiscordBtnDisabled(true);
        const resultsPanel = document.getElementById('resultsPanel');
        if (resultsPanel) resultsPanel.style.display = 'none';
        const statusSection = document.getElementById('statusSection');
        const statusText = document.getElementById('statusText');
        if (statusSection) statusSection.style.display = 'block';
        if (statusText) statusText.textContent = 'Initializing...';
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start generation');
        }
        
        // Mark that we want to auto-send to Discord when generation completes
        window.__autoSendToDiscord = true;

        // Start polling for status
        pollStatus();
        
    } catch (error) {
        showError(error.message);
            safeSetDisabled(generateBtn, false);
        const statusSection = document.getElementById('statusSection');
        if (statusSection) statusSection.style.display = 'none';
    }
});
    }

// Poll for status updates
let statusPollingInterval = null;

function pollStatus() {
    statusPollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            if (status.status === 'processing') {
                const statusText = document.getElementById('statusText');
                if (statusText) statusText.textContent = status.status_message || 'Processing...';
            } else if (status.status === 'completed') {
                clearInterval(statusPollingInterval);
                const statusSection = document.getElementById('statusSection');
                if (statusSection) statusSection.style.display = 'none';
                safeSetDisabled(generateBtn, false);
                await displayRecommendations();
                showSuccess('Recommendations generated successfully!');
                // Auto-send is handled by backend, no need to send again from frontend
            } else if (status.status === 'error') {
                clearInterval(statusPollingInterval);
                const statusSection = document.getElementById('statusSection');
                if (statusSection) statusSection.style.display = 'none';
                if (generateBtn) generateBtn.disabled = false;
                showError(status.status_message || `Error: ${status.error}`);
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 1000);
}

// Background status polling for page refresh scenarios
function startStatusPolling() {
    setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            if (status.status === 'processing' && statusPollingInterval === null) {
                        safeSetDisabled(generateBtn, true);
                const statusSection = document.getElementById('statusSection');
                const statusText = document.getElementById('statusText');
                if (statusSection) statusSection.style.display = 'block';
                if (statusText) statusText.textContent = status.status_message || 'Processing...';
                pollStatus();
            }
        } catch (error) {
            console.error('Error in background polling:', error);
        }
    }, 5000);
}

// Display recommendations
async function displayRecommendations() {
    try {
        const response = await fetch('/api/recommendations');
        const data = await response.json();
        
        const recommendations = document.getElementById('recommendations');
        const resultsPanel = document.getElementById('resultsPanel');
        if (recommendations) recommendations.textContent = data.recommendations;
        if (resultsPanel) resultsPanel.style.display = 'block';
        
        // Show flyer image
        if (data.flyer_image) {
            const flyerImage = document.getElementById('flyerImage');
            const flyerSection = document.getElementById('flyerSection');
            if (flyerImage) flyerImage.src = `/api/flyer-image?t=${Date.now()}`;
            if (flyerSection) flyerSection.style.display = 'block';
        }
        
        // Enable Discord button (no-op if button was removed)
        setDiscordBtnDisabled(false);
        
        // Scroll to results
        if (resultsPanel) resultsPanel.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        console.error('Error displaying recommendations:', error);
        showError('Failed to load recommendations');
    }
}

// Discord modal handling
const modal = document.getElementById('discordModal');
const discordBtn = document.getElementById('discordBtn');
const closeBtn = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');

if (discordBtn) {
    discordBtn.addEventListener('click', () => {
        if (modal) modal.style.display = 'block';
    });
}

if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        if (modal) modal.style.display = 'none';
    });
}

if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
        if (modal) modal.style.display = 'none';
    });
}

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Send to Discord
// Centralized send-to-discord helper used by the modal and auto-send flow
async function sendToDiscord(webhookUrl) {
    if (!webhookUrl) {
        throw new Error('Discord webhook URL is required');
    }

    // Provide lightweight UI feedback
    showAlert('Sending recommendations to Discord...', 'info');

    const response = await fetch('/api/send-discord', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ webhook_url: webhookUrl })
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Failed to send to Discord');
    }

    showSuccess('Successfully sent to Discord! 🎉');
}

// Modal form still uses the centralized helper so user can supply a webhook when needed
const discordForm = document.getElementById('discordForm');
if (discordForm) {
    discordForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const webhookUrlInput = document.getElementById('webhookUrl');
    if (!webhookUrlInput) return;
    const webhookUrl = webhookUrlInput.value.trim();

    if (!webhookUrl) {
        showError('Please enter a Discord webhook URL');
        return;
    }

    try {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        safeSetDisabled(submitBtn, true);
        if (submitBtn) submitBtn.textContent = 'Sending...';

        await sendToDiscord(webhookUrl);

        const modal = document.getElementById('discordModal');
        if (modal) modal.style.display = 'none';

        safeSetDisabled(submitBtn, false);
        if (submitBtn) submitBtn.textContent = 'Send';
    } catch (error) {
        showError(error.message);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        safeSetDisabled(submitBtn, false);
        if (submitBtn) submitBtn.textContent = 'Send';
    }
    });
}

// Utility functions for notifications
function showSuccess(message) {
    showAlert(message, 'success');
}

function showError(message) {
    showAlert(message, 'error');
}

function showAlert(message, type) {
    // Remove any existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    const main = document.querySelector('main');
    main.insertBefore(alert, main.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alert.style.opacity = '0';
        alert.style.transition = 'opacity 0.5s';
        setTimeout(() => alert.remove(), 500);
    }, 5000);
}
