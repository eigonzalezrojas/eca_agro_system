const openModal = document.getElementById("openUsuarioModal");
const closeModal = document.getElementById("closeUsuarioModal");

if (openModal && closeModal) {
    openModal.addEventListener("click", () => {
        usuarioModal.classList.remove("hidden");
    });

    closeModal.addEventListener("click", () => {
        usuarioModal.classList.add("hidden");
    });
}


// Función para abrir el modal de edición usuario
function openEditModal(rut) {
    fetch(`/admin/usuario/buscar/${rut}`)
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
            document.getElementById('editUserForm').action = `/admin/usuario/editar/${rut}`;
            document.getElementById('editUsuarioModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos del usuario:', error));
}

// Función para cerrar el modal
function closeEditModal() {
    document.getElementById('editUsuarioModal').classList.add('hidden');
}


// Función para abrir el modal de eliminación
function openDeleteModal(rut) {
    document.getElementById('deleteUsuarioForm').action = `/admin/usuario/eliminar/${rut}`;
    document.getElementById('deleteUsuarioModal').classList.remove('hidden');
}

// Función para cerrar el modal de eliminación
function closeDeleteModal() {
    document.getElementById('deleteUsuarioModal').classList.add('hidden');
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        usuarioModal.classList.add("hidden");
        editUsuarioModal.classList.add("hidden");
        deleteUsuarioModal.classList.add("hidden")
    }
});