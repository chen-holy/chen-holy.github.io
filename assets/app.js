const body = document.querySelector('#article-body');
if (body) {
  const headings = [...body.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(h => h.id);
  const links = [...document.querySelectorAll('.article-toc a')];
  const bar = document.querySelector('.reading-progress');
  let queued = false;
  function update() {
    queued = false;
    let current = headings[0];
    for (const heading of headings) {
      if (heading.getBoundingClientRect().top <= 140) current = heading;
    }
    for (const link of links) {
      const active = current && decodeURIComponent(link.hash.slice(1)) === current.id;
      link.classList.toggle('active', Boolean(active));
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
    const height = body.getBoundingClientRect().height - window.innerHeight;
    const progress = height > 0 ? -body.getBoundingClientRect().top / height : 1;
    bar.style.width = `${Math.min(1, Math.max(0, progress)) * 100}%`;
  }
  window.addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(update); } }, {passive:true});
  window.addEventListener('resize', update);
  update();
}
const widget = document.querySelector('#comments-widget');
if (widget) {
  const script = document.createElement('script');
  script.src = 'https://utteranc.es/client.js';
  script.setAttribute('repo', widget.dataset.repo);
  script.setAttribute('issue-term', 'pathname');
  script.setAttribute('theme', 'github-light');
  script.crossOrigin = 'anonymous';
  script.async = true;
  widget.append(script);
}
