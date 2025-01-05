function updateData() {
    fetch('/latest-data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperatura').textContent = data.temperatura !== null ? `${data.temperatura}°C` : '--°C';
            document.getElementById('humedad').textContent = data.humedad !== null ? `${data.humedad}%` : '--%';
        })
        .catch(error => console.error('Error al obtener los datos:', error));
}

// Actualizar los datos al cargar la página
updateData();

// Actualizar los datos cada 1 minuto
setInterval(updateData, 60000);