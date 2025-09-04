// ========================
// CSRF token handling
// ========================
function getCSRFToken() {
    let csrfToken = null;
    const name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                csrfToken = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return csrfToken;
}

// ========================
// Toast notification
// ========================
function showToast(message, type = 'info') {
    const existing = document.querySelectorAll('.toast');
    existing.forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-message">${message}</div>
        <button class="toast-close">&times;</button>
    `;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);

    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    });
}

// ========================
// Add / Remove wishlist
// ========================
function setupWishlistButtons() {
    const wishlistButtons = document.querySelectorAll('.btn-wishlist');

    wishlistButtons.forEach(button => {
        button.addEventListener('click', function () {
            const movieId = this.getAttribute('data-movie-id');
            const icon = this.querySelector('i');
            const csrfToken = getCSRFToken();

            if (!csrfToken) {
                showToast('Authentication error. Refresh page.', 'error');
                return;
            }

            fetch(`/add_to_wishlist/${movieId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            })
            .then(response => {
                if (response.status === 403) throw new Error('Authentication failed');
                return response.json();
            })
            .then(data => {
                if (data.added) {
                    icon.classList.replace('far', 'fas');
                    this.innerHTML = '<i class="fas fa-bookmark"></i> In Wishlist';
                    this.classList.add('in-wishlist');
                    showToast(data.message, 'success');
                } else {
                    icon.classList.replace('fas', 'far');
                    this.innerHTML = '<i class="far fa-bookmark"></i> Wishlist';
                    this.classList.remove('in-wishlist');
                    showToast(data.message, 'info');

                    // Remove item if we are on wishlist page
                    if (window.location.pathname === '/wishlist/') {
                        const movieElement = this.closest('[data-movie-id]');
                        if (movieElement) {
                            movieElement.style.opacity = '0';
                            movieElement.style.transform = 'translateX(100px)';
                            setTimeout(() => {
                                movieElement.remove();
                                if (document.querySelectorAll('.wishlist-item').length === 0) {
                                    location.reload();
                                }
                            }, 300);
                        }
                    }
                }
            })
            .catch(error => {
                if (error.message === 'Authentication failed') {
                    showToast('Please login to manage wishlist', 'error');
                    setTimeout(() => window.location.href = '/login/', 1500);
                } else {
                    showToast('Error updating wishlist.', 'error');
                }
            });
        });
    });
}

// ========================
// Overlay Wishlist Buttons
// ========================
function setupOverlayWishlistButtons() {
    const overlayWishlistButtons = document.querySelectorAll('.btn-wishlist-overlay');

    overlayWishlistButtons.forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const movieId = this.getAttribute('data-movie-id');
            const icon = this.querySelector('i');
            const csrfToken = getCSRFToken();

            if (!csrfToken) {
                showToast('Authentication error. Refresh page.', 'error');
                return;
            }

            fetch(`/add_to_wishlist/${movieId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            })
            .then(response => {
                if (response.status === 403) throw new Error('Authentication failed');
                return response.json();
            })
            .then(data => {
                if (data.added) {
                    icon.classList.replace('far', 'fas');
                    showToast(data.message, 'success');

                    const mainButton = document.querySelector(`.btn-wishlist[data-movie-id="${movieId}"]`);
                    if (mainButton) {
                        mainButton.innerHTML = '<i class="fas fa-bookmark"></i> In Wishlist';
                        mainButton.classList.add('in-wishlist');
                    }
                } else {
                    icon.classList.replace('fas', 'far');
                    showToast(data.message, 'info');

                    const mainButton = document.querySelector(`.btn-wishlist[data-movie-id="${movieId}"]`);
                    if (mainButton) {
                        mainButton.innerHTML = '<i class="far fa-bookmark"></i> Wishlist';
                        mainButton.classList.remove('in-wishlist');
                    }
                }
            })
            .catch(error => {
                if (error.message === 'Authentication failed') {
                    showToast('Please login to manage wishlist', 'error');
                    setTimeout(() => window.location.href = '/login/', 1500);
                } else {
                    showToast('Error updating wishlist.', 'error');
                }
            });
        });
    });
}

// ========================
// Remove from Wishlist Page
// ========================
function setupRemoveButtons() {
    const removeButtons = document.querySelectorAll('.btn-remove-wishlist');

    removeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const movieId = this.getAttribute('data-movie-id');
            const wishlistItem = this.closest('.wishlist-item');
            const csrfToken = getCSRFToken();

            if (!csrfToken) {
                showToast('Authentication error. Refresh page.', 'error');
                return;
            }

            fetch(`/remove_from_wishlist/${movieId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            })
            .then(response => {
                if (response.status === 403) throw new Error('Authentication failed');
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    wishlistItem.style.opacity = '0';
                    wishlistItem.style.transform = 'translateX(100px)';
                    setTimeout(() => {
                        wishlistItem.remove();
                        if (document.querySelectorAll('.wishlist-item').length === 0) {
                            location.reload();
                        }
                    }, 300);
                    showToast(data.message, 'info');
                }
            })
            .catch(error => {
                if (error.message === 'Authentication failed') {
                    showToast('Please login to manage wishlist', 'error');
                    setTimeout(() => window.location.href = '/login/', 1500);
                } else {
                    showToast('Error removing from wishlist.', 'error');
                }
            });
        });
    });
}

// ========================
// Init
// ========================
document.addEventListener('DOMContentLoaded', function () {
    setupWishlistButtons();
    setupOverlayWishlistButtons();
    setupRemoveButtons();
});
