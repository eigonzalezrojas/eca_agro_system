const openModal = document.getElementById("openFaseModal");
const closeModal = document.getElementById("closeFaseModal");

if (openModal && closeModal) {
    openModal.addEventListener("click", () => {
        faseModal.classList.remove("hidden");
    });

    closeModal.addEventListener("click", () => {
        faseModal.classList.add("hidden");
    });
}

// Función para abrir el modal de edición cultivo
function openEditCultivoModal(id) {
    fetch(`/admin/fase/buscar/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos de cultivo");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('idCultivo').value = data.id;
            document.getElementById('editNombre').value = data.nombre;
            document.getElementById('editVariedad').value = data.variedad;
            document.getElementById('editDetalle').value = data.detalle;
            document.getElementById('editCultivoForm').action = `/admin/cultivo/editar/${id}`;
            document.getElementById('editCultivoModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos de Cultivo:', error));
}

// Función para cerrar el modal
function closeEditCultivoModal() {
    document.getElementById('editCultivoModal').classList.add('hidden');
}


// Función para abrir el modal de eliminación
function openDeleteCultivoModal(id) {
    document.getElementById('deleteCultivoForm').action = `/admin/cultivo/eliminar/${id}`;
    document.getElementById('deleteCultivoModal').classList.remove('hidden');
}

// Función para cerrar el modal de eliminación
function closeDeleteCultivoModal() {
    document.getElementById('deleteCultivoModal').classList.add('hidden');
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        faseModal.classList.add("hidden");
        editCultivoModal.classList.add("hidden");
        deleteCultivoModal.classList.add("hidden")
    }
});