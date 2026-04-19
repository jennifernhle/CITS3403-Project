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

// Password requirements validation
const passwordInput = document.getElementById("login-password");
const messageBox = document.getElementById("password-requirements");

if (passwordInput && messageBox) {
  const lowerCase = document.getElementById("lowerCase");
  const upperCase = document.getElementById("upperCase");
  const number = document.getElementById("number");
  const length = document.getElementById("length");
  const specialCheck = document.getElementById("specialCheck");

  passwordInput.onfocus = function () {
    messageBox.style.display = "block";
  };

  passwordInput.onblur = function () {
    messageBox.style.display = "none";
  };

  passwordInput.onkeyup = function () {
    const lowerCaseLetters = /[a-z]/g;
    if (passwordInput.value.match(lowerCaseLetters)) {
      lowerCase.classList.remove("invalid");
      lowerCase.classList.add("valid");
    } else {
      lowerCase.classList.remove("valid");
      lowerCase.classList.add("invalid");
    }

    const upperCaseLetters = /[A-Z]/g;
    if (passwordInput.value.match(upperCaseLetters)) {
      upperCase.classList.remove("invalid");
      upperCase.classList.add("valid");
    } else {
      upperCase.classList.remove("valid");
      upperCase.classList.add("invalid");
    }

    const numbers = /[0-9]/g;
    if (passwordInput.value.match(numbers)) {
      number.classList.remove("invalid");
      number.classList.add("valid");
    } else {
      number.classList.remove("valid");
      number.classList.add("invalid");
    }

    if (passwordInput.value.length >= 8 && passwordInput.value.length <= 20) {
      length.classList.remove("invalid");
      length.classList.add("valid");
    } else {
      length.classList.remove("valid");
      length.classList.add("invalid");
    }

    const forbiddenChars = /[^a-zA-Z0-9]/g;
    if (!forbiddenChars.test(passwordInput.value)) {
      specialCheck.classList.remove("invalid");
      specialCheck.classList.add("valid");
    } else {
      specialCheck.classList.remove("valid");
      specialCheck.classList.add("invalid");
    }
  };
}

// Submission validation
function validateForm() {
  const username = document.getElementById("username");
  const password = document.getElementById("login-password");
  const confirmPassword = document.getElementById("confirm-password");
  const submitBtn = document.getElementById("submitBtn");
  const errorElement = document.getElementById("passwordError");

  let isValid = true;
  let usernameVal = "";
  let passwordVal = "";
  let confirmPasswordVal = "";

  if (username) {
    usernameVal = username.value;
  } else {
    usernameVal = "guest";
  }

  if (password) {
    passwordVal = password.value;
  }

  if (confirmPassword) {
    confirmPasswordVal = confirmPassword.value;
  }

  if (!username || !password) {
    isValid = false;
  }

  if (confirmPassword) {
    if (confirmPasswordVal.length > 0) {
      if (passwordVal != confirmPasswordVal) {
        errorElement.textContent = "Passwords do not match";
        errorElement.classList.remove("success");
        errorElement.classList.add("error");
        isValid = false;
      } else {
        errorElement.textContent = "Passwords match";
        errorElement.classList.remove("error");
        errorElement.classList.add("success");
      }
    } else {
      errorElement.textContent = "";
      isValid = false;
    }
  }
  if (submitBtn) {
    if (isValid) {
      submitBtn.classList.add("enabled");
      submitBtn.disabled = false;
    } else {
      submitBtn.classList.remove("enabled");
      submitBtn.disabled = true;
    }
  }
}

const authForm =
  document.getElementById("registration-form") ||
  document.getElementById("login-form");
if (authForm) {
  authForm.addEventListener("input", validateForm);
}
