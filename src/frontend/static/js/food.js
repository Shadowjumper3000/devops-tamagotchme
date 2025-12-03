// Food tracker page JavaScript

let caloriesChart = null;
let macrosChart = null;

// Show add meal modal
function showAddModal() {
    showModal('addMealModal');
}

// Initialize charts
function initializeCharts(chartData) {
    // Calories chart
    const caloriesCtx = document.getElementById('caloriesChart');
    if (caloriesCtx) {
        if (caloriesChart) caloriesChart.destroy();
        
        caloriesChart = new Chart(caloriesCtx, {
            type: 'bar',
            data: {
                labels: chartData.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Calories',
                    data: chartData.calories || [0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: '#f97316'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Macros chart
    const macrosCtx = document.getElementById('macrosChart');
    if (macrosCtx) {
        if (macrosChart) macrosChart.destroy();
        
        macrosChart = new Chart(macrosCtx, {
            type: 'doughnut',
            data: {
                labels: ['Protein', 'Carbs', 'Fats'],
                datasets: [{
                    data: chartData.macros || [30, 50, 20],
                    backgroundColor: ['#ef4444', '#f59e0b', '#8b5cf6']
                }]
            },
            options: {
                responsive: true
            }
        });
    }
}

// Add meal
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addMealForm');
    if (form) {
        form.onsubmit = async function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            const result = await apiCall('/api/food', 'POST', data);
            
            if (result.error) {
                showToast(result.error, 'error');
            } else {
                showToast('Meal logged successfully!', 'success');
                hideModal('addMealModal');
                setTimeout(() => location.reload(), 1000);
            }
        };
    }
    
    initializeCharts({ labels: [], calories: [], macros: [] });
});

// Edit meal
function editMeal(id) {
    console.log('Edit meal:', id);
}

// Delete meal
async function deleteMeal(id) {
    if (!confirm('Are you sure you want to delete this meal?')) return;
    
    const result = await apiCall(`/api/food/${id}`, 'DELETE');
    
    if (result.error) {
        showToast(result.error, 'error');
    } else {
        showToast('Meal deleted successfully!', 'success');
        setTimeout(() => location.reload(), 1000);
    }
}
