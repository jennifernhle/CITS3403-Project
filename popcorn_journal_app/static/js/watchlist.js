document.addEventListener("DOMContentLoaded", function () {
  const watchlistBtns = document.querySelectorAll(".watchlist-toggle-btn");

  watchlistBtns.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();

      const movieId = this.getAttribute("data-movie-id");
      const csrfToken = this.getAttribute("data-csrf-token");

      fetch(`/watchlist/toggle/${movieId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => {
          if (!response.ok) throw new Error("Network response was not ok");
          return response.json();
        })
        .then((data) => {
          if (data.success) {
            if (data.action === "added") {
              this.innerHTML = '<i class="bi bi-check-lg me-1"></i> Added';
              this.classList.add("btn-success");
              this.classList.remove("btn-outline-danger"); // If coming from watchlist page
            } else {
              this.innerHTML = '<i class="bi bi-plus-lg me-1"></i> Watchlist';
              this.classList.remove("btn-success");
            }

            if (data.action === "removed") {
              const card = document.getElementById(`movie-card-${movieId}`);
              if (card) {
                card.style.transition = "opacity 0.3s ease, transform 0.3s ease";
                card.style.opacity = "0";
                card.style.transform = "scale(0.95)";
                setTimeout(() => {
                  card.remove();
                  const container = document.getElementById("watchlist-results");
                  const remainingCards = container.querySelectorAll(".col:not(#empty-watchlist-msg)");
                  if (remainingCards.length === 0) {
                    const emptyMsg = document.getElementById("empty-watchlist-msg");
                    if (emptyMsg) {
                      emptyMsg.classList.remove("d-none");
                    }
                  }
                }, 300);
              }
            }
          }
        })
        .catch((error) => console.error("Watchlist Error:", error));
    });
  });
});
