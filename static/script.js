// ===========================================
// 1. MOBILE NAV TOGGLE
// ===========================================
const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');
const siteHeader = document.querySelector('.site-header');

navToggle.addEventListener('click', () => {
  mainNav.classList.toggle('open');
  navToggle.classList.toggle('open'); // lets CSS flip the bars to dark
});

// Close the mobile menu automatically once a link is clicked
mainNav.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    mainNav.classList.remove('open');
    navToggle.classList.remove('open');
  });
});

// Give the sticky header a solid background once you scroll
// past the hero image, so it doesn't float transparently over
// light page content (and so the hamburger stays visible)
window.addEventListener('scroll', () => {
  if (window.scrollY > 60) {
    siteHeader.classList.add('scrolled');
  } else {
    siteHeader.classList.remove('scrolled');
  }
});

// Accordion behavior for mobile dropdown submenus
document.querySelectorAll('.nav-dropdown-caret').forEach((caret) => {
  caret.addEventListener('click', (e) => {
    e.preventDefault();
    caret.closest('.nav-dropdown').classList.toggle('open');
  });
});

// Only autoplay videos when they're actually visible on screen —
// prevents multiple videos decoding at once, which can cause
// scroll rendering glitches on mobile, and saves visitors' data
const galleryVideos = document.querySelectorAll('.gallery-tile video');

const videoObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.play();
    } else {
      entry.target.pause();
    }
  });
}, { threshold: 0.5 });

galleryVideos.forEach((video) => {
  video.removeAttribute('autoplay'); // let the observer control playback instead
  videoObserver.observe(video);
});

// Open the video only on tap, instead of always decoding inline —
// avoids competing with the map for rendering resources
const videoThumb = document.getElementById('videoThumb');
const videoModal = document.getElementById('videoModal');
const videoModalClose = document.getElementById('videoModalClose');
const modalVideo = document.getElementById('modalVideo');

if (videoThumb) {
  videoThumb.addEventListener('click', () => {
    videoModal.classList.add('open');
    modalVideo.play();
  });

  videoModalClose.addEventListener('click', () => {
    videoModal.classList.remove('open');
    modalVideo.pause();
  });
}

// FAQ accordion — each question toggles independently
document.querySelectorAll('.faq-question').forEach((question) => {
  question.addEventListener('click', () => {
    const item = question.closest('.faq-item');
    const answer = item.querySelector('.faq-answer');
    const isOpen = item.classList.contains('open');

    item.classList.toggle('open');
    question.setAttribute('aria-expanded', !isOpen);
    answer.style.maxHeight = isOpen ? null : answer.scrollHeight + 'px';
  });
});