"""Download the FOM modules pinned in fom/SOURCE.json and check their sha256."""

from __future__ import annotations

import hashlib
import urllib.parse
import urllib.request
from pathlib import Path

from .model import GeneratorError
from .parse import module_key

RAW_BASE = "https://raw.githubusercontent.com"


def raw_url(source: dict, name: str) -> str:
    repo = urllib.parse.urlparse(source["repository"]).path.strip("/")
    return f"{RAW_BASE}/{repo}/{source['commit']}/{source['path']}/{name}"


def fetch(source: dict, dest: Path) -> list[Path]:
    # Names become paths under dest: check them all before anything is written.
    for entry in source["files"]:
        module_key(entry["name"])
    dest.mkdir(parents=True, exist_ok=True)
    paths = []
    for entry in source["files"]:
        url = raw_url(source, entry["name"])
        with urllib.request.urlopen(url, timeout=60) as resp:
            data = resp.read()
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"]:
            raise GeneratorError(f"{url}: sha256 {digest} does not match {entry['sha256']}")
        path = dest / entry["name"]
        path.write_bytes(data)
        paths.append(path)
    return paths
