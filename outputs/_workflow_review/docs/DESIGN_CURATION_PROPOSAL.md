# CAPAS / KRENIQ — Design Curation Proposal

> **PROPOSAL ONLY — nothing here is applied.** A human picks what ships. This document
> synthesizes six independent scale-reviews into one ranked plan. Generated 2026-06-24.

## Statement of intent

This is **curation, not a re-theme.** The job is to hang the accepted collection better —
not to repaint it. The brand identity is **fixed and out of scope**: the pink `--pink:#e8185d`,
the near-black `--bg:#050507` dark aesthetic, the floating 3D background logo, the 60px sticky
nav, the canonical layout tokens (`--col:1200px` / `--gutter:48px` / `--nav-h:60px` /
`--radius:14px`), and the Inter heavy-display voice. Not one of the moves below changes a hue,
the dark look, the shell structure, the logo, or the nav. Every move either (a) restores a
single-source-of-truth the canon already promised, (b) snaps a drifting value back onto a number
the canon already uses, or (c) closes a genuine a11y gap using the existing pink. The test each
move had to pass: *"could a curator justify this as hanging the accepted image more cleanly?"*
If not, it was dropped. Every proposal here is marked `preserves_canon: true`; none that failed
that test survived.

The document spirals from **general → particular**: design-system canon → page-level vertical
rhythm → section composition → components → type/color micro → front-to-back (a11y/render). A
recurring theme surfaced independently in all six reviews and is treated as the spine of the
plan: **the shell exists to make inconsistency "structurally impossible," but 6 of 9 pages froze
a hand-copied paste of it instead of linking it, and several canon hooks (`.section.alt`,
`:focus-visible`) were authored in markup but never defined in CSS.** Curation here is largely
*re-connecting the collection to the rails the author already nailed into the wall.*

---

## Layer 1 — Design system / canon (most general): `docs/kreniq-shell.css`

**What's working, keep it:** the brand value tokens (`--pink`, `--pink2`, `--bg`, `--accent`/
`--green`/`--amber`) and the four load-bearing layout tokens are correct and disciplined; the
shell *internally* consumes its own `var(--col)`/`var(--gutter)`/`var(--nav-h)`/`var(--radius)`
correctly. The hover transitions (.15s–.2s, right properties) are consistent. The rot is not in
the shell — it's in the pages that re-inline a drifting copy of it.

| # | Move | Where | Why it elevates | Effort | Preserves canon |
|---|------|-------|-----------------|--------|-----------------|
| 1.1 | **Re-point the 6 inlined pages at `kreniq-shell.css`; delete the duplicated chrome rules, keep only page-specific blocks** | `index.html` (+ `app/audit/benchmark/security/pilot-packet/customer-brief.html`) `<head>`; source stays `kreniq-shell.css` | The shell's whole premise — "1200-vs-1400 / box-in-box becomes structurally impossible" — is fiction for 6/9 pages today; they froze a copy. Re-linking restores the single source so any future curation lands on all pages at once. The inline copies hardcode the *same values* (1200/48/60/14), so this is a verified no-pixel-change refactor. | moderate | **yes** — same values, restores the guarantee |
| 1.2 | **Add a small named vertical-spacing scale to `:root` using the EXISTING values** (e.g. `--space-4:16px … --space-section:96px`) and reference it in `.section`/`.hero`/`.core-card`/`.section-sub` | `kreniq-shell.css` `:root` + shell rules | Vertical spacing is as load-bearing to the calm "no box-in-box" feel as `--col`/`--gutter`, yet it's the one axis left as magic numbers. Naming what's already there makes off-scale values (56 next to a 48/64 token) visible — no new measurement invented. | moderate | **yes** — names existing values only |
| 1.3 | **Tokenize the recurring accent-tint rgba's** (`--green-bg`/`--green-line`, `--accent-bg`, `--pink-line`, `--amber-bg` …) at their existing alphas | `kreniq-shell.css` `:root` + card/badge usages | The four hues are fixed and correct; what's loose is that their soft fills are re-mixed by hand at 0.1 vs 0.12 vs 0.15 for the same role. One definition per tint keeps the four-color family crisp. | moderate | **yes** — tints of existing hues, no new color |

