// UI-lab render worker — Playwright (global install; run with NODE_PATH="$(npm root -g)").
// Given a config {base, viewports, pages[{label,path,column}]} and the vendored axe.min.js, for each
// page x viewport it: navigates the LOCAL server, full-page screenshots, extracts layout geometry
// (content column rect, nav signature, nav-logo gutter, horizontal overflow), collects console errors,
// and runs axe-core. axe is injected via addInitScript (CDP) so the strict CSP on app.html can't block it.
// Output: a single JSON report on the path passed as argv[4]. Pure measurement — assertions live in ui_lab.py.
import fs from 'fs';
import { createRequire } from 'node:module';
// ESM `import` does not honor NODE_PATH (only CommonJS require does), so resolve the GLOBAL playwright
// by absolute path off NODE_PATH (set by ui_lab.py to `npm root -g`).
const require = createRequire(import.meta.url);
const gRoot = (process.env.NODE_PATH || '').split(':')[0];
const { chromium } = require(gRoot ? `${gRoot}/playwright` : 'playwright');

const cfgPath = process.argv[2];
const axePath = process.argv[3];
const reportPath = process.argv[4];
const outDir = process.argv[5];

const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const axeSrc = fs.readFileSync(axePath, 'utf8');

const browser = await chromium.launch();
const report = { base: cfg.base, pages: [] };

for (const page of cfg.pages) {
  for (const vp of cfg.viewports) {
    const ctx = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
      deviceScaleFactor: 1,
    });
    // CDP-injected init script runs in the main world before page scripts and is NOT subject to the
    // page CSP — this is how axe loads even on the CSP-locked Gate App.
    await ctx.addInitScript({ content: axeSrc });
    const p = await ctx.newPage();
    const consoleErrors = [];
    p.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text().slice(0, 240)); });
    p.on('pageerror', (e) => consoleErrors.push('pageerror: ' + String(e).slice(0, 240)));

    let navOk = true, errText = null;
    try {
      await p.goto(cfg.base + page.path, { waitUntil: 'networkidle', timeout: 30000 });
      await p.waitForTimeout(450);
    } catch (e) { navOk = false; errText = String(e).slice(0, 200); }

    const shot = `${outDir}/${page.label}__${vp.name}.png`;
    try { await p.screenshot({ path: shot, fullPage: true }); } catch (e) { /* keep going */ }

    const geo = await p.evaluate((sel) => {
      const vw = window.innerWidth;
      const navLinks = [...document.querySelectorAll('nav .nav-links a')].map((a) => a.textContent.trim());
      const navLogo = document.querySelector('.nav-logo');
      const navLogoLeft = navLogo ? Math.round(navLogo.getBoundingClientRect().left) : null;
      let column = null;
      const el = document.querySelector(sel);
      if (el) {
        const r = el.getBoundingClientRect();
        column = {
          left: Math.round(r.left),
          right: Math.round(vw - r.right),
          width: Math.round(r.width),
          centered: Math.abs(r.left - (vw - r.right)) < 24,
        };
      }
      const overflow = document.documentElement.scrollWidth > vw + 2;
      return { vw, navLinks, navLogoLeft, column, horizontalOverflow: overflow, scrollWidth: document.documentElement.scrollWidth };
    }, page.column || 'body');

    let axeViolations = [];
    try {
      axeViolations = await p.evaluate(async () => {
        if (!window.axe) return [{ id: '__axe_not_loaded__', impact: 'serious', nodes: 0 }];
        const r = await window.axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] } });
        return r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length,
          sample: (v.nodes[0] && v.nodes[0].target && v.nodes[0].target.join(' ')) || '' }));
      });
    } catch (e) { axeViolations = [{ id: '__axe_error__', impact: 'serious', nodes: 0, sample: String(e).slice(0, 120) }]; }

    report.pages.push({
      label: page.label, viewport: vp.name, path: page.path, shot,
      navOk, navError: errText, ...geo, consoleErrors, axe: axeViolations,
    });
    await ctx.close();
  }
}

await browser.close();
fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
console.log(`rendered ${report.pages.length} page×viewport combos -> ${reportPath}`);
