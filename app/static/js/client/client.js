document.addEventListener("DOMContentLoaded", function () {
    // Menú hamburguesa
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
    });

    const userMenuButton = document.getElementById("userMenuButton");
    const userMenu = document.getElementById("userMenu");

    userMenuButton.addEventListener("click", function (event) {
        event.stopPropagation();
        userMenu.classList.toggle("hidden");
    });

    document.addEventListener("click", function (event) {
        if (!userMenu.contains(event.target) && !userMenuButton.contains(event.target)) {
            userMenu.classList.add("hidden");
        }
    });
});