*Degradation risks avoided:* silent token drift (someone bumps a gutter on one frozen copy and
the "identical shell" promise breaks invisibly); spacing entropy (a new section lands at 90px/
50px, one px off-rhythm); accent-alpha drift (the green "success" fill at three opacities).

---

## Layer 2 — Page layout & vertical rhythm: `docs/index.html` section cadence

**What's working, keep it:** the hero block (min-height `calc(100vh - nav)`, 1fr/460px split, 80px
gap, clamp(36–58) h1) is the strongest-paced moment — leave it. The full-bleed banded device
(`.stat-bar`/`.pipeline` — tinted band + hairline against open `.section`) is the page's main
rhythm tool; keep the device, only its consistency needs work. The eyebrow→h2→sub three-beat unit
is a clean canonical opener.

| # | Move | Where | Why it elevates | Effort | Preserves canon |
|---|------|-------|-----------------|--------|-----------------|
| 2.1 | **Define the missing `.section.alt` rule** — `background:rgba(255,255,255,0.015);border-top/bottom:1px solid rgba(255,255,255,0.06)` (values lifted verbatim from `.pipeline`) | `kreniq-shell.css` after `.section`; HTML already tags `index.html:565,600,617` | **Verified: 3 sections request `class="section alt"` but NO `.section.alt` rule exists** — the modifier is dead markup, so those sections render identical to plain `.section`. The author already encoded an ABAB rhythm; activating it restores the rest-stops the eye needs across ~16 stacked sections, using a surface value already canon in `.pipeline`. | trivial | **yes** — reuses `.pipeline`'s own values |
| 2.2 | **Unify section vertical padding to the dominant 96px** — snap `.pipeline-inner` (80px) and `.cta-section` (100px) to `96px 48px`; leave the hero's bespoke 80/60 | `index.html` `.pipeline-inner`, `.cta-section` | 96px is already every `.section`; collapsing the two outliers onto it removes the micro-jolts between a banded block and its neighbors. Snapping to an existing value, not inventing an 8pt system. | trivial | **yes** — matches existing 96px |
| 2.3 | **Collapse the double-hairline where two banded blocks meet** — `.section.alt + .section.alt, .pipeline + .section.alt {border-top:none}` | adjacent to the new 2.1 rule | Once 2.1 activates `.alt`, two adjacent bands' hairlines read as a thick double-rule and their paddings stack into an oversized void. Sharing one divider is the standard move that makes banding read as deliberate alternation, not accidental seams. Removes only a redundant duplicate hairline. | small | **yes** — never removes the band or canonical single divider |
| 2.4 | **Standardize the sub→content gap** — make every `.section-sub` that precedes a self-spacing grid (`margin-top:48px`) use the same rule; pick one baseline so content always drops from the same height | `index.html` `margin-bottom:0` overrides at 296/360 vs the 56px subs at 326/401/417 | The header-to-content interval is the most-repeated spacing event (~14×); it currently wobbles 48 vs 56 for no visible reason, degrading the scannability of the repeating label/h2/sub/content unit. | small | **yes** — consolidates onto existing values |
| 2.5 | **Give the trailing disclaimer list an exhale before the footer** — raise `.home-disclaimers` top padding to a clear interval and/or add the footer's `border-top` hairline | `index.html` `.home-disclaimers`, between `.cta-section` and `<footer>` | The page's one genuinely crowded spot: 8px above the legal bullets right under the CTA. A defined gap demotes fine-print to its correct quieter tier instead of reading as a run-on of the marketing block. | trivial | **yes** — whitespace + at most the footer's existing 0.06 hairline |

*Degradation risks avoided:* the dead-token trap (markup promising alternation CSS never
delivers → a 16-section monotone wall); inventing a third arbitrary padding number; a heavy
double-line seam; the legal text fighting the CTA for attention.

---

## Layer 3 — Section composition & hierarchy

