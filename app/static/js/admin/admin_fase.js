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

// Función para abrir el modal de edición fase
function openEditFaseModal(id) {
    fetch(`/admin/fase/buscar/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos de fase");
            }
            console.log(response)
            return response.json();
        })
        .then(data => {
            document.getElementById('idFase').value = data.id;
            document.getElementById('editFase').value = data.nombre;
            document.getElementById('editFaseForm').action = `/admin/fase/editar/${id}`;
            document.getElementById('editFaseModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos de la Fase:', error));
}

// Función para cerrar el modal
function closeEditFaseModal() {
    document.getElementById('editFaseModal').classList.add('hidden');
}


// Función para abrir el modal de eliminación
function openDeleteFaseModal(id) {
    document.getElementById('deleteFaseForm').action = `/admin/fase/eliminar/${id}`;
    document.getElementById('deleteFaseModal').classList.remove('hidden');
}

// Función para cerrar el modal de eliminación
function closeDeleteFaseModal() {
    document.getElementById('deleteFaseModal').classList.add('hidden');
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        faseModal.classList.add("hidden");
        editFaseModal.classList.add("hidden");
        deleteFaseModal.classList.add("hidden")
    }
});