/**
 * GlaCK0N GarageHub - Calendar and Booking System
 * This file handles the calendar functionality for service bookings
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize booking calendar if it exists
    const calendarElement = document.getElementById('booking-calendar');
    if (calendarElement) {
        initializeBookingCalendar();
    }
});

/**
 * Initialize the booking calendar with FlatPickr
 */
function initializeBookingCalendar() {
    // Get DOM elements
    const calendarElement = document.getElementById('booking-calendar');
    const selectedDateInfo = document.getElementById('selected-date-info');
    const selectedDateDisplay = document.getElementById('selected-date-display');
    const timeSlotsContainer = document.getElementById('time-slots');
    const bookingLink = document.getElementById('booking-link');
    const calendarInstructions = document.getElementById('calendar-instructions');
    
    // Initialize flatpickr calendar
    const calendar = flatpickr(calendarElement, {
        inline: true,
        minDate: "today",
        dateFormat: "Y-m-d",
        disable: [
            function(date) {
                // Disable weekends (Sunday)
                return (date.getDay() === 0);
            }
        ],
        onChange: function(selectedDates, dateStr) {
            if (selectedDates.length === 0) return;
            
            // Format the selected date for display
            const formattedDate = formatSelectedDate(selectedDates[0]);
            selectedDateDisplay.textContent = formattedDate;
            
            // Show the loading state
            timeSlotsContainer.innerHTML = '<p class="text-center"><i class="fas fa-spinner fa-spin me-2"></i> Loading available times...</p>';
            selectedDateInfo.classList.remove('d-none');
            calendarInstructions.classList.add('d-none');
            
            // Fetch available time slots for the selected date
            fetchAvailableTimeSlots(dateStr, timeSlotsContainer, bookingLink);
        }
    });
}

/**
 * Format a date object for display
 * @param {Date} date 
 * @returns {string}
 */
function formatSelectedDate(date) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Fetch available time slots for a given date
 * @param {string} dateStr - Date in YYYY-MM-DD format
 * @param {HTMLElement} container - Container for time slots
 * @param {HTMLElement} bookingLink - Link to booking page
 */
function fetchAvailableTimeSlots(dateStr, container, bookingLink) {
    // Make API request for available time slots
    fetch(`/api/timeslots/${dateStr}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Clear the container
            container.innerHTML = '';
            
            if (data.available && data.available.length > 0) {
                // Create time slot buttons
                data.available.forEach(slot => {
                    const timeButton = document.createElement('button');
                    timeButton.className = 'btn btn-outline-primary mb-2';
                    timeButton.textContent = slot.label;
                    timeButton.dataset.time = slot.value;
                    
                    // Add click event to select time
                    timeButton.addEventListener('click', function() {
                        // Remove active class from all buttons
                        container.querySelectorAll('.btn').forEach(btn => {
                            btn.classList.remove('btn-primary');
                            btn.classList.add('btn-outline-primary');
                        });
                        
                        // Add active class to clicked button
                        this.classList.remove('btn-outline-primary');
                        this.classList.add('btn-primary');
                        
                        // Update booking link with selected date and time
                        const currentHref = bookingLink.href.split('?')[0];
                        bookingLink.href = `${currentHref}?booking_date=${dateStr}&booking_time=${this.dataset.time}`;
                    });
                    
                    container.appendChild(timeButton);
                });
                
                // Update booking link with just the date initially
                const currentHref = bookingLink.href.split('?')[0];
                bookingLink.href = `${currentHref}?booking_date=${dateStr}`;
            } else {
                // Show no available slots message
                container.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        No available time slots for this date. Please select another date.
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error fetching time slots:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading time slots. Please try again.
                </div>
            `;
        });
}
