from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from src.ui.package_card import PackageCard
from src.winget import WingetPackage


class SearchView(QWidget):
    """En-tête (barre de recherche) + liste de cartes."""

    search_requested = Signal(str)
    install_requested = Signal(WingetPackage)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: dict[str, PackageCard] = {}
        self._build_ui()

    # ---- construction ----------------------------------------------------

    def _build_ui(self) -> None:
        title = QLabel("Winget GUI")
        title.setObjectName("title")

        subtitle = QLabel("Recherchez et installez vos paquets Windows")
        subtitle.setObjectName("subtitle")

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

        # zone scrollable pour les cartes
        self._results_host = QWidget()
        self._results_layout = QVBoxLayout(self._results_host)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(10)
        self._results_layout.addStretch()

        self._placeholder = QLabel("Tapez une requête puis appuyez sur Entrée.")
        self._placeholder.setObjectName("subtitle")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._results_layout.insertWidget(0, self._placeholder)

        scroll = QScrollArea()
        scroll.setWidget(self._results_host)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 16)
        root.setSpacing(14)
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(8)
        root.addLayout(search_row)
        root.addSpacing(6)
        root.addWidget(scroll, stretch=1)

    # ---- API publique ----------------------------------------------------

    def set_busy(self, busy: bool) -> None:
        self._button.setEnabled(not busy)
        self._button.setText("Recherche…" if busy else "Rechercher")
        self._input.setEnabled(not busy)

    def show_results(self, packages: list[WingetPackage]) -> None:
        self._clear_results()
        if not packages:
            self._placeholder.setText("Aucun résultat.")
            self._placeholder.show()
            return

        self._placeholder.hide()
        for pkg in packages:
            card = PackageCard(pkg)
            card.install_requested.connect(self.install_requested.emit)
            self._cards[pkg.id] = card
            self._results_layout.insertWidget(self._results_layout.count() - 1, card)

    def show_error(self, message: str) -> None:
        self._clear_results()
        self._placeholder.setText(f"Erreur : {message}")
        self._placeholder.show()

    def mark_installed(self, package: WingetPackage, success: bool) -> None:
        card = self._cards.get(package.id)
        if card:
            card.mark_installed(success)

    # ---- interne ---------------------------------------------------------

    def _emit_search(self) -> None:
        query = self._input.text().strip()
        if query:
            self.search_requested.emit(query)

    def _clear_results(self) -> None:
        for card in self._cards.values():
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
