// Authentication handling for BlueRoom.cc
// This is a client-side mock - in production, connect to your backend API

(function() {
  'use strict';

  // Mock user storage (localStorage for demo)
  const AUTH_KEY = 'blueroom_user';

  // Login form handler
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', handleLogin);
  }

  // Register form handler
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', handleRegister);
  }

  function handleLogin(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');
    const remember = formData.get('remember');

    // TODO: Replace with actual API call
    // For now, mock successful login
    const mockUser = {
      id: 'user_' + Date.now(),
      email: email,
      username: email.split('@')[0],
      points: 0,
      posts: 0,
      comments: 0,
      joinDate: new Date().toISOString(),
      avatar: null
    };

    // Store user data
    if (remember) {
      localStorage.setItem(AUTH_KEY, JSON.stringify(mockUser));
    } else {
      sessionStorage.setItem(AUTH_KEY, JSON.stringify(mockUser));
    }

    // Show success message
    showMessage('Login successful! Redirecting...', 'success');

    // Redirect to home page
    setTimeout(() => {
      window.location.href = '/';
    }, 1000);
  }

  function handleRegister(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const username = formData.get('username');
    const email = formData.get('email');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm-password');

    // Validate password match
    if (password !== confirmPassword) {
      showMessage('Passwords do not match', 'error');
      return;
    }

    // TODO: Replace with actual API call
    // For now, mock successful registration
    const mockUser = {
      id: 'user_' + Date.now(),
      email: email,
      username: username,
      points: 0,
      posts: 0,
      comments: 0,
      joinDate: new Date().toISOString(),
      avatar: null
    };

    // Store user data
    localStorage.setItem(AUTH_KEY, JSON.stringify(mockUser));

    // Show success message
    showMessage('Account created successfully! Redirecting...', 'success');

    // Redirect to home page
    setTimeout(() => {
      window.location.href = '/';
    }, 1000);
  }

  function showMessage(message, type) {
    // Create toast notification
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

    // Remove after 3 seconds
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease-out';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // Add CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(400px);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);

})();
