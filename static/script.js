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
        document.getElementById('headless').checked = config.headless;
        
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
            document.getElementById('discordBtn').disabled = false;
        }
    } catch (error) {
        console.error('Error checking results:', error);
    }
}

// Generate recommendations
document.getElementById('generateBtn').addEventListener('click', async () => {
    const form = document.getElementById('configForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const request = {
        postal_code: document.getElementById('postalCode').value.trim(),
        num_people: parseInt(document.getElementById('numPeople').value),
        num_meals: parseInt(document.getElementById('numMeals').value),
        cuisine: document.getElementById('cuisine').value.trim(),
        headless: document.getElementById('headless').checked
    };
    
    try {
        document.getElementById('generateBtn').disabled = true;
        document.getElementById('discordBtn').disabled = true;
        document.getElementById('resultsPanel').style.display = 'none';
        document.getElementById('statusSection').style.display = 'block';
        document.getElementById('statusText').textContent = 'Initializing...';
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start generation');
        }
        
        // Start polling for status
        pollStatus();
        
    } catch (error) {
        showError(error.message);
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('statusSection').style.display = 'none';
    }
});

// Poll for status updates
let statusPollingInterval = null;

function pollStatus() {
    statusPollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();
            
            if (status.status === 'processing') {
                document.getElementById('statusText').textContent = status.status_message || 'Processing...';
            } else if (status.status === 'completed') {
                clearInterval(statusPollingInterval);
                document.getElementById('statusSection').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
                await displayRecommendations();
                showSuccess('Recommendations generated successfully!');
            } else if (status.status === 'error') {
                clearInterval(statusPollingInterval);
                document.getElementById('statusSection').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
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
                document.getElementById('generateBtn').disabled = true;
                document.getElementById('statusSection').style.display = 'block';
                document.getElementById('statusText').textContent = status.status_message || 'Processing...';
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
        
        document.getElementById('recommendations').textContent = data.recommendations;
        document.getElementById('resultsPanel').style.display = 'block';
        
        // Show flyer image
        if (data.flyer_image) {
            document.getElementById('flyerImage').src = `/api/flyer-image?t=${Date.now()}`;
            document.getElementById('flyerSection').style.display = 'block';
        }
        
        // Enable Discord button
        document.getElementById('discordBtn').disabled = false;
        
        // Scroll to results
        document.getElementById('resultsPanel').scrollIntoView({ behavior: 'smooth' });
        
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

discordBtn.addEventListener('click', () => {
    modal.style.display = 'block';
});

closeBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

cancelBtn.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === modal) {
        modal.style.display = 'none';
    }
});

// Send to Discord
document.getElementById('discordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const webhookUrl = document.getElementById('webhookUrl').value.trim();
    
    if (!webhookUrl) {
        showError('Please enter a Discord webhook URL');
        return;
    }
    
    try {
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
        
        const response = await fetch('/api/send-discord', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ webhook_url: webhookUrl })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to send to Discord');
        }
        
        modal.style.display = 'none';
        showSuccess('Successfully sent to Discord! 🎉');
        
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send';
        
    } catch (error) {
        showError(error.message);
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send';
    }
});

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
