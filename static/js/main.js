/**
 * GlaCK0N GarageHub - Main JavaScript
 * This file contains general JavaScript functionality for the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize popovers
    initializePopovers();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Add event listener for mobile menu toggle if present
    const menuToggle = document.querySelector('.navbar-toggler');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            document.body.classList.toggle('menu-open');
        });
    }
    
    // Initialize any image galleries if they exist
    initializeImageGalleries();
    
    // Initialize form validation
    initializeFormValidation();
    
    // Add fade-in animation to main content
    animatePageLoad();
});

/**
 * Initialize Bootstrap popovers
 */
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl, {
            trigger: 'focus'
        });
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize image galleries
 * This function sets up image click handlers for vehicle detail pages
 */
function initializeImageGalleries() {
    const imageGallery = document.querySelector('.carousel-indicators');
    if (imageGallery) {
        const thumbs = imageGallery.querySelectorAll('button');
        thumbs.forEach(thumb => {
            thumb.addEventListener('click', function() {
                // Remove active class from all thumbs
                thumbs.forEach(t => t.classList.remove('active'));
                // Add active class to clicked thumb
                this.classList.add('active');
            });
        });
    }
}

/**
 * Form validation initialization
 * Add custom validation to forms
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Add fade-in animation to main content
 */
function animatePageLoad() {
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
}

/**
 * Show loading overlay when submitting forms
 * @param {HTMLFormElement} form 
 */
function showLoadingOverlay(form) {
    form.addEventListener('submit', function() {
        // Create loading overlay
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        overlay.appendChild(spinner);
        document.body.appendChild(overlay);
        
        return true;
    });
}

/**
 * Format currency based on country (ZAR for South Africa, USD for Zimbabwe)
 * @param {number} amount 
 * @param {string} country 
 * @returns {string}
 */
function formatCurrency(amount, country = 'SA') {
    if (!amount) return '';
    
    const formatter = new Intl.NumberFormat(country === 'SA' ? 'en-ZA' : 'en-US', {
        style: 'currency',
        currency: country === 'SA' ? 'ZAR' : 'USD',
        minimumFractionDigits: 0
    });
    
    return formatter.format(amount);
}

/**
 * Confirm action with a custom confirm dialog
 * @param {string} message 
 * @param {Function} callback 
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}
