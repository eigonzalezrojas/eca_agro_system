const openModal = document.getElementById("openDispositivoModal");
const closeModal = document.getElementById("closeDispositivoModal");

if (openModal && closeModal) {
    openModal.addEventListener("click", () => {
        dispositivoModal.classList.remove("hidden");
    });

    closeModal.addEventListener("click", () => {
        dispositivoModal.classList.add("hidden");
    });
}

// Función para abrir el modal de edición dispositivo
function openEditDispositivoModal(id) {
    fetch(`/admin/dispositivo/buscar/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos del dispositivo");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('idDispositivo').value = data.id;
            document.getElementById('editChipid').value = data.chipid;
            document.getElementById('editModelo').value = data.modelo;
            document.getElementById('editCaracteristica').value = data.caracteristica;
            document.getElementById('editDispositivoForm').action = `/admin/dispositivo/editar/${id}`;
            document.getElementById('editDispositivoModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos del dispositivo:', error));
}

// Función para cerrar el modal
function closeEditDispositivoModal() {
    document.getElementById('editDispositivoModal').classList.add('hidden');
}


// Función para abrir el modal de eliminación
function openDeleteDispositivoModal(id) {
    document.getElementById('deleteDispositivoForm').action = `/admin/dispositivo/eliminar/${id}`;
    document.getElementById('deleteDispositivoModal').classList.remove('hidden');
}

// Función para cerrar el modal de eliminación
function closeDeleteDispositivoModal() {
    document.getElementById('deleteDispositivoModal').classList.add('hidden');
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        dispositivoModal.classList.add("hidden");
        editDispositivoModal.classList.add("hidden");
        deleteDispositivoModal.classList.add("hidden")
    }
});