"""Pytest bootstrap for the whitebox MoneyPoly test suite."""

from pathlib import Path
import sys


WHITEBOX_CODE_ROOT = Path(__file__).resolve().parents[1] / "code" / "moneypoly"

if str(WHITEBOX_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(WHITEBOX_CODE_ROOT))
