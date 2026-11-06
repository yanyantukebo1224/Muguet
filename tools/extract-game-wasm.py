#!/usr/bin/env python3
"""Extract only b/<build>/game.wasm from a Muguet-compatible game ZIP."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path


PATTERN = re.compile(r"(?:^|/)b/[^/]+/game\.wasm$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Original game-data ZIP")
    parser.add_argument("output", type=Path, help="Destination game.wasm path")
    args = parser.parse_args()

    if not args.archive.is_file():
        parser.error(f"archive does not exist: {args.archive}")

    try:
        with zipfile.ZipFile(args.archive) as archive:
            matches = [entry for entry in archive.infolist() if not entry.is_dir() and PATTERN.search(entry.filename.replace("\\", "/"))]
            if len(matches) != 1:
                raise ValueError(f"expected exactly one b/<build>/game.wasm entry; found {len(matches)}")
            entry = matches[0]
            args.output.parent.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256()
            written = 0
            with archive.open(entry, "r") as source, args.output.open("wb") as target:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)
                    digest.update(chunk)
                    written += len(chunk)
            with args.output.open("rb") as result:
                magic = result.read(4)
            if magic != b"\x00asm":
                args.output.unlink(missing_ok=True)
                raise ValueError("extracted file does not have the WebAssembly magic header")
    except (OSError, zipfile.BadZipFile, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"source entry: {entry.filename}")
    print(f"output: {args.output}")
    print(f"size: {written} bytes")
    print(f"sha256: {digest.hexdigest()}")
    print("The original ZIP was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
