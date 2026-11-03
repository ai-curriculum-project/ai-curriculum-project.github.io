# ai-curriculum-project.github.io

The landing page for the **AI Career Curriculum**: six free, open-source curricula,
organized by what you do relative to a model (AI Workforce, AI Startup, AI Governance,
AI Engineering, ML Engineering, AI Infrastructure). Served at <https://ai-curriculum-project.github.io/>.

This repo also builds **each org's own site** (`https://<org>.github.io/`): that org's
relationship to the model, what it owns, its tracks by level, and its handoffs with the
other five.

## How it's built

Plain HTML and CSS, no framework, no JavaScript. The HTML is generated; don't edit it by hand.

- `data/curricula.json` holds every org and role: names, levels, focus lines, repo links,
  module counts, and each org's stance (from the content generator's `config/stances.json`).
- `templates/index.html` (umbrella) and `templates/org.html` (per-org) are the page shells.
- `render.py` has the shared pieces; `build.py` writes the umbrella page; `org_page.py` writes an org page.
- `styles.css` is hand-written and shared by every site; each org has one color token,
  applied with a `theme--<org>` class.

```bash
python3 scripts/export-data.py      # refresh data from ../ai-infra-content-generator + GitHub (needs `gh`)
python3 build.py                    # write index.html and dist/<org>/
python3 -m http.server 8000         # preview: / and /dist/<org>/
scripts/publish-org-sites.sh        # push dist/<org>/ to each <org>.github.io (DRY_RUN=1 to preview)
```

Role names, levels, and repos come from the content generator's manifests; focus lines,
level groupings, and taglines from its org profiles (`config/profiles/<domain>.json`);
stances and handoffs from `config/stances.json`. Change them there, then re-export,
rebuild, and publish.

The publish script refuses to write into a repo whose name only redirects (this repo used
to be `ai-infra-curriculum/ai-infra-curriculum.github.io`), so it can't overwrite the umbrella.

GitHub Pages serves the `main` branch root. The repo must stay public.
