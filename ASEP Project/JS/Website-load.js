function detectDevice() {
    // Check if the redirection has already occurred
    if (!localStorage.getItem('redirected')) {
        if (window.innerWidth <= 768) {
            window.location.href = "phone-home.html";
        } else {
            window.location.href = "home.html";
        }
        // Set the flag in local storage to indicate that redirection has occurred
        localStorage.setItem('redirected', 'true');
    }
}

// Call the function on page load
detectDevice();

