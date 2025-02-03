const openModal = document.getElementById("openCultivoModal");
const closeModal = document.getElementById("closeCultivoModal");

if (openModal && closeModal) {
    openModal.addEventListener("click", () => {
        cultivoModal.classList.remove("hidden");
    });

    closeModal.addEventListener("click", () => {
        cultivoModal.classList.add("hidden");
    });
}
