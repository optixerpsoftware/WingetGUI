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


class InstallWorker(QThread):
    """Exécute une installation winget hors du thread UI."""

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
