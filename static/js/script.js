// Header scroll effect
window.addEventListener('scroll', function() {
    const header = document.querySelector('header');
    if (window.scrollY > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }
});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

if (hamburger && navLinks) {
    hamburger.addEventListener('click', function() {
        navLinks.classList.toggle('active');
        hamburger.innerHTML = navLinks.classList.contains('active') ?
            '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
    });
}

// Simple wishlist functionality
const wishlistButtons = document.querySelectorAll('.btn-wishlist');

wishlistButtons.forEach(button => {
    button.addEventListener('click', function() {
        const movieId = this.getAttribute('data-movie-id');
        const icon = this.querySelector('i');

        // Send AJAX request to add/remove from wishlist
        fetch(`/add_to_wishlist/${movieId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.added) {
                    icon.classList.replace('far', 'fas');
                    this.innerHTML = '<i class="fas fa-bookmark"></i> Saved';
                    this.style.background = 'rgba(34, 197, 94, 0.2)';
                    this.style.color = '#22c55e';
                } else {
                    icon.classList.replace('fas', 'far');
                    this.innerHTML = '<i class="far fa-bookmark"></i> Wishlist';
                    this.style.background = 'transparent';
                    this.style.color = 'var(--text)';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Redirect to login if not authenticated
                window.location.href = '/login/';
            });
    });
});

// Filter buttons active state
const filterButtons = document.querySelectorAll('.filter-btn');

filterButtons.forEach(button => {
    button.addEventListener('click', function() {
        filterButtons.forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
    });
});

// Rating stars interaction
const ratingInputs = document.querySelectorAll('input[type="radio"][name="rating"]');
const ratingStars = document.querySelectorAll('.rating-star');

if (ratingInputs.length && ratingStars.length) {
    ratingStars.forEach(star => {
        star.addEventListener('click', function() {
            const ratingValue = this.getAttribute('data-value');
            document.querySelector(`#id_rating_${ratingValue}`).checked = true;

            // Update visual rating
            ratingStars.forEach(s => {
                if (s.getAttribute('data-value') <= ratingValue) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });
}

// Form validation
const forms = document.querySelectorAll('form');

forms.forEach(form => {
    form.addEventListener('submit', function(e) {
        const inputs = this.querySelectorAll('input[required], textarea[required], select[required]');
        let valid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                valid = false;
                input.style.borderColor = '#ef4444';
            } else {
                input.style.borderColor = '';
            }
        });

        if (!valid) {
            e.preventDefault();
            alert('Please fill in all required fields.');
        }
    });
});

// Initialize tooltips
const tooltips = document.querySelectorAll('[data-tooltip]');

tooltips.forEach(tooltip => {
    tooltip.addEventListener('mouseenter', function() {
        const tooltipText = this.getAttribute('data-tooltip');
        const tooltipElement = document.createElement('div');
        tooltipElement.className = 'tooltip';
        tooltipElement.textContent = tooltipText;
        document.body.appendChild(tooltipElement);

        const rect = this.getBoundingClientRect();
        tooltipElement.style.left = rect.left + rect.width / 2 - tooltipElement.offsetWidth / 2 + 'px';
        tooltipElement.style.top = rect.top - tooltipElement.offsetHeight - 10 + 'px';
    });

    tooltip.addEventListener('mouseleave', function() {
        const tooltipElement = document.querySelector('.tooltip');
        if (tooltipElement) {
            tooltipElement.remove();
        }
    });
});


// Wishlist functionality
// Add this to your script.js or in the template
// Update your wishlist JavaScript functionality
function setupWishlistButtons() {
    const wishlistButtons = document.querySelectorAll('.btn-wishlist');

    wishlistButtons.forEach(button => {
        button.addEventListener('click', function() {
            const movieId = this.getAttribute('data-movie-id');
            const icon = this.querySelector('i');

            // Send AJAX request to add/remove from wishlist
            fetch(`/add_to_wishlist/${movieId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.added) {
                    icon.classList.replace('far', 'fas');
                    this.innerHTML = '<i class="fas fa-bookmark"></i> In Wishlist';
                    this.classList.add('in-wishlist');

                    // Show success message
                    showToast(data.message, 'success');
                } else {
                    icon.classList.replace('fas', 'far');
                    this.innerHTML = '<i class="far fa-bookmark"></i> Wishlist';
                    this.classList.remove('in-wishlist');

                    // Show info message
                    showToast(data.message, 'info');

                    // If we're on the wishlist page, remove the item
                    if (window.location.pathname === '/wishlist/') {
                        const movieElement = this.closest('[data-movie-id]');
                        if (movieElement) {
                            movieElement.style.opacity = '0';
                            setTimeout(() => {
                                movieElement.remove();
                                // Check if wishlist is empty now
                                if (document.querySelectorAll('.wishlist-item').length === 0) {
                                    location.reload();
                                }
                            }, 300);
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Redirect to login if not authenticated
                window.location.href = '/login/';
            });
        });
    });
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to show toast messages
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
    `;

    // Add to page
    document.body.appendChild(toast);

    // Show toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Hide after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);

    // Close button functionality
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    });
}

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupWishlistButtons();
});



// Add to your script.js
document.addEventListener('DOMContentLoaded', function() {
    // Close message alerts
    const closeButtons = document.querySelectorAll('.alert .close');

    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.parentElement;
            alert.style.animation = 'slideOut 0.3s ease';

            setTimeout(() => {
                alert.remove();
            }, 300);
        });
    });

    // Auto-dismiss messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.animation = 'slideOut 0.3s ease';

                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
});

// ========================
// WEBZMOVIES SCRIPT.JS
// ========================

document.addEventListener("DOMContentLoaded", function () {
    // ------------------------
    // Hamburger Menu Toggle
    // ------------------------
    const hamburger = document.querySelector(".hamburger");
    const navLinks = document.querySelector(".nav-links");

    if (hamburger && navLinks) {
        hamburger.addEventListener("click", () => {
            navLinks.classList.toggle("active");
            hamburger.classList.toggle("active");

            // Change icon dynamically
            const icon = hamburger.querySelector("i");
            if (hamburger.classList.contains("active")) {
                icon.classList.remove("fa-bars");
                icon.classList.add("fa-times");
            } else {
                icon.classList.remove("fa-times");
                icon.classList.add("fa-bars");
            }
        });
    }

    // ------------------------
    // Dismiss Django Messages
    // ------------------------
    const closeButtons = document.querySelectorAll(".messages-container .close");
    closeButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            this.parentElement.style.display = "none";
        });
    });

    // Auto hide messages after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll(".messages-container .alert");
        alerts.forEach((alert) => {
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 600);
        });
    }, 5000);

    // ------------------------
    // Newsletter Subscribe
    // ------------------------
    const subscribeBtn = document.querySelector(".subscribe-btn");
    const subscribeInput = document.querySelector(".subscribe-input");

    if (subscribeBtn && subscribeInput) {
        subscribeBtn.addEventListener("click", () => {
            const email = subscribeInput.value.trim();
            if (!email) {
                alert("Please enter your email address.");
                return;
            }

            // Simple email format check
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                alert("Please enter a valid email address.");
                return;
            }

            // For now, just show success
            alert("✅ Thanks for subscribing! You’ll now receive WebzMovies updates.");
            subscribeInput.value = "";
        });
    }
});

