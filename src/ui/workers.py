from PySide6.QtCore import QObject, QThread, Signal

from src.winget import Winget, WingetPackage


class SearchWorker(QThread):
    """Exécute une recherche winget hors du thread UI."""

    finished_with_results = Signal(list)   # list[WingetPackage]
    failed = Signal(str)

    def __init__(self, query: str, winget: Winget, parent: QObject | None = None):
        super().__init__(parent)
        self._query = query
        self._winget = winget

    def run(self) -> None:
        try:
            results = self._winget.search(self._query)
            self.finished_with_results.emit(results)
        except Exception as exc:
            self.failed.emit(str(exc))


class InstalledScanWorker(QThread):
    """Scanne les paquets déjà installés sur le système."""

    finished_with_ids = Signal(set)        # set[str]
    failed = Signal(str)

    def __init__(self, winget: Winget, parent: QObject | None = None):
        super().__init__(parent)
        self._winget = winget

    def run(self) -> None:
        try:
            self.finished_with_ids.emit(self._winget.installed_ids())
        except Exception as exc:
            self.failed.emit(str(exc))


class InstallWorker(QThread):
    """Installe un paquet hors du thread UI."""

    finished_with_code = Signal(int, WingetPackage)
    failed = Signal(str, WingetPackage)

    def __init__(self, package: WingetPackage, winget: Winget, parent: QObject | None = None):
        super().__init__(parent)
        self._package = package
        self._winget = winget

    def run(self) -> None:
        try:
            code = self._winget.install(self._package.id)
            self.finished_with_code.emit(code, self._package)
        except Exception as exc:
            self.failed.emit(str(exc), self._package)


class InstalledListWorker(QThread):
    """Récupère la liste complète des paquets installés (avec détails)."""

    finished_with_packages = Signal(list, set)   # list[WingetPackage], set[str] upgradable ids
    failed = Signal(str)

    def __init__(self, winget: Winget, parent: QObject | None = None):
        super().__init__(parent)
        self._winget = winget

    def run(self) -> None:
        try:
            packages = self._winget.list_installed()
            upgradable = self._winget.list_upgradable_ids()
            self.finished_with_packages.emit(packages, upgradable)
        except Exception as exc:
            self.failed.emit(str(exc))


class UninstallWorker(QThread):
    """Désinstalle un paquet hors du thread UI."""

    finished_with_code = Signal(int, WingetPackage)
    failed = Signal(str, WingetPackage)

    def __init__(self, package: WingetPackage, winget: Winget, parent: QObject | None = None):
        super().__init__(parent)
        self._package = package
        self._winget = winget

    def run(self) -> None:
        try:
            code = self._winget.uninstall(self._package.id)
            self.finished_with_code.emit(code, self._package)
        except Exception as exc:
            self.failed.emit(str(exc), self._package)


class UpgradeWorker(QThread):
    """Met à jour un paquet hors du thread UI."""

    finished_with_code = Signal(int, WingetPackage)
    failed = Signal(str, WingetPackage)

    def __init__(self, package: WingetPackage, winget: Winget, parent: QObject | None = None):
        super().__init__(parent)
        self._package = package
        self._winget = winget

    def run(self) -> None:
        try:
            code = self._winget.upgrade(self._package.id)
            self.finished_with_code.emit(code, self._package)
        except Exception as exc:
            self.failed.emit(str(exc), self._package)


class BulkInstallWorker(QThread):
    """Installe plusieurs paquets en série avec progression."""

    progress = Signal(int, int, str)       # index (1-based), total, package_id
    item_done = Signal(str, int)           # package_id, return_code
    finished_all = Signal(int, int)        # n_success, n_total
    failed = Signal(str)

    def __init__(self, package_ids: list[str], winget: Winget,
                 parent: QObject | None = None, action: str = "install"):
        super().__init__(parent)
        self._ids = package_ids
        self._winget = winget
        self._action = action

    def run(self) -> None:
        total = len(self._ids)
        ok = 0
        try:
            for i, pid in enumerate(self._ids, start=1):
                self.progress.emit(i, total, pid)
                if self._action == "upgrade":
                    code = self._winget.upgrade(pid)
                else:
                    code = self._winget.install(pid)
                self.item_done.emit(pid, code)
                if code == 0:
                    ok += 1
            self.finished_all.emit(ok, total)
        except Exception as exc:
            self.failed.emit(str(exc))
