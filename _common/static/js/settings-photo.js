document.addEventListener("DOMContentLoaded", function () {
    var settingsShell = document.querySelector(".crm-settings-shell");
    var modalEl = document.getElementById("profilePhotoModal");
    var previewImage = document.getElementById("profilePhotoPreview");
    var previewPlaceholder = document.getElementById("profilePhotoPreviewPlaceholder");
    var fileName = document.getElementById("profilePhotoFilename");
    var fileInput = modalEl ? modalEl.querySelector('input[type="file"][name="photo"]') : null;
    var originalPreviewUrl = previewImage ? (previewImage.getAttribute("src") || "") : "";
    var temporaryObjectUrl = null;
    var shouldOpenModal = settingsShell && settingsShell.dataset.openPhotoModal === "1";

    function setPreview(url) {
        if (!previewImage || !previewPlaceholder) {
            return;
        }

        if (url) {
            previewImage.src = url;
            previewImage.classList.remove("d-none");
            previewPlaceholder.classList.add("d-none");
            return;
        }

        previewImage.classList.add("d-none");
        previewPlaceholder.classList.remove("d-none");
    }

    function setFileName(message) {
        if (fileName) {
            fileName.textContent = message;
        }
    }

    if (fileInput) {
        fileInput.addEventListener("change", function (event) {
            var selectedFile = event.target.files && event.target.files[0] ? event.target.files[0] : null;

            if (temporaryObjectUrl) {
                URL.revokeObjectURL(temporaryObjectUrl);
                temporaryObjectUrl = null;
            }

            if (selectedFile) {
                temporaryObjectUrl = URL.createObjectURL(selectedFile);
                setPreview(temporaryObjectUrl);
                setFileName("Vybrany soubor: " + selectedFile.name);
                return;
            }

            setPreview(originalPreviewUrl);
            setFileName("Zatim neni vybrany novy soubor.");
        });
    }

    if (modalEl) {
        modalEl.addEventListener("hidden.bs.modal", function () {
            if (fileInput) {
                fileInput.value = "";
            }

            if (temporaryObjectUrl) {
                URL.revokeObjectURL(temporaryObjectUrl);
                temporaryObjectUrl = null;
            }

            setPreview(originalPreviewUrl);
            setFileName("Zatim neni vybrany novy soubor.");
        });
    }

    var savedPill = document.querySelector(".crm-avatar-saved-pill.show");
    if (savedPill) {
        window.setTimeout(function () {
            savedPill.classList.remove("show");
        }, 2600);
    }

    if (shouldOpenModal && modalEl && window.bootstrap) {
        var modal = new bootstrap.Modal(modalEl);
        modal.show();
    }
});
