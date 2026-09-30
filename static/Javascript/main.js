function toggleNotifications() {
    var dropdown = document.getElementById("notificationDropdown");
    if (dropdown.style.display === "none" || dropdown.style.display === "") {
        dropdown.style.display = "block";
    } else {
        dropdown.style.display = "none";
    }
}

// Optional: Close the pop-out if the user clicks anywhere else on the page
window.onclick = function(event) {
    if (!event.target.matches('.notification-container') && !event.target.closest('.notification-container')) {
        var dropdown = document.getElementById("notificationDropdown");
        if (dropdown && dropdown.style.display === "block") {
            dropdown.style.display = "none";
        }
    }
}