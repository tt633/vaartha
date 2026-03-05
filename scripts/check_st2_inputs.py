"""
Audit ST2 raw inputs before running the ingestion notebook.

This script does not parse the full `.xls` payload; it validates presence,
extracts embedded UTF-16 strings to confirm the workbook schema, and flags
format blockers that will prevent preprocessing.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from config import ST2_RAW

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def extract_utf16_strings(path: Path) -> list[str]:
    """Extract readable UTF-16LE ASCII strings embedded in a binary workbook."""
    raw = path.read_bytes()
    matches = re.findall(rb"(?:[\x20-\x7E]\x00){3,}", raw)
    values = [m.decode("utf-16le", errors="ignore").strip() for m in matches]

    seen = set()
    ordered = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def main() -> int:
    gpr_candidates = [
        ST2_RAW / "data_gpr_export.xlsx",
        ST2_RAW / "data_gpr_export.xls",
    ]
    gscpi_candidates = [
        ST2_RAW / "gscpi.csv",
        ST2_RAW / "gscpi.xlsx",
        ST2_RAW / "gscpi_data.xls",
        Path.home() / "Downloads" / "gscpi_data.xls",
    ]

    gpr_path = next((p for p in gpr_candidates if p.exists()), None)
    gscpi_path = next((p for p in gscpi_candidates if p.exists()), None)

    if gpr_path is None:
        log.error("Missing GPR file. Expected one of: %s", ", ".join(p.name for p in gpr_candidates))
    else:
        log.info("Found GPR file: %s", gpr_path)
        if gpr_path.suffix.lower() == ".xls":
            log.warning(
                "GPR file is legacy .xls. This environment cannot parse it directly without xlrd. "
                "Convert it to data_gpr_export.xlsx before running notebook 02."
            )

        strings = extract_utf16_strings(gpr_path)
        required_headers = {"month", "GPR", "GPRT", "GPRA"}
        detected = {value for value in strings if value in required_headers}
        if detected == required_headers:
            log.info("GPR schema check passed. Core headers detected: %s", ", ".join(sorted(detected)))
        else:
            log.error("GPR schema check incomplete. Detected only: %s", ", ".join(sorted(detected)))

        country_cols = [value for value in strings if value.startswith("GPRC_")]
        if country_cols:
            log.info("Detected %s country-level GPR columns in workbook metadata.", len(country_cols))

    if gscpi_path is None:
        log.error("Missing GSCPI file. Expected one of: %s", ", ".join(p.name for p in gscpi_candidates))
    else:
        log.info("Found GSCPI file: %s", gscpi_path)
        if gscpi_path.suffix.lower() == ".xls":
            log.warning(
                "GSCPI file is legacy .xls. If notebook ingestion fails, convert it to "
                "gscpi.xlsx or gscpi.csv in data/raw/ST2 before running notebook 02."
            )

    if gpr_path is not None and gpr_path.suffix.lower() == ".xlsx" and gscpi_path is not None:
        log.info("ST2 raw inputs are structurally ready for notebook ingestion.")
        return 0

    log.warning("ST2 raw inputs are not fully ready for preprocessing yet.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
