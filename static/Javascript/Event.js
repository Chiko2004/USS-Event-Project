let currentDate = new Date();

// 1. Toggle Event Dropdown (Handles card opening/closing)
function toggleEvent(element) {
    element.classList.toggle('active');
}

// 2. Render Calendar Grid & Highlight Today
function renderCalendar() {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // Update the Month & Year header text
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const displayElement = document.getElementById('month-year-display');
    if (displayElement) {
        displayElement.innerText = `${monthNames[month]} ${year}`;
    }

    const daysContainer = document.getElementById('days-container');
    if (!daysContainer) return;
    daysContainer.innerHTML = '';

    // Calculate days and alignment (Monday start)
    const firstDayIndex = new Date(year, month, 1).getDay();
    const adjustedFirstDay = (firstDayIndex === 0) ? 6 : firstDayIndex - 1; 
    const totalDays = new Date(year, month + 1, 0).getDate();

    // Format today's date for comparison (YYYY-MM-DD)
    const today = new Date();
    const todayString = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;

    // Add empty slots for month padding alignment
    for (let i = 0; i < adjustedFirstDay; i++) {
        const emptyDiv = document.createElement('div');
        emptyDiv.className = 'calendar-day empty';
        daysContainer.appendChild(emptyDiv);
    }

    // Populate each day of the month
    for (let day = 1; day <= totalDays; day++) {
        const dayDiv = document.createElement('div');
        dayDiv.className = 'calendar-day';
        
        const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        dayDiv.setAttribute('data-date', dateString);
        dayDiv.innerText = day;

        // Apply "today" highlight class if it matches
        if (dateString === todayString) {
            dayDiv.classList.add('today');
        }

        daysContainer.appendChild(dayDiv);
    }

    // Re-attach hover sync listeners whenever the calendar renders/switches months
    setupEventHoverSync();
}

// 3. Month Navigation Buttons Handler (-1 for prev, 1 for next)
function changeMonth(direction) {
    currentDate.setMonth(currentDate.getMonth() + direction);
    renderCalendar();
}

// 4. Hover Synchronization (Made robust against format differences)
function setupEventHoverSync() {
    const eventCards = document.querySelectorAll('.Event');

    eventCards.forEach(card => {
        let rawDate = card.getAttribute('data-date');
        if (!rawDate) return;

        // Clean up the date string (grabs just the YYYY-MM-DD part and normalizes numbers)
        const cleanDateParts = rawDate.trim().split('T')[0].split('-');
        if (cleanDateParts.length === 3) {
            const year = cleanDateParts[0];
            const month = String(parseInt(cleanDateParts[1], 10)); // removes leading zero for matching
            const day = String(parseInt(cleanDateParts[2], 10));   // removes leading zero for matching
            
            // Rebuild matching format or search dynamically
            card.addEventListener('mouseenter', () => {
                // Find all days and check parts to ensure a match
                const allDays = document.querySelectorAll('.calendar-day');
                allDays.forEach(dayCell => {
                    const cellDate = dayCell.getAttribute('data-date');
                    if (cellDate) {
                        const cellParts = cellDate.split('-');
                        if (
                            parseInt(cellParts[0], 10) === parseInt(year, 10) &&
                            parseInt(cellParts[1], 10) === parseInt(month, 10) &&
                            parseInt(cellParts[2], 10) === parseInt(day, 10)
                        ) {
                            dayCell.classList.add('event-target');
                        }
                    }
                });
            });

            card.addEventListener('mouseleave', () => {
                const allDays = document.querySelectorAll('.calendar-day');
                allDays.forEach(dayCell => {
                    dayCell.classList.remove('event-target');
                });
            });
        }
    });
}

// Handle "I'm Interested" button clicks dynamically
document.addEventListener('click', function(e) {
    if (e.target && e.target.classList.contains('Interested')) {
        const button = e.target;
        const eventId = button.getAttribute('data-id');

        fetch(`/api/interest/${eventId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Toggle button text and state based on server response
                if (data.is_interested) {
                    button.textContent = "Interested ✓";
                    button.classList.add('active');
                } else {
                    button.textContent = "I'm interested";
                    button.classList.remove('active');
                }
            } else {
                alert(data.message || "You must be logged in to track event interest.");
            }
        })
        .catch(error => {
            console.error('Error recording interest:', error);
        });
    }
});

// Initialize calendar on page load
document.addEventListener('DOMContentLoaded', () => {
    renderCalendar();
});

