import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import ROOT
from app.ai.weights import compact_safetensors

if __name__ == "__main__":
    result = compact_safetensors(ROOT / "models/v1-5-pruned-emaonly.safetensors", ROOT / "models/sd15-compact.safetensors")
    print(json.dumps(result))
