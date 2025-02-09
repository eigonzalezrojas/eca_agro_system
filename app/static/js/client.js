document.addEventListener("DOMContentLoaded", function () {
    // Menú hamburguesa
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
    });

    // Actualizar datos automáticamente cada 5 minutos
    setInterval(actualizarDatos, 300000);

    // Manejar cambios en el selector de dispositivos
    document.getElementById("dispositivoSelect").addEventListener("change", function () {
        actualizarDatos();
    });

    // Manejo de filtros para el Resumen de Datos
    const periodoSelect = document.getElementById("periodo");
    const fechaContainer = document.getElementById("contenedor-fecha");
    const mesContainer = document.getElementById("contenedor-mes");
    const anioContainer = document.getElementById("contenedor-anio");

    function actualizarVisibilidad() {
        const periodo = periodoSelect.value;

        fechaContainer.classList.toggle("hidden", periodo !== "day");
        mesContainer.classList.toggle("hidden", periodo !== "month");
        anioContainer.classList.toggle("hidden", periodo !== "month" && periodo !== "year");
    }

    periodoSelect.addEventListener("change", actualizarVisibilidad);
    actualizarVisibilidad();

    // Inicializar gráficos con Chart.js
    const ctxTemp = document.getElementById('grafico-temperatura').getContext('2d');
    const ctxHum = document.getElementById('grafico-humedad').getContext('2d');

    let tempChart = new Chart(ctxTemp, getChartConfig('Temperatura', '°C', 'rgba(255, 99, 132, 0.6)'));
    let humChart = new Chart(ctxHum, getChartConfig('Humedad', '%', 'rgba(54, 162, 235, 0.6)'));

    // Evento para filtrar datos y actualizar gráficos
    document.getElementById("filtrar").addEventListener("click", function () {
        actualizarResumen(tempChart, humChart);
    });

    // Cargar datos al inicio
    actualizarDatos();
    actualizarResumen(tempChart, humChart);
});

// Función para obtener la configuración de los gráficos
function getChartConfig(label, unit, color) {
    return {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                borderColor: color,
                backgroundColor: color.replace('0.6', '0.3'),
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Periodo' } },
                y: { title: { display: true, text: unit } }
            }
        }
    };
}

// Función para actualizar el bloque "Estado Actual"
function actualizarDatos() {
    const chipid = document.getElementById("dispositivoSelect").value;

    if (!chipid) {
        console.warn("No hay dispositivo seleccionado");
        return;
    }

    fetch(`/client/datos?chipid=${chipid}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error:", data.error);
                return;
            }

            document.getElementById('temperatura').innerText = data.temperatura + "°C";
            document.getElementById('humedad').innerText = data.humedad + "%";
            document.getElementById('fecha_hora').innerText = data.fecha_hora;
            document.getElementById('horas_frio').innerText = data.horas_frio !== "--" ? data.horas_frio + "h" : "--";
            document.getElementById('gda').innerText = data.gda !== "--" ? data.gda.toFixed(2) : "--";
        })
        .catch(error => console.error("Error al obtener los datos:", error));
}

// Función para actualizar el resumen de datos y los gráficos
function actualizarResumen(tempChart, humChart) {
    const chipid = document.getElementById("dispositivoSelect").value;
    const periodo = document.getElementById("periodo").value;
    const fecha = document.getElementById("fecha").value;
    const mes = document.getElementById("mes").value;
    const anio = document.getElementById("anio").value;

    let url = `/client/resumen?chipid=${chipid}&periodo=${periodo}`;
    if (periodo === "day") url += `&fecha=${fecha}`;
    if (periodo === "month") url += `&mes=${mes}&anio=${anio}`;
    if (periodo === "year") url += `&anio=${anio}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            actualizarTabla(data);
            actualizarGraficos(tempChart, humChart, data, periodo);
        })
        .catch(error => console.error('Error al obtener datos:', error));
}

// Función para actualizar la tabla de resumen de datos
function actualizarTabla(data) {
    const tbody = document.getElementById("tabla-resumen");
    tbody.innerHTML = "";
    data.forEach(row => {
        let tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="border p-2 text-center">${row.periodo}</td>
            <td class="border p-2 text-center">${row.temp_max}°C</td>
            <td class="border p-2 text-center">${row.temp_min}°C</td>
            <td class="border p-2 text-center">${row.hum_max}%</td>
            <td class="border p-2 text-center">${row.hum_min}%</td>
        `;
        tbody.appendChild(tr);
    });
}

// Función para actualizar los gráficos según el período seleccionado
function actualizarGraficos(tempChart, humChart, data, periodo) {
    let labels = data.map(d => d.periodo);
    let tempMax = data.map(d => d.temp_max);
    let tempMin = data.map(d => d.temp_min);
    let humMax = data.map(d => d.hum_max);
    let humMin = data.map(d => d.hum_min);

    // Ajustar etiquetas en el eje X según el período seleccionado
    if (periodo === 'day') {
        labels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
    } else if (periodo === 'month') {
        labels = Array.from({ length: 30 }, (_, i) => `Día ${i + 1}`);
    } else if (periodo === 'year') {
        labels = Array.from({ length: 52 }, (_, i) => `Semana ${i + 1}`);
    }

    // Actualizar gráfico de Temperatura
    tempChart.data.labels = labels;
    tempChart.data.datasets[0].data = tempMax;
    tempChart.update();

    // Actualizar gráfico de Humedad
    humChart.data.labels = labels;
    humChart.data.datasets[0].data = humMax;
    humChart.update();
}
