from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QSizePolicy,
)

from src.winget import WingetPackage


class PackageCard(QFrame):
    """Carte d'un paquet winget avec bouton d'installation."""

    install_requested = Signal(WingetPackage)

    def __init__(self, package: WingetPackage, parent=None):
        super().__init__(parent)
        self._package = package
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._install_btn = QPushButton("Installer")
        self._install_btn.setObjectName("primary")
        self._install_btn.setCursor(Qt.PointingHandCursor)
        self._install_btn.clicked.connect(self._emit_install)

        self._build_layout()

    def _build_layout(self) -> None:
        name = QLabel(self._package.name)
        name.setObjectName("cardName")
        name.setWordWrap(True)

        pkg_id = QLabel(self._package.id)
        pkg_id.setObjectName("cardId")
        pkg_id.setTextInteractionFlags(Qt.TextSelectableByMouse)

        version = QLabel(f"v{self._package.version}")
        version.setObjectName("cardVersion")

        source = QLabel(self._package.source or "—")
        source.setObjectName("cardSource")

        # Colonne de gauche : nom + id
        left = QVBoxLayout()
        left.setSpacing(4)
        left.addWidget(name)
        left.addWidget(pkg_id)

        # Colonne du milieu : badges
        meta = QHBoxLayout()
        meta.setSpacing(6)
        meta.addWidget(version)
        meta.addWidget(source)
        meta.addStretch()

        center = QVBoxLayout()
        center.setSpacing(8)
        center.addLayout(left)
        center.addLayout(meta)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(16)
        root.addLayout(center, stretch=1)
        root.addWidget(self._install_btn, alignment=Qt.AlignVCenter)

    def _emit_install(self) -> None:
        self._install_btn.setEnabled(False)
        self._install_btn.setText("Installation…")
        self.install_requested.emit(self._package)

    def mark_installed(self, success: bool) -> None:
        self._install_btn.setEnabled(True)
        self._install_btn.setText("Installé ✓" if success else "Réessayer")
