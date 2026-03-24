#!/usr/bin/env python3
"""
Mirror docs/**/*.md into a GitHub Wiki clone using flat page names GitHub can resolve.

GitHub Wiki web URLs do not reliably map to nested paths like Documentation/foo.md in the
wiki Git repo. Pages are addressed as a single slug; nested directories in the wiki repo
often correspond to slugs built by joining path segments with hyphens.

This script:
  1. Removes legacy Documentation/ subtree and prior flat Documentation-*.md pages from the wiki.
  2. Copies each docs/**/*.md to <wiki>/Documentation-<relpath-with-slashes-as-hyphens>.md
  3. Writes Home.md with markdown links to https://github.com/{repo}/wiki/{slug} (slug = stem).

Only .md files are mirrored (no .sql / .jsonl). Exclude paths under dirs that only hold jsonl.
"""

from __future__ import annotations

import argparse
import shutil
from collections import defaultdict
from pathlib import Path


def wiki_stem_from_docs_rel(rel: Path) -> str:
    """Stem for wiki filename and URL slug, e.g. docs/ecosystem.md -> Documentation-ecosystem."""
    rel_no_ext = rel.with_suffix("").as_posix()
    return "Documentation-" + rel_no_ext.replace("/", "-")


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


def clean_wiki_mirror_targets(wiki_root: Path) -> None:
    legacy = wiki_root / "Documentation"
    if legacy.is_dir():
        shutil.rmtree(legacy)
    for p in wiki_root.glob("Documentation-*.md"):
        p.unlink()


def sync_markdown(docs_root: Path, wiki_root: Path) -> list[tuple[Path, str]]:
    """
    Copy markdown files; return list of (source_path, wiki_stem) for the index.
    """
    copied: list[tuple[Path, str]] = []
    for src in sorted(docs_root.rglob("*.md")):
        rel = src.relative_to(docs_root)
        stem = wiki_stem_from_docs_rel(rel)
        dest = wiki_root / f"{stem}.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        copied.append((src, stem))
    return copied


def write_home(
    repo: str,
    ref_name: str,
    sha_short: str,
    docs_root: Path,
    entries: list[tuple[Path, str]],
    output: Path,
) -> None:
    """entries: (source_path_under_docs, wiki_stem)."""
    groups: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for src, stem in entries:
        try:
            parent_rel = src.parent.relative_to(docs_root)
        except ValueError:
            parent_rel = Path(".")
        key = "" if parent_rel == Path(".") else parent_rel.as_posix()
        groups[key].append((src, stem))

    lines: list[str] = [
        "# Claw Adventure Wiki",
        "",
        f"This wiki mirrors [`docs/`](https://github.com/{repo}/tree/{ref_name}/docs) "
        "from the main repository.",
        "",
        "Pages use flat names (`Documentation-…`) so links open the rendered wiki page instead of "
        "the “create new page” flow.",
        "",
        "_Authoritative edits belong in the main repo; mirrored pages are updated by CI and may be overwritten._",
        "",
    ]
    if sha_short:
        lines.append(f"_Last sync: commit `{sha_short}`._")
        lines.append("")

    lines.extend(
        [
            "## Documentation index",
            "",
        ]
    )

    def group_key(p: str) -> tuple[int, str]:
        return (0 if p == "" else 1, p)

    for parent in sorted(groups.keys(), key=group_key):
        items = sorted(groups[parent], key=lambda x: x[0].as_posix().lower())
        if parent == "":
            lines.append("### Top level (`docs/` root)")
        else:
            lines.append(f"### `{parent}/`")
        lines.append("")
        for src, stem in items:
            url = f"https://github.com/{repo}/wiki/{stem}"
            title = title_from_markdown(src)
            lines.append(f"- [{title}]({url})")
        lines.append("")

    output.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mirror docs markdown into wiki flat pages + Home.md")
    parser.add_argument("--docs-root", type=Path, required=True)
    parser.add_argument("--wiki-root", type=Path, required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--ref-name", default="main")
    parser.add_argument("--sha-short", default="")
    args = parser.parse_args()

    docs_root = args.docs_root.resolve()
    wiki_root = args.wiki_root.resolve()
    if not docs_root.is_dir():
        raise SystemExit(f"docs root not found: {docs_root}")
    if not wiki_root.is_dir():
        raise SystemExit(f"wiki root not found: {wiki_root}")

    clean_wiki_mirror_targets(wiki_root)
    entries = sync_markdown(docs_root, wiki_root)
    write_home(
        args.repo,
        args.ref_name,
        args.sha_short,
        docs_root,
        entries,
        wiki_root / "Home.md",
    )


if __name__ == "__main__":
    main()
