import sys
from pathlib import Path

GENERATOR = Path(__file__).resolve().parents[1]
REPO = GENERATOR.parent
sys.path.insert(0, str(GENERATOR))
