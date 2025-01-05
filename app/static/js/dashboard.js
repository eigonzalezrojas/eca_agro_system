// dashboard.js
function updateData() {
    //console.log('Actualizando datos del estado general...');
    fetch('/latest-data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            //console.log('Datos recibidos del estado general:', data);

            // Actualizar temperatura
            const tempElement = document.getElementById('temperatura');
            if (tempElement) {
                tempElement.textContent = data.temperatura !== null 
                    ? `${parseFloat(data.temperatura).toFixed(1)}°C` 
                    : '--°C';
            }

            // Actualizar humedad
            const humElement = document.getElementById('humedad');
            if (humElement) {
                humElement.textContent = data.humedad !== null 
                    ? `${parseFloat(data.humedad).toFixed(1)}%` 
                    : '--%';
            }

            // Actualizar fecha y hora
            const fechaElement = document.getElementById('fecha-hora');
            if (fechaElement) {
                fechaElement.textContent = data.fecha_hora || '--/--/---- --:--:--';
            }
        })
        .catch(error => {
            //console.error('Error al obtener los datos del estado general:', error);
            const tempElement = document.getElementById('temperatura');
            const humElement = document.getElementById('humedad');
            const fechaElement = document.getElementById('fecha-hora');

            if (tempElement) tempElement.textContent = '--°C';
            if (humElement) humElement.textContent = '--%';
            if (fechaElement) fechaElement.textContent = '--/--/---- --:--:--';
        });
}

// Inicializar la actualización de datos cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    updateData();
    setInterval(updateData, 60000);
});