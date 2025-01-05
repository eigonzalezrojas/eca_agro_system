let tempChart, humChart;

// Inicializar los gráficos
function initCharts() {
    const tempCtx = document.getElementById('tempChart').getContext('2d');
    const humCtx = document.getElementById('humChart').getContext('2d');
    
    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
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
            datasets: []
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

// Actualizar los gráficos con datos de la API
function updateCharts() {
    const chipid = document.getElementById('chipidSelect').value;
    const period = document.getElementById('periodSelect').value;
    const customDate = document.getElementById('customDate').value;
    const customMonth = document.getElementById('customMonth').value;

    let url = `/api/data?period=${period}`;
    if (chipid) url += `&chipid=${chipid}`;
    if (customDate && period === 'custom') url += `&date=${customDate}`;
    if (customMonth && period === 'month') url += `&month=${customMonth}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('Datos recibidos para los gráficos:', data);

            // Limpiar gráficos
            tempChart.data.labels = [];
            tempChart.data.datasets = [];
            humChart.data.labels = [];
            humChart.data.datasets = [];

            // Agregar datos por dispositivo
            Object.keys(data).forEach((chipid, index) => {
                const color = `hsl(${index * 60}, 70%, 50%)`;

                // Actualizar gráfico de temperatura
                tempChart.data.labels = data[chipid].labels;
                tempChart.data.datasets.push({
                    label: `Dispositivo ${chipid} - Temperatura Máxima`,
                    data: data[chipid].max_temp,
                    borderColor: color,
                    fill: false,
                    tension: 0.4
                });
                tempChart.data.datasets.push({
                    label: `Dispositivo ${chipid} - Temperatura Mínima`,
                    data: data[chipid].min_temp,
                    borderColor: color,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4
                });

                // Actualizar gráfico de humedad
                humChart.data.labels = data[chipid].labels;
                humChart.data.datasets.push({
                    label: `Dispositivo ${chipid} - Humedad Máxima`,
                    data: data[chipid].max_hum,
                    borderColor: color,
                    fill: false,
                    tension: 0.4
                });
                humChart.data.datasets.push({
                    label: `Dispositivo ${chipid} - Humedad Mínima`,
                    data: data[chipid].min_hum,
                    borderColor: color,
                    borderDash: [5, 5],
                    fill: false,
                    tension: 0.4
                });
            });

            tempChart.update();
            humChart.update();
        })
        .catch(error => console.error('Error al actualizar los gráficos:', error));
}

// Generar dinámicamente los meses en el menú desplegable
function populateMonths(startYear, endYear) {
    const monthNames = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ];
    const customMonthSelect = document.getElementById('customMonth');

    customMonthSelect.innerHTML = '';
    
    for (let year = startYear; year <= endYear; year++) {
        monthNames.forEach((month, index) => {
            const option = document.createElement('option');
            const monthValue = `${year}-${String(index + 1).padStart(2, '0')}`;
            option.value = monthValue;
            option.textContent = `${month} ${year}`;
            customMonthSelect.appendChild(option);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    updateCharts();
    const currentYear = new Date().getFullYear();
    populateMonths(currentYear - 1, currentYear + 1);


    // Configurar eventos de los filtros
    document.getElementById('periodSelect').addEventListener('change', function() {
        const period = this.value;
        document.getElementById('customDateContainer').style.display = 
            (period === 'custom') ? 'block' : 'none';
        document.getElementById('customMonthContainer').style.display = 
            (period === 'month') ? 'block' : 'none';
        updateCharts();
    });

    document.getElementById('chipidSelect').addEventListener('change', updateCharts);
    document.getElementById('customDate').addEventListener('change', updateCharts);
    document.getElementById('customMonth').addEventListener('change', updateCharts);
});