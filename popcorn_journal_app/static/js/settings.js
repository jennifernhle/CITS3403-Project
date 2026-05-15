document.addEventListener("DOMContentLoaded", function () {
  const deleteBtn = document.getElementById("delete-account-btn");

  if (deleteBtn) {
    deleteBtn.addEventListener("click", function () {
      const userId = this.getAttribute("data-user-id");
      const csrfToken = this.getAttribute("data-csrf");

      if (confirm("Are you sure? This will delete your account and all your reviews/lists forever.")) {
        fetch(`/user/delete/${userId}`, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => {
            if (response.redirected) {
              window.location.href = response.url;
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while deleting the account.");
          });
      }
    });
  }

  const resetProfilePicBtn = document.getElementById("reset-profile-pic-btn");

  if (resetProfilePicBtn) {
    resetProfilePicBtn.addEventListener("click", function () {
      const csrfToken = this.getAttribute("data-csrf");

      if (!confirm("Reset your profile picture to the default image?")) {
        return;
      }

      fetch("/reset-profile-pic", {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success && data.redirect) {
            window.location.href = data.redirect;
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("An error occurred while resetting your profile picture.");
        });
    });
  }

  // Favourite movies management
  let searchTimeout;
  const favouriteSearchInput = document.getElementById("favouriteSearch");
  const favouriteSearchResults = document.getElementById("favouriteSearchResults");
  const favouriteSearchEmpty = document.getElementById("favouriteSearchEmpty");

  if (favouriteSearchInput) {
    favouriteSearchInput.addEventListener("input", function () {
      clearTimeout(searchTimeout);
      const query = this.value.trim();

      if (!query) {
        favouriteSearchResults.innerHTML = "";
        favouriteSearchEmpty.style.display = "block";
        return;
      }

      searchTimeout = setTimeout(() => {
        fetch(`/search?query=${encodeURIComponent(query)}`)
          .then((response) => response.text())
          .then((html) => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const movieCards = doc.querySelectorAll(".row.row-cols-1.row-cols-md-3 .col");

            if (movieCards.length === 0) {
              favouriteSearchResults.innerHTML = "";
              favouriteSearchEmpty.innerHTML = "<p>No movies found.</p>";
              favouriteSearchEmpty.style.display = "block";
              return;
            }

            favouriteSearchEmpty.style.display = "none";
            favouriteSearchResults.innerHTML = "";

            movieCards.forEach((card) => {
              const link = card.querySelector("a[href*='/movie/']");
              const movieId = link?.href?.match(/\/movie\/(\d+)/)?.[1];
              
              if (!movieId) return;

              const title = card.querySelector(".card-title")?.textContent?.trim() || "Unknown";
              const genreYear = card.querySelector(".card-text")?.textContent?.trim() || "";
              const poster = card.querySelector("img")?.src || "";

              const resultCard = document.createElement("div");
              resultCard.className = "col";
              resultCard.innerHTML = `
                <div class="card h-100 shadow-sm">
                  <img src="${poster}" class="card-img-top" alt="${title}" style="max-height: 250px; object-fit: cover;" />
                  <div class="card-body d-flex flex-column">
                    <h6 class="card-title fw-bold small">${title}</h6>
                    <p class="card-text text-secondary small mb-3">${genreYear}</p>
                    <button 
                      type="button" 
                      class="btn btn-main btn-sm add-favourite-btn mt-auto"
                      data-movie-id="${movieId}"
                      data-bs-dismiss="modal"
                    >
                      Add to Favourites
                    </button>
                  </div>
                </div>
              `;
              favouriteSearchResults.appendChild(resultCard);
            });
          })
          .catch((error) => {
            console.error("Search error:", error);
            favouriteSearchEmpty.innerHTML = "<p>Error searching for movies.</p>";
            favouriteSearchEmpty.style.display = "block";
          });
      }, 300);
    });
  }

  // Handle add favourite button clicks
  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("add-favourite-btn")) {
      const movieId = e.target.getAttribute("data-movie-id");
      const csrfToken = document.querySelector("[name='csrf_token']")?.value;

      fetch(`/favourite-movie/${movieId}/add`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            alert(data.message);
            location.reload();
          } else {
            alert(data.error || "Failed to add favourite.");
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("An error occurred while adding the favourite.");
        });
    }

    if (e.target.classList.contains("remove-favourite-btn")) {
      const movieId = e.target.getAttribute("data-movie-id");
      const csrfToken = e.target.getAttribute("data-csrf");

      if (confirm("Remove this movie from your favourites?")) {
        fetch(`/favourite-movie/${movieId}/remove`, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
          },
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              location.reload();
            } else {
              alert(data.error || "Failed to remove favourite.");
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            alert("An error occurred while removing the favourite.");
          });
      }
    }
  });
});
