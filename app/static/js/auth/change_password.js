document.addEventListener("DOMContentLoaded", function () {
    const changePasswordForm = document.getElementById("changePasswordForm");

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
});