**What's working, keep it:** the canonical eyebrow→h2→sub ladder (pink 11px label → 900-weight
clamp h2 → .5-opacity sub) is the document's spine across all sections and reads cleanly — do not
alter its tokens. The pink eyebrow as the sole "new section starts here" signal is consistent and
correct. The 900-weight h2 as the single loudest element per section, with everything else
deliberately quieter, already guides the eye top-down. The 2×2/4-up grids (core/verdicts/pipeline)
have clean internal hierarchy.

| # | Move | Where | Why it elevates | Effort | Preserves canon |
|---|------|-------|-----------------|--------|-----------------|
| 3.1 | *(Same hook as 2.1 — counted once)* Activating `.section.alt` also groups the evidence/moat/governance cluster | `index.html:565,600,617` | The composition-level payoff of 2.1: the IBM-proof / moat / governance arc stops reading as one undifferentiated block. | trivial | **yes** |
| 3.2 | **Demote the trailing "honest-scope" footnotes to a true sub-tier** — give the caveats one shared aside treatment (muted color + the hero caveat's `border-left:2px solid rgba(255,255,255,.12);padding-left:12px`) | `index.html` section-sub footnote variants at 427/462/537/562/596 | Today the lead sub and the closing caveat read at near-equal weight, so the eye can't tell "this is the claim" from "this is the disclaimer." A consistent aside (idiom already set by the hero caveat) creates a clean eyebrow / headline+lead / quiet-caveat three-tier and makes the honesty discipline scannable. | small | **yes** — reuses the existing hero-caveat idiom |
| 3.3 | **Unify the one disclaimer that uses `opacity:.7` instead of the explicit muted color** — drop `opacity:.7`, use the siblings' `font-size:13px;color:rgba(255,255,255,.5)` | `index.html:585` | Same semantic element styled two ways: `opacity` also dims its own `<strong>`/`<em>` and resolves to a different lightness than its four siblings — exactly the one-off drift the single-source shell exists to prevent. | trivial | **yes** — matches sibling treatment |

*Degradation risks avoided:* hierarchy flattening (lead sentence and trailing caveat shouting at
identical volume); one-off styling drift on a repeated semantic element.

---

## Layer 4 — Components (nav, cards, buttons, tables, chips)

**What's working, keep it:** the shared card DNA (`rgba(255,255,255,0.03)` fill + ~0.07 border +
`backdrop-filter:blur(8px)`) is the correct family signature. The btn-primary/btn-secondary/nav-cta
button system is internally consistent and on-canon. The `.vs-table` (pink-tinted CAPAS row,
green/muted/amber semantic cells, uppercase 10px headers) is a finished, legible component. The
`.stat-bar` 4-up grid with right-dividers and pink unit accent is clean — do not touch.

| # | Move | Where | Why it elevates | Effort | Preserves canon |
|---|------|-------|-----------------|--------|-----------------|
| 4.1 | **Unify the card-family radius on `--radius` (14px)** — `.verdict-card`/`.case-card`/`.vs-table` use 12px while `.core-card` uses 14px; bind all to `var(--radius)` (currently referenced 0× in index.html) | `index.html` `.core-card`/`.verdict-card`/`.case-card`/`.vs-table`; token in `kreniq-shell.css` | A consistent corner radius is what makes a set of boxes read as one system rather than several. Aligning all siblings to the one token tightens the image and makes `--radius` actually load-bearing. | trivial | **yes** — adopts the canonical token |
| 4.2 | **Promote the IBM "evidence strip" from inline styles to card-family tokens** — the flagship proof boxes use hand-set `border-radius:12px`, `padding:20px`, `font-size:34px` numbers (vs canonical `.stat-num` 32px); re-express with the radius token, the standard 0.07 border, and 32px numerals, keeping the green-tinted box as a sanctioned semantic variant | `index.html` IBM metric row + proof boxes (~570–594); refs `.stat-num`, `.core-card` | The page's most important section is currently its largest one-off — off-by-2px numerals and ad-hoc radii where inconsistency most undermines the "rigorous system" impression. Folding it into existing tokens makes the proof read as first-class CAPAS components. | moderate | **yes** — uses existing tokens, keeps the semantic green |
| 4.3 | **Make card hover one language — drop the `.verdict-card` translateY one-off** — replace `transform:translateY(-3px)` with the calmer border-color brighten `.core-card`/`.case-card` use | `index.html` `.verdict-card:hover` vs `.core-card`/`.case-card:hover` | When two cards glow and one jumps, the interaction reads inconsistent. Converging on the quiet border-brighten keeps the family speaking one language and suits the restrained dark aesthetic. | trivial | **yes** — converges on the existing hover idiom |
| 4.4 | **Align `.case-card:hover` to also restore background like `.core-card`** — add the same `background:rgba(255,255,255,0.05)` lift | `index.html` `.case-card:hover` | These two cards share fill/border/blur — same component, different content — so their hover should match exactly. | trivial | **yes** — mirrors the twin card |
| 4.5 | **Give `.fam-chip` the hover/`:focus-visible` the rest of the interactive set has** — quiet border/text brighten + the shell focus ring (Layer 6) | `index.html` `.fam-chip`; mirror `.nav-links a:hover` | The chips are the only repeated interactive element giving no feedback, and the only one with no keyboard-focus state. A restrained brighten matches the established hover idiom without changing the resting look. | trivial | **yes** — reuses the nav hover idiom |

