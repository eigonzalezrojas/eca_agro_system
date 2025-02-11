document.addEventListener("DOMContentLoaded", function () {
    cargarAlertas();
});

function cargarAlertas() {
    fetch("/client/alertasCliente/listar", {
        method: "GET",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("flash-messages").innerHTML = `<div class="p-3 bg-red-500 text-white">${data.error}</div>`;
            return;
        }

        const tbody = document.getElementById("alertas-table-body");
        tbody.innerHTML = "";

        data.alertas.forEach(alerta => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td class="border px-4 py-2 text-center">${alerta.cultivo}</td>
                <td class="border px-4 py-2 text-center">${alerta.fase}</td>
                <td class="border px-4 py-2 text-center">${alerta.fecha}</td>
                <td class="border px-4 py-2 text-center">${alerta.mensaje}</td>
                <td class="border px-4 py-2 text-center">
                    <span class="px-2 py-1 rounded ${obtenerClaseNivel(alerta.nivel)}">${alerta.nivel}</span>
                </td>
            `;

            tbody.appendChild(row);
        });
    })
    .catch(error => console.error("Error al cargar alertas:", error));
}

function obtenerClaseNivel(nivel) {
    switch (nivel) {
        case "Crítica":
            return "bg-red-500 text-white";
        case "Advertencia":
            return "bg-yellow-500 text-black";
        default:
            return "bg-green-500 text-white";
    }
}
