#!/usr/bin/env python3
"""Render the umbrella page and one site per org from data/curricula.json. No dependencies.

    python3 scripts/export-data.py      # refresh the data (optional)
    python3 build.py                    # write index.html and dist/<org>/
    scripts/publish-org-sites.sh        # push dist/<org>/ to each <org>.github.io repo
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from org_page import render_org_page
from render import counts, esc, inline_md, number_word, org_links, overview, stack, tracks

SITE = Path(__file__).resolve().parent
DATA = json.loads((SITE / "data" / "curricula.json").read_text(encoding="utf-8"))
DIST = SITE / "dist"
SHARED_ASSETS = ("styles.css", "favicon.svg")


def section(org: dict) -> str:
    start = next(r for r in org["roles"] if r["id"] == org["start"])
    n_tracks, n_mods, noun = counts(org)
    count_text = (f"{n_tracks} {noun} and {n_mods} modules." if n_mods
                  else f"{n_tracks} {noun}, new and being written now.")
    return (
        f'<section class="org theme--{org["key"]}" id="{org["key"]}" aria-labelledby="{org["key"]}-h">'
        '<div class="org__intro">'
        f'<h2 id="{org["key"]}-h">{esc(org["name"])}</h2>'
        f'<p class="org__verb">{esc(org["verb"])}</p>'
        f'<p class="org__overview">{inline_md(overview(org))}</p>'
        f'<p class="org__count">{count_text}</p>'
        f'<p class="org__actions"><a class="start" href="{start["learning"]}">Start with {esc(start["title"])}</a>'
        f'<a class="org__all" href="{org["pages_url"]}">Visit the {esc(org["name"])} site</a></p>'
        "</div>"
        f'<div class="org__tracks">{tracks(org)}</div>'
        "</section>"
    )


def umbrella() -> str:
    orgs = DATA["orgs"]
    n_tracks = sum(len(o["roles"]) for o in orgs)
    n_mods = sum(r["modules"] for o in orgs for r in o["roles"])
    template = (SITE / "templates" / "index.html").read_text(encoding="utf-8")
    return (template.replace("{{STACK}}", stack(orgs, lambda o: f'#{o["key"]}'))
            .replace("{{SECTIONS}}", "".join(section(o) for o in orgs))
            .replace("{{ORG_LINKS}}", org_links(orgs, lambda o: o["pages_url"]))
            .replace("{{COUNT_WORD}}", number_word(len(orgs)))
            .replace("{{COUNT_LOWER}}", number_word(len(orgs)).lower())
            .replace("{{TRACKS}}", str(n_tracks))
            .replace("{{MODULES}}", str(n_mods)))


def org_sites() -> list[Path]:
    template = (SITE / "templates" / "org.html").read_text(encoding="utf-8")
    shutil.rmtree(DIST, ignore_errors=True)
    written = []
    for org in DATA["orgs"]:
        out = DIST / org["key"]
        out.mkdir(parents=True)
        (out / "index.html").write_text(render_org_page(org, DATA["orgs"], template), encoding="utf-8")
        for asset in SHARED_ASSETS:
            shutil.copy(SITE / asset, out / asset)
        legacy = SITE / "legacy" / org["key"]
        if legacy.is_dir():  # redirect pages for old URLs that now land on this org's site
            shutil.copytree(legacy, out, dirs_exist_ok=True)
        written.append(out)
    return written


if __name__ == "__main__":
    (SITE / "index.html").write_text(umbrella(), encoding="utf-8")
    print("wrote index.html")
    for path in org_sites():
        print(f"wrote {path.relative_to(SITE)}/")