*Degradation risks avoided:* two-radius incoherence (adjacent cards almost-but-not-quite the same
family → reads as templated); the flagship section silently diverging from the component language;
a jarring single-card bounce; a barely-perceptible hover asymmetry between pixel-sibling cards.

---

## Layer 5 — Typography & color micro (particular)

**What's working, keep it:** the pink discipline (a true accent — eyebrows, REJECT state, inline
links, one hero stat figure; never body copy, never a large fill) and its `#e8185d`/`#a855f7`
gradient pairing. The two display clamps (hero-h1 `clamp(36,4.5vw,58)`, section-h2
`clamp(28,3vw,42)`) are the ramp's anchors. The heavy-900 + `-0.03em` Inter voice. The four-tier
opacity *intent* (.88/.6/.5/.44) and `line-height:1.65` body / 1.1 display. The concept is correct;
only enforcement drifts.

| # | Move | Where | Why it elevates | Effort | Preserves canon |
|---|------|-------|-----------------|--------|-----------------|
| 5.1 | **Strip the 19 redundant inline `section-h2` overrides** (verified byte-for-byte identical to the `.section-h2` CSS rule) + the hero h1 variant | `index.html` every `<h2 class="section-h2" style=…>` | **Verified: 19 headings re-state the exact CSS rule inline**, so the type scale lives in 20 places. To ever refine heading rhythm you'd edit 20 attributes and hope none drift. Stripping them makes `.section-h2` the sole authority. Zero visual change — pure rigor. | small | **yes** — no visual change, restores single source |
| 5.2 | **Collapse mid-band text opacities to the canonical .6/.5/.44 tiers** — `index.html` smears the secondary/tertiary band across .4/.44/.45/.48/.5/.55/.6/.62/.65; snap secondary→.6, tertiary→.5, most-muted→.44 | `index.html` `.pipe-step-desc`/`.verdict-card p`/`.differ-row p`/`.case-card p`/`.fam-chip`/`.vs-table td` + inline captions | A four-step value ladder is what makes a dark page read as deliberate; 9 indistinct steps flatten it so the eye can't tell secondary from tertiary. Snapping to .6/.5/.44 sharpens the legibility hierarchy the canon already specifies. No new colors. | small | **yes** — consolidates onto canon values |
| 5.3 | **Route the four text tiers through `--text`/`--muted` (+ `--text-2`/`--text-3`) tokens** instead of ~46 hand-typed rgba literals | `index.html` `:root` + text rules; mirror `kreniq-shell.css` | `index.html` uses `var(--text)` once and `var(--muted)` zero times — the canon tiers exist as tokens but are bypassed. Tokenizing makes the 5.2 drift structurally hard to reintroduce. | moderate | **yes** — binds to existing tokens |
| 5.4 | **Unify the page-title H1 across the 7 nav pages to the shell's `clamp(36,4.5vw,58)`** — sibling pages introduce competing `clamp(38,5vw,64)` and `clamp(32,4vw,48)` for the identical page-hero slot | `audit/benchmark/security/pilot-packet/customer-brief.html` H1; align to `.hero-h1` | A ramp is only a ramp if the same role is the same size everywhere; three max-sizes for one slot makes the pages feel authored by different hands. Anchoring to 58 hangs the collection at a consistent height. | small | **yes** — adopts the shell anchor |
| 5.5 | **Fix eyebrow/label tracking to a single 0.12em** (index ships both 0.12em and 0.1em for the same component) and normalize `-.03em`/`-0.03em` spelling splits | `index.html` eyebrow/label rules; canon `.hero-eyebrow`/`.section-label` | Uppercase micro-labels are read paired with their heading; inconsistent tracking on identical components is a small but visible tell. | trivial | **yes** — matches the canon value |
| 5.6 | **Tokenize the inline-link pink to a single spelling** — ~27 raw `#e8185d`/`232,24,93` literals vs 4 `var(--pink)`; route through `var(--pink)` with no change to where/how often pink appears | `index.html` inline link styles + rgba badge/state backgrounds | One spelling means the accent can never drift and is provably the same hue everywhere — reinforcing the single-accent discipline. A consistency move, not a color change. | small | **yes** — same hue, one source |

