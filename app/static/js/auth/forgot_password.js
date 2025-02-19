document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("forgotPasswordForm");

    form.addEventListener("submit", function (event) {
        const emailInput = document.getElementById("email");

        if (!emailInput.value.trim()) {
            event.preventDefault();
            alert("⚠️ Por favor, ingresa tu correo electrónico.");
        }
    });
});
