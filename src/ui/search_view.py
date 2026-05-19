from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from src.ui.package_card import PackageCard
from src.ui.selection_panel import SelectionPanel
from src.ui.spinner import SpinnerWithLabel
from src.winget import WingetPackage


class SearchView(QWidget):
    """En-tête (titre + toolbar + barre de recherche) et liste de cartes."""

    search_requested  = Signal(str)
    install_requested = Signal(WingetPackage)
    bundle_toggled    = Signal(WingetPackage, bool)
    import_requested  = Signal()
    export_requested  = Signal()
    bulk_install_requested = Signal()
    bundle_cleared    = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: dict[str, PackageCard] = {}
        self._installed_ids: set[str] = set()
        self._build_ui()
        self._refresh_bundle_button(0)

    # ---- construction ----------------------------------------------------

    def _build_ui(self) -> None:
        title = QLabel("Winget GUI")
        title.setObjectName("title")

        subtitle = QLabel("Recherchez et installez vos paquets Windows")
        subtitle.setObjectName("subtitle")

        # Toolbar : Importer / Exporter / Installer la sélection
        self._import_btn = QPushButton("📥  Importer")
        self._import_btn.setObjectName("ghost")
        self._import_btn.setCursor(Qt.PointingHandCursor)
        self._import_btn.clicked.connect(self.import_requested.emit)

        self._export_btn = QPushButton("📤  Exporter la sélection")
        self._export_btn.setObjectName("ghost")
        self._export_btn.setCursor(Qt.PointingHandCursor)
        self._export_btn.clicked.connect(self.export_requested.emit)

        self._bulk_btn = QPushButton()
        self._bulk_btn.setObjectName("primary")
        self._bulk_btn.setCursor(Qt.PointingHandCursor)
        self._bulk_btn.clicked.connect(self.bulk_install_requested.emit)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        toolbar.addWidget(self._import_btn)
        toolbar.addWidget(self._export_btn)
        toolbar.addStretch()
        toolbar.addWidget(self._bulk_btn)

        # Barre de recherche
        self._input = QLineEdit()
        self._input.setObjectName("search")
        self._input.setPlaceholderText("Rechercher un paquet (ex. vscode, firefox)…")
        self._input.returnPressed.connect(self._emit_search)

        self._button = QPushButton("Rechercher")
        self._button.setObjectName("primary")
        self._button.setCursor(Qt.PointingHandCursor)
        self._button.clicked.connect(self._emit_search)

        search_row = QHBoxLayout()
        search_row.setSpacing(10)
        search_row.addWidget(self._input, stretch=1)
        search_row.addWidget(self._button)

        # Résultats
        self._results_host = QWidget()
        self._results_layout = QVBoxLayout(self._results_host)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(10)
        self._results_layout.addStretch()

        self._placeholder = QLabel("Tapez une requête puis appuyez sur Entrée.")
        self._placeholder.setObjectName("subtitle")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._results_layout.insertWidget(0, self._placeholder)

        self._loading = SpinnerWithLabel("Recherche en cours…")
        self._loading.hide()
        self._results_layout.insertWidget(1, self._loading)

        scroll = QScrollArea()
        scroll.setWidget(self._results_host)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Panneau latéral de sélection
        self._selection_panel = SelectionPanel()
        self._selection_panel.remove_requested.connect(self._on_remove_from_selection)
        self._selection_panel.clear_requested.connect(self.bundle_cleared.emit)

        content_row = QHBoxLayout()
        content_row.setSpacing(14)
        content_row.addWidget(scroll, stretch=1)
        content_row.addWidget(self._selection_panel)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 16)
        root.setSpacing(12)
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(4)
        root.addLayout(toolbar)
        root.addLayout(search_row)
        root.addSpacing(4)
        root.addLayout(content_row, stretch=1)

    # ---- API publique ----------------------------------------------------

    def set_busy(self, busy: bool) -> None:
        self._button.setEnabled(not busy)
        self._button.setText("Recherche…" if busy else "Rechercher")
        self._input.setEnabled(not busy)
        if busy:
            self._clear_results()
            self._placeholder.hide()
            self._loading.start()
        else:
            self._loading.stop()

    @property
    def installed_ids(self) -> set[str]:
        return self._installed_ids

    def set_installed_ids(self, installed: set[str]) -> None:
        self._installed_ids = installed
        for pkg_id, card in self._cards.items():
            card.set_already_installed(pkg_id in installed)

    def show_results(self, packages: list[WingetPackage], bundle_ids: set[str]) -> None:
        self._clear_results()
        if not packages:
            self._placeholder.setText("Aucun résultat.")
            self._placeholder.show()
            return

        self._placeholder.hide()
        for pkg in packages:
            card = PackageCard(pkg)
            card.install_requested.connect(self.install_requested.emit)
            card.bundle_toggled.connect(self.bundle_toggled.emit)
            card.set_already_installed(pkg.id in self._installed_ids)
            card.set_bundle_state(pkg.id in bundle_ids)
            self._cards[pkg.id] = card
            self._results_layout.insertWidget(self._results_layout.count() - 1, card)

    def show_error(self, message: str) -> None:
        self._clear_results()
        self._placeholder.setText(f"Erreur : {message}")
        self._placeholder.show()

    def mark_installed(self, package: WingetPackage, success: bool) -> None:
        if success:
            self._installed_ids.add(package.id)
        card = self._cards.get(package.id)
        if card:
            card.mark_install_result(success)

    def update_bundle_state(self, package: WingetPackage, in_bundle: bool) -> None:
        card = self._cards.get(package.id)
        if card:
            card.set_bundle_state(in_bundle)

    def refresh_bundle_count(self, count: int) -> None:
        self._refresh_bundle_button(count)

    def set_bundle(self, packages: list[WingetPackage]) -> None:
        """Met à jour le panneau latéral et synchronise l'état des cartes."""
        self._selection_panel.set_packages(packages)
        bundle_ids = {p.id for p in packages}
        for pid, card in self._cards.items():
            card.set_bundle_state(pid in bundle_ids)
        self._refresh_bundle_button(len(packages))

    def _on_remove_from_selection(self, package: WingetPackage) -> None:
        # le retrait depuis le panneau émet le même signal qu'un décochage de carte
        self.bundle_toggled.emit(package, False)

    # ---- interne ---------------------------------------------------------

    def _refresh_bundle_button(self, count: int) -> None:
        if count == 0:
            self._bulk_btn.setText("Installer la sélection")
            self._bulk_btn.setEnabled(False)
            self._export_btn.setEnabled(False)
        else:
            self._bulk_btn.setText(f"Installer la sélection ({count})")
            self._bulk_btn.setEnabled(True)
            self._export_btn.setEnabled(True)

    def _emit_search(self) -> None:
        query = self._input.text().strip()
        if query:
            self.search_requested.emit(query)

    def _clear_results(self) -> None:
        for card in self._cards.values():
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