*Degradation risks avoided:* type-scale fork (one h2 tweaked, two now differ); the .88/.6/.5/.44
ladder muddying into a featureless smear; per-section grey invention dropping below legibility on
`#050507`; cross-page ramp incoherence reading as an unmaintained templated site; micro-label
death-by-a-thousand-cuts; the accent fragmenting into several almost-identical reds.

---

## Layer 6 — Front-to-back: a11y, render, responsive

**What's working, keep it:** the floating 3D bg-logo iframe (already `tabindex=-1` + `aria-hidden`)
and its veil; the `@media(max-width:760px)` shell breakpoint (nav wrap, core-grid→1fr, hero→single
column — axe reports `horizontalOverflow=false` everywhere); the canonical nav order/links (fixed
per CLAUDE.md); the existing hover transitions.

| # | Move | Where | Why it elevates | Effort | Preserves canon |
|---|------|-------|-----------------|--------|-----------------|
| 6.1 | **Add one canonical `:focus-visible` ring to the shell in the brand pink** — `a,button,.nav-cta,.btn-primary,.btn-secondary:focus-visible{outline:2px solid var(--pink);outline-offset:2px}` + `:focus:not(:focus-visible){outline:none}` | `kreniq-shell.css` near nav/button rules; inherited by all 7 shell pages | **Verified: zero focus styles anywhere.** Keyboard users fall back to a UA ring nearly invisible on `#050507`. A crisp pink ring (keyboard-only via `:focus-visible`, mouse unaffected) makes traversal legible and reads as intentional brand polish — the antithesis-fix for a tool that sells deterministic auditability. The shell tokenized hover but forgot focus. | trivial | **yes** — uses existing `--pink`, keyboard-only |
| 6.2 | **Honor `prefers-reduced-motion` on the animated 3D logo** — `@media(prefers-reduced-motion:reduce){.bg-logo iframe{display:none}.bg-logo{background:radial-gradient(circle at 60% 35%,rgba(232,24,93,0.06),transparent 70%)}}` | `kreniq-shell.css` `.bg-logo` block | **Verified: no reduced-motion guard anywhere.** Motion-sensitive users get a still pink wash instead of a continuously rotating iframe; also drops the iframe's repaint cost for them. Default view is unchanged for everyone else. | trivial | **yes** — default look untouched |
| 6.3 | **Underline inline body links** (color-alone fails WCAG 1.4.1) — scope to prose only: `.section-inner p a,.hero-sub a{text-decoration:underline;text-decoration-color:rgba(232,24,93,0.5);text-underline-offset:2px}`; leave nav/footer/button/chip links | `kreniq-shell.css` scoped rule | axe flags `link-in-text-block` (serious) on 6 shell pages. A subtle pink-tinted underline keeps the brand cue and adds the required non-color signal; *not* underlining the chrome avoids clutter. | trivial | **yes** — keeps pink, scoped to prose |
| 6.4 | **Give the mobile `.nav-links` scroll-strip an accessible name** — `aria-label="Primary"` so the overflow-x scroller announces itself | `<nav> .nav-links` in the shell pages | axe reports `scrollable-region-focusable` (serious) on every mobile render: the horizontally-scrolling link bar is a tab stop with no name. One attribute resolves it without touching the visual nav or its link order. | small | **yes** — content/order unchanged |
| 6.5 | **Add a visually-hidden skip-to-content link** — first focusable element, `href="#main"`, hidden until focused, reusing the 6.1 focus styling | shell pages body top + `.skip-link` in `kreniq-shell.css` | Every page opens with the same ~10-item sticky nav; a skip link (keyboard-only, invisible to mouse/visual users) spares keyboard users tabbing the whole nav on every page. Zero visual impact on the default image. | small | **yes** — invisible unless focused |
| 6.6 | **Stabilize hero web-font load** — move the Inter `<link>` ahead of the inline `<style>` and add a metric-matched fallback (`@font-face 'Inter Fallback'` with `size-adjust`/`ascent-override`); keep `display=swap` | `index.html` head | The hero h1 (weight 900, up to 58px) is the LCP candidate; with the font link loading late + swap, Inter arrives after first paint and reflows the headline (FOUT/CLS). A size-adjusted fallback makes the swap near-imperceptible — same typeface, weight, and size. | moderate | **yes** — typeface/scale unchanged |

