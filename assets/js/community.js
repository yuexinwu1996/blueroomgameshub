// Community forum functionality for BlueRoom.cc

(function() {
  'use strict';

  const AUTH_KEY = 'blueroom_user';
  const POSTS_KEY = 'blueroom_posts';

  // Initialize community features
  function initCommunity() {
    // New post button
    const newPostBtn = document.querySelector('[data-new-post]');
    if (newPostBtn) {
      newPostBtn.addEventListener('click', showNewPostModal);
    }

    // Close modal buttons
    const closeModalBtns = document.querySelectorAll('[data-close-modal]');
    closeModalBtns.forEach(btn => {
      btn.addEventListener('click', hideNewPostModal);
    });

    // New post form
    const newPostForm = document.getElementById('new-post-form');
    if (newPostForm) {
      newPostForm.addEventListener('submit', handleNewPost);
    }

    // Category filter
    const categoryItems = document.querySelectorAll('[data-category]');
    categoryItems.forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        filterByCategory(item.dataset.category);
      });
    });

    // Sort buttons
    const sortBtns = document.querySelectorAll('[data-sort]');
    sortBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        sortBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        sortPosts(btn.dataset.sort);
      });
    });

    // Load posts
    loadPosts();
  }

  function showNewPostModal() {
    // Check if user is logged in
    const userData = localStorage.getItem(AUTH_KEY) || sessionStorage.getItem(AUTH_KEY);

    if (!userData) {
      showMessage('Please login to create a post', 'error');
      setTimeout(() => {
        window.location.href = '/auth/login/';
      }, 1500);
      return;
    }

    const modal = document.getElementById('new-post-modal');
    if (modal) {
      modal.style.display = 'flex';
      document.body.style.overflow = 'hidden';
    }
  }

  function hideNewPostModal() {
    const modal = document.getElementById('new-post-modal');
    if (modal) {
      modal.style.display = 'none';
      document.body.style.overflow = '';
    }

    // Reset form
    const form = document.getElementById('new-post-form');
    if (form) {
      form.reset();
    }
  }

  function handleNewPost(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const title = formData.get('title');
    const category = formData.get('category');
    const content = formData.get('content');
    const tagsInput = formData.get('tags');

    // Validate
    if (!title || title.length < 10) {
      showMessage('Title must be at least 10 characters', 'error');
      return;
    }

    if (!category) {
      showMessage('Please select a category', 'error');
      return;
    }

    if (!content || content.length < 50) {
      showMessage('Content must be at least 50 characters', 'error');
      return;
    }

    // Get user data
    const userData = localStorage.getItem(AUTH_KEY) || sessionStorage.getItem(AUTH_KEY);
    if (!userData) {
      showMessage('Please login to create a post', 'error');
      return;
    }

    const user = JSON.parse(userData);

    // Parse tags
    const tags = tagsInput ? tagsInput.split(/\s+/).filter(t => t.startsWith('#')) : [];

    // Create post object
    const post = {
      id: 'post_' + Date.now(),
      authorId: user.id,
      authorName: user.username,
      title: title,
      category: category,
      content: content,
      tags: tags,
      views: 0,
      replies: 0,
      likes: 0,
      createdAt: new Date().toISOString()
    };

    // Save post
    savePost(post);

    // Update user stats
    user.posts = (user.posts || 0) + 1;
    user.points = (user.points || 0) + 15; // Award points for creating post
    if (localStorage.getItem(AUTH_KEY)) {
      localStorage.setItem(AUTH_KEY, JSON.stringify(user));
    } else {
      sessionStorage.setItem(AUTH_KEY, JSON.stringify(user));
    }

    // Show success message
    showMessage('Post created successfully! +15 points', 'success');

    // Hide modal and reload posts
    hideNewPostModal();
    setTimeout(() => {
      loadPosts();
    }, 500);
  }

  function savePost(post) {
    const existingPosts = JSON.parse(localStorage.getItem(POSTS_KEY) || '[]');
    existingPosts.unshift(post); // Add to beginning
    localStorage.setItem(POSTS_KEY, JSON.stringify(existingPosts));
  }

  function loadPosts() {
    const posts = JSON.parse(localStorage.getItem(POSTS_KEY) || '[]');

    if (posts.length === 0) {
      return; // Keep sample posts
    }

    const postsContainer = document.getElementById('posts-container');
    if (!postsContainer) return;

    // Clear existing posts
    postsContainer.innerHTML = '';

    // Render posts
    posts.forEach(post => {
      const postCard = createPostCard(post);
      postsContainer.appendChild(postCard);
    });
  }

  function createPostCard(post) {
    const card = document.createElement('article');
    card.className = 'post-card';

    const timeAgo = getTimeAgo(new Date(post.createdAt));
    const authorInitial = (post.authorName || 'U')[0].toUpperCase();

    const tagsHtml = post.tags.map(tag =>
      `<span class="badge-soft">${tag}</span>`
    ).join('');

    card.innerHTML = `
      <div class="post-author">
        <span class="user-avatar-text">${authorInitial}</span>
        <div>
          <strong>${escapeHtml(post.authorName)}</strong>
          <span style="color: var(--text-secondary); font-size: 0.875rem;">• ${timeAgo}</span>
        </div>
      </div>
      <div class="post-content">
        <h3><a href="/community/posts/${post.id}/">${escapeHtml(post.title)}</a></h3>
        <p>${escapeHtml(post.content.substring(0, 150))}${post.content.length > 150 ? '...' : ''}</p>
        <div class="post-tags">
          ${tagsHtml}
          <span class="badge-soft">#${post.category}</span>
        </div>
      </div>
      <div class="post-stats">
        <span>👁️ ${post.views} views</span>
        <span>💬 ${post.replies} replies</span>
        <span>👍 ${post.likes} likes</span>
      </div>
    `;

    return card;
  }

  function filterByCategory(category) {
    // Update active state
    const categoryItems = document.querySelectorAll('[data-category]');
    categoryItems.forEach(item => {
      item.classList.toggle('active', item.dataset.category === category);
    });

    // TODO: Implement actual filtering
    console.log('Filter by category:', category);
  }

  function sortPosts(sortType) {
    // TODO: Implement actual sorting
    console.log('Sort by:', sortType);
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
    document.addEventListener('DOMContentLoaded', initCommunity);
  } else {
    initCommunity();
  }

})();
