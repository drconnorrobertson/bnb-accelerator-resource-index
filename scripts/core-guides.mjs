import fs from 'node:fs';

const guides = JSON.parse(fs.readFileSync(new URL('../content/core-guides.json', import.meta.url), 'utf8'));
const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const paragraph = text => `<p>${escape(text)}</p>`;
const money = value => new Intl.NumberFormat('en-US', {style:'currency',currency:'USD',maximumFractionDigits:0}).format(value);

function renderLedger(ledger) {
  if (!Number.isFinite(ledger.opening) || ledger.opening < 0 || ledger.deductions.some(row => !Number.isFinite(row.amount) || row.amount < 0)) {
    throw new Error('Cash bridge requires finite nonnegative amounts.');
  }
  const remaining = ledger.opening - ledger.deductions.reduce((sum, row) => sum + row.amount, 0);
  return `<table style="width:100%;border-collapse:collapse"><caption style="text-align:left">${escape(ledger.caption)}</caption><thead><tr><th scope="col" style="text-align:left;padding:.4rem .75rem .4rem 0">Allocation</th><th scope="col" style="text-align:right">Amount</th></tr></thead><tbody><tr><th scope="row" style="text-align:left;padding:.4rem .75rem .4rem 0">Dated starting cash</th><td style="white-space:nowrap;text-align:right">${money(ledger.opening)}</td></tr>${ledger.deductions.map(row => `<tr><th scope="row" style="text-align:left;padding:.4rem .75rem .4rem 0">${escape(row.label)}</th><td style="white-space:nowrap;text-align:right">−${money(row.amount)}</td></tr>`).join('')}<tr><th scope="row" style="text-align:left;padding:.4rem .75rem .4rem 0">Unallocated cash after protected reserve</th><td style="white-space:nowrap;text-align:right">${money(remaining)}</td></tr></tbody></table>`;
}

export function renderCoreGuide(slug) {
  const guide = guides[slug];
  if (!guide) return '';
  return `<section class="core-guide"><h2>${escape(guide.heading)}</h2>${paragraph(guide.intro)}${guide.sections.map(section => `<h3>${escape(section.heading)}</h3>${section.paragraphs.map(paragraph).join('')}${section.ledger ? renderLedger(section.ledger) : ''}${section.items ? `<ul>${section.items.map(item => `<li>${escape(item)}</li>`).join('')}</ul>` : ''}`).join('')}<h3>Source and scope</h3>${guide.sources.map(source => {
    if (!/^https:\/\//.test(source.url)) throw new Error('Core guide source must use HTTPS.');
    return `<p><a href="${escape(source.url)}">${escape(source.label)}</a>. ${escape(source.note)}</p>`;
  }).join('')}</section>`;
}
