import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from config import settings

_PACKAGE_URL = "https://aka.ms/getwinget"
_MODULE_NAME = "WinGet.msixbundle"
_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
if sys.platform == "win32":
    _STARTUPINFO = subprocess.STARTUPINFO()
    _STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    _STARTUPINFO.wShowWindow = subprocess.SW_HIDE
else:
    _STARTUPINFO = None


def is_winget_installed() -> bool:
    try:
        subprocess.run(
            ["winget", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=_NO_WINDOW,
            startupinfo=_STARTUPINFO,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def ensure_winget(download_dir: Path | None = None) -> bool:
    """S'assure que winget est présent ; l'installe sinon."""
    if is_winget_installed():
        return True

    target_dir = download_dir or getattr(settings, "DOWNLOAD_DIR")
    package_path = _download(target_dir)
    _install_msix(package_path)
    return True


def _download(download_dir: Path) -> Path:
    download_dir.mkdir(parents=True, exist_ok=True)
    output_file = download_dir / _MODULE_NAME
    try:
        urllib.request.urlretrieve(_PACKAGE_URL, output_file)
    except urllib.error.URLError as error:
        raise RuntimeError(f"Échec du téléchargement : {error}") from error
    return output_file


def _install_msix(package_path: Path) -> None:
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden",
             "-Command", f"Add-AppxPackage -Path '{package_path}'"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=_NO_WINDOW,
            startupinfo=_STARTUPINFO,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Échec de l'installation : {error}") from error
