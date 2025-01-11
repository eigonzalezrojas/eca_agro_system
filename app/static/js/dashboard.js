// Función para actualizar los datos del estado general
function updateData() {
    fetch('/latest-data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {            
            const tempElement = document.getElementById('temperatura');
            if (tempElement) {
                tempElement.textContent = data.temperatura !== null 
                    ? `${parseFloat(data.temperatura).toFixed(1)}°C` 
                    : '--°C';
            }
            
            const humElement = document.getElementById('humedad');
            if (humElement) {
                humElement.textContent = data.humedad !== null 
                    ? `${parseFloat(data.humedad).toFixed(1)}%` 
                    : '--%';
            }

            const fechaElement = document.getElementById('fecha-hora');
            if (fechaElement) {
                fechaElement.textContent = data.fecha_hora || '--/--/---- --:--:--';
            }
        })
        .catch(error => {
            console.error('Error al obtener los datos del estado general:', error);
            const tempElement = document.getElementById('temperatura');
            const humElement = document.getElementById('humedad');
            const fechaElement = document.getElementById('fecha-hora');

            if (tempElement) tempElement.textContent = '--°C';
            if (humElement) humElement.textContent = '--%';
            if (fechaElement) fechaElement.textContent = '--/--/---- --:--:--';
        });
}

// Función para poblar el selector de años
function populateYears() {
    const yearSelect = document.getElementById('yearSelect');
    if (!yearSelect) return;

    const startYear = 2024;
    const currentYear = new Date().getFullYear();
    
    yearSelect.innerHTML = '';
    
    for (let year = startYear; year <= currentYear; year++) {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    }
    
    yearSelect.value = currentYear;
}

// Función para manejar la visibilidad de los contenedores de filtros
function handleFilterVisibility() {
    const period = document.getElementById('periodSelect').value;
    const monthYearContainer = document.getElementById('monthYearContainer');
    const customDateContainer = document.getElementById('customDateContainer');
    
    monthYearContainer.style.display = 'none';
    customDateContainer.style.display = 'none';
    
    if (period === 'month') {
        monthYearContainer.style.display = 'block';
    } else if (period === 'custom') {
        customDateContainer.style.display = 'block';
    }
}

// Función para obtener el valor del filtro de mes
function getMonthFilterValue() {
    const period = document.getElementById('periodSelect').value;
    if (period === 'month') {
        const year = document.getElementById('yearSelect').value;
        const month = document.getElementById('monthSelect').value;
        return `${year}-${month}`;
    }
    return null;
}

// Función para formatear las horas frío
function formatearHorasFrio(horas) {
    if (horas === 1) {
        return "1 hora";
    }
    return `${horas} horas`;
}

// Función para obtener y actualizar las Horas Frío
function actualizarHorasFrio() {
    const horasFrioElement = document.getElementById('horas-frio');
    
    fetch('/api/horas-frio')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.horas_frio !== undefined) {
                const horasFormateadas = formatearHorasFrio(data.horas_frio);
                horasFrioElement.textContent = horasFormateadas;

                if (data.periodo) {
                    const inicio = new Date(data.periodo.inicio).toLocaleString();
                    const fin = new Date(data.periodo.fin).toLocaleString();
                    horasFrioElement.title = `Período: ${inicio} - ${fin}`;
                }
                
                if (data.horas_frio > 0) {
                    horasFrioElement.classList.add('text-primary');
                } else {
                    horasFrioElement.classList.remove('text-primary');
                }
            } else {
                horasFrioElement.textContent = "Sin datos";
                horasFrioElement.title = "No hay datos disponibles";
            }
        })
        .catch(error => {
            console.error("Error al obtener las Horas Frío:", error);
            horasFrioElement.textContent = "Error";
            horasFrioElement.title = "Error al obtener los datos";
            horasFrioElement.classList.add('text-danger');
        });
}

// Función para inicializar las actualizaciones
function inicializarActualizaciones() {    
    actualizarHorasFrio();
    setInterval(actualizarHorasFrio, 300000);
}

function actualizarGDA() {
    const gdaElement = document.getElementById('gda');
    const tempBase = 7.2;
    const dias = 7;
    
    const isProduction = window.location.hostname !== '127.0.0.1' && window.location.hostname !== 'localhost';
    const apiUrl = `${isProduction ? '/monitor' : ''}/api/gda?temp_base=${tempBase}&dias=${dias}`;

    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.gda_acumulado !== undefined) {
                gdaElement.textContent = `${data.gda_acumulado.toFixed(1)} GDA`;
                gdaElement.title = `Período: ${new Date(data.periodo.inicio).toLocaleDateString()} - ${new Date(data.periodo.fin).toLocaleDateString()}`;
            } else {
                gdaElement.textContent = "Sin datos";
                gdaElement.title = "No hay datos disponibles";
            }
        })
        .catch(error => {
            console.error("Error al obtener los GDA:", error);
            gdaElement.textContent = "Error";
            gdaElement.title = "Error al obtener los datos";
        });
}

// Inicializar cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {    
    updateData();
    inicializarActualizaciones();
    setInterval(updateData, 60000);
    actualizarGDA();    
    populateYears();

    document.getElementById('periodSelect').addEventListener('change', function() {
        handleFilterVisibility();
        if (typeof updateCharts === 'function') {
            updateCharts();
        }
    });

    document.getElementById('yearSelect').addEventListener('change', function() {
        if (typeof updateCharts === 'function') {
            updateCharts();
        }
    });

    document.getElementById('monthSelect').addEventListener('change', function() {
        if (typeof updateCharts === 'function') {
            updateCharts();
        }
    });

    handleFilterVisibility();
});