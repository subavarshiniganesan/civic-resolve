/**
 * CivicResolve - Admin Authority Portal Scripts
 */

document.addEventListener("DOMContentLoaded", () => {
    initStatusUpdateModal();
    initAdminFilterSync();
});

function initStatusUpdateModal() {
    const modal = document.getElementById("status-modal");
    if (!modal) return;

    const modalTicketId = document.getElementById("modal-ticket-id");
    const modalFormTicketId = document.getElementById("modal-form-ticket-id");
    const modalStatusSelect = document.getElementById("modal-status-select");
    const modalNotes = document.getElementById("modal-notes");
    const closeBtn = document.getElementById("modal-close-btn");
    const cancelBtn = document.getElementById("modal-cancel-btn");

    // Open modal when any "Update Status" button is clicked
    document.querySelectorAll(".btn-open-status-modal").forEach((btn) => {
        btn.addEventListener("click", () => {
            const ticketId = btn.getAttribute("data-ticket-id");
            const currentStatus = btn.getAttribute("data-current-status");
            const currentNotes = btn.getAttribute("data-admin-notes") || "";

            if (modalTicketId) modalTicketId.textContent = `#${ticketId}`;
            if (modalFormTicketId) modalFormTicketId.value = ticketId;
            if (modalStatusSelect) modalStatusSelect.value = currentStatus;
            if (modalNotes) modalNotes.value = currentNotes;

            modal.classList.remove("hidden");
            modal.setAttribute("aria-hidden", "false");
            if (modalStatusSelect) modalStatusSelect.focus();
        });
    });

    const closeModal = () => {
        modal.classList.add("hidden");
        modal.setAttribute("aria-hidden", "true");
    };

    if (closeBtn) closeBtn.addEventListener("click", closeModal);
    if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

    // Close on Escape key
    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !modal.classList.contains("hidden")) {
            closeModal();
        }
    });

    // Close on background backdrop click
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });
}

function initAdminFilterSync() {
    // Quick copy ticket ID to clipboard
    document.querySelectorAll(".btn-copy-ticket").forEach((btn) => {
        btn.addEventListener("click", () => {
            const ticket = btn.getAttribute("data-ticket");
            if (!ticket) return;

            navigator.clipboard.writeText(ticket).then(() => {
                const originalTitle = btn.getAttribute("title");
                btn.setAttribute("title", "Copied!");
                btn.classList.add("text-emerald-600");

                setTimeout(() => {
                    btn.setAttribute("title", originalTitle || "Copy Ticket ID");
                    btn.classList.remove("text-emerald-600");
                }, 1500);
            });
        });
    });
}
