document.addEventListener("DOMContentLoaded", function () {
    // Menú hamburguesa
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
    });
    // Actualizar cada 5 segundos
    setInterval(actualizarDatos, 5000);
    // Cargar datos al inicio
    actualizarDatos();
});

function actualizarDatos() {
    fetch('/client/datos')
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