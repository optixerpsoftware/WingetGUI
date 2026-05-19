from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy,
    QVBoxLayout, QWidget,
)

from src.winget import WingetPackage


class _SelectionRow(QFrame):
    """Une ligne dans le panneau de sélection : nom + bouton supprimer."""

    remove_clicked = Signal(WingetPackage)

    def __init__(self, package: WingetPackage, parent=None):
        super().__init__(parent)
        self._package = package
        self.setObjectName("selectionRow")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        name = QLabel(package.name)
        name.setObjectName("selectionName")
        name.setWordWrap(True)

        pkg_id = QLabel(package.id)
        pkg_id.setObjectName("selectionId")
        pkg_id.setWordWrap(True)

        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)
        info.addWidget(name)
        info.addWidget(pkg_id)

        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("selectionRemove")
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setFixedSize(26, 26)
        remove_btn.setToolTip("Retirer de la sélection")
        remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self._package))

        root = QHBoxLayout(self)
        root.setContentsMargins(10, 8, 8, 8)
        root.setSpacing(8)
        root.addLayout(info, stretch=1)
        root.addWidget(remove_btn, alignment=Qt.AlignTop)


class SelectionPanel(QWidget):
    """Panneau latéral droit listant les paquets sélectionnés."""

    remove_requested = Signal(WingetPackage)
    clear_requested  = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: dict[str, _SelectionRow] = {}
        self.setObjectName("selectionPanel")
        self.setFixedWidth(280)
        self._build_ui()
        self._refresh_header(0)

    def _build_ui(self) -> None:
        self._title = QLabel("Sélection")
        self._title.setObjectName("selectionTitle")

        self._clear_btn = QPushButton("Tout vider")
        self._clear_btn.setObjectName("ghost")
        self._clear_btn.setCursor(Qt.PointingHandCursor)
        self._clear_btn.clicked.connect(self.clear_requested.emit)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.addWidget(self._title, stretch=1)
        header.addWidget(self._clear_btn)

        self._list_host = QWidget()
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._list_layout.addStretch()

        self._placeholder = QLabel("Aucun paquet sélectionné.\n\nClique sur « + Ajouter » sur une carte pour ajouter un paquet à la sélection.")
        self._placeholder.setObjectName("selectionPlaceholder")
        self._placeholder.setWordWrap(True)
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._list_layout.insertWidget(0, self._placeholder)

        scroll = QScrollArea()
        scroll.setObjectName("selectionScroll")
        scroll.setWidget(self._list_host)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)
        root.addLayout(header)
        root.addWidget(scroll, stretch=1)

    # ---- API publique ----------------------------------------------------

    def set_packages(self, packages: list[WingetPackage]) -> None:
        # supprime les rangées qui ne sont plus là
        current_ids = {p.id for p in packages}
        for pid in list(self._rows.keys()):
            if pid not in current_ids:
                row = self._rows.pop(pid)
                row.setParent(None)
                row.deleteLater()

        # ajoute les nouvelles
        for pkg in packages:
            if pkg.id not in self._rows:
                row = _SelectionRow(pkg)
                row.remove_clicked.connect(self.remove_requested.emit)
                self._rows[pkg.id] = row
                self._list_layout.insertWidget(self._list_layout.count() - 1, row)

        self._refresh_header(len(packages))
        self._placeholder.setVisible(not packages)

    def _refresh_header(self, count: int) -> None:
        self._title.setText(f"Sélection ({count})" if count else "Sélection")
        self._clear_btn.setEnabled(count > 0)
