// Water tracker page JavaScript

let waterChart = null;

// Show add water modal
function showAddModal() {
    showModal('addWaterModal');
}

// Set quick amount
function setAmount(amount) {
    document.getElementById('amount').value = amount;
}

// Initialize chart
function initializeChart(chartData) {
    const ctx = document.getElementById('waterChart');
    if (!ctx) return;
    
    if (waterChart) {
        waterChart.destroy();
    }
    
    waterChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Water Intake (ml)',
                data: chartData.data || [0, 0, 0, 0, 0, 0, 0],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Add water entry
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addWaterForm');
    if (form) {
        form.onsubmit = async function(e) {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            const result = await apiCall('/api/water', 'POST', data);
            
            if (result.error) {
                showToast(result.error, 'error');
            } else {
                showToast('Water logged successfully!', 'success');
                hideModal('addWaterModal');
                setTimeout(() => location.reload(), 1000);
            }
        };
    }
    
    // Initialize chart with placeholder data
    initializeChart({ labels: [], data: [] });
});

// Edit entry
function editEntry(id) {
    // TODO: Implement edit functionality
    console.log('Edit entry:', id);
}

// Delete entry
async function deleteEntry(id) {
    if (!confirm('Are you sure you want to delete this entry?')) return;
    
    const result = await apiCall(`/api/water/${id}`, 'DELETE');
    
    if (result.error) {
        showToast(result.error, 'error');
    } else {
        showToast('Entry deleted successfully!', 'success');
        setTimeout(() => location.reload(), 1000);
    }
}
