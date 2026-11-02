#!/usr/bin/env python3
"""Render index.html from data/curricula.json. No dependencies.

    python3 scripts/export-data.py   # refresh the data (optional)
    python3 build.py                 # write index.html
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

SITE = Path(__file__).resolve().parent
DATA = json.loads((SITE / "data" / "curricula.json").read_text(encoding="utf-8"))

# Stack widths (percent) shape the cross-section: a lens around the model.
STACK_WIDTH = {"ai-startup": 100, "ai-governance": 92, "ai-engineering": 80,
               "ml-engineering": 80, "ai-infra": 100}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def inline_md(text: str) -> str:
    """The few Markdown forms the profiles use: links, bold, italic."""
    out = esc(text)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|#[\w-]+)\)",
                 lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    return out


def overview(org: dict) -> str:
    """The org overview minus the repo-pairing sentence, which the hero and the
    'How the tracks work' section already explain once for the whole page."""
    return re.sub(r"\s*Every role track has a paired .*$", "", org["overview"]).strip()


def stack() -> str:
    rows = []
    orgs = DATA["orgs"]
    for i, org in enumerate(orgs):
        if org["position"] == "below" and orgs[i - 1]["position"] != "below":
            rows.append('<li class="stack__core" aria-hidden="true"><span>the model</span></li>')
        rows.append(
            f'<li class="stack__layer" style="--w:{STACK_WIDTH[org["key"]]}%;--i:{i}">'
            f'<a class="layer layer--{org["key"]}" href="#{org["key"]}">'
            f'<span class="layer__name">{esc(org["name"])}</span>'
            f'<span class="layer__verb">{esc(org["verb"])}</span></a></li>'
        )
    return '<ol class="stack" aria-label="The AI stack, by curriculum">' + "".join(rows) + "</ol>"


def role_row(org: dict, role: dict) -> str:
    links = (f'<a href="{role["learning"]}">Curriculum</a>' if role["solutions"] is None else
             f'<a href="{role["learning"]}">Learning</a><a href="{role["solutions"]}">Solutions</a>')
    mods = f'{role["modules"]} modules' if role["modules"] else ""
    level = "" if org["single_repo"] else f'<span class="role__level">L{role["level"]}</span>'
    return (
        '<li class="role">'
        f'<div class="role__head"><a class="role__title" href="{role["learning"]}">{esc(role["title"])}</a>'
        f'{level}</div>'
        f'<p class="role__focus">{esc(role["focus"])}</p>'
        f'<p class="role__meta"><span>{mods}</span><span class="role__links">{links}</span></p>'
        "</li>"
    )


def tracks(org: dict) -> str:
    groups: dict[str, list[dict]] = {}
    for role in org["roles"]:
        groups.setdefault(role["band"], []).append(role)
    parts = []
    for band, roles in groups.items():
        heading = f'<h3 class="band">{esc(band)}</h3>' if band else ""
        parts.append(heading + '<ul class="roles">' + "".join(role_row(org, r) for r in roles) + "</ul>")
    return "".join(parts)


def section(org: dict) -> str:
    start = next(r for r in org["roles"] if r["id"] == org["start"])
    n_tracks = len(org["roles"])
    n_mods = sum(r["modules"] for r in org["roles"])
    noun = "curricula" if org["single_repo"] else "role tracks"
    return (
        f'<section class="org org--{org["key"]}" id="{org["key"]}" aria-labelledby="{org["key"]}-h">'
        '<div class="org__intro">'
        f'<h2 id="{org["key"]}-h">{esc(org["name"])}</h2>'
        f'<p class="org__verb">{esc(org["verb"])}</p>'
        f'<p class="org__overview">{inline_md(overview(org))}</p>'
        f'<p class="org__count">{n_tracks} {noun} and {n_mods} modules.</p>'
        f'<p class="org__actions"><a class="start" href="{start["learning"]}">Start with {esc(start["title"])}</a>'
        f'<a class="org__all" href="{org["org_url"]}">See every repo on GitHub</a></p>'
        "</div>"
        f'<div class="org__tracks">{tracks(org)}</div>'
        "</section>"
    )


def page() -> str:
    n_tracks = sum(len(o["roles"]) for o in DATA["orgs"])
    n_mods = sum(r["modules"] for o in DATA["orgs"] for r in o["roles"])
    sections = "".join(section(o) for o in DATA["orgs"])
    template = (SITE / "templates" / "index.html").read_text(encoding="utf-8")
    return (template.replace("{{STACK}}", stack())
            .replace("{{SECTIONS}}", sections)
            .replace("{{TRACKS}}", str(n_tracks))
            .replace("{{MODULES}}", str(n_mods)))


if __name__ == "__main__":
    (SITE / "index.html").write_text(page(), encoding="utf-8")
    print("wrote index.html")
