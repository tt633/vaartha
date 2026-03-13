#!/usr/bin/env python3
"""Generate the analysis plots without running the notebooks."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
MPLCONFIGDIR = ROOT / ".mplconfig"
MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from analysis_plots import generate_all_phase2_charts  # noqa: E402


def main() -> int:
    results = generate_all_phase2_charts()
    for result in results:
        print(f"{result.path}: {result.status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
