from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar, QVBoxLayout, QWidget

from src.ui.search_view import SearchView
from src.ui.theme import QSS
from src.ui.workers import InstallWorker, SearchWorker
from src.winget import Winget, WingetPackage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winget GUI")
        self.resize(960, 680)
        self.setMinimumSize(720, 480)

        self._winget = Winget()
        self._search_worker: SearchWorker | None = None
        self._install_workers: list[InstallWorker] = []

        self._build_ui()
        self.setStyleSheet(QSS)

    # ---- construction ----------------------------------------------------

    def _build_ui(self) -> None:
        self._view = SearchView()
        self._view.search_requested.connect(self._on_search_requested)
        self._view.install_requested.connect(self._on_install_requested)

        root = QWidget(objectName="root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)
        self.setCentralWidget(root)

        self._status_label = QLabel("Prêt.")
        self._status_label.setObjectName("status")

        bar = QStatusBar()
        bar.setSizeGripEnabled(False)
        bar.addWidget(self._status_label, stretch=1)
        self.setStatusBar(bar)

    # ---- slots de recherche ---------------------------------------------

    def _on_search_requested(self, query: str) -> None:
        if self._search_worker and self._search_worker.isRunning():
            return

        self._view.set_busy(True)
        self._status_label.setText(f"Recherche de « {query} »…")

        self._search_worker = SearchWorker(query, self._winget, self)
        self._search_worker.finished_with_results.connect(self._on_results_ready)
        self._search_worker.failed.connect(self._on_search_failed)
        self._search_worker.start()

    def _on_results_ready(self, packages: list[WingetPackage]) -> None:
        self._view.set_busy(False)
        self._view.show_results(packages)
        self._status_label.setText(f"{len(packages)} résultat(s).")

    def _on_search_failed(self, message: str) -> None:
        self._view.set_busy(False)
        self._view.show_error(message)
        self._status_label.setText("Erreur pendant la recherche.")

    # ---- slots d'installation -------------------------------------------

    def _on_install_requested(self, package: WingetPackage) -> None:
        self._status_label.setText(f"Installation de {package.name}…")
        worker = InstallWorker(package, self._winget, self)
        worker.finished_with_code.connect(self._on_install_done)
        worker.failed.connect(self._on_install_failed)
        worker.finished.connect(lambda w=worker: self._install_workers.remove(w))
        self._install_workers.append(worker)
        worker.start()

    def _on_install_done(self, code: int, package: WingetPackage) -> None:
        success = code == 0
        self._view.mark_installed(package, success)
        self._status_label.setText(
            f"{package.name} installé." if success
            else f"Échec de l'installation de {package.name} (code {code})."
        )

    def _on_install_failed(self, message: str, package: WingetPackage) -> None:
        self._view.mark_installed(package, False)
        self._status_label.setText(f"Erreur : {message}")
