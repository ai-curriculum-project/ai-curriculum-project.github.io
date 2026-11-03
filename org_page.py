"""One org's own site: its stance toward the model, its tracks, and who it works with."""

from __future__ import annotations

from render import counts, esc, inline_md, number_word, org_links, overview, stack, tracks

UMBRELLA = "https://ai-curriculum-project.github.io/"


def _facts(n_tracks: int, n_mods: int, noun: str) -> str:
    if n_mods == 0:
        return f"{n_tracks} {noun}, new and being written now. Free and MIT-licensed."
    return f"{n_tracks} {noun} and {n_mods} modules, free and MIT-licensed."


def _hero(org: dict, orgs: list[dict]) -> str:
    n_tracks, n_mods, noun = counts(org)
    start = next(r for r in org["roles"] if r["id"] == org["start"])
    figure = stack(orgs, lambda o: o["pages_url"], current=org["key"])
    return (
        '<section class="hero" aria-labelledby="hero-h">'
        '<div class="hero__text">'
        f'<p class="eyebrow">One of {number_word(len(orgs)).lower()} curricula in the '
        f'<a href="{UMBRELLA}">AI Career Curriculum</a></p>'
        f'<h1 id="hero-h">{esc(org["name"])}</h1>'
        f'<p class="hero__sub">{inline_md(org["stance"]["headline"])}</p>'
        f'<p class="hero__facts">{_facts(n_tracks, n_mods, noun)}</p>'
        f'<p class="org__actions"><a class="start" href="{start["learning"]}">Start with {esc(start["title"])}</a>'
        f'<a class="org__all" href="{org["org_url"]}">Every repo on GitHub</a></p>'
        "</div>"
        f'<figure class="hero__figure">{figure}'
        f'<figcaption class="hero__caption">Where {esc(org["name"])} sits among the '
        f'{number_word(len(orgs)).lower()} curricula. Pick another layer to visit its site.</figcaption></figure>'
        "</section>"
    )


def _stance(org: dict) -> str:
    st = org["stance"]
    owns = "".join(f"<li>{inline_md(item)}</li>" for item in st["owns"])
    return (
        '<section class="panel stance" aria-labelledby="stance-h">'
        '<div class="panel__head"><h2 id="stance-h">Your relationship to the model</h2></div>'
        '<div class="stance__body">'
        f'<p class="stance__lead">{inline_md(st["stance"])}</p>'
        f'<p class="stance__overview">{inline_md(overview(org))}</p>'
        "</div>"
        '<div class="stance__owns">'
        f'<h3>What you own</h3><ul class="owns">{owns}</ul>'
        f'<p class="not-owns"><strong>What you don\'t own:</strong> {inline_md(st["not_owns"])}</p>'
        "</div>"
        "</section>"
    )


def _tracks(org: dict) -> str:
    return (
        '<section class="panel" id="tracks" aria-labelledby="tracks-h">'
        '<div class="panel__head"><h2 id="tracks-h">The tracks</h2>'
        '<p class="panel__note">Ordered by level. Each one opens with Module 00, which maps '
        "the role's place relative to the model before the technical work starts.</p></div>"
        f'<div class="org__tracks">{tracks(org)}</div>'
        "</section>"
    )


def _handoff_card(org: dict, sib: dict) -> str:
    gives = org["stance"]["hands_to"][sib["key"]]
    gets = sib["stance"]["hands_to"][org["key"]]
    return (
        f'<li class="handoff theme--{sib["key"]}">'
        f'<h3><a href="{sib["pages_url"]}">{esc(sib["name"])}</a></h3>'
        f'<p class="handoff__verb">{esc(sib["verb"])}</p>'
        f'<dl><dt>You hand them</dt><dd>{inline_md(gives)}</dd>'
        f'<dt>They hand you</dt><dd>{inline_md(gets)}</dd></dl>'
        "</li>"
    )


def _handoffs(org: dict, orgs: list[dict]) -> str:
    cards = "".join(_handoff_card(org, s) for s in orgs if s["key"] != org["key"])
    return (
        '<section class="panel" aria-labelledby="handoffs-h">'
        '<div class="panel__head"><h2 id="handoffs-h">Who you work with</h2>'
        '<p class="panel__note">No curriculum owns the model end to end. These are the '
        "handoffs with each of the others.</p></div>"
        f'<ul class="handoffs">{cards}</ul>'
        "</section>"
    )


def _technologies(org: dict) -> str:
    tech = org.get("technologies") or {}
    if not tech:
        return ""
    rows = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in tech.items())
    return (
        '<section class="panel" aria-labelledby="tech-h">'
        '<div class="panel__head"><h2 id="tech-h">What you\'ll work with</h2></div>'
        f'<dl class="tech">{rows}</dl>'
        "</section>"
    )


def _how(org: dict) -> str:
    if org["single_repo"]:
        check = ("Each curriculum includes worked exemplars: completed founder artifacts to "
                 "compare your own against.")
    else:
        check = ("The paired solutions repo has a reference walkthrough for every exercise. "
                 "Attempt each one first; the gap between your answer and the reference is "
                 "where the learning happens.")
    return (
        '<section class="how" aria-labelledby="how-h"><h2 id="how-h">How the tracks work</h2>'
        '<div class="how__grid">'
        "<div><h3>Learn</h3><p>Each track is a sequence of modules: lecture chapters, hands-on "
        "exercises, quizzes, and projects. Start with Module 00 and work forward.</p></div>"
        f"<div><h3>Check your work</h3><p>{check}</p></div>"
        "<div><h3>Built in the open</h3><p>The content is written with AI assistance and under "
        "ongoing human review, so it can contain mistakes. Report anything wrong through the "
        "repo's Issues; fixes ship continuously.</p></div>"
        "</div></section>"
    )


def render_org_page(org: dict, orgs: list[dict], template: str) -> str:
    body = (_hero(org, orgs) + _stance(org) + _tracks(org) + _handoffs(org, orgs)
            + _technologies(org) + _how(org))
    return (template
            .replace("{{KEY}}", org["key"])
            .replace("{{NAME}}", esc(org["name"]))
            .replace("{{DESCRIPTION}}", esc(org["tagline"]))
            .replace("{{URL}}", org["pages_url"])
            .replace("{{GITHUB}}", org["org_url"])
            .replace("{{UMBRELLA}}", UMBRELLA)
            .replace("{{BODY}}", body)
            .replace("{{ORG_LINKS}}", org_links(orgs, lambda o: o["pages_url"])))
