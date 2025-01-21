let tempChart, humChart;

// Inicializar los gráficos
function initCharts() {
    const tempCtx = document.getElementById('tempChart').getContext('2d');
    const humCtx = document.getElementById('humChart').getContext('2d');
    
    const commonOptions = {
        responsive: true,
        scales: {
            y: {
                beginAtZero: true
            }
        },
        plugins: {
            title: {
                display: true,
                font: {
                    size: 16
                }
            }
        }
    };
    
    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: []
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                title: {
                    ...commonOptions.plugins.title,
                    text: 'Temperatura (°C)'
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
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                title: {
                    ...commonOptions.plugins.title,
                    text: 'Humedad (%)'
                }
            }
        }
    });
}


function updateTables(data) {
    // Actualizar tabla de temperatura
    const temperatureTableBody = document.querySelector('#temperatureTable tbody');
    temperatureTableBody.innerHTML = '';

    // Actualizar tabla de humedad
    const humidityTableBody = document.querySelector('#humidityTable tbody');
    humidityTableBody.innerHTML = '';

    Object.keys(data).forEach((chipid) => {
        const deviceData = data[chipid];
        
        const tempRow = document.createElement('tr');
        tempRow.innerHTML = `
            <td>${chipid}</td>
            <td>${Math.max(...deviceData.max_temp)}</td>
            <td>${Math.min(...deviceData.min_temp)}</td>
        `;
        temperatureTableBody.appendChild(tempRow);

        // Crear fila para la tabla de humedad
        const humRow = document.createElement('tr');
        humRow.innerHTML = `
            <td>${chipid}</td>
            <td>${Math.max(...deviceData.max_hum)}</td>
            <td>${Math.min(...deviceData.min_hum)}</td>
        `;
        humidityTableBody.appendChild(humRow);
    });
}


// Actualizar los gráficos con datos de la API
function updateCharts() {
    const chipid = document.getElementById('chipidSelect').value;
    const period = document.getElementById('periodSelect').value;
    const customDate = document.getElementById('customDate').value;

    let url = `/api/data?period=${period}`;
    if (chipid) url += `&chipid=${chipid}`;

    if (period === 'custom' && customDate) {
        url += `&date=${customDate}`;
    } else if (period === 'month') {
        const year = document.getElementById('yearSelect').value;
        const month = document.getElementById('monthSelect').value;
        url += `&month=${year}-${month}`;
    }

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {

            // Actualizar gráficos
            tempChart.data.labels = [];
            tempChart.data.datasets = [];
            humChart.data.labels = [];
            humChart.data.datasets = [];

            Object.keys(data).forEach((chipid, index) => {
                const color = `hsl(${index * 60}, 70%, 50%)`;
                const deviceData = data[chipid];

                function createDataset(label, data, isDashed = false) {
                    return {
                        label: label,
                        data: data,
                        borderColor: color,
                        borderDash: isDashed ? [5, 5] : [],
                        fill: false,
                        tension: 0.4
                    };
                }

                tempChart.data.labels = deviceData.labels;
                tempChart.data.datasets.push(
                    createDataset(`Dispositivo ${chipid} - Temperatura Máxima`, deviceData.max_temp),
                    createDataset(`Dispositivo ${chipid} - Temperatura Mínima`, deviceData.min_temp, true)
                );

                humChart.data.labels = deviceData.labels;
                humChart.data.datasets.push(
                    createDataset(`Dispositivo ${chipid} - Humedad Máxima`, deviceData.max_hum),
                    createDataset(`Dispositivo ${chipid} - Humedad Mínima`, deviceData.min_hum, true)
                );
            });

            const titleSuffix = getTitleSuffix(period);
            tempChart.options.plugins.title.text = `Temperatura (°C) ${titleSuffix}`;
            humChart.options.plugins.title.text = `Humedad (%) ${titleSuffix}`;

            tempChart.update();
            humChart.update();

            // Actualizar tablas
            updateTables(data);
        })
        .catch(error => {
            console.error('Error al actualizar los gráficos y las tablas:', error);
            [tempChart, humChart].forEach(chart => {
                chart.data.labels = [];
                chart.data.datasets = [];
                chart.update();
            });
        });
}

// Función helper para obtener el sufijo del título según el período
function getTitleSuffix(period) {
    switch (period) {
        case 'day':
            return '- Último día';
        case 'week':
            return '- Última semana';
        case 'month':
            const year = document.getElementById('yearSelect').value;
            const month = document.getElementById('monthSelect');
            const monthName = month.options[month.selectedIndex].text;
            return `- ${monthName} ${year}`;
        case 'custom':
            const date = document.getElementById('customDate').value;
            return date ? `- ${date}` : '';
        default:
            return '';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    updateCharts();
    
    const filterElements = [
        'chipidSelect',
        'periodSelect',
        'yearSelect',
        'monthSelect',
        'customDate'
    ];

    filterElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.addEventListener('change', updateCharts);
        }
    });
});