# React SPA build output

Place the production build of the external React front-end here so the Evennia
web server can serve it under **`/app/`** (see `web/urls.py` and `web/views.py`).

## Expected layout

- `index.html` — required for `/app/` and client-side routes under `/app/**`
- JS/CSS bundles — typically `static/` or `assets/` next to `index.html`; adjust
  your bundler `homepage` or `publicPath` so asset URLs resolve under `/static/...`
  or `/app/...` as configured.

## Build steps (example)

From your React project:

```bash
npm run build
cp -r build/* /path/to/claw-adventure/web/static/app/
```

Or use a CI step to copy artifacts after `npm run build`.

## Note

Django’s `STATICFILES_DIRS` already includes `web/static/`. After adding files,
run `evennia collectstatic` in production if you deploy with collected static files.

If `index.html` is missing, `/app/` returns HTTP 404 with a short message.
