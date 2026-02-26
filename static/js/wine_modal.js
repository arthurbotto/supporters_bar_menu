// Modal logic
const overlay = document.getElementById("overlay");
const modalBody = document.getElementById("modalBody");
const closeModalBtn = document.getElementById("closeModal");

function openModalWithContent(html) {
  modalBody.innerHTML = html;
  overlay.hidden = false;
  overlay.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");
}

function closeModal() {
  overlay.hidden = true;
  overlay.setAttribute("aria-hidden", "true");
  modalBody.innerHTML = "";
  document.body.classList.remove("modal-open");
}

document.addEventListener("click", async (e) => {
  const moreBtn = e.target.closest(".more-button-wines");
  if (!moreBtn) return;

  const id = moreBtn.dataset.moreId;
  const res = await fetch(`/wines/${id}/modal`);
  if (!res.ok) {
    openModalWithContent("<p>Could not load wine details.</p>");
    return;
  }

  const html = await res.text();
  openModalWithContent(html);
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