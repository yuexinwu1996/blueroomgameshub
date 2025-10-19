// Profile page functionality for BlueRoom.cc

(function() {
  'use strict';

  const AUTH_KEY = 'blueroom_user';

  // Load user data
  function loadUserData() {
    const userData = localStorage.getItem(AUTH_KEY) || sessionStorage.getItem(AUTH_KEY);

    if (!userData) {
      // Redirect to login if not authenticated
      window.location.href = '/auth/login/';
      return;
    }

    const user = JSON.parse(userData);

    // Update profile UI
    document.getElementById('profile-username').textContent = user.username || 'User';
    document.getElementById('user-points').textContent = user.points || 0;
    document.getElementById('user-posts').textContent = user.posts || 0;
    document.getElementById('user-comments').textContent = user.comments || 0;

    // Update avatar
    const avatarText = (user.username || 'U')[0].toUpperCase();
    document.querySelectorAll('.user-avatar-text').forEach(el => {
      el.textContent = avatarText;
    });
  }

  // Initialize on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadUserData);
  } else {
    loadUserData();
  }

})();
