const el = id => document.getElementById(id);
let examples = [];
function display() {
  const example = examples[Number(el('example').value)];
  if (!example) return;
  el('title').textContent = example.title;
  el('description').textContent = example.text;
  el('caption').textContent = example.caption;
  for (const id of ['before', 'before-slide']) el(id).src = example.before;
  for (const id of ['after', 'after-slide']) el(id).src = example.after;
}
el('example').addEventListener('change', display);
for (const mode of ['side','slide']) el(mode).addEventListener('click', () => {
  el('pair').hidden = mode !== 'side';
  el('slider-view').hidden = mode !== 'slide';
  el('side').setAttribute('aria-pressed', String(mode === 'side'));
  el('slide').setAttribute('aria-pressed', String(mode === 'slide'));
});
el('zoom').addEventListener('click', () => {
  const zoomed = document.body.classList.toggle('zoom');
  el('zoom').setAttribute('aria-pressed', String(zoomed));
  el('zoom').textContent = zoomed ? 'Ver imagen completa' : 'Acercar detalle';
});
el('range').addEventListener('input', () => {
  const value = Number(el('range').value);
  el('before-slide').style.clipPath = `inset(0 ${100-value}% 0 0)`;
  el('divider').style.left = `${value}%`;
  el('percentage').textContent = `${value} %`;
});
fetch('/demo/ejemplos.json').then(response => { if (!response.ok) throw new Error(); return response.json(); }).then(items => {
  examples = items.filter(item => /^\/demo\/[\w.-]+$/.test(item.before) && /^\/demo\/[\w.-]+$/.test(item.after));
  examples.sort((a,b) => (a.tool === 'realista' ? -1 : b.tool === 'realista' ? 1 : 0));
  el('example').replaceChildren(...examples.map((item,index) => {
    const option = document.createElement('option'); option.value = String(index); option.textContent = item.title; return option;
  }));
  display();
}).catch(() => { el('error').hidden = false; el('error').textContent = 'No se pudieron cargar los ejemplos. Abre esta página desde LUMIA encendido.'; });