*Degradation risks avoided:* an invisible focus state on an auditability product (WCAG 2.4.7);
vestibular discomfort + needless GPU/battery churn; a real serious-level color-only-link finding;
an unlabelled keyboard scroll-trap on mobile; forcing keyboard users through the full nav every
page (2.4.1); the felt "cheapness" of the headline snapping into place on load.

---

## TOP 5 to do first — highest leverage, lowest risk

Ranked for maximum payoff at minimal effort/risk. Four of five are **trivial** and three are
**verified dead/missing today** (pure activation, not change):

1. **2.1 / 3.1 — Define the missing `.section.alt` rule** (trivial). *Verified:* 3 sections request
   it, no CSS delivers it. Reuses `.pipeline`'s own surface values. Instantly restores the ABAB
   banding the author already authored — the single biggest rhythm gain on the page for one rule.

2. **6.1 — One canonical `:focus-visible` pink ring in the shell** (trivial). *Verified:* zero
   focus styles exist anywhere. Keyboard-only, uses `--pink`, lands on all 7 shell pages at once.
   Closes the most embarrassing gap for a product that sells auditability.

3. **5.1 — Strip the 19 redundant inline `section-h2` overrides** (small). *Verified:* byte-for-byte
   identical to the CSS rule. Zero visual change; restores `.section-h2` as the single source so the
   type scale can never silently fork.

4. **2.2 — Snap section padding to the dominant 96px** (trivial). Two outliers (80/100) onto a value
   already used by every `.section`; removes the micro-jolts without inventing any new spacing.

5. **4.1 — Unify the card-family radius on `--radius` (14px)** (trivial). Three siblings at 12px →
   the one canonical token; makes the boxes read as one system and makes `--radius` load-bearing.

> **The one thing to NEVER touch:** the brand identity — the pink `--pink:#e8185d`, the near-black
> `--bg:#050507` dark aesthetic, the floating background logo, the 60px sticky nav, and the
> `--col:1200px` / `--gutter:48px` / `--nav-h:60px` / `--radius:14px` tokens with Inter type. Every
> move above hangs this accepted image more cleanly; none repaints it. The deeper structural rule:
> **the shell is the single source of truth — re-connect pages to it, never fork it.**

---

### Sequencing note
Do **1.1 (re-link the 6 inlined pages)** before the shell-level moves (1.2, 1.3, 2.1, 2.3, 6.1–6.5)
ship widely — otherwise a shell-only change reaches just 3 of 9 pages. The five quick wins above are
all safe to apply directly to `index.html` today and to back-port into the shell once 1.1 lands.
All proposals with `preserves_canon: false` were dropped (there were none — the reviews were
disciplined; the synthesis confirms each survivor is curation-of-the-accepted-image).
