// Main JavaScript file

// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Modal functionality
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

function hideModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Close button functionality
document.addEventListener('DOMContentLoaded', function() {
    const closeBtns = document.querySelectorAll('.close');
    closeBtns.forEach(btn => {
        btn.onclick = function() {
            this.closest('.modal').style.display = 'none';
        }
    });
});

// API helper functions
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        
        // Check if response is ok
        if (!response.ok) {
            console.error(`API Error: ${response.status} ${response.statusText}`);
            return { error: `Server error: ${response.status}` };
        }
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('API Error: Response is not JSON');
            const text = await response.text();
            console.error('Response text:', text.substring(0, 200));
            return { error: 'Invalid response from server' };
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        return { error: error.message };
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
