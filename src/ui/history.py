import json
from datetime import datetime
from pathlib import Path

from config import settings
from src.winget.models import WingetPackage

_LOG_PATH = Path(settings.BASE_DIR) / "history.json"
_MAX_ENTRIES = 500


class ActionHistory:
    """Historique des actions install/upgrade/uninstall en JSON."""

    def __init__(self, path: Path = _LOG_PATH):
        self._path = path
        self._entries: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self._entries = json.loads(self._path.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._entries, ensure_ascii=False, indent=2),
                              encoding="utf-8")

    def log(self, action: str, package: WingetPackage, success: bool,
            error: str = "") -> None:
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "package_id": package.id,
            "package_name": package.name,
            "version": package.version,
            "success": success,
        }
        if error and not success:
            entry["error"] = error[:500]
        self._entries.append(entry)
        if len(self._entries) > _MAX_ENTRIES:
            self._entries = self._entries[-_MAX_ENTRIES:]
        self._save()

    @property
    def entries(self) -> list[dict]:
        return list(self._entries)
