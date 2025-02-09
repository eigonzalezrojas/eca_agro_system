document.addEventListener("DOMContentLoaded", function () {
    // Menú hamburguesa
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
    });
    const userMenuButton = document.getElementById("userMenuButton");
    const userMenu = document.getElementById("userMenu");

    // Alternar visibilidad del menú al hacer clic en el botón
    userMenuButton.addEventListener("click", function (event) {
        event.stopPropagation();
        userMenu.classList.toggle("hidden");
    });

    // Cerrar el menú con clic fuera
    document.addEventListener("click", function (event) {
        if (!userMenu.contains(event.target) && !userMenuButton.contains(event.target)) {
            userMenu.classList.add("hidden");
        }
    });
});