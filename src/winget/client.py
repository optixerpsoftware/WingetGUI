import subprocess
from typing import Optional

from src.winget.bootstrap import ensure_winget
from src.winget.compatibility import check_compatibility
from src.winget.models import WingetPackage
from src.winget.parser import parse_search_output


class Winget:
    """Façade haut-niveau sur le CLI `winget`."""

    def __init__(self, auto_bootstrap: bool = False):
        if not check_compatibility():
            raise RuntimeError("Système non supporté (Windows 10/11 requis).")
        if auto_bootstrap:
            ensure_winget()

    # ---------------------------------------------------------------- search
    def search(self, query: str) -> list[WingetPackage]:
        try:
            result = subprocess.run(
                ["winget", "search", "--query", query, "--disable-interactivity"],
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
            result = subprocess.run(
                ["winget", "list", "--disable-interactivity"],
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
    def install(self, package_id: str, version: Optional[str] = None) -> int:
        args = [
            "winget", "install", "--id", package_id, "--exact",
            "--accept-package-agreements", "--accept-source-agreements",
            "--disable-interactivity",
        ]
        if version:
            args.extend(["--version", version])
        return subprocess.run(args).returncode
