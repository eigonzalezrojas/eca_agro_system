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
        .then(response => response.json())
        .then(data => {
            document.getElementById('idRegistro').value = data.id;
            document.getElementById('editUsuario').value = data.fk_usuario;
            document.getElementById('editParcela').value = data.fk_parcela;
            document.getElementById('editDispositivo').value = data.fk_dispositivo;
            document.getElementById('editFuente').value = data.fuente;

            // Cargar parcelas del usuario seleccionado
            cargarParcelasEdit(data.fk_usuario, data.fk_parcela);

            // Seleccionar automáticamente el cultivo correcto
            let cultivoSelect = document.getElementById('editCultivo');
            for (let option of cultivoSelect.options) {
                if (option.getAttribute("data-nombre") === data.cultivo_nombre) {
                    option.selected = true;
                    break;
                }
            }

            // Cargar fases asociadas al cultivo y preseleccionar la fase del registro
            cargarFasesEdit(data.cultivo_nombre, data.fk_fase);

            document.getElementById('editRegistroForm').action = `/admin/registro/editar/${id}`;
            document.getElementById('editRegistroModal').classList.remove('hidden');
        })
        .catch(error => console.error('Error al obtener los datos del registro:', error));
}


// Función para cerrar el modal de edición
function closeEditRegistroModal() {
    document.getElementById("editRegistroModal").classList.add("hidden");
}


// Función para abrir el modal de eliminación de un registro
function openDeleteRegistroModal(id) {
    document.getElementById('registroIdToDelete').value = id;
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


function cargarFases() {
    let cultivoSelect = document.getElementById("cultivo");
    let faseSelect = document.getElementById("fase");

    let cultivoNombre = cultivoSelect.value;  // Obtener el nombre del cultivo seleccionado

    // Limpiar el select de fases
    faseSelect.innerHTML = '<option value="">Cargando fases...</option>';

    if (cultivoNombre) {
        fetch(`/admin/registro/fase/por_cultivo?cultivo_nombre=${encodeURIComponent(cultivoNombre)}`)
            .then(response => response.json())
            .then(fases => {
                faseSelect.innerHTML = '<option value="">Seleccione una Fase</option>';

                if (fases.length === 0) {
                    faseSelect.innerHTML = '<option value="">No hay fases disponibles</option>';
                }

                fases.forEach(fase => {
                    let option = document.createElement("option");
                    option.value = fase.id;
                    option.textContent = fase.nombre;
                    faseSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error("Error al obtener fases:", error);
                faseSelect.innerHTML = '<option value="">Error al cargar fases</option>';
            });
    } else {
        faseSelect.innerHTML = '<option value="">Seleccione un Cultivo primero</option>';
    }
}


function cargarFasesEdit(cultivoNombre, faseSeleccionada = null) {
    let faseSelect = document.getElementById("editFase");
    faseSelect.innerHTML = '<option value="">Cargando fases...</option>';

    fetch(`/admin/registro/fase/por_cultivo?cultivo_nombre=${encodeURIComponent(cultivoNombre)}`)
        .then(response => response.json())
        .then(fases => {
            console.log(fases)
            faseSelect.innerHTML = '<option value="">Seleccione una Fase</option>';

            if (fases.length === 0) {
                faseSelect.innerHTML = '<option value="">No hay fases disponibles</option>';
            }

            fases.forEach(fase => {
                let option = document.createElement("option");
                option.value = fase.id;
                option.textContent = fase.nombre;

                if (fase.id == faseSeleccionada) {
                    option.selected = true;
                }
                faseSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Error al obtener fases:", error);
            faseSelect.innerHTML = '<option value="">Error al cargar fases</option>';
        });
}


function cargarParcelasEdit(usuarioId, parcelaSeleccionada = null) {
    let parcelaSelect = document.getElementById("editParcela");
    parcelaSelect.innerHTML = '<option value="">Cargando parcelas...</option>';

    fetch(`/admin/parcela/buscar_por_usuario/${usuarioId}`)
        .then(response => response.json())
        .then(parcelas => {
            parcelaSelect.innerHTML = '<option value="">Seleccione una Parcela</option>';
            parcelas.forEach(parcela => {
                let option = document.createElement("option");
                option.value = parcela.id;
                option.textContent = `${parcela.nombre} - ${parcela.comuna}`;

                if (parcela.id == parcelaSeleccionada) {
                    option.selected = true;
                }
                parcelaSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Error al obtener parcelas:", error);
            parcelaSelect.innerHTML = '<option value="">No hay parcelas disponibles</option>';
        });
}


