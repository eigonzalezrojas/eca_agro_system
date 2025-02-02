// Función para abrir el modal de edición usuario
function openEditModal(rut) {
    fetch(`/admin/usuarios/buscar/${rut}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos del usuario");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('editRut').value = data.rut;
            document.getElementById('editNombre').value = data.nombre;
            document.getElementById('editApellido').value = data.apellido;
            document.getElementById('editFono').value = data.fono;
            document.getElementById('editCorreo').value = data.correo;
            document.getElementById('editRol').value = data.fk_rol;
            document.getElementById('editUserForm').action = `/admin/usuarios/editar/${rut}`;
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