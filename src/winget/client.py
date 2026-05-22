import subprocess
import sys
from typing import Optional

from src.winget.bootstrap import ensure_sources, ensure_winget
from src.winget.compatibility import check_compatibility
from src.winget.models import WingetPackage
from src.winget.parser import parse_search_output

# Empêche toute fenêtre console (cmd / conhost) d'apparaître pour les enfants.
# CREATE_NO_WINDOW seul peut être contourné par certains hôtes ; on combine
# donc avec STARTUPINFO + SW_HIDE pour blinder le cas Windows.
_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
if sys.platform == "win32":
    _STARTUPINFO = subprocess.STARTUPINFO()
    _STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _STARTUPINFO.wShowWindow = subprocess.SW_HIDE
else:
    _STARTUPINFO = None


def _run(args, **kwargs):
    """subprocess.run avec masquage systématique de la console enfant."""
    kwargs.setdefault("creationflags", _NO_WINDOW)
    kwargs.setdefault("startupinfo", _STARTUPINFO)
    return subprocess.run(args, **kwargs)


class Winget:
    """Façade haut-niveau sur le CLI `winget`."""

    def __init__(self, auto_bootstrap: bool = False):
        if not check_compatibility():
            raise RuntimeError("Système non supporté (Windows 10/11 requis).")
        if auto_bootstrap:
            ensure_winget()
        ensure_sources()

    # ---------------------------------------------------------------- search
    def search(self, query: str) -> list[WingetPackage]:
        try:
            result = _run(
                ["winget", "search", "--query", query,
                 "--accept-source-agreements", "--disable-interactivity"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
        return parse_search_output(result.stdout)

    # ------------------------------------------------------------- installed
    def list_installed(self) -> list[WingetPackage]:
        try:
            result = _run(
                ["winget", "list", "--accept-source-agreements",
                 "--disable-interactivity"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
        return parse_search_output(result.stdout)

    def installed_ids(self) -> set[str]:
        return {p.id for p in self.list_installed()}

    # --------------------------------------------------------------- install
    def install(self, package_id: str, version: Optional[str] = None) -> tuple[int, str]:
        args = [
            "winget", "install", "--id", package_id, "--exact",
            "--accept-package-agreements", "--accept-source-agreements",
            "--disable-interactivity",
        ]
        if version:
            args.extend(["--version", version])
        proc = _run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     encoding="utf-8", errors="replace")
        return proc.returncode, (proc.stderr or proc.stdout or "").strip()

    # ------------------------------------------------------------- uninstall
    def uninstall(self, package_id: str) -> tuple[int, str]:
        args = [
            "winget", "uninstall", "--id", package_id, "--exact",
            "--accept-source-agreements", "--disable-interactivity",
        ]
        proc = _run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     encoding="utf-8", errors="replace")
        return proc.returncode, (proc.stderr or proc.stdout or "").strip()

    # --------------------------------------------------------------- upgrade
    def upgrade(self, package_id: str) -> tuple[int, str]:
        args = [
            "winget", "upgrade", "--id", package_id, "--exact",
            "--accept-package-agreements", "--accept-source-agreements",
            "--disable-interactivity",
        ]
        proc = _run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     encoding="utf-8", errors="replace")
        return proc.returncode, (proc.stderr or proc.stdout or "").strip()

    # ----------------------------------------------------------------- show
    def show(self, package_id: str) -> str:
        try:
            result = _run(
                ["winget", "show", "--id", package_id, "--exact",
                 "--accept-source-agreements", "--disable-interactivity"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
        return result.stdout.strip()

    # ----------------------------------------------------------- upgradable
    def list_upgradable_ids(self) -> set[str]:
        try:
            result = _run(
                ["winget", "upgrade", "--accept-source-agreements",
                 "--disable-interactivity"],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
        except FileNotFoundError:
            return set()
        return {p.id for p in parse_search_output(result.stdout)}
