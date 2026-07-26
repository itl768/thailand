#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GALLERIES = ROOT / "assets" / "images" / "galleries"
MANIFEST = ROOT / "assets" / "images" / "gallery-manifest.json"

IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def is_image_file(path: Path) -> bool:
    if path.name.lower() == "images.md":
        return False
    return path.suffix.lower() in IMAGE_EXT


SHOT_RE = re.compile(
    r"^\d+\.\s+\*\*(.+?)\*\*(?:\s*—\s*search:\s*`([^`]+)`)?\s*$",
    re.IGNORECASE,
)


def parse_images_md(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    shots: list[tuple[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = SHOT_RE.match(line.strip())
        if m:
            query = m.group(2).strip() if m.group(2) else ""
            shots.append((m.group(1).strip(), query))
    return shots


def humanize(name: str) -> str:
    stem = Path(name).stem.replace("-", " ").replace("_", " ")
    return stem[:1].upper() + stem[1:] if stem else "Photo"


def caption_for(index: int, filename: str, shots: list[tuple[str, str]]) -> str:
    if index < len(shots):
        title, _query = shots[index]
        return title
    return humanize(filename)


def collect_folder(key: str) -> list[dict[str, str]]:
    folder = GALLERIES / key
    if not folder.is_dir():
        return []
    shots = parse_images_md(folder / "IMAGES.md")
    files = sorted(p for p in folder.iterdir() if p.is_file() and is_image_file(p))
    items: list[dict[str, str]] = []
    for i, path in enumerate(files):
        rel = path.relative_to(ROOT).as_posix()
        items.append({"src": rel, "caption": caption_for(i, path.name, shots)})
    return items


def main() -> None:
    manifest: dict[str, list[dict[str, str]]] = {}
    if not GALLERIES.is_dir():
        GALLERIES.mkdir(parents=True, exist_ok=True)
    for folder in sorted(GALLERIES.iterdir()):
        if not folder.is_dir():
            continue
        key = folder.name
        items = collect_folder(key)
        manifest[key] = items
        print(f"{key}: {len(items)} image(s)")
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {MANIFEST}")


if __name__ == "__main__":
    main()
