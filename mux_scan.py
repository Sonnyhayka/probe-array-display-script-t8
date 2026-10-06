"""Launcher for the standalone ADG726 MUX scanner (implementation lives in ``src/``)."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from mux_scan import main

if __name__ == "__main__":
    raise SystemExit(main())
