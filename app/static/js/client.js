document.addEventListener("DOMContentLoaded", function () {
    // Menú hamburguesa
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
    });
    // Actualizar cada 5 minutos
    setInterval(actualizarDatos, 50000);


    // Manejar cambios en el selector de dispositivos
    document.getElementById("dispositivoSelect").addEventListener("change", function () {
        actualizarDatos();
    });

    //Resumen de datos
    const periodoSelect = document.getElementById("periodo");
    const fechaContainer = document.getElementById("contenedor-fecha");
    const mesContainer = document.getElementById("contenedor-mes");
    const añoContainer = document.getElementById("contenedor-año");

    function actualizarVisibilidad() {
        const periodo = periodoSelect.value;

        fechaContainer.classList.toggle("hidden", periodo !== "day");
        mesContainer.classList.toggle("hidden", periodo !== "month");
        añoContainer.classList.toggle("hidden", periodo !== "month" && periodo !== "year");
    }

    periodoSelect.addEventListener("change", actualizarVisibilidad);
    actualizarVisibilidad();
});

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


document.getElementById("filtrar").addEventListener("click", function () {
    const chipid = "1543087";  // Debe obtenerse dinámicamente
    const periodo = document.getElementById("periodo").value;
    const fecha = document.getElementById("fecha").value;
    const mes = document.getElementById("mes").value;
    const año = document.getElementById("año").value;

    let url = `/client/resumen?chipid=${chipid}&periodo=${periodo}`;
    if (periodo === "day") url += `&fecha=${fecha}`;
    if (periodo === "month") url += `&mes=${mes}&año=${año}`;
    if (periodo === "year") url += `&año=${año}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const tabla = document.getElementById("tabla-resumen");
            tabla.innerHTML = data.map(d =>
                `<tr><td>${d.periodo}</td><td>${d.temp_max}°C</td><td>${d.temp_min}°C</td>
                <td>${d.hum_max}%</td><td>${d.hum_min}%</td></tr>`).join("");
        });
});
