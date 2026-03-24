#!/usr/bin/env python3
"""
Generate GitHub Wiki Home.md with a full TOC for mirrored docs under Documentation/.

Wiki URLs for nested files use percent-encoded paths (e.g. Documentation%2Fecosystem),
which matches how GitHub serves pages stored as Documentation/ecosystem.md in the wiki repo.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote


def title_from_markdown(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path.stem.replace("-", " ").title()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or path.stem.replace("-", " ").title()
    return path.stem.replace("-", " ").title()


def wiki_url(repo: str, rel_no_ext: str) -> str:
    # rel_no_ext uses forward slashes, e.g. Documentation/ecosystem or ecosystem under doc root
    path = rel_no_ext.replace("\\", "/").strip("/")
    encoded = quote(path, safe="")
    return f"https://github.com/{repo}/wiki/{encoded}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Write wiki Home.md with documentation index.")
    parser.add_argument(
        "--documentation-root",
        type=Path,
        required=True,
        help="Path to Documentation/ inside the wiki clone (mirrored docs/).",
    )
    parser.add_argument("--repo", required=True, help="owner/name, e.g. Fankouzu/Claw-Adventure")
    parser.add_argument("--ref-name", default="main", help="Branch name for source tree link")
    parser.add_argument("--sha-short", default="", help="Short commit SHA for footer")
    parser.add_argument("--output", type=Path, required=True, help="Path to write Home.md")
    args = parser.parse_args()

    root: Path = args.documentation_root
    if not root.is_dir():
        raise SystemExit(f"documentation root not found: {root}")

    md_files = sorted(root.rglob("*.md"))
    # Group by parent directory relative to root (posix string for display)
    groups: dict[str, list[Path]] = defaultdict(list)
    for f in md_files:
        rel = f.relative_to(root)
        parent = rel.parent.as_posix() if rel.parent != Path(".") else ""
        groups[parent].append(f)

    lines: list[str] = [
        "# Claw Adventure Wiki",
        "",
        f"This wiki mirrors [`docs/`](https://github.com/{args.repo}/tree/{args.ref_name}/docs) "
        "from the main repository.",
        "",
        "_Authoritative edits belong in the main repo; mirrored pages under `Documentation/` are "
        "updated by CI and may be overwritten._",
        "",
    ]
    if args.sha_short:
        lines.append(f"_Last sync: commit `{args.sha_short}`._")
        lines.append("")

    lines.extend(
        [
            "## Documentation index",
            "",
            "All pages below live under wiki path prefix `Documentation/` (mirrored from `docs/`).",
            "",
        ]
    )

    # Sort groups: root first, then alphabetically by folder path
    def group_key(p: str) -> tuple[int, str]:
        return (0 if p == "" else 1, p)

    for parent in sorted(groups.keys(), key=group_key):
        files = sorted(groups[parent], key=lambda p: p.as_posix().lower())
        if parent == "":
            lines.append("### Top level")
        else:
            lines.append(f"### `{parent}/`")
        lines.append("")
        for f in files:
            rel = f.relative_to(root)
            rel_no_ext = rel.with_suffix("").as_posix()
            wiki_rel = f"Documentation/{rel_no_ext}"
            url = wiki_url(args.repo, wiki_rel)
            title = title_from_markdown(f)
            lines.append(f"- [{title}]({url})")
        lines.append("")

    args.output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
