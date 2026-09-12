// ===========================================
// 1. MOBILE NAV TOGGLE
// This is the kind of thing JS is FOR in a browser:
// listening for a click, then changing something on the page.
// ===========================================
const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');

navToggle.addEventListener('click', () => {
  mainNav.classList.toggle('open');
});

// Close the mobile menu automatically once a link is clicked
mainNav.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    mainNav.classList.remove('open');
  });
});


// ===========================================
// 2. CONTACT FORM (front-end only for now)
// Right now this just shows a message — it does NOT actually
// send an email anywhere yet. Wiring it up to really send messages
// needs a backend or a form service (we can add that later).
// ===========================================

