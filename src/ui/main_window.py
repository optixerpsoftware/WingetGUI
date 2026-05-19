from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog, QLabel, QMainWindow, QMessageBox, QProgressBar,
    QStatusBar, QVBoxLayout, QWidget,
)

from src.ui.search_view import SearchView
from src.ui.theme import QSS
from src.ui.workers import (
    BulkInstallWorker, InstallWorker, InstalledScanWorker, SearchWorker,
)
from src.winget import Winget, WingetPackage, export_packages, import_package_ids


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winget GUI")
        self.resize(1000, 720)
        self.setMinimumSize(760, 500)

        self._winget = Winget()
        self._bundle: dict[str, WingetPackage] = {}

        self._search_worker: SearchWorker | None = None
        self._scan_worker: InstalledScanWorker | None = None
        self._bulk_worker: BulkInstallWorker | None = None
        self._install_workers: list[InstallWorker] = []

        self._build_ui()
        self.setStyleSheet(QSS)
        self._scan_installed()

    # ---- construction ----------------------------------------------------

    def _build_ui(self) -> None:
        self._view = SearchView()
        self._view.search_requested.connect(self._on_search_requested)
        self._view.install_requested.connect(self._on_install_requested)
        self._view.bundle_toggled.connect(self._on_bundle_toggled)
        self._view.import_requested.connect(self._on_import_requested)
        self._view.export_requested.connect(self._on_export_requested)
        self._view.bulk_install_requested.connect(self._on_bulk_install_requested)

        root = QWidget(objectName="root")
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._view)
        self.setCentralWidget(root)

        self._status_label = QLabel("Prêt.")
        self._status_label.setObjectName("status")

        self._progress = QProgressBar()
        self._progress.setMaximumWidth(220)
        self._progress.setVisible(False)

        bar = QStatusBar()
        bar.setSizeGripEnabled(False)
        bar.addWidget(self._status_label, stretch=1)
        bar.addPermanentWidget(self._progress)
        self.setStatusBar(bar)

    # ---- scan paquets installés -----------------------------------------

    def _scan_installed(self) -> None:
        self._status_label.setText("Analyse des paquets installés…")
        self._scan_worker = InstalledScanWorker(self._winget, self)
        self._scan_worker.finished_with_ids.connect(self._on_installed_scanned)
        self._scan_worker.failed.connect(
            lambda msg: self._status_label.setText(f"Scan échoué : {msg}")
        )
        self._scan_worker.start()

    def _on_installed_scanned(self, installed_ids: set[str]) -> None:
        self._view.set_installed_ids(installed_ids)
        self._status_label.setText(f"{len(installed_ids)} paquets installés détectés.")

    # ---- recherche ------------------------------------------------------

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
        self._view.show_results(packages, set(self._bundle.keys()))
        self._status_label.setText(f"{len(packages)} résultat(s).")

    def _on_search_failed(self, message: str) -> None:
        self._view.set_busy(False)
        self._view.show_error(message)
        self._status_label.setText("Erreur pendant la recherche.")

    # ---- bundle ---------------------------------------------------------

    def _on_bundle_toggled(self, package: WingetPackage, in_bundle: bool) -> None:
        if in_bundle:
            self._bundle[package.id] = package
        else:
            self._bundle.pop(package.id, None)
        self._view.refresh_bundle_count(len(self._bundle))
        self._status_label.setText(f"Sélection : {len(self._bundle)} paquet(s).")

    # ---- installation unitaire ------------------------------------------

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
        if success:
            # désélectionne du bundle puisqu'il est désormais installé
            self._bundle.pop(package.id, None)
            self._view.refresh_bundle_count(len(self._bundle))
        self._status_label.setText(
            f"{package.name} installé." if success
            else f"Échec de l'installation de {package.name} (code {code})."
        )

    def _on_install_failed(self, message: str, package: WingetPackage) -> None:
        self._view.mark_installed(package, False)
        self._status_label.setText(f"Erreur : {message}")

    # ---- import / export ------------------------------------------------

    def _on_export_requested(self) -> None:
        if not self._bundle:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Exporter la configuration", "winget-config.json",
            "Configuration winget (*.json)",
        )
        if not path:
            return
        try:
            export_packages(list(self._bundle.values()), Path(path))
            self._status_label.setText(f"Configuration exportée vers {Path(path).name}.")
        except Exception as exc:
            QMessageBox.critical(self, "Export impossible", str(exc))

    def _on_import_requested(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Importer une configuration", "",
            "Configuration winget (*.json)",
        )
        if not path:
            return
        try:
            ids = import_package_ids(Path(path))
        except Exception as exc:
            QMessageBox.critical(self, "Import impossible", str(exc))
            return

        if not ids:
            QMessageBox.information(self, "Import",
                                    "Aucun paquet trouvé dans le fichier.")
            return

        # filtre les paquets déjà installés
        installed = set(self._view.installed_ids)
        to_install = [pid for pid in ids if pid not in installed]
        skipped = len(ids) - len(to_install)

        msg = (f"{len(to_install)} paquet(s) à installer"
               + (f" ({skipped} déjà installé(s) seront ignorés)" if skipped else "")
               + ".\n\nLancer l'installation ?")
        confirm = QMessageBox.question(self, "Confirmer l'installation", msg)
        if confirm != QMessageBox.Yes or not to_install:
            return

        self._run_bulk_install(to_install)

    # ---- installation en série -----------------------------------------

    def _on_bulk_install_requested(self) -> None:
        ids = [pid for pid in self._bundle.keys()
               if pid not in self._view.installed_ids]
        if not ids:
            return
        self._run_bulk_install(ids)

    def _run_bulk_install(self, ids: list[str]) -> None:
        if self._bulk_worker and self._bulk_worker.isRunning():
            return

        self._progress.setRange(0, len(ids))
        self._progress.setValue(0)
        self._progress.setVisible(True)

        self._bulk_worker = BulkInstallWorker(ids, self._winget, self)
        self._bulk_worker.progress.connect(self._on_bulk_progress)
        self._bulk_worker.item_done.connect(self._on_bulk_item_done)
        self._bulk_worker.finished_all.connect(self._on_bulk_finished)
        self._bulk_worker.failed.connect(self._on_bulk_failed)
        self._bulk_worker.start()

    def _on_bulk_progress(self, index: int, total: int, package_id: str) -> None:
        self._progress.setValue(index - 1)
        self._status_label.setText(f"[{index}/{total}] Installation de {package_id}…")

    def _on_bulk_item_done(self, package_id: str, code: int) -> None:
        self._progress.setValue(self._progress.value() + 1)
        pkg = self._bundle.get(package_id)
        if pkg:
            self._view.mark_installed(pkg, code == 0)
            if code == 0:
                self._bundle.pop(package_id, None)
        else:
            # paquet importé qui n'est pas dans la vue actuelle
            if code == 0:
                self._view.set_installed_ids(
                    self._view.installed_ids | {package_id}
                )

    def _on_bulk_finished(self, n_success: int, n_total: int) -> None:
        self._progress.setVisible(False)
        self._view.refresh_bundle_count(len(self._bundle))
        QMessageBox.information(
            self, "Installation terminée",
            f"{n_success}/{n_total} paquet(s) installé(s) avec succès.",
        )
        self._status_label.setText(f"{n_success}/{n_total} paquet(s) installé(s).")

    def _on_bulk_failed(self, message: str) -> None:
        self._progress.setVisible(False)
        QMessageBox.critical(self, "Installation interrompue", message)
        self._status_label.setText(f"Erreur : {message}")
