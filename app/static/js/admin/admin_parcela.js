const openModal = document.getElementById("openModalParcela");
const closeModal = document.getElementById("closeParcelaModal");

if (openModal && closeModal) {
    openModal.addEventListener("click", () => {
        ParcelaModal.classList.remove("hidden");
    });

    closeModal.addEventListener("click", () => {
        ParcelaModal.classList.add("hidden");
    });
}

// Función para abrir el modal de edición parcela
function openEditParcelaModal(id) {
    fetch(`/admin/parcela/buscar/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos de parcela");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('idParcela').value = data.id;
            document.getElementById('editNombre').value = data.nombre;
            document.getElementById('regiones').value = data.region;
            document.getElementById('comunas').value = data.comuna;
            document.getElementById('editDireccion').value = data.direccion;
            document.getElementById('editUsuario').value = data.fk_usuario;
            document.getElementById('editParcelaForm').action = `/admin/parcela/editar/${id}`;
            document.getElementById('editParcelaModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos de Parcela:', error));
}

// Función para cerrar el modal
function closeEditParcelaModal() {
    document.getElementById('editParcelaModal').classList.add('hidden');
}


// Función para abrir el modal de eliminación
function openDeleteParcelaModal(id) {
    document.getElementById('deleteParcelaForm').action = `/admin/parcela/eliminar/${id}`;
    document.getElementById('deleteParcelaModal').classList.remove('hidden');
}

// Función para cerrar el modal de eliminación
function closeDeleteParcelaModal() {
    document.getElementById('deleteParcelaModal').classList.add('hidden');
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        ParcelaModal.classList.add("hidden");
        editParcelaModal.classList.add("hidden");
        deleteParcelaModal.classList.add("hidden")
    }
});