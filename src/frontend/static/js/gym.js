// Gym tracker page JavaScript

let activityChart = null;
let workoutTypesChart = null;

// Show add workout modal
function showAddModal() {
    showModal('addWorkoutModal');
}

// Initialize charts
function initializeCharts(chartData) {
    // Activity chart
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        if (activityChart) activityChart.destroy();
        
        activityChart = new Chart(activityCtx, {
            type: 'bar',
            data: {
                labels: chartData.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Minutes',
                    data: chartData.minutes || [0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: '#ec4899'
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
    
    // Workout types chart
    const typesCtx = document.getElementById('workoutTypesChart');
    if (typesCtx) {
        if (workoutTypesChart) workoutTypesChart.destroy();
        
        workoutTypesChart = new Chart(typesCtx, {
            type: 'pie',
            data: {
                labels: chartData.types || ['Cardio', 'Strength', 'HIIT', 'Yoga'],
                datasets: [{
                    data: chartData.typesData || [25, 25, 25, 25],
                    backgroundColor: ['#3b82f6', '#ef4444', '#f59e0b', '#8b5cf6']
                }]
            },
            options: {
                responsive: true
            }
        });
    }
}

// Add workout
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addWorkoutForm');
    if (form) {
        form.onsubmit = async function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            const result = await apiCall('/api/gym', 'POST', data);
            
            if (result.error) {
                showToast(result.error, 'error');
            } else {
                showToast('Workout logged successfully!', 'success');
                hideModal('addWorkoutModal');
                setTimeout(() => location.reload(), 1000);
            }
        };
    }
    
    initializeCharts({ labels: [], minutes: [], types: [], typesData: [] });
});

// Edit workout
function editWorkout(id) {
    console.log('Edit workout:', id);
}

// Delete workout
async function deleteWorkout(id) {
    if (!confirm('Are you sure you want to delete this workout?')) return;
    
    const result = await apiCall(`/api/gym/${id}`, 'DELETE');
    
    if (result.error) {
        showToast(result.error, 'error');
    } else {
        showToast('Workout deleted successfully!', 'success');
        setTimeout(() => location.reload(), 1000);
    }
}
