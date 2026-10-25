# User interface

There are two ways to give the app a UI, and you can use either, both or neither.

## Built-in pages (optional)

`example_web` is a small server-rendered UI: Django templates with [HTMX](https://htmx.org/) for partial page updates. It needs no Node, no build step and no separate deployment. HTMX is vendored in `example_web/static/example_web/htmx.min.js`, so pages work offline and under a strict Content-Security-Policy.

It shows a landing page, sign-in and sign-out (the built-in Django views), and a notes list where signed-in users add and delete notes without reloading the page. Turn it off with `EXAMPLE_UI_ENABLED=false`, or delete the `example_web` app.

To build your own pages, add views and templates to `example_web`, or create another app. Keep views thin: validate input, call `example_package` or the ORM, render a template.

Pages get a same-origin Content-Security-Policy. If you add inline scripts or load assets from a CDN, change `UI_CSP` in `example_core/middleware.py` deliberately.

## A separate frontend (React, Vue, Svelte, Node tooling)

Keep it in **its own repository**, so this repo stays Python-only and each side releases on its own schedule. The two meet at the API.

1. **Contract:** generate a typed client from [openapi.json](openapi.json), for example with `openapi-typescript`. Re-generate when the contract changes. The `api-compat` workflow here warns when a change would break the client.
2. **Origins:** list the frontend origin in `EXAMPLE_CORS_ORIGINS`. Add `EXAMPLE_CSRF_TRUSTED_ORIGINS` if it submits forms to Django.
3. **Authentication:** choose one of the following.
   - Same site, session cookies: serve the frontend and the API from one domain behind a proxy (`/` for the frontend, `/api/` for Django). Cookies and CSRF just work, and no CORS is needed. This is the simplest and most secure setup.
   - Different sites, tokens: use `jwt` mode with tokens from your identity provider, and `EXAMPLE_CORS_ORIGINS` for the frontend. Keep tokens out of local storage where you can.
4. **Deployment:** build the frontend to static files and serve them from the proxy or a CDN. Django does not need to serve them.

Turn the built-in UI off (`EXAMPLE_UI_ENABLED=false`) when a separate frontend replaces it.
