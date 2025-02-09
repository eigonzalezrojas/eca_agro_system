function cargarHistorialClima() {
        fetch('/client/historial_clima')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('historial_clima_body');
                tbody.innerHTML = "";

                data.forEach(registro => {
                    let fila = `<tr>
                        <td class="border px-4 py-2">${registro.fecha}</td>
                        <td class="border px-4 py-2">${registro.chipid}</td>
                        <td class="border px-4 py-2">${registro.temp_max}</td>
                        <td class="border px-4 py-2">${registro.temp_min}</td>
                        <td class="border px-4 py-2">${registro.horas_frio} h</td>
                        <td class="border px-4 py-2">${registro.gda.toFixed(2)}</td>
                    </tr>`;
                    tbody.innerHTML += fila;
                });
            })
            .catch(error => console.error("Error cargando historial climático:", error));
    }

    cargarHistorialClima();