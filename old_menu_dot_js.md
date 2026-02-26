This was the first menu.js , before adding 'Search' and delegation to deal with buttons not working after search.

// Dropdown toggles
const toggles = document.querySelectorAll(".cocktail-toggle");

toggles.forEach((btn) => {
  btn.addEventListener("click", () => {
    const panelId = btn.getAttribute("aria-controls");
    const panel = document.getElementById(panelId);
    const isOpen = btn.getAttribute("aria-expanded") === "true";

    // Close all panels first
    toggles.forEach((otherBtn) => {
      const otherPanel = document.getElementById(otherBtn.getAttribute("aria-controls"));
      otherBtn.setAttribute("aria-expanded", "false");
      otherPanel.hidden = true;
    });

    // If the clicked one was closed, open it (if it was open, keep it closed)
    if (!isOpen) {
      btn.setAttribute("aria-expanded", "true");
      panel.hidden = false;
    }
  });
});

// Modal logic
const overlay = document.getElementById("overlay");
const modalBody = document.getElementById("modalBody");
const closeModalBtn = document.getElementById("closeModal");

function openModalWithContent(html) {
  modalBody.innerHTML = html;
  overlay.hidden = false;
  overlay.setAttribute("aria-hidden", "false");
}

function closeModal() {
  overlay.hidden = true;
  overlay.setAttribute("aria-hidden", "true");
  modalBody.innerHTML = "";
}

document.querySelectorAll(".more-button").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const id = btn.dataset.moreId;
    const res = await fetch(`/cocktails/${id}/modal`);
    if (!res.ok) {
      openModalWithContent("<p>Could not load cocktail details.</p>");
      return;
    }

    const html = await res.text();
    openModalWithContent(html);
  });
});

closeModalBtn.addEventListener("click", closeModal);

// Close when clicking outside the modal box
overlay.addEventListener("click", (e) => {
  if (e.target === overlay) closeModal();
});

// Close on Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !overlay.hidden) closeModal();
});

