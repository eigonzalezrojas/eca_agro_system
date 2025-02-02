document.addEventListener("DOMContentLoaded", function () {
    // Menú hamburguesa
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
    });

    // Modal usuarios
    const openModal = document.getElementById("openModal");
    const closeModal = document.getElementById("closeModal");
    const modal = document.getElementById("modal");

    if (openModal && closeModal && modal) {
        openModal.addEventListener("click", () => {
            modal.classList.remove("hidden");
        });

        closeModal.addEventListener("click", () => {
            modal.classList.add("hidden");
        });
    }
});





// Función para abrir el modal de edición
function openEditModal(rut) {
    console.log("RUT recibido:", rut);
    fetch(`/admin/usuarios/buscar/${rut}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos del usuario");
            }
            return response.json();
        })
        .then(data => {
            console.log(data)
            document.getElementById('editRut').value = data.rut;
            document.getElementById('editNombre').value = data.nombre;
            document.getElementById('editApellido').value = data.apellido;
            document.getElementById('editFono').value = data.fono;
            document.getElementById('editCorreo').value = data.correo;
            document.getElementById('editRol').value = data.fk_rol;
            document.getElementById('editForm').action = `/admin/usuarios/editar/${rut}`;
            document.getElementById('editModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos del usuario:', error));
}

// Función para cerrar el modal
function closeEditModal() {
    document.getElementById('editModal').classList.add('hidden');
}


// Función para abrir el modal de eliminación
function openDeleteModal(rut) {
    document.getElementById('deleteForm').action = `/admin/usuarios/eliminar/${rut}`;
    document.getElementById('deleteModal').classList.remove('hidden');
}

// Función para cerrar el modal de eliminación
function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        modal.classList.add("hidden");
        editModal.classList.add("hidden");
    }
});