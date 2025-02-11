// Obtener los elementos del DOM
const openRegistroModalBtn = document.getElementById("openRegistroModal");
const closeRegistroModalBtn = document.getElementById("closeRegistroModal");
const registroModal = document.getElementById("registroModal");

// Verificar si los elementos existen antes de añadir los eventos
if (openRegistroModalBtn && closeRegistroModalBtn && registroModal) {
    openRegistroModalBtn.addEventListener("click", () => {
        registroModal.classList.remove("hidden");
    });

    closeRegistroModalBtn.addEventListener("click", () => {
        registroModal.classList.add("hidden");
    });
}


// Función para cerrar el modal
function closeEditRegistroModal() {
    document.getElementById('editRegistroModal').classList.add('hidden');
}


// Función para abrir el modal de edición de un registro
function openEditRegistroModal(id) {
    fetch(`/admin/registro/buscar/${id}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener los datos del registro");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('idRegistro').value = data.id;
            document.getElementById('editUsuario').value = data.fk_usuario;
            document.getElementById('editDispositivo').value = data.fk_dispositivo;
            document.getElementById('editCultivo').value = data.fk_cultivo;
            document.getElementById('editFase').value = data.fk_cultivo_fase;

            let parcelaSelect = document.getElementById("editParcela");

            // Limpiar las opciones anteriores
            parcelaSelect.innerHTML = '<option value="">Cargando parcelas...</option>';

            // Cargar las parcelas asociadas al usuario
            fetch(`/admin/parcela/buscar_por_usuario/${data.fk_usuario}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("No se encontraron parcelas para este usuario");
                    }
                    return response.json();
                })
                .then(parcelas => {
                    parcelaSelect.innerHTML = '<option value="">Seleccione una Parcela</option>';
                    parcelas.forEach(parcela => {
                        let option = document.createElement("option");
                        option.value = parcela.id;
                        option.textContent = `${parcela.nombre} - ${parcela.comuna}`;
                        parcelaSelect.appendChild(option);
                    });

                    // Esperar a que todas las parcelas estén cargadas antes de seleccionar la actual
                    parcelaSelect.value = data.fk_parcela;
                })
                .catch(error => {
                    console.error("Error al obtener parcelas:", error);
                    parcelaSelect.innerHTML = '<option value="">No hay parcelas disponibles</option>';
                });

            // Finalmente, mostrar el modal después de cargar los datos
            document.getElementById('editRegistroForm').action = `/admin/registro/editar/${id}`;
            document.getElementById('editRegistroModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos del registro:', error));
}


// Función para cerrar el modal de edición
function closeEditRegistroModal() {
    document.getElementById("editRegistroModal").classList.add("hidden");
}


function cargarParcelasEdit() {
    let usuarioId = document.getElementById("editUsuario").value;
    let parcelaSelect = document.getElementById("editParcela");

    // Limpiar opciones anteriores
    parcelaSelect.innerHTML = '<option value="">Cargando parcelas...</option>';

    if (usuarioId) {
        fetch(`/admin/parcela/buscar_por_usuario/${usuarioId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("No se encontraron parcelas para este usuario");
                }
                return response.json();
            })
            .then(data => {
                parcelaSelect.innerHTML = '<option value="">Seleccione una Parcela</option>';
                data.forEach(parcela => {
                    let option = document.createElement("option");
                    option.value = parcela.id;
                    option.textContent = `${parcela.nombre} - ${parcela.comuna}`;
                    parcelaSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Error al obtener parcelas:", error);
                parcelaSelect.innerHTML = '<option value="">No hay parcelas disponibles</option>';
            });
    }
}


// Función para abrir el modal de eliminación de un registro
function openDeleteRegistroModal(id) {
    document.getElementById('deleteRegistroForm').action = `/admin/registro/eliminar/${id}`;
    document.getElementById('deleteRegistroModal').classList.remove('hidden');
}


// Función para cerrar el modal de eliminación
function closeDeleteRegistroModal() {
    document.getElementById('deleteRegistroModal').classList.add('hidden');
}


document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
        registroModal.classList.add("hidden");
        editRegistroModal.classList.add("hidden");
        deleteRegistroModal.classList.add("hidden")
    }
});


function cargarParcelas() {
    let usuarioId = document.getElementById("usuario").value;
    let parcelaSelect = document.getElementById("parcela");

    // Limpiar opciones anteriores
    parcelaSelect.innerHTML = '<option value="">Seleccione una Parcela</option>';

    if (usuarioId) {
        fetch(`/admin/parcela/buscar_por_usuario/${usuarioId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error("No se encontraron parcelas para este usuario");
                }
                return response.json();
            })
            .then(data => {
                data.forEach(parcela => {
                    let option = document.createElement("option");
                    option.value = parcela.id;
                    option.textContent = `${parcela.nombre}`;
                    parcelaSelect.appendChild(option);
                });
            })
            .catch(error => console.error("Error al obtener parcelas:", error));
    }
}
