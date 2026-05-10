document.addEventListener("DOMContentLoaded", function () {
  const followBtn = document.getElementById("follow-button");
  const followerCountSpan = document.getElementById("follower-count-value");

  if (followBtn) {
    followBtn.addEventListener("click", function (e) {
      e.preventDefault();

      const userId = this.getAttribute("data-user-id");
      const currentAction = this.getAttribute("data-action");
      const csrfToken = this.getAttribute("data-csrf-token");

      this.disabled = true;

      fetch(`/follow/${userId}/${currentAction}`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            if (followerCountSpan) {
              followerCountSpan.textContent = data.follower_count;
            }
            this.setAttribute("data-action", data.action);

            if (data.action === "unfollow") {
              // Currenly following, so now showing 'Unfollow'
              this.textContent = "Unfollow";
              this.className = "btn btn-primary";
            } else {
              // Currently not following, so now showing 'Follow'
              this.textContent = "Follow";
              this.className = "btn btn-outline-primary";
            }
          }
        })
        .catch((error) => console.error("Error:", error))
        .finally(() => {
          this.disabled = false;
          this.blur();
        });
    });
  }
});
