# Upstream GitHub Actions Warning Policy

Status: explicit project position.

CAPAS currently treats the GitHub Pages Node runtime warning as an upstream
platform warning, not as a CAPAS product defect.

## What the warning means

GitHub Pages deployment currently emits warnings such as:

- `Node.js 20 is deprecated`
- `actions/upload-artifact ... target Node.js 20 but are being forced to run on Node.js 24`
- Node deprecation warnings for internal dependencies such as `punycode` or
  `url.parse()`

These warnings are emitted by GitHub-maintained Actions used under the Pages
deployment path. CAPAS does not ship Node runtime code in the browser product
and does not depend on Node for the deterministic claim gate.

## What we will do

We will:

1. keep first-party workflow actions on current supported major versions,
2. monitor CI and Pages status on every push,
3. treat successful CI and Pages deployment as release-green when the only
   remaining warning is the upstream Node runtime notice,
4. upgrade GitHub-maintained Actions when GitHub publishes a replacement that
   removes the warning.

## What we will not do

We will not set:

```text
ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true
```

That variable would intentionally keep an insecure/deprecated runtime path alive
only to silence a warning. CAPAS will prefer a noisy but supported runtime over
a quiet but deprecated runtime.

## When this becomes a CAPAS issue

This becomes a CAPAS release blocker only if one of the following occurs:

1. CI fails,
2. Pages deployment fails,
3. the public static demo is not updated,
4. a CAPAS-maintained action or script directly targets a deprecated runtime,
5. the warning changes into a GitHub deprecation deadline that requires a
   workflow migration.

Until then, the warning is logged as upstream operational noise.
