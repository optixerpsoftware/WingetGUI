"""Import / export de configurations winget (bulk install).

Format natif compatible avec la commande `winget import`.
Référence schéma : https://aka.ms/winget-packages.schema.2.0.json
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from src.winget.models import WingetPackage

_SCHEMA_URL = "https://aka.ms/winget-packages.schema.2.0.json"
_SOURCE_DETAILS = {
    "Argument": "https://cdn.winget.microsoft.com/cache",
    "Identifier": "Microsoft.Winget.Source_8wekyb3d8bbwe",
    "Name": "winget",
    "Type": "Microsoft.PreIndexed.Package",
}


def export_packages(packages: list[WingetPackage], path: Path) -> None:
    """Sérialise une sélection au format JSON compatible `winget import`."""
    payload = {
        "$schema": _SCHEMA_URL,
        "CreationDate": datetime.now(timezone.utc).isoformat(),
        "Sources": [{
            "Packages": [{"PackageIdentifier": p.id} for p in packages],
            "SourceDetails": _SOURCE_DETAILS,
        }],
        "WinGetVersion": "1.x",
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def import_package_ids(path: Path) -> list[str]:
    """Lit un fichier de configuration et retourne la liste des PackageIdentifier.

    Accepte le format natif winget et un format simplifié
    `{"packages": ["Id1", "Id2", ...]}`.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    ids: list[str] = []

    if isinstance(data, dict) and "Sources" in data:
        for source in data.get("Sources", []):
            for pkg in source.get("Packages", []):
                pid = pkg.get("PackageIdentifier")
                if pid:
                    ids.append(pid)
    elif isinstance(data, dict) and "packages" in data:
        for pkg in data["packages"]:
            if isinstance(pkg, dict):
                pid = pkg.get("id") or pkg.get("PackageIdentifier")
                if pid:
                    ids.append(pid)
            elif isinstance(pkg, str):
                ids.append(pkg)

    return ids
