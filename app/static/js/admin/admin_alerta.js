// Función para abrir el modal de edición alerta
function openEditAlertaModal(id) {
    fetch(`/admin/alertasAdmin/buscar/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos de alerta");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('idAlerta').value = data.id;
            document.getElementById('editMensaje').value = data.mensaje;

            // Mostrar cultivo y fase en el modal (si necesitas editarlos en el futuro)
            document.getElementById('editCultivo').textContent = data.cultivo;
            document.getElementById('editFase').textContent = data.fase;

            document.getElementById('editAlertaForm').action = `/admin/alertasAdmin/editar/${id}`;
            document.getElementById('editAlertaModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos de alerta:', error));
}

// Función para cerrar el modal
function closeEditAlertaModal() {
    document.getElementById('editAlertaModal').classList.add('hidden');
}


// Función para abrir el modal de eliminación
function openDeleteAlertaModal(id) {
    document.getElementById('deleteAlertaForm').action = `/admin/alertasAdmin/eliminar/${id}`;
    document.getElementById('deleteAlertaModal').classList.remove('hidden');
}

// Función para cerrar el modal de eliminación
function closeDeleteAlertaModal() {
    document.getElementById('deleteAlertaModal').classList.add('hidden');
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        editAlertaModal.classList.add("hidden");
        deleteAlertaModal.classList.add("hidden")
    }
});