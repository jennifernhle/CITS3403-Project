document.addEventListener("DOMContentLoaded", function () {
  const listSelect = document.getElementById("listSelect");

  if (listSelect) {
    listSelect.addEventListener("change", function () {
      if (this.value === "NEW") {
        this.value = "";

        const modalElem = document.getElementById("quickCreateListModal");
        if (modalElem) {
          const modal = new bootstrap.Modal(modalElem);
          modal.show();
        }
      }
    });
  }
});

document.addEventListener("click", function (e) {
  if (e.target.classList.contains("toggle-btn")) {
    const targetId = e.target.getAttribute("data-target");
    const content = document.getElementById(targetId);

    if (content) {
      if (content.classList.contains("collapsed")) {
        content.classList.remove("collapsed");
        content.classList.add("expanded");
        e.target.textContent = "Show Less";
      } else {
        content.classList.remove("expanded");
        content.classList.add("collapsed");
        e.target.textContent = "Read More";
      }
    }
  }
});
