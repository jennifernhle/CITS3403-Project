document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("userSearchInput");
  const resultsList = document.getElementById("searchResultsList");

  if (!searchInput || !resultsList) return;

  let debounceTimer;

  searchInput.addEventListener("input", (e) => {
    const query = e.target.value.trim();
    clearTimeout(debounceTimer);

    if (query.length < 1) {
      resultsList.style.display = "none";
      resultsList.innerHTML = "";
      return;
    }

    // Only starting the search after the user stops typing for 300ms
    debounceTimer = setTimeout(async () => {
      try {
        const response = await fetch(`/api/search-users?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error("Network response was not ok");
        const users = await response.json();
        renderResults(users);
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    }, 300);
  });

  function renderResults(users) {
    resultsList.innerHTML = "";
    if (users.length > 0) {
      users.forEach((user) => {
        const row = document.createElement("a");
        row.href = `/user/${user.id}`;
        row.className = "list-group-item list-group-item-action d-flex align-items-center gap-2 py-2";
        const img = document.createElement("img");
        img.src = user.profile_pic;
        img.className = "rounded-circle border";
        img.width = 30;
        img.height = 30;
        img.style.objectFit = "cover";
        const span = document.createElement("span");
        span.className = "small fw-bold text-dark";
        span.textContent = user.username;
        row.appendChild(img);
        row.appendChild(span);
        resultsList.appendChild(row);
      });
      resultsList.style.display = "block";
    } else {
      const emptyMsg = document.createElement("div");
      emptyMsg.className = "list-group-item small text-muted";
      emptyMsg.textContent = "No users found";
      resultsList.appendChild(emptyMsg);
      resultsList.style.display = "block";
    }
  }

  document.addEventListener("click", (e) => {
    if (!searchInput.contains(e.target) && !resultsList.contains(e.target)) {
      resultsList.style.display = "none";
    }
  });
});
