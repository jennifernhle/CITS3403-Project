(function () {
  const TMDB_PREF_KEY = "tmdb-suggestions-enabled";
  const SEARCH_VIEW_KEY = "search-view-mode";
  const useTmdbApiEnabled = typeof USE_TMDB_API !== "undefined" ? USE_TMDB_API : false;

  document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("movie-search");
    const genreFilter = document.getElementById("genre-filter");
    const yearFilter = document.getElementById("year-filter");
    const tmdbContainer = document.getElementById("tmdb-results");
    const tmdbSection = document.getElementById("tmdb-section");
    const localSection = document.getElementById("local-results-section");
    const searchForm = document.querySelector('form[action$="/search"]');
    const viewButtons = document.querySelectorAll("[data-search-view]");
    const clearBtn = document.getElementById("clear-filters-btn");

    const activeSearchView = localStorage.getItem(SEARCH_VIEW_KEY) || "local";

    const tmdbEnabled = () => useTmdbApiEnabled && localStorage.getItem(TMDB_PREF_KEY) !== "off";
    const localViewActive = () => localStorage.getItem(SEARCH_VIEW_KEY) !== "tmdb";

    const debounce = (fn, wait = 500) => {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), wait);
      };
    };

    function autoSubmitLocalSearch() {
      if (!searchForm || !localViewActive()) return;
      searchForm.submit();
    }

    function triggerTmdbSearch() {
      if (!localViewActive()) {
        const query = searchInput?.value || "";
        const year = yearFilter?.value || "";
        const genre = genreFilter?.value || "";

        if (!query && !year && !genre) {
          if (tmdbContainer) {
            tmdbContainer.innerHTML = "";
            const placeholder = document.getElementById("tmdb-placeholder-template")?.content.cloneNode(true);
            if (placeholder) tmdbContainer.appendChild(placeholder);
          }
          return;
        }
        performTmdbSearch(query, year, genre);
      }
    }

    const debouncedLocalSearch = debounce(autoSubmitLocalSearch);
    const debouncedTmdbSearch = debounce(triggerTmdbSearch);

    searchInput?.addEventListener("input", () => {
      localViewActive() ? debouncedLocalSearch() : debouncedTmdbSearch();
    });

    [genreFilter, yearFilter].forEach((filter) => {
      filter?.addEventListener("change", () => {
        localViewActive() ? autoSubmitLocalSearch() : triggerTmdbSearch();
      });
    });

    clearBtn?.addEventListener("click", () => {
      if (searchInput) searchInput.value = "";
      if (genreFilter) genreFilter.value = "";
      if (yearFilter) yearFilter.value = "";
      localViewActive() ? (window.location.href = window.location.pathname) : triggerTmdbSearch();
    });

    viewButtons.forEach((button) => {
      button.addEventListener("click", () => setSearchView(button.dataset.searchView));
    });

    function setSearchView(view) {
      localStorage.setItem(SEARCH_VIEW_KEY, view);
      viewButtons.forEach((btn) => btn.classList.toggle("active", btn.dataset.searchView === view));

      // Checking if elements exist before toggling classes
      if (tmdbSection && localSection) {
        if (view === "tmdb") {
          tmdbSection.classList.remove("d-none-initial");
          localSection.classList.add("d-none-initial");
          triggerTmdbSearch();
        } else {
          tmdbSection.classList.add("d-none-initial");
          localSection.classList.remove("d-none-initial");
        }
      }
    }

    function performTmdbSearch(query, year, genre) {
      if (!tmdbEnabled() || !tmdbContainer) return;

      tmdbContainer.innerHTML = "";
      const loader = document.getElementById("tmdb-loading-template")?.content.cloneNode(true);
      if (loader) tmdbContainer.appendChild(loader);

      fetch(`/tmdb-search?query=${encodeURIComponent(query)}&year=${encodeURIComponent(year)}&genre=${encodeURIComponent(genre)}`)
        .then((res) => res.json())
        .then((data) => {
          tmdbContainer.innerHTML = "";
          if (!data.length) {
            tmdbContainer.appendChild(document.getElementById("tmdb-empty-template").content.cloneNode(true));
            return;
          }
          const template = document.getElementById("tmdb-card-template");
          data.forEach((movie) => {
            const clone = template.content.cloneNode(true);
            const img = clone.querySelector(".tmdb-poster");
            img.src = movie.poster_path ? `https://image.tmdb.org/t/p/w500${movie.poster_path}` : "/static/posters/default.jpg";
            clone.querySelector(".tmdb-title").textContent = movie.title;
            clone.querySelector(".tmdb-info").textContent = `${movie.genre || "General"} • ${movie.release_year}`;
            const btn = clone.querySelector(".tmdb-import-btn");
            btn.setAttribute("onclick", `window.importMovie(${movie.tmdb_id})`);
            tmdbContainer.appendChild(clone);
          });
        })
        .catch(() => {
          tmdbContainer.innerHTML = "";
          tmdbContainer.appendChild(document.getElementById("tmdb-error-template").content.cloneNode(true));
        });
    }

    // Initialise
    setSearchView(activeSearchView);
  });

  window.importMovie = function (tmdbId) {
    const button = document.querySelector(`button[onclick="window.importMovie(${tmdbId})"]`);
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");

    if (button) {
      button.disabled = true;
      const loader = document.getElementById("btn-loading-template")?.content.cloneNode(true);
      button.replaceChildren(loader);
    }

    fetch(`/import-tmdb-movie/${tmdbId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": token },
    })
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then(() => {
        if (button) {
          button.className = "btn btn-success btn-sm mt-auto disabled";
          button.innerHTML = '<i class="bi bi-check-lg me-1"></i> Imported';
          button.removeAttribute("onclick");
        }
      })
      .catch(() => {
        if (typeof window.showToast === "function") window.showToast("Import failed.", "danger");
        if (button) {
          button.disabled = false;
          button.textContent = "Import";
        }
      });
  };
})();
