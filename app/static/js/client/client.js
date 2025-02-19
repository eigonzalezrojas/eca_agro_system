document.addEventListener("DOMContentLoaded", function () {

    // ✅ Menú lateral
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("hidden");
        });
    }

    // ✅ Menú de usuario
    const userMenuButton = document.getElementById("userMenuButton");
    const userMenu = document.getElementById("userMenu");

    if (userMenuButton && userMenu) {
        userMenuButton.addEventListener("click", function (event) {
            event.stopPropagation();
            userMenu.classList.toggle("hidden");
        });

        // Cerrar el menú si se hace clic fuera
        document.addEventListener("click", function (event) {
            if (!userMenu.contains(event.target) && event.target !== userMenuButton) {
                userMenu.classList.add("hidden");
            }
        });
    }

    // ✅ Modal Cambiar Contraseña
    const changePasswordModal = document.getElementById("changePasswordModal");
    const openChangePasswordModalButton = document.getElementById("openChangePasswordModal");
    const closeChangePasswordModalButton = document.getElementById("closeChangePasswordModal");
    const changePasswordForm = document.getElementById("changePasswordForm");

    // Solo abre el modal cuando se hace clic en el botón
    if (openChangePasswordModalButton && changePasswordModal) {
        openChangePasswordModalButton.addEventListener("click", function (event) {
            event.preventDefault(); // Evita que el enlace recargue la página
            changePasswordModal.classList.remove("hidden");
            if (userMenu) userMenu.classList.add("hidden"); // Oculta el menú de usuario
        });
    }

    // Cierra el modal cuando se hace clic en el botón de cerrar
    if (closeChangePasswordModalButton && changePasswordModal) {
        closeChangePasswordModalButton.addEventListener("click", function () {
            changePasswordModal.classList.add("hidden");
        });

        // Cierra el modal si se hace clic fuera del contenido
        changePasswordModal.addEventListener("click", function (event) {
            if (event.target === changePasswordModal) {
                changePasswordModal.classList.add("hidden");
            }
        });
    }

    // Evita que el modal se abra automáticamente al cargar la página
    if (changePasswordModal && !openChangePasswordModalButton) {
        changePasswordModal.classList.add("hidden");
    }

    // ✅ Envío del formulario para cambiar la contraseña
    if (changePasswordForm) {
        changePasswordForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const oldPassword = document.getElementById("old_password").value.trim();
            const newPassword = document.getElementById("new_password").value.trim();
            const confirmPassword = document.getElementById("confirm_password").value.trim();

            if (newPassword !== confirmPassword) {
                alert("❗ Las contraseñas no coinciden");
                return;
            }

            fetch("/auth/change_password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ old_password: oldPassword, new_password: newPassword })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("✅ Contraseña cambiada con éxito. Redirigiendo al login...");
                    window.location.href = "/auth/logout";
                } else {
                    alert(data.error || "⚠️ Ocurrió un error");
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        });
    }


    // Notificaciones
    const notificacionesButton = document.getElementById("notificacionesButton");
    const notificacionesMenu = document.getElementById("notificacionesMenu");
    const notificacionesLista = document.getElementById("notificacionesLista");
    const notificacionesBadge = document.getElementById("notificacionesBadge");

    function cargarNotificaciones() {
        fetch("/client/alertasCliente/notificaciones")
            .then(response => response.json())
            .then(data => {

                notificacionesLista.innerHTML = "";

                if (data.length > 0) {
                    notificacionesBadge.classList.remove("hidden");
                    notificacionesBadge.textContent = data.length;

                    data.forEach(notificacion => {
                        let li = document.createElement("li");
                        li.className = "p-3 hover:bg-gray-100 cursor-pointer";
                        li.innerHTML = `
                            <div class="text-sm font-medium text-gray-800">${notificacion.mensaje}</div>
                            <div class="text-xs text-gray-500">${notificacion.fecha}</div>
                        `;

                        li.addEventListener("click", () => {
                            // Marcar como leída
                            fetch(`/client/alertasCliente/marcar_leida/${notificacion.id}`, { method: "POST" })
                                .then(res => res.json())
                                .then(response => {

                                    // Eliminar la notificación del listado
                                    li.remove();

                                    // Actualizar el contador
                                    let totalNotificaciones = document.querySelectorAll("#notificacionesLista li").length;
                                    if (totalNotificaciones === 0) {
                                        notificacionesBadge.classList.add("hidden");
                                    } else {
                                        notificacionesBadge.textContent = totalNotificaciones;
                                    }

                                    // Redirigir al panel de alertas
                                    window.location.href = "/client/alertasCliente/listar";
                                })
                                .catch(error => console.error("Error al marcar como leída:", error));
                        });

                        notificacionesLista.appendChild(li);
                    });
                } else {
                    notificacionesBadge.classList.add("hidden");
                    notificacionesLista.innerHTML = `<li class="p-3 text-center text-gray-500">No hay nuevas notificaciones</li>`;
                }
            })
            .catch(error => console.error("Error al cargar notificaciones:", error));
    }

    // Cargar notificaciones al iniciar
    cargarNotificaciones();
    setInterval(cargarNotificaciones, 30000);

    if (notificacionesButton) {
        notificacionesButton.addEventListener("click", function () {
            notificacionesMenu.classList.toggle("hidden");
        });

        document.addEventListener("click", function (event) {
            if (!notificacionesButton.contains(event.target) && !notificacionesMenu.contains(event.target)) {
                notificacionesMenu.classList.add("hidden");
            }
        });
    }

});
