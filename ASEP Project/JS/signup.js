function signup() {
    const newUsername = document.getElementById('new-username').value;
    const newPassword = document.getElementById('new-password').value;

    // Simple validation
    if (newUsername === '' || newPassword === '') {
        alert('Please fill in both fields');
        return;
    }

    // Store user data in localStorage
    localStorage.setItem('username', newUsername);
    localStorage.setItem('password', newPassword);

    alert('Sign up successful');
    // Redirect to login page
    window.location.href = 'Login.html';
}