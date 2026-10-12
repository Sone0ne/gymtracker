from pathlib import Path

BASE_DIR = Path(__file__).parent
FLAG_FILE = BASE_DIR / "training_active.flag"

def is_training_active():
    return FLAG_FILE.exists()

def set_training_active(active: bool):
    if active:
        FLAG_FILE.touch()
    else:
        if FLAG_FILE.exists():
            FLAG_FILE.unlink()
