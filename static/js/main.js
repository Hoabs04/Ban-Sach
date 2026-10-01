/**
 * BookStore - Main JavaScript
 * Handles: mobile menu, messages auto-dismiss, quantity inputs, etc.
 */

document.addEventListener('DOMContentLoaded', function() {

  // ==========================================
  // Mobile Menu Toggle
  // ==========================================
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', function() {
      mobileMenu.classList.toggle('hidden');
      // Animate
      if (!mobileMenu.classList.contains('hidden')) {
        mobileMenu.style.maxHeight = mobileMenu.scrollHeight + 'px';
      } else {
        mobileMenu.style.maxHeight = '0';
      }
    });
  }

  // ==========================================
  // Auto-dismiss messages
  // ==========================================
  const messages = document.querySelectorAll('.alert[data-auto-dismiss]');
  messages.forEach(function(msg) {
    const delay = parseInt(msg.dataset.autoDismiss) || 5000;
    setTimeout(function() {
      msg.style.transition = 'opacity 0.5s, transform 0.5s';
      msg.style.opacity = '0';
      msg.style.transform = 'translateY(-10px)';
      setTimeout(() => msg.remove(), 500);
    }, delay);
  });

  // Close message on click
  document.querySelectorAll('.alert-close').forEach(function(btn) {
    btn.addEventListener('click', function() {
      const alert = btn.closest('.alert');
      alert.style.transition = 'opacity 0.3s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 300);
    });
  });

  // ==========================================
  // Quantity Input Controls
  // ==========================================
  document.querySelectorAll('.qty-control').forEach(function(container) {
    const input = container.querySelector('input[type="number"]');
    const btnMinus = container.querySelector('.qty-minus');
    const btnPlus = container.querySelector('.qty-plus');

    if (btnMinus) {
      btnMinus.addEventListener('click', function() {
        const min = parseInt(input.min) || 1;
        const current = parseInt(input.value) || 1;
        if (current > min) {
          input.value = current - 1;
          input.dispatchEvent(new Event('change'));
        }
      });
    }

    if (btnPlus) {
      btnPlus.addEventListener('click', function() {
        const max = parseInt(input.max) || 999;
        const current = parseInt(input.value) || 1;
        if (current < max) {
          input.value = current + 1;
          input.dispatchEvent(new Event('change'));
        }
      });
    }
  });

  // ==========================================
  // Search Bar Enhancement
  // ==========================================
  const searchInput = document.getElementById('search-input');
  const searchClear = document.getElementById('search-clear');

  if (searchInput && searchClear) {
    searchInput.addEventListener('input', function() {
      searchClear.style.display = this.value ? 'block' : 'none';
    });
    searchClear.addEventListener('click', function() {
      searchInput.value = '';
      searchInput.focus();
      searchClear.style.display = 'none';
    });
  }

  // ==========================================
  // Image Gallery (Book Detail)
  // ==========================================
  const mainImage = document.getElementById('main-book-image');
  const thumbs = document.querySelectorAll('.book-thumb');

  thumbs.forEach(function(thumb) {
    thumb.addEventListener('click', function() {
      if (mainImage) {
        mainImage.src = this.dataset.src;
        mainImage.alt = this.alt;
      }
      thumbs.forEach(t => t.classList.remove('ring-2', 'ring-primary-500'));
      this.classList.add('ring-2', 'ring-primary-500');
    });
  });

  // ==========================================
  // Back to Top Button
  // ==========================================
  const backToTop = document.getElementById('back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 500) {
        backToTop.classList.remove('opacity-0', 'pointer-events-none');
        backToTop.classList.add('opacity-100');
      } else {
        backToTop.classList.add('opacity-0', 'pointer-events-none');
        backToTop.classList.remove('opacity-100');
      }
    });
    backToTop.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ==========================================
  // Format currency
  // ==========================================
  window.formatCurrency = function(amount) {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND',
      maximumFractionDigits: 0,
    }).format(amount);
  };

});
