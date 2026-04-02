/**
 * Lovely Hands Homecare — Frontend Application Logic
 * Handles navigation, forms, modal, scroll animations, and API calls.
 */

// ============ Configuration ============
const API_BASE = window.location.origin + '/api';

// ============ DOM Elements ============
const navbar = document.getElementById('navbar');
const navToggle = document.getElementById('navToggle');
const navLinks = document.getElementById('navLinks');
const backToTop = document.getElementById('backToTop');
const appointmentModal = document.getElementById('appointmentModal');
const modalClose = document.getElementById('modalClose');
const contactForm = document.getElementById('contactForm');
const appointmentForm = document.getElementById('appointmentForm');
const toastContainer = document.getElementById('toastContainer');

// Book buttons
const bookButtons = [
  document.getElementById('heroBookBtn'),
  document.getElementById('navBookBtn'),
  document.getElementById('ctaBookBtn'),
];

// ============ Toast Notifications ============
function showToast(message, type = 'success') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icons[type] || ''}</span> ${message}`;
  toastContainer.appendChild(toast);
  setTimeout(() => toast.remove(), 4200);
}

// ============ Navbar Scroll Effect ============
let lastScroll = 0;
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY;
  
  // Add scrolled class
  if (scrollY > 60) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }

  // Back to top visibility
  if (scrollY > 500) {
    backToTop.classList.add('visible');
  } else {
    backToTop.classList.remove('visible');
  }

  lastScroll = scrollY;
});

// ============ Back to Top ============
backToTop.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ============ Mobile Nav Toggle ============
navToggle.addEventListener('click', () => {
  navLinks.classList.toggle('open');
  const spans = navToggle.querySelectorAll('span');
  if (navLinks.classList.contains('open')) {
    spans[0].style.transform = 'rotate(45deg) translate(6px, 6px)';
    spans[1].style.opacity = '0';
    spans[2].style.transform = 'rotate(-45deg) translate(6px, -6px)';
  } else {
    spans[0].style.transform = '';
    spans[1].style.opacity = '';
    spans[2].style.transform = '';
  }
});

// Close mobile nav on link click
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    const spans = navToggle.querySelectorAll('span');
    spans[0].style.transform = '';
    spans[1].style.opacity = '';
    spans[2].style.transform = '';
  });
});

// ============ Active Nav Link on Scroll ============
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
  const scrollY = window.scrollY + 100;
  sections.forEach(section => {
    const top = section.offsetTop;
    const height = section.offsetHeight;
    const id = section.getAttribute('id');
    const link = navLinks.querySelector(`a[href="#${id}"]`);
    if (link) {
      if (scrollY >= top && scrollY < top + height) {
        navLinks.querySelectorAll('a').forEach(a => a.classList.remove('active'));
        link.classList.add('active');
      }
    }
  });
});

// ============ Appointment Modal ============
function openModal() {
  appointmentModal.classList.add('active');
  document.body.style.overflow = 'hidden';
  // Set min date to today
  const dateInput = document.getElementById('appt-date');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.setAttribute('min', today);
  }
}

function closeModal() {
  appointmentModal.classList.remove('active');
  document.body.style.overflow = '';
}

bookButtons.forEach(btn => {
  if (btn) {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      openModal();
    });
  }
});

modalClose.addEventListener('click', closeModal);
appointmentModal.addEventListener('click', (e) => {
  if (e.target === appointmentModal) closeModal();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

// ============ Form Submission Helper ============
async function submitForm(form, endpoint, submitBtn, spinner) {
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  // Validate
  if (!data.full_name || data.full_name.trim().length < 2) {
    showToast('Please enter your full name.', 'error');
    return;
  }
  if (!data.phone || data.phone.trim().length < 7) {
    showToast('Please enter a valid phone number.', 'error');
    return;
  }
  if (!data.service_needed) {
    showToast('Please select a service.', 'error');
    return;
  }

  // Show loading
  const btnText = submitBtn.querySelector('span');
  const btnSpinner = submitBtn.querySelector('.spinner');
  btnText.textContent = 'Sending...';
  if (btnSpinner) btnSpinner.style.display = 'block';
  submitBtn.disabled = true;
  submitBtn.style.opacity = '0.7';

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (response.ok && result.success) {
      showToast(result.message, 'success');
      form.reset();
      if (endpoint === '/appointment') {
        setTimeout(closeModal, 1500);
      }
    } else {
      const errMsg = result.detail
        ? (Array.isArray(result.detail) ? result.detail.map(e => e.msg).join(', ') : result.detail)
        : 'Something went wrong. Please try again.';
      showToast(errMsg, 'error');
    }
  } catch (err) {
    console.error('Form submission error:', err);
    // Fallback: open mailto
    const subject = encodeURIComponent(`${endpoint === '/appointment' ? 'Appointment Request' : 'Contact Form'} from ${data.full_name}`);
    const body = encodeURIComponent(
      Object.entries(data).map(([k, v]) => `${k.replace(/_/g, ' ')}: ${v}`).join('\n')
    );
    window.location.href = `mailto:anwarjohn108@gmail.com?subject=${subject}&body=${body}`;
    showToast('Redirecting to email as fallback...', 'info');
  } finally {
    btnText.textContent = endpoint === '/appointment' ? 'Book Appointment' : 'Send Message';
    if (btnSpinner) btnSpinner.style.display = 'none';
    submitBtn.disabled = false;
    submitBtn.style.opacity = '1';
  }
}

// ============ Contact Form ============
contactForm.addEventListener('submit', (e) => {
  e.preventDefault();
  submitForm(
    contactForm,
    '/contact',
    document.getElementById('contactSubmitBtn'),
    document.getElementById('contactSpinner')
  );
});

// ============ Appointment Form ============
appointmentForm.addEventListener('submit', (e) => {
  e.preventDefault();
  submitForm(
    appointmentForm,
    '/appointment',
    document.getElementById('appointmentSubmitBtn'),
    document.getElementById('appointmentSpinner')
  );
});

// ============ Scroll Reveal Animations ============
const revealElements = document.querySelectorAll('.reveal');

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      revealObserver.unobserve(entry.target);
    }
  });
}, {
  threshold: 0.15,
  rootMargin: '0px 0px -50px 0px'
});

revealElements.forEach(el => revealObserver.observe(el));

// ============ Smooth Scroll for Anchor Links ============
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const href = this.getAttribute('href');
    if (href === '#') return; // skip book buttons
    e.preventDefault();
    const target = document.querySelector(href);
    if (target) {
      const offset = 80;
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ============ Phone Number Formatting ============
document.querySelectorAll('input[type="tel"]').forEach(input => {
  input.addEventListener('input', (e) => {
    let val = e.target.value.replace(/\D/g, '');
    if (val.length > 0 && val[0] === '1') {
      // US number with country code
      if (val.length > 11) val = val.slice(0, 11);
      if (val.length > 1) val = `+1 (${val.slice(1, 4)}) ${val.slice(4, 7)}-${val.slice(7)}`;
      else val = `+${val}`;
    } else {
      if (val.length > 10) val = val.slice(0, 10);
      if (val.length > 6) val = `(${val.slice(0, 3)}) ${val.slice(3, 6)}-${val.slice(6)}`;
      else if (val.length > 3) val = `(${val.slice(0, 3)}) ${val.slice(3)}`;
    }
    e.target.value = val;
  });
});

// ============ Counter Animation ============
function animateCounters() {
  const counters = document.querySelectorAll('.stat-number');
  counters.forEach(counter => {
    const text = counter.textContent;
    const num = parseInt(text.replace(/\D/g, ''));
    const suffix = text.replace(/[\d]/g, '');
    
    if (isNaN(num)) return;
    
    let current = 0;
    const step = Math.ceil(num / 60);
    const timer = setInterval(() => {
      current += step;
      if (current >= num) {
        current = num;
        clearInterval(timer);
      }
      counter.textContent = current + suffix;
    }, 25);
  });
}

// Run counter when hero is in view
const heroObserver = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    animateCounters();
    heroObserver.disconnect();
  }
}, { threshold: 0.5 });

const heroSection = document.getElementById('home');
if (heroSection) heroObserver.observe(heroSection);

// ============ Init ============
console.log('💖 Lovely Hands Homecare — Ready');
