'use strict';
const language = document.documentElement.lang;
const search = document.querySelector('#search');
const articles = [...document.querySelectorAll('article.section')];
const navLinks = [...document.querySelectorAll('nav a')];
const status = document.querySelector('#status');
const normalize = text => text.toLocaleLowerCase(language).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ı/g, 'i');
const index = articles.map(article => normalize(article.textContent));
function filter() {
  const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
  let count = 0;
  articles.forEach((article, i) => {
    const found = words.every(word => index[i].includes(word));
    article.hidden = !found;
    navLinks[i].hidden = !found;
    if (found) count++;
    if (words.length && found) article.querySelectorAll('details').forEach(detail => detail.open = true);
  });
  document.querySelector('#empty').hidden = count !== 0;
  status.textContent = words.length ? (language === 'tr' ? `${count} bölüm bulundu. Aramayı temizleyerek tümünü gösterin.` : `${count} sections found. Clear search to show all.`) : '';
}
search.addEventListener('input', filter);
function revealHash() {
  if (!location.hash) return;
  const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if (target) {
    if (target.hidden) { search.value = ''; filter(); }
    target.closest('details')?.setAttribute('open', '');
    target.scrollIntoView({behavior: 'instant'});
  }
}
window.addEventListener('hashchange', revealHash);
revealHash();
document.querySelector('.language').addEventListener('click', event => {
  event.currentTarget.href = event.currentTarget.dataset.page + location.hash;
});
document.querySelector('.mobile-menu').addEventListener('click', event => {
  const open = document.querySelector('.sidebar').classList.toggle('mobile-open');
  event.currentTarget.setAttribute('aria-expanded', String(open));
});
navLinks.forEach(link => link.addEventListener('click', () => {
  document.querySelector('.sidebar').classList.remove('mobile-open');
  document.querySelector('.mobile-menu').setAttribute('aria-expanded', 'false');
}));
document.querySelector('.expand').addEventListener('click', event => {
  const expand = event.currentTarget.getAttribute('aria-expanded') !== 'true';
  articles.filter(a => !a.hidden).forEach(a => a.querySelectorAll('details').forEach(d => d.open = expand));
  event.currentTarget.setAttribute('aria-expanded', String(expand));
  event.currentTarget.textContent = language === 'tr' ? (expand ? 'Bölümleri daralt' : 'Bölümleri genişlet') : (expand ? 'Collapse sections' : 'Expand sections');
});
document.querySelector('.print').addEventListener('click', () => window.print());
let printState;
window.addEventListener('beforeprint', () => {
  printState = [...document.querySelectorAll('details')].map(d => d.open);
  document.querySelectorAll('details').forEach(d => d.open = true);
});
window.addEventListener('afterprint', () => {
  document.querySelectorAll('details').forEach((d,i) => d.open = printState[i]);
});
const viewer = document.querySelector('#viewer');
document.querySelectorAll('.image-button').forEach(button => button.addEventListener('click', () => {
  const image = button.querySelector('img');
  document.querySelector('#viewer-image').src = image.src;
  document.querySelector('#viewer-image').alt = image.alt;
  document.querySelector('#viewer-title').textContent = image.alt;
  document.querySelector('#full-image').href = image.src;
  viewer.showModal();
}));
document.querySelector('#close-viewer').addEventListener('click', () => viewer.close());
viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) navLinks.forEach(link => link.classList.toggle('active', link.hash === '#' + entry.target.id));
  });
}, {rootMargin: '-10% 0px -75% 0px'});
articles.forEach(article => observer.observe(article));
