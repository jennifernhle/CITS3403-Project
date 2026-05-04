$(document).ready(function () {
  $(".heart-btn").click(function () {
    const button = $(this);
    const reviewId = button.data("review-id");

    $.ajax({
      url: "/like-review/" + reviewId,
      method: "POST",
      headers: {
        "X-CSRFToken": csrf_token,
      },
      success: function (response) {
        if (response.success) {
          button.html('<i class="bi bi-heart' + (response.action === "liked" ? "-fill" : "") + '"></i> ' + response.count);

          if (response.action === "liked") {
            button.removeClass("btn-outline-danger").addClass("btn-danger text-white");
          } else {
            button.removeClass("btn-danger text-white").addClass("btn-outline-danger");
          }
        }
      },
      error: function () {
        alert("Login required to like reviews!");
      },
    });
  });
});
