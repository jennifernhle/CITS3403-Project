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
});
