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
            const idAlerta = document.getElementById('idAlerta');
            const editMensaje = document.getElementById('editMensaje');
            const editCultivo = document.getElementById('editCultivo');
            const editFase = document.getElementById('editFase');
            const editAlertaForm = document.getElementById('editAlertaForm');
            const editAlertaModal = document.getElementById('editAlertaModal');

            if (!idAlerta || !editMensaje || !editAlertaForm || !editAlertaModal) {
                console.error("Uno o más elementos del modal no se encontraron en el DOM.");
                return;
            }

            idAlerta.value = data.id;
            editMensaje.value = data.mensaje;

            if (editCultivo) editCultivo.textContent = data.cultivo;
            if (editFase) editFase.textContent = data.fase;

            editAlertaForm.action = `/admin/alertasAdmin/editar/${id}`;
            editAlertaModal.classList.remove('hidden');
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