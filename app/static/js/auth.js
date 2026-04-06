// Toggling password visibility
const togglePassword = document.querySelectorAll(".toggle-password");
togglePassword.forEach((button) => {
  button.addEventListener("click", function () {
    const passwordInput = this.parentElement.querySelector("input");
    const icon = this.querySelector("i");

    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      icon.classList.replace("bi-eye-slash", "bi-eye");
    } else {
      passwordInput.type = "password";
      icon.classList.replace("bi-eye", "bi-eye-slash");
    }
  });
});
