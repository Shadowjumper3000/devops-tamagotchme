// Gym tracker page JavaScript

let activityChart = null;
let workoutTypesChart = null;

// Show add workout modal
function showAddModal() {
    showModal('addWorkoutModal');
}

// Fetch chart data from backend
async function fetchChartData() {
    try {
        const response = await apiCall('/api/gym', 'GET');

        if (response.error) {
            console.error('Failed to fetch workout data:', response.error);
            return null;
        }

        const workouts = response.workouts || [];

        // Process last 7 days for activity chart
        const last7Days = [];
        const dailyMinutes = {};
        const today = new Date();

        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateStr = date.toLocaleDateString('en-US', { weekday: 'short' });
            last7Days.push(dateStr);
            dailyMinutes[dateStr] = 0;
        }

        // Aggregate workout minutes by day
        workouts.forEach(workout => {
            const workoutDate = new Date(workout.created_at);
            const dayStr = workoutDate.toLocaleDateString('en-US', { weekday: 'short' });
            if (dailyMinutes.hasOwnProperty(dayStr)) {
                dailyMinutes[dayStr] += workout.duration_minutes || 0;
            }
        });

        const minutesData = last7Days.map(day => dailyMinutes[day]);

        // Process workout types for pie chart
        const typeCount = {};
        workouts.forEach(workout => {
            const type = workout.name || workout.type || 'Other';
            typeCount[type] = (typeCount[type] || 0) + 1;
        });

        const types = Object.keys(typeCount);
        const typesData = Object.values(typeCount);

        return {
            labels: last7Days,
            minutes: minutesData,
            types: types.length > 0 ? types : ['No data'],
            typesData: typesData.length > 0 ? typesData : [1]
        };

    } catch (error) {
        console.error('Error fetching chart data:', error);
        return null;
    }
}

// Initialize charts
function initializeCharts(chartData) {
    if (!chartData) {
        chartData = {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            minutes: [0, 0, 0, 0, 0, 0, 0],
            types: ['No data'],
            typesData: [1]
        };
    }

    // Activity chart
    const activityCtx = document.getElementById('activityChart');
    if (activityCtx) {
        if (activityChart) activityChart.destroy();

        activityChart = new Chart(activityCtx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: 'Minutes',
                    data: chartData.minutes,
                    backgroundColor: '#ec4899',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 10
                        }
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
            type: 'doughnut',
            data: {
                labels: chartData.types,
                datasets: [{
                    data: chartData.typesData,
                    backgroundColor: [
                        '#3b82f6',
                        '#ef4444',
                        '#f59e0b',
                        '#8b5cf6',
                        '#10b981',
                        '#ec4899'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Add workout
document.addEventListener('DOMContentLoaded', async function() {
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

    // Load chart data on page load
    const chartData = await fetchChartData();
    initializeCharts(chartData);
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
