// Review system for game pages
// Handles rating and review submission

(function() {
  'use strict';

  const AUTH_KEY = 'blueroom_user';
  const REVIEWS_KEY_PREFIX = 'blueroom_reviews_';

  // Get current game slug from URL
  const pathParts = window.location.pathname.split('/').filter(p => p);
  const gameSlug = pathParts[pathParts.length - 1] || pathParts[pathParts.length - 2];

  // Initialize review functionality
  function initReviews() {
    // Star rating input
    const ratingInput = document.querySelector('[data-rating-input]');
    if (ratingInput) {
      const stars = ratingInput.querySelectorAll('.star');
      stars.forEach((star, index) => {
        star.addEventListener('click', () => selectRating(index + 1));
        star.addEventListener('mouseenter', () => hoverRating(index + 1));
      });
      ratingInput.addEventListener('mouseleave', resetHover);
    }

    // Write review button
    const writeReviewBtn = document.querySelector('[data-write-review]');
    if (writeReviewBtn) {
      writeReviewBtn.addEventListener('click', showReviewForm);
    }

    // Cancel review button
    const cancelBtn = document.querySelector('[data-cancel-review]');
    if (cancelBtn) {
      cancelBtn.addEventListener('click', hideReviewForm);
    }

    // Review form submission
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
      reviewForm.addEventListener('submit', handleReviewSubmit);
    }

    // Load existing reviews
    loadReviews();
  }

  function selectRating(value) {
    const stars = document.querySelectorAll('[data-rating-input] .star');
    const ratingValue = document.getElementById('rating-value');

    stars.forEach((star, index) => {
      star.textContent = index < value ? '★' : '☆';
    });

    if (ratingValue) {
      ratingValue.value = value;
    }
  }

  function hoverRating(value) {
    const stars = document.querySelectorAll('[data-rating-input] .star');
    stars.forEach((star, index) => {
      star.textContent = index < value ? '★' : '☆';
    });
  }

  function resetHover() {
    const ratingValue = document.getElementById('rating-value');
    const currentValue = ratingValue ? parseInt(ratingValue.value) || 0 : 0;
    const stars = document.querySelectorAll('[data-rating-input] .star');

    stars.forEach((star, index) => {
      star.textContent = index < currentValue ? '★' : '☆';
    });
  }

  function showReviewForm() {
    // Check if user is logged in
    const userData = localStorage.getItem(AUTH_KEY) || sessionStorage.getItem(AUTH_KEY);

    if (!userData) {
      showMessage('Please login to write a review', 'error');
      setTimeout(() => {
        window.location.href = '/auth/login/';
      }, 1500);
      return;
    }

    const formContainer = document.getElementById('review-form-container');
    if (formContainer) {
      formContainer.style.display = 'block';
      formContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  function hideReviewForm() {
    const formContainer = document.getElementById('review-form-container');
    if (formContainer) {
      formContainer.style.display = 'none';
    }

    // Reset form
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
      reviewForm.reset();
      selectRating(0);
    }
  }

  function handleReviewSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const rating = formData.get('rating');
    const reviewText = formData.get('review');

    // Validate
    if (!rating || rating < 1 || rating > 5) {
      showMessage('Please select a rating', 'error');
      return;
    }

    if (!reviewText || reviewText.length < 20) {
      showMessage('Review must be at least 20 characters', 'error');
      return;
    }

    // Get user data
    const userData = localStorage.getItem(AUTH_KEY) || sessionStorage.getItem(AUTH_KEY);
    if (!userData) {
      showMessage('Please login to submit a review', 'error');
      return;
    }

    const user = JSON.parse(userData);

    // Create review object
    const review = {
      id: 'review_' + Date.now(),
      gameSlug: gameSlug,
      userId: user.id,
      username: user.username,
      rating: parseInt(rating),
      text: reviewText,
      helpful: 0,
      createdAt: new Date().toISOString()
    };

    // Save review
    saveReview(review);

    // Update user stats
    user.comments = (user.comments || 0) + 1;
    user.points = (user.points || 0) + 10; // Award points for review
    if (localStorage.getItem(AUTH_KEY)) {
      localStorage.setItem(AUTH_KEY, JSON.stringify(user));
    } else {
      sessionStorage.setItem(AUTH_KEY, JSON.stringify(user));
    }

    // Show success message
    showMessage('Review submitted successfully! +10 points', 'success');

    // Hide form and reload reviews
    hideReviewForm();
    setTimeout(() => {
      loadReviews();
    }, 500);
  }

  function saveReview(review) {
    const reviewsKey = REVIEWS_KEY_PREFIX + gameSlug;
    const existingReviews = JSON.parse(localStorage.getItem(reviewsKey) || '[]');
    existingReviews.unshift(review); // Add to beginning
    localStorage.setItem(reviewsKey, JSON.stringify(existingReviews));
  }

  function loadReviews() {
    const reviewsKey = REVIEWS_KEY_PREFIX + gameSlug;
    const reviews = JSON.parse(localStorage.getItem(reviewsKey) || '[]');

    if (reviews.length === 0) {
      return; // Keep sample reviews
    }

    const reviewsList = document.getElementById('reviews-list');
    if (!reviewsList) return;

    // Clear existing reviews
    reviewsList.innerHTML = '';

    // Render reviews
    reviews.forEach(review => {
      const reviewCard = createReviewCard(review);
      reviewsList.appendChild(reviewCard);
    });

    // Update review count
    const totalReviews = document.getElementById('total-reviews');
    if (totalReviews) {
      totalReviews.textContent = reviews.length + 10; // +10 for demo purposes
    }
  }

  function createReviewCard(review) {
    const card = document.createElement('div');
    card.className = 'review-card';

    const timeAgo = getTimeAgo(new Date(review.createdAt));
    const stars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);

    card.innerHTML = `
      <div class="review-header">
        <div class="review-author">
          <span class="user-avatar-text">${review.username[0].toUpperCase()}</span>
          <div>
            <strong>${review.username}</strong>
            <div class="review-meta">
              <span class="rating-stars">${stars}</span>
              <span style="color: var(--text-secondary); font-size: 0.875rem;">• ${timeAgo}</span>
            </div>
          </div>
        </div>
      </div>
      <p class="review-text">${escapeHtml(review.text)}</p>
      <div class="review-actions">
        <button class="review-action-btn" data-review-id="${review.id}">👍 Helpful (${review.helpful || 0})</button>
      </div>
    `;

    return card;
  }

  function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return 'just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + ' minutes ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
    if (seconds < 604800) return Math.floor(seconds / 86400) + ' days ago';
    if (seconds < 2592000) return Math.floor(seconds / 604800) + ' weeks ago';
    return Math.floor(seconds / 2592000) + ' months ago';
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function showMessage(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      background: ${type === 'success' ? '#10b981' : '#ef4444'};
      color: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 10000;
      animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // Initialize on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initReviews);
  } else {
    initReviews();
  }

})();
