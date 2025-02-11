document.addEventListener("DOMContentLoaded", function () {
    // Menú hamburguesa
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
    });

    const userMenuButton = document.getElementById("userMenuButton");
    const userMenu = document.getElementById("userMenu");

    userMenuButton.addEventListener("click", function (event) {
        event.stopPropagation();
        userMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", function (event) {
        if (!userMenu.contains(event.target) && !userMenuButton.contains(event.target)) {
            userMenu.classList.add("hidden");
        }
    });

    setInterval(actualizarDatos, 300000);

    document.getElementById("dispositivoSelect").addEventListener("change", function () {
        actualizarDatos();
    });

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

    const ctxTemp = document.getElementById('grafico-temperatura').getContext('2d');
    const ctxHum = document.getElementById('grafico-humedad').getContext('2d');

    let tempChart = new Chart(ctxTemp, getChartConfig('Temperatura', '°C', 'rgba(255, 99, 132, 0.6)'));
    let humChart = new Chart(ctxHum, getChartConfig('Humedad', '%', 'rgba(54, 162, 235, 0.6)'));

    document.getElementById("filtrar").addEventListener("click", function () {
        actualizarResumen(tempChart, humChart);
    });

    actualizarDatos();
    actualizarResumen(tempChart, humChart);
});

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

function actualizarResumen(tempChart, humChart) {
    const chipid = document.getElementById("dispositivoSelect").value;
    const periodo = document.getElementById("periodo").value;
    const fecha = document.getElementById("fecha").value;
    const mes = document.getElementById("mes").value;
    const anio = document.getElementById("anio").value;

    let url = `/client/datos/resumen?chipid=${chipid}&periodo=${periodo}`;
    if (periodo === "day") url += `&fecha=${fecha}`;
    if (periodo === "month") url += `&mes=${mes}&anio=${anio}`;
    if (periodo === "year") url += `&anio=${anio}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log("Datos recibidos:", data); // 🔍 Verificar la estructura en la consola
            if (!Array.isArray(data)) {
                console.error("Error: la respuesta del servidor no es un array.", data);
                return;
            }
            actualizarTabla(data);
            actualizarGraficos(tempChart, humChart, data, periodo);
        })
        .catch(error => console.error('Error al obtener datos:', error));
}

function actualizarTabla(data) {
    const tbody = document.getElementById("tabla-resumen");
    tbody.innerHTML = "";

    if (!Array.isArray(data)) {
        console.error("Error: Se esperaba un array en actualizarTabla", data);
        return;
    }

    data.forEach(row => {
        let tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="border p-2 text-center">${row.periodo}</td>
            <td class="border p-2 text-center">${row.temp_max ?? "--"}°C</td>
            <td class="border p-2 text-center">${row.temp_min ?? "--"}°C</td>
            <td class="border p-2 text-center">${row.hum_max ?? "--"}%</td>
            <td class="border p-2 text-center">${row.hum_min ?? "--"}%</td>
        `;
        tbody.appendChild(tr);
    });
}


function actualizarGraficos(tempChart, humChart, data, periodo) {
    if (!Array.isArray(data) || data.length === 0) {
        console.warn("⚠️ No hay datos para graficar.");
        return;
    }

    console.log("📊 Datos para el gráfico:", data);

    // Obtener los datos de temperatura y humedad
    let labels = data.map(d => d.periodo);
    let tempMax = data.map(d => d.temp_max ?? null);
    let tempMin = data.map(d => d.temp_min ?? null);
    let humMax = data.map(d => d.hum_max ?? null);
    let humMin = data.map(d => d.hum_min ?? null);

    // Ajustar etiquetas del eje X según el período seleccionado
    if (periodo === 'day') {
        labels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
    } else if (periodo === 'month') {
        labels = Array.from({ length: 30 }, (_, i) => `Día ${i + 1}`);
    } else if (periodo === 'year') {
        labels = Array.from({ length: 52 }, (_, i) => `Semana ${i + 1}`);
    }

    // Actualizar gráfico de Temperatura
    tempChart.data.labels = labels;
    tempChart.data.datasets = [
        {
            label: "Temperatura Máx",
            data: tempMax,
            borderColor: "rgba(255, 99, 132, 1)",
            backgroundColor: "rgba(255, 99, 132, 0.2)",
            fill: true
        },
        {
            label: "Temperatura Mín",
            data: tempMin,
            borderColor: "rgba(255, 159, 64, 1)",
            backgroundColor: "rgba(255, 159, 64, 0.2)",
            fill: true
        }
    ];
    tempChart.update();

    // Actualizar gráfico de Humedad
    humChart.data.labels = labels;
    humChart.data.datasets = [
        {
            label: "Humedad Máx",
            data: humMax,
            borderColor: "rgba(54, 162, 235, 1)",
            backgroundColor: "rgba(54, 162, 235, 0.2)",
            fill: true
        },
        {
            label: "Humedad Mín",
            data: humMin,
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            fill: true
        }
    ];
    humChart.update();
}

