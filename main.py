#!/usr/bin/env python3
"""news-image-20261121 v6 entrypoint (stdlib only).

Copies the pre-rendered front page (entry.png, drawn by build_image.py)
into MAKEFUN_OUTPUT_DIR. No network, no randomness, deterministic bytes.
"""
import os
import shutil
import sys


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out:
        print("MAKEFUN_OUTPUT_DIR is not set", file=sys.stderr)
        return 1
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    os.makedirs(out, exist_ok=True)
    shutil.copyfile(src, os.path.join(out, "entry.png"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
