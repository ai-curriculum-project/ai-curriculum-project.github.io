# ai-infra-curriculum.github.io

The landing page for the **AI Career Curriculum**: five free, open-source curricula
covering every layer of the AI stack (AI Infrastructure, ML Engineering, AI Engineering,
AI Governance, AI Startup). Served at <https://ai-infra-curriculum.github.io/>.

## How it's built

Plain HTML and CSS, no framework, no JavaScript. `index.html` is generated, so
don't edit it by hand:

- `data/curricula.json` holds every org and role: names, levels, focus lines,
  repo links, and module counts.
- `templates/index.html` is the page shell; `build.py` fills it in.
- `styles.css` is hand-written; each org has one color token used everywhere it appears.

```bash
python3 scripts/export-data.py   # refresh data from ../ai-infra-content-generator + GitHub (needs `gh`)
python3 build.py                 # write index.html
python3 -m http.server 8000      # preview at http://localhost:8000/
```

Role names, levels, and repos come from the content generator's manifests; focus
lines, career-level groupings, and taglines come from its org profiles
(`config/profiles/<domain>.json`). Change them there, then re-export and rebuild.

GitHub Pages serves the `main` branch root. The repo must stay public.
