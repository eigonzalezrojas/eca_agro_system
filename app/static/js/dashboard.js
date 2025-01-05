function updateData() {
    fetch('/latest-data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('temperatura').textContent = data.temperatura !== null ? `${data.temperatura}°C` : '--°C';
            document.getElementById('humedad').textContent = data.humedad !== null ? `${data.humedad}%` : '--%';
            document.getElementById('fecha-hora').textContent = data.fecha_hora ? data.fecha_hora : '--/--/---- --:--:--';
        })
        .catch(error => console.error('Error al obtener los datos:', error));
}

updateData();
setInterval(updateData, 60000);