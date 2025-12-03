// Home page JavaScript

// Get the appropriate health level for image selection
function getHealthLevel(health) {
    if (health === 0) return 0;
    if (health === 100) return 100;
    
    // For values between 1-99, round to nearest 5 and find closest level
    const levels = [5, 15, 25, 35, 45, 55, 65, 75, 85, 95];
    
    // Find the closest level
    let closest = levels[0];
    let minDiff = Math.abs(health - closest);
    
    for (let level of levels) {
        const diff = Math.abs(health - level);
        if (diff < minDiff) {
            minDiff = diff;
            closest = level;
        }
    }
    
    return closest;
}

// Try to load image with multiple extensions
async function tryLoadImage(basePath, healthLevel) {
    const extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'];
    const baseUrl = `${basePath}/health_${healthLevel}`;
    
    for (let ext of extensions) {
        try {
            const imageUrl = `${baseUrl}.${ext}`;
            const response = await fetch(imageUrl, { method: 'HEAD' });
            if (response.ok) {
                return imageUrl;
            }
        } catch (e) {
            // Continue to next extension
        }
    }
    
    return null;
}

// Update Tamagotchi sprite based on health
async function updateTamagotchiSprite() {
    const sprite = document.getElementById('tamagotchi-sprite');
    if (!sprite) return;
    
    const health = parseInt(sprite.dataset.health);
    const image = document.getElementById('tamagotchi-image');
    const loading = document.getElementById('image-loading');
    
    if (!image) return;
    
    // Get the appropriate health level
    const healthLevel = getHealthLevel(health);
    
    // Show loading indicator
    if (loading) {
        loading.style.display = 'block';
    }
    image.style.display = 'none';
    
    // Try to load the image
    const basePath = '/static/images/mascot';
    const imageUrl = await tryLoadImage(basePath, healthLevel);
    
    if (imageUrl) {
        image.src = imageUrl;
        image.onload = function() {
            if (loading) {
                loading.style.display = 'none';
            }
            image.style.display = 'block';
        };
    } else {
        // Fallback: show message if no image found
        if (loading) {
            loading.textContent = `No image found for health level ${healthLevel}`;
            loading.style.color = '#64748b';
        }
    }
}

// Quick log functionality
function quickLog(type) {
    const modal = document.getElementById('quickLogModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    
    let content = '';
    
    switch(type) {
        case 'water':
            modalTitle.textContent = '💧 Log Water';
            content = `
                <div class="form-group">
                    <label for="quickAmount">Amount (ml)</label>
                    <input type="number" id="quickAmount" name="amount" required min="0" step="50">
                </div>
                <div class="quick-amounts">
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickAmount').value = 250">250ml</button>
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickAmount').value = 500">500ml</button>
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickAmount').value = 750">750ml</button>
                </div>
            `;
            break;
        case 'food':
            modalTitle.textContent = '🍎 Log Food';
            content = `
                <div class="form-group">
                    <label for="quickMeal">Meal Name</label>
                    <input type="text" id="quickMeal" name="meal" required>
                </div>
                <div class="form-group">
                    <label for="quickCalories">Calories</label>
                    <input type="number" id="quickCalories" name="calories" required min="0">
                </div>
            `;
            break;
        case 'gym':
            modalTitle.textContent = '💪 Log Workout';
            content = `
                <div class="form-group">
                    <label for="quickWorkout">Workout Type</label>
                    <select id="quickWorkout" name="workout" required>
                        <option value="Cardio">Cardio</option>
                        <option value="Strength">Strength Training</option>
                        <option value="HIIT">HIIT</option>
                        <option value="Yoga">Yoga</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="quickDuration">Duration (min)</label>
                    <input type="number" id="quickDuration" name="duration" required min="1">
                </div>
            `;
            break;
        case 'health':
            modalTitle.textContent = '❤️ Set Health (Dev Mode)';
            content = `
                <div class="form-group">
                    <label for="quickHealth">Health Percentage (0-100)</label>
                    <input type="number" id="quickHealth" name="health" required min="0" max="100" step="1">
                </div>
                <div class="quick-amounts">
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickHealth').value = 0">0%</button>
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickHealth').value = 25">25%</button>
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickHealth').value = 50">50%</button>
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickHealth').value = 75">75%</button>
                    <button type="button" class="btn-quick" onclick="document.getElementById('quickHealth').value = 100">100%</button>
                </div>
            `;
            break;
    }
    
    modalBody.innerHTML = content;
    modal.style.display = 'block';
    
    // Update form submission
    const form = document.getElementById('quickLogForm');
    form.onsubmit = async function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Special handling for health endpoint
        const endpoint = type === 'health' ? '/api/tamagotchi/health' : `/api/${type}`;
        
        const result = await apiCall(endpoint, 'POST', data);
        
        if (result.error) {
            showToast(result.error, 'error');
        } else {
            if (type === 'health') {
                showToast('Health updated successfully!', 'success');
                modal.style.display = 'none';
                // Update the UI immediately
                const sprite = document.getElementById('tamagotchi-sprite');
                if (sprite) {
                    sprite.dataset.health = data.health;
                    const healthFill = document.querySelector('.health-fill');
                    const healthText = document.querySelector('.health-text');
                    if (healthFill) healthFill.style.width = `${data.health}%`;
                    if (healthText) healthText.textContent = `${data.health}% Health`;
                    updateTamagotchiSprite();
                }
            } else {
                showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} logged successfully!`, 'success');
                modal.style.display = 'none';
                setTimeout(() => location.reload(), 1000);
            }
        }
    };
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateTamagotchiSprite();
    
    // Update sprite every 30 seconds
    setInterval(updateTamagotchiSprite, 30000);
});
