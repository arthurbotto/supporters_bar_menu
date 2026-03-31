document.querySelector('.admin-filter-controls').addEventListener('click', function(e) {
  const btn = e.target.closest('button');
  if (!btn) return;
  this.querySelectorAll('button').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
});
