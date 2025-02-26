function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Retrieve stored user data
    const storedUsername = localStorage.getItem('username');
    const storedPassword = localStorage.getItem('password');

    // Simple validation
    if (username === '' || password === '') {
        alert('Please fill in both fields');
        return;
    }

    // Check if the entered credentials match the stored credentials
    if (username === storedUsername && password === storedPassword) {
        alert('Login successful');
        // Redirect to another page
        window.location.href = 'Index.html';
    } else {
        alert('Invalid username or password');
    }
}