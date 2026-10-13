const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const rows = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
  const b = await chromium.launch(); const page = await b.newPage();
  await page.goto('file://' + process.argv[2] + '/docs/app.html', { waitUntil: 'load' });
  const res = await page.evaluate((rows) => rows.map(r => { try { return rule(r.payload).verdict; } catch (e) { return 'ERR'; } }), rows);
  let same = 0; const diff = {};
  rows.forEach((r, i) => { if (res[i] === r.py) same++; else { const k = r.py + '→' + res[i]; diff[k] = (diff[k] || 0) + 1; } });
  console.log(JSON.stringify({ n: rows.length, same, mismatch: rows.length - same, by_kind: diff }));
  await b.close();
})();
