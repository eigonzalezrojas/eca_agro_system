let tempChart, humChart;

function initCharts() {
    const tempCtx = document.getElementById('tempChart').getContext('2d');
    const humCtx = document.getElementById('humChart').getContext('2d');
    
    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperatura (°C)',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
    
    humChart = new Chart(humCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Humedad (%)',
                data: [],
                borderColor: 'rgb(54, 162, 235)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateCharts() {
    const chipid = document.getElementById('chipidSelect').value;
    const period = document.getElementById('periodSelect').value;
    
    fetch(`/api/data?chipid=${chipid}&period=${period}`)
        .then(response => response.json())
        .then(data => {
            tempChart.data.labels = data.labels;
            tempChart.data.datasets[0].data = data.temperatura;
            tempChart.update();
            
            humChart.data.labels = data.labels;
            humChart.data.datasets[0].data = data.humedad;
            humChart.update();
        });
}

document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    updateCharts();
    
    document.getElementById('chipidSelect').addEventListener('change', updateCharts);
    document.getElementById('periodSelect').addEventListener('change', updateCharts);
});