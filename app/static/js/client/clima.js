document.addEventListener("DOMContentLoaded", function () {
    cargarClima();
});

function cargarClima() {
    fetch('/client/clima/obtener')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error al obtener el clima:", data.error);
                return;
            }

            // Verifica si los elementos existen antes de modificar
            const ubicacionEl = document.getElementById("ubicacion");
            const descripcionEl = document.getElementById("descripcion");
            const tempActualEl = document.getElementById("temp_actual");
            const humedadEl = document.getElementById("humedad");
            const vientoEl = document.getElementById("viento");
            const iconoClimaEl = document.getElementById("icono-clima");
            const pronosticoContainer = document.getElementById("pronostico-container");

            if (!ubicacionEl || !descripcionEl || !tempActualEl || !humedadEl || !vientoEl || !iconoClimaEl || !pronosticoContainer) {
                console.error("Error: Elementos HTML no encontrados en el DOM.");
                return;
            }

            // Clima Actual
            ubicacionEl.innerText = data.clima_actual.ubicacion;
            descripcionEl.innerText = data.clima_actual.descripcion;
            tempActualEl.innerText = `${data.clima_actual.temp_actual}°C`;
            humedadEl.innerText = `Humedad: ${data.clima_actual.humedad}%`;
            vientoEl.innerText = `Viento: ${data.clima_actual.viento} km/h`;

            // Obtener ícono basado en el código de condición del clima
            const iconoClima = getWeatherIcon(data.clima_actual.codigo_clima);
            iconoClimaEl.innerHTML = `<i data-lucide="${iconoClima}" class="w-16 h-16 mx-auto"></i>`;
            lucide.createIcons();

            // Pronóstico de 5 días
            pronosticoContainer.innerHTML = "";
            data.pronostico.forEach(dia => {
                let iconoDia = getWeatherIcon(dia.codigo_clima);
                let card = `
                    <div class="bg-gray-100 p-4 rounded-lg shadow-md">
                        <h3 class="font-bold">${dia.fecha}</h3>
                        <i data-lucide="${iconoDia}" class="w-14 h-14 mx-auto"></i>
                        <p>${dia.descripcion}</p>
                        <p class="font-semibold">Máx: ${dia.temp_max}°C</p>
                        <p class="font-semibold">Mín: ${dia.temp_min}°C</p>
                    </div>
                `;
                pronosticoContainer.innerHTML += card;
            });

            lucide.createIcons();
        })
        .catch(error => console.error("Error al cargar el clima:", error));
}

// Mapeo de códigos de WeatherAPI a iconos de Lucide.dev
function getWeatherIcon(weatherCode) {
    const iconMap = {
        1000: "sun", // Soleado
        1003: "cloud-sun", // Parcialmente nublado
        1006: "cloud", // Nublado
        1009: "cloud", // Muy nublado
        1030: "cloud-fog", // Neblina
        1063: "cloud-drizzle", // Lluvia ligera
        1066: "cloud-snow", // Nieve ligera
        1069: "cloud-rain", // Lluvia con nieve
        1087: "cloud-lightning", // Tormenta eléctrica
        1114: "wind", // Viento fuerte
        1135: "cloud-fog", // Niebla
        1150: "cloud-drizzle", // Llovizna ligera
        1180: "cloud-rain", // Lluvia ligera
        1183: "cloud-rain", // Lluvia moderada
        1195: "cloud-rain", // Lluvia fuerte
        1204: "cloud-rain", // Nieve con lluvia ligera
        1210: "cloud-snow", // Nieve ligera
        1273: "cloud-lightning", // Tormenta con lluvia
        1279: "cloud-lightning", // Tormenta con nieve
    };
    return iconMap[weatherCode] || "help-circle";
}
