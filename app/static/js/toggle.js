// toggle.js

document.addEventListener('DOMContentLoaded', function () {
    const loginToggle = document.getElementById('loginToggle');
    const registerToggle = document.getElementById('registerToggle');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');

    // Initially display the login form only
    loginForm.style.display = 'block';
    registerForm.style.display = 'none';

    // Toggle to show the login form
    loginToggle.addEventListener('click', () => {
        loginToggle.classList.add('active');
        registerToggle.classList.remove('active');
        loginForm.style.display = 'block';
        registerForm.style.display = 'none';
    });

    // Toggle to show the register form
    registerToggle.addEventListener('click', () => {
        registerToggle.classList.add('active');
        loginToggle.classList.remove('active');
        registerForm.style.display = 'block';
        loginForm.style.display = 'none';
    });
});
