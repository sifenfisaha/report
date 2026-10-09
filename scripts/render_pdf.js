#!/usr/bin/env node
// usage: render_pdf.js <in.html> <out.pdf> [footer text] [a4|letter]
//        render_pdf.js --check        (exit 0 when Playwright and a browser are usable)
// Renders an HTML file to PDF with Playwright: A4 by default, 18 mm side and
// 20 mm top/bottom margins, a running footer with the given text on the left
// and "Page X of Y" on the right. Playwright is looked up in the usual places
// (local node_modules, the global npm root, mise installs); set
// PLAYWRIGHT_MODULE to a path to override.
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execSync } = require('child_process');

function findPlaywright() {
  const candidates = [];
  if (process.env.PLAYWRIGHT_MODULE) candidates.push(process.env.PLAYWRIGHT_MODULE);
  candidates.push('playwright');
  try { candidates.push(path.join(execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(), 'playwright')); } catch (e) {}
  const mise = path.join(os.homedir(), '.local/share/mise/installs/npm-playwright');
  if (fs.existsSync(mise)) for (const v of fs.readdirSync(mise)) candidates.push(path.join(mise, v, 'node_modules/playwright'));
  for (const c of candidates) { try { return require(c); } catch (e) {} }
  throw new Error('playwright not found; npm i -g playwright && npx playwright install chromium, or set PLAYWRIGHT_MODULE');
}

async function launch(chromium) {
  try { return await chromium.launch(); } catch (e) {
    for (const exe of [process.env.CHROME_PATH, '/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].filter(Boolean)) {
      if (fs.existsSync(exe)) { try { return await chromium.launch({ executablePath: exe }); } catch (e2) {} }
    }
    throw e;
  }
}

(async () => {
  const { chromium } = findPlaywright();
  if (process.argv[2] === '--check') { const b = await launch(chromium); await b.close(); console.log('ok'); return; }
  const [input, output, footerText = '', paper = 'a4'] = process.argv.slice(2);
  if (!input || !output) { console.error('usage: render_pdf.js <in.html> <out.pdf> [footer text] [a4|letter]'); process.exit(2); }
  const browser = await launch(chromium);
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const footer = `<div style="width:100%;font-family:'Noto Sans','Liberation Sans',Arial,sans-serif;font-size:7.5pt;color:#5a5a5a;padding:0 18mm;display:flex;justify-content:space-between;"><span>${esc(footerText)}</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`;
  await page.pdf({ path: output, format: paper === 'letter' ? 'Letter' : 'A4', printBackground: true, displayHeaderFooter: true,
    headerTemplate: '<div></div>', footerTemplate: footer, margin: { top: '20mm', bottom: '20mm', left: '18mm', right: '18mm' } });
  await browser.close();
})().catch(e => { console.error(e.message || e); process.exit(1); });
