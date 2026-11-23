#!/usr/bin/env python3
"""Entry point for the news-image-20261123 make.fun entry.

The front page itself is drawn by render.py (Pillow) at build time and
stored in this repository as entry.png. This program's one job is to
write that image to the output directory, byte for byte, so the two
grading runs produce identical output. Standard library only.
"""

import os
import shutil
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def output_dir():
    """Where the harness wants the entry image: $MAKEFUN_OUTPUT_DIR or /output."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    if not os.path.isfile(src):
        print(f"error: {src} is missing", file=sys.stderr)
        return 1
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    dst = os.path.join(out, "entry.png")
    shutil.copyfile(src, dst)
    # Verify the copy landed whole: same size, and a real PNG header.
    with open(dst, "rb") as fh:
        head = fh.read(len(PNG_SIGNATURE))
    if head != PNG_SIGNATURE or os.path.getsize(dst) != os.path.getsize(src):
        print(f"error: {dst} failed verification after copy", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({os.path.getsize(dst)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
