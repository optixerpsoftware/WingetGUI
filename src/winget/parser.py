import urllib.error
import urllib.request
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from src import settings

_PACKAGE_URL = "https://aka.ms/getwinget"
_MODULE_NAME = "WinGet.msixbundle"


@dataclass
class WingetPackage:
    name: str
    id: str
    version: str
    source: str

    def __str__(self):
        return f"{self.name} ({self.id}) — v{self.version} [{self.source}]"


class Winget:
    def __init__(self):
        self.download_dir: Path = getattr(settings, "DOWNLOAD_DIR")

    def ensure_requirements(self):
        if self._is_winget_installed():
            print("WinGet est déjà installé.")
            return

        print("WinGet non trouvé. Installation en cours...")
        package_path = self._download_requirements()
        self._install(package_path)

    def _is_winget_installed(self) -> bool:
        try:
            subprocess.run(
                ["winget", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _download_requirements(self) -> Path:
        self.download_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.download_dir / _MODULE_NAME

        print(f"Téléchargement depuis {_PACKAGE_URL}...")
        try:
            urllib.request.urlretrieve(_PACKAGE_URL, output_file)
        except urllib.error.URLError as error:
            raise RuntimeError(f"Échec du téléchargement : {error}") from error

        return output_file

    def _install(self, package_path: Path):
        print(f"Installation de {package_path.name}...")
        try:
            subprocess.run(
                ["powershell", "-Command", f"Add-AppxPackage -Path '{package_path}'"],
                check=True,
            )
            print("WinGet installé avec succès.")
        except subprocess.CalledProcessError as error:
            raise RuntimeError(f"Échec de l'installation : {error}") from error

    def search(self, query: str) -> list[WingetPackage]:
        """Recherche des paquets winget et retourne une liste structurée."""
        try:
            result = subprocess.run(
                ["winget", "search", "--query", query, "--disable-interactivity"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as error:
            print(f"Erreur lors de la recherche : {error}")
            return []

        return self._parse_search_output(result.stdout)

    @staticmethod
    def install(package_id: str, version: Optional[str] = None):
        """Installe un paquet winget."""
        args = ["winget", "install", package_id]
        if version:
            args.extend(["--version", version])

        try:
            subprocess.run(args, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'installation du paquet {package_id}: {e}")


    @staticmethod
    def _parse_search_output(output: str) -> list[WingetPackage]:
        """Parse la sortie tabulaire de `winget search`."""
        lines = output.splitlines()

        # Trouver la ligne d'en-tête (contient "Name" et "Id")
        header_index = next(
            (i for i, line in enumerate(lines) if "Name" in line and "Id" in line),
            None,
        )
        if header_index is None:
            return []

        header = lines[header_index]

        # Détecter les positions des colonnes depuis l'en-tête
        col_name   = header.index("Name")
        col_id     = header.index("Id")
        col_version= header.index("Version")
        col_source = header.index("Source") if "Source" in header else None

        # Ignorer la ligne de séparation (------)
        data_lines = [
            line for line in lines[header_index + 1:]
            if line.strip() and not line.startswith("-")
        ]

        packages = []
        for line in data_lines:
            if len(line) < col_version:
                continue

            name    = line[col_name:col_id].strip()
            id_     = line[col_id:col_version].strip()
            version = line[col_version:col_source].strip() if col_source else line[col_version:].strip()
            source  = line[col_source:].strip() if col_source else ""

            if name and id_:
                packages.append(WingetPackage(name=name, id=id_, version=version, source=source))

        return packages

