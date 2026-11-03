"""Shared HTML pieces for the umbrella page and the per-org pages. No dependencies."""

from __future__ import annotations

import html
import re

# Stack widths (percent) shape the cross-section: a lens around the model.
STACK_WIDTH = {"ai-workforce": 100, "ai-startup": 96, "ai-governance": 90,
               "ai-engineering": 80, "ml-engineering": 80, "ai-infra": 100}


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def inline_md(text: str) -> str:
    """The few Markdown forms the profiles and stances use: links, bold, italic."""
    out = esc(text)
    out = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|#[\w-]+)\)",
                 lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", out)
    return out


def overview(org: dict) -> str:
    """The org overview minus the repo-pairing sentence, which each page explains once."""
    return re.sub(r"\s*Every role track has a paired .*$", "", org["overview"]).strip()


def counts(org: dict) -> tuple[int, int, str]:
    noun = "curricula" if org["single_repo"] else "role tracks"
    return len(org["roles"]), sum(r["modules"] for r in org["roles"]), noun


def stack(orgs: list[dict], href, current: str | None = None) -> str:
    """The cross-section of orgs around the model. ``href(org)`` gives each layer's link."""
    rows = []
    for i, org in enumerate(orgs):
        if org["position"] == "below" and orgs[i - 1]["position"] != "below":
            rows.append('<li class="stack__core" aria-hidden="true"><span>the model</span></li>')
        here = org["key"] == current
        aria = ' aria-current="page"' if here else ""
        cls = " layer--here" if here else ""
        rows.append(
            f'<li class="stack__layer" style="--w:{STACK_WIDTH[org["key"]]}%;--i:{i}">'
            f'<a class="layer layer--{org["key"]}{cls}" href="{href(org)}"{aria}>'
            f'<span class="layer__name">{esc(org["name"])}</span>'
            f'<span class="layer__verb">{esc(org["verb"])}</span></a></li>'
        )
    return '<ol class="stack" aria-label="The AI stack, by curriculum">' + "".join(rows) + "</ol>"


def role_row(org: dict, role: dict) -> str:
    links = (f'<a href="{role["learning"]}">Curriculum</a>' if role["solutions"] is None else
             f'<a href="{role["learning"]}">Learning</a><a href="{role["solutions"]}">Solutions</a>')
    mods = f'{role["modules"]} modules' if role["modules"] else "In progress"
    level = "" if org["single_repo"] else f'<span class="role__level">L{role["level"]}</span>'
    return (
        '<li class="role">'
        f'<div class="role__head"><a class="role__title" href="{role["learning"]}">{esc(role["title"])}</a>'
        f'{level}</div>'
        f'<p class="role__focus">{esc(role["focus"])}</p>'
        f'<p class="role__meta"><span>{mods}</span><span class="role__links">{links}</span></p>'
        "</li>"
    )


def tracks(org: dict, heading_tag: str = "h3") -> str:
    groups: dict[str, list[dict]] = {}
    for role in org["roles"]:
        groups.setdefault(role["band"], []).append(role)
    parts = []
    for band, roles in groups.items():
        heading = f'<{heading_tag} class="band">{esc(band)}</{heading_tag}>' if band else ""
        parts.append(heading + '<ul class="roles">' + "".join(role_row(org, r) for r in roles) + "</ul>")
    return "".join(parts)


def org_links(orgs: list[dict], href) -> str:
    items = "".join(f'<li><a href="{href(o)}">{esc(o["name"])}</a></li>' for o in orgs)
    return f'<ul class="foot__orgs" aria-label="The {len(orgs)} curriculum organizations">{items}</ul>'


NUMBER_WORDS = {3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight"}


def number_word(n: int) -> str:
    return NUMBER_WORDS.get(n, str(n))
