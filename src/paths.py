"""Project directory layout (repository root is the parent of ``src/``)."""

from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_DIR = PROJECT_ROOT / "Data"
SHOT_DATA_DIR = DATA_DIR / "SHOT_DATA"
DATA_LOGS_DIR = DATA_DIR / "DATA_LOGS"
MULTI_ANALYSIS_DIR = DATA_DIR / "MULTI_ANALYSIS"
EXCEL_SHOT_LOG = DATA_DIR / "supRISEshots.xlsx"
