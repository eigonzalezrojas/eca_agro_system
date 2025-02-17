window.openEditCultivoModal = function(cultivoId, cultivoNombre, cultivoVariedad) {
    document.getElementById("cultivo-id").value = cultivoId;

    fetch(`/client/cultivoCliente/fases?nombre=${encodeURIComponent(cultivoNombre)}`)
    .then(response => response.json())
    .then(data => {
        const faseSelect = document.getElementById("fase-select");
        faseSelect.innerHTML = "";
        data.fases.forEach(fase => {
            let option = document.createElement("option");
            option.value = fase;
            option.textContent = fase;
            faseSelect.appendChild(option);
        });
    });

    document.getElementById("editCultivoModal").classList.remove("hidden");
};

window.closeEditCultivoModal = function() {
    const modal = document.getElementById("editCultivoModal");
    modal.classList.add("fade-out");
    setTimeout(() => {
        modal.classList.add("hidden");
        modal.classList.remove("fade-out");
    }, 300);
};

window.guardarCambioFase = function() {
    const cultivoId = document.getElementById("cultivo-id").value;
    const nuevaFase = document.getElementById("fase-select").value;
    const guardarBtn = document.getElementById("guardar-btn");

    if (!nuevaFase) {
        mostrarFlashMessage("⚠️ Debes seleccionar una fase.", "error");
        return;
    }

    // Deshabilitar botón y mostrar loader
    guardarBtn.disabled = true;
    guardarBtn.innerHTML = "⏳ Guardando...";

    fetch("/client/cultivoCliente/cambiar_fase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cultivo_id: cultivoId, nueva_fase: nuevaFase })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            mostrarFlashMessage(data.error, "error");
        } else {
            document.getElementById(`fase-${cultivoId}`).textContent = nuevaFase;
            mostrarFlashMessage("✅ Fase actualizada correctamente.", "success");
            closeEditCultivoModal();
        }
    })
    .catch(error => {
        mostrarFlashMessage("❌ Ocurrió un error. Inténtalo de nuevo.", "error");
    })
    .finally(() => {
        guardarBtn.disabled = false;
        guardarBtn.innerHTML = "Guardar";
    });
};

// Mostrar mensajes fuera del modal para mejor visibilidad
function mostrarFlashMessage(mensaje, tipo) {
    const flashContainer = document.getElementById("flash-messages");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("p-3", "rounded", "mb-2");

    if (tipo === "success") {
        messageDiv.classList.add("bg-green-500", "text-white");
    } else {
        messageDiv.classList.add("bg-red-500", "text-white");
    }

    messageDiv.textContent = mensaje;
    flashContainer.appendChild(messageDiv);

    setTimeout(() => {
        messageDiv.remove();
    }, 4000);
}
