#!/usr/bin/env python3
"""Export curriculum data for the landing page into ``data/curricula.json``.

Reads role names, levels, and repos from the content generator's manifests and
the editorial text (focus lines, bands, taglines) from its org profiles, then
counts each learning repo's modules on GitHub. Run it whenever roles change,
then run ``build.py``.

    python3 scripts/export-data.py      # needs ../ai-infra-content-generator and `gh`
    python3 build.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
GEN = SITE.parent / "ai-infra-content-generator"

# Stack order, top to bottom, with each org's position relative to the model.
ORGS = [
    ("ai-startup", "AI Startup", "Turn it into a company", "outer"),
    ("ai-governance", "AI Governance", "Govern, secure, and assure AI", "outer"),
    ("ai-engineering", "AI Engineering", "Build with the models", "above"),
    ("ml-engineering", "ML Engineering", "Build and train the models", "below"),
    ("ai-infra", "AI Infrastructure", "Run the platforms models live on", "below"),
]


def manifest_path(key: str) -> Path:
    return GEN / "config" / ("aicg-org.yaml" if key == "ai-infra" else f"domains/{key}.yaml")


def module_count(org: str, repo: str) -> int:
    out = subprocess.run(
        ["gh", "api", f"repos/{org}/{repo}/git/trees/main?recursive=1"],
        capture_output=True, text=True, check=False,
    )
    if out.returncode != 0:
        print(f"warning: could not read {org}/{repo}", file=sys.stderr)
        return 0
    paths = [t["path"] for t in json.loads(out.stdout)["tree"]]
    mods = {p.split("/")[1] for p in paths
            if re.match(r"^(lessons|modules)/mod-[^/]+/", p)}
    return len(mods)


def band_for(role: dict, bands: list[dict] | None) -> str:
    for band in bands or []:
        hit = role["id"] in band["roles"] if "roles" in band else (
            band["min_level"] <= role["level"] <= band["max_level"])
        if hit:
            return re.sub(r"^\W+\s*", "", band["title"]).strip()
    return ""


def export_org(key: str, name: str, verb: str, position: str) -> dict:
    manifest = json.loads(manifest_path(key).read_text())
    profile = json.loads((GEN / "config" / "profiles" / f"{key}.json").read_text())
    org = manifest["org"].lower()
    roles = []
    for r in sorted(manifest["roles"], key=lambda x: (x["level"], x["title"])):
        sol = r.get("solution_repo")
        roles.append({
            "id": r["id"], "title": r["title"], "level": r["level"],
            "focus": profile["focus"][r["id"]], "band": band_for(r, profile.get("bands")),
            "learning": f"https://github.com/{org}/{r['learning_repo']}",
            "solutions": f"https://github.com/{org}/{sol}" if sol else None,
            "modules": module_count(org, r["learning_repo"]),
        })
    start = next(r for r in roles if r["id"] == profile["quick_start_role"])
    return {
        "key": key, "name": name, "verb": verb, "position": position,
        "org_url": f"https://github.com/{org}", "tagline": profile["tagline"],
        "overview": profile["overview"], "start": start["id"],
        "single_repo": all(r["solutions"] is None for r in roles), "roles": roles,
    }


def main() -> int:
    data = {"orgs": [export_org(*o) for o in ORGS]}
    out = SITE / "data" / "curricula.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tracks = sum(len(o["roles"]) for o in data["orgs"])
    mods = sum(r["modules"] for o in data["orgs"] for r in o["roles"])
    print(f"wrote {out}: {len(data['orgs'])} orgs, {tracks} tracks, {mods} modules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
