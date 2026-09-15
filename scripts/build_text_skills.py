"""Sync text standards; package all three skills and the complete project kit."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "skills" / "lexprism"
REVIEWER = ROOT / "skills" / "lexprism-review"
DRAWING = ROOT / "skills" / "drawio-diagram"
PROJECT_SKILLS = (GENERATOR, REVIEWER, DRAWING)
# The legacy diagrams reference stays with the existing generator tree unchanged;
# the text reviewer does not invoke its independent drawing workflow.
EXCLUDED_SHARED = {"diagrams.md"}


def shared_references() -> list[Path]:
    return sorted(p for p in (GENERATOR / "references").glob("*.md")
                  if p.name not in EXCLUDED_SHARED)


def check_local_links(folder: Path) -> None:
    """Ensure each skill's Markdown references resolve inside its own package."""
    for document in folder.rglob("*.md"):
        content = document.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]\n]*\]\(([^)]+)\)", content):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                continue
            target = (document.parent / link.split("#", 1)[0]).resolve()
            if not target.is_relative_to(folder.resolve()) or not target.is_file():
                raise ValueError(f"Unresolved package reference: {document}: {link}")


def build(check_only: bool) -> None:
    for source in shared_references():
        target = REVIEWER / "references" / source.name
        if check_only:
            if not target.exists() or target.read_bytes() != source.read_bytes():
                raise ValueError(f"Shared reference out of sync: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

    for folder in PROJECT_SKILLS:
        check_local_links(folder)
        if check_only:
            continue
        content = (folder / "SKILL.md").read_text(encoding="utf-8")
        match = re.search(r"^  version: ([a-zA-Z0-9.-]+)$", content, re.MULTILINE)
        if not match:
            raise ValueError(f"Missing version: {folder}")
        output = ROOT / "dist" / f"{folder.name}-{match.group(1)}.zip"
        output.parent.mkdir(parents=True, exist_ok=True)
        files = [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))]
        with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, path.relative_to(folder.parent).as_posix())
        with ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError(f"Corrupt archive: {output}")
            expected = {p.relative_to(folder.parent).as_posix(): p.read_bytes() for p in files}
            if set(archive.namelist()) != set(expected):
                raise ValueError(f"Unexpected archive content: {output}")
            for name, data in expected.items():
                if archive.read(name) != data:
                    raise ValueError(f"Archive mismatch: {name}")
        print(f"Built {output.name}: {len(files)} files, {output.stat().st_size} bytes")
    print("Shared text references and package links are valid.")
    if not check_only:
        build_project_kit()


def build_project_kit() -> None:
    """Bundle the runtime separately from independently importable skill ZIPs."""
    version = "0.5.1-project-bundle"
    files = {
        "README.md": ROOT / "docs" / "项目协作操作说明.md",
        "scripts/document_workflow.py": ROOT / "scripts" / "document_workflow.py",
        "scripts/generate_diagram.py": ROOT / "scripts" / "generate_diagram.py",
        "scripts/verify_diagram.py": ROOT / "scripts" / "verify_diagram.py",
        "evals/templates/diagram_plan.template.json": ROOT / "evals" / "templates" / "diagram_plan.template.json",
        "THIRD_PARTY_NOTICES.md": ROOT / "THIRD_PARTY_NOTICES.md",
    }
    for folder in PROJECT_SKILLS:
        for path in [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))]:
            files[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / "templates" / "legal-project").glob("*.md"):
        files[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / "tools" / "drawio").rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".html", ".drawio"}:
            files[path.relative_to(ROOT).as_posix()] = path
    expected_skills = {f"skills/{folder.name}/SKILL.md" for folder in PROJECT_SKILLS}
    included_skills = {name for name in files if name.startswith("skills/") and name.endswith("/SKILL.md")}
    if included_skills != expected_skills or len(included_skills) != 3:
        raise ValueError("Project kit must contain generator, reviewer and drawing skills")
    output = ROOT / "dist" / f"lexprism-project-{version}.zip"
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, path in sorted(files.items()):
            archive.write(path, f"lexprism-project/{name}")
    with ZipFile(output) as archive:
        if archive.testzip() is not None or len(archive.namelist()) != len(files):
            raise ValueError("Project kit integrity check failed")
        for name, path in files.items():
            if archive.read(f"lexprism-project/{name}") != path.read_bytes():
                raise ValueError(f"Project kit mismatch: {name}")
    print(f"Built {output.name}: {len(files)} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing files")
    build(parser.parse_args().check)
