"""Writes 21 November 2026's front page to /output/entry.png.

The program runs with no network and a read-only /bot, and is run twice with both runs required
to write the same bytes, so the image is drawn once and shipped in the repository: this copies
those exact bytes through. `draw.py` beside it is the source that produced entry.png; re-running
it reproduces the same file.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"), os.path.join(OUT_DIR, "entry.png"))
