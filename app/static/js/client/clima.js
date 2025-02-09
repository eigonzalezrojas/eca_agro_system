document.addEventListener("DOMContentLoaded", function () {
    cargarParcelas(); // Cargar parcelas al iniciar
});

function cargarParcelas() {
    fetch('/client/clima/parcelas')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error al obtener las parcelas:", data.error);
                return;
            }

            const selectParcelas = document.getElementById("parcelas");
            selectParcelas.innerHTML = '<option value="" selected disabled>Selecciona una parcela...</option>';

            data.parcelas.forEach(parcela => {
                let option = document.createElement("option");
                option.value = parcela.id;
                option.textContent = parcela.nombre;
                selectParcelas.appendChild(option);
            });

            // Escuchar cambios en la selección de parcela
            selectParcelas.addEventListener("change", function () {
                let parcelaId = this.value;
                if (parcelaId) {
                    cargarClima(parcelaId);
                }
            });
        })
        .catch(error => console.error("Error al cargar las parcelas:", error));
}

function cargarClima(parcelaId) {
    fetch(`/client/clima/obtener-clima?parcela_id=${parcelaId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error al obtener el clima:", data.error);
                return;
            }

            console.log("Datos del clima recibidos:", data); // ✅ Verificar estructura

            // Clima actual
            document.getElementById("ubicacion").innerText = data.clima_actual.ubicacion;
            document.getElementById("descripcion").innerText = data.clima_actual.descripcion;
            document.getElementById("temp_actual").innerText = `${data.clima_actual.temp_actual}°C`;
            document.getElementById("humedad").innerText = `Humedad: ${data.clima_actual.humedad}%`;
            document.getElementById("viento").innerText = `Viento: ${data.clima_actual.viento} km/h`;

            // Obtener ícono basado en el código de condición del clima
            const iconoClima = getWeatherIcon(data.clima_actual.codigo_clima);
            document.getElementById("icono-clima").innerHTML = `<i data-lucide="${iconoClima}" class="w-16 h-16 mx-auto"></i>`;
            lucide.createIcons();

            // Verificamos si data.pronostico tiene datos
            if (!data.pronostico || data.pronostico.length === 0) {
                console.warn("⚠️ No se encontraron datos de pronóstico en la respuesta.");
                return;
            }

            // Pronóstico de 5 días
            const pronosticoContainer = document.getElementById("pronostico-container");
            pronosticoContainer.innerHTML = ""; // Limpiar contenido anterior

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
        1072: "cloud-drizzle", // Llovizna congelante
        1087: "cloud-lightning", // Tormenta eléctrica
        1114: "wind", // Viento fuerte
        1117: "wind", // Ventisca
        1135: "cloud-fog", // Niebla
        1147: "cloud-fog", // Niebla congelante
        1150: "cloud-drizzle", // Llovizna ligera
        1153: "cloud-drizzle", // Llovizna
        1168: "cloud-drizzle", // Llovizna helada
        1171: "cloud-drizzle", // Llovizna intensa
        1180: "cloud-rain", // Lluvia ligera
        1183: "cloud-rain", // Lluvia moderada
        1186: "cloud-rain", // Lluvia intensa
        1189: "cloud-rain", // Lluvia fuerte
        1192: "cloud-rain", // Lluvia torrencial
        1195: "cloud-rain", // Lluvia extrema
        1198: "cloud-drizzle", // Llovizna helada ligera
        1201: "cloud-drizzle", // Llovizna helada intensa
        1204: "cloud-rain", // Nieve con lluvia ligera
        1207: "cloud-rain", // Nieve con lluvia fuerte
        1210: "cloud-snow", // Nieve ligera
        1213: "cloud-snow", // Nieve moderada
        1216: "cloud-snow", // Nieve fuerte
        1219: "cloud-snow", // Nieve intensa
        1222: "cloud-snow", // Nieve abundante
        1225: "cloud-snow", // Tormenta de nieve
        1237: "cloud-snow", // Granizo
        1240: "cloud-rain", // Lluvia dispersa
        1243: "cloud-rain", // Lluvia dispersa fuerte
        1246: "cloud-rain", // Lluvia torrencial dispersa
        1249: "cloud-snow", // Lluvia y nieve dispersa
        1252: "cloud-snow", // Lluvia y nieve fuerte
        1255: "cloud-snow", // Nieve dispersa
        1258: "cloud-snow", // Nieve fuerte dispersa
        1261: "cloud-snow", // Granizo disperso
        1264: "cloud-snow", // Granizo fuerte disperso
        1273: "cloud-lightning", // Tormenta con lluvia
        1276: "cloud-lightning", // Tormenta fuerte con lluvia
        1279: "cloud-lightning", // Tormenta con nieve
        1282: "cloud-lightning", // Tormenta fuerte con nieve
    };
    return iconMap[weatherCode] || "help-circle"; // Default en caso de error
}


