from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout,
)

from src.ui.spinner import Spinner

from src.winget import WingetPackage


class PackageCard(QFrame):
    """Carte d'un paquet winget.

    États possibles :
      - default      → bouton "+ Ajouter" et bouton "Installer"
      - in bundle    → bouton "✓ Sélectionné" (checked) et bouton "Installer"
      - installing   → bouton "Installation…" désactivé
      - installed    → badge vert "Installé", aucun bouton
    """

    install_requested = Signal(WingetPackage)
    update_requested = Signal(WingetPackage)
    detail_requested = Signal(WingetPackage)
    bundle_toggled = Signal(WingetPackage, bool)   # package, is_in_bundle

    def __init__(self, package: WingetPackage, parent=None):
        super().__init__(parent)
        self._package = package
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setProperty("installed", False)

        self._build_layout()

    # ---- construction ----------------------------------------------------

    def _build_layout(self) -> None:
        name_btn = QPushButton(self._package.name)
        name_btn.setObjectName("cardNameBtn")
        name_btn.setCursor(Qt.PointingHandCursor)
        name_btn.setFlat(True)
        name_btn.setStyleSheet(
            "QPushButton#cardNameBtn { text-align: left; font-size: 14px; "
            "font-weight: 600; border: none; padding: 0; color: #2563eb; } "
            "QPushButton#cardNameBtn:hover { text-decoration: underline; }"
        )
        name_btn.clicked.connect(self._emit_detail)

        pkg_id = QLabel(self._package.id)
        pkg_id.setObjectName("cardId")
        pkg_id.setTextInteractionFlags(Qt.TextSelectableByMouse)

        version = QLabel(f"v{self._package.version}" if self._package.version else "—")
        version.setObjectName("cardVersion")

        source = QLabel(self._package.source or "—")
        source.setObjectName("cardSource")

        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)
        meta_row.addWidget(version)
        meta_row.addWidget(source)
        meta_row.addStretch()

        info = QVBoxLayout()
        info.setSpacing(4)
        info.addWidget(name_btn)
        info.addWidget(pkg_id)
        info.addSpacing(4)
        info.addLayout(meta_row)

        # actions (right side)
        self._add_btn = QPushButton("+ Ajouter")
        self._add_btn.setObjectName("add")
        self._add_btn.setCheckable(True)
        self._add_btn.setCursor(Qt.PointingHandCursor)
        self._add_btn.toggled.connect(self._on_bundle_toggled)

        self._install_btn = QPushButton("Installer")
        self._install_btn.setObjectName("primary")
        self._install_btn.setCursor(Qt.PointingHandCursor)
        self._install_btn.clicked.connect(self._emit_install)

        self._installed_badge = QLabel("Installé ✓")
        self._installed_badge.setObjectName("installedBadge")
        self._installed_badge.hide()

        self._update_btn = QPushButton("Mettre à jour")
        self._update_btn.setObjectName("primary")
        self._update_btn.setCursor(Qt.PointingHandCursor)
        self._update_btn.clicked.connect(self._emit_update)
        self._update_btn.hide()

        self._spinner = Spinner(size=20, line_width=2)
        self._spinner.hide()

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self._add_btn)
        actions.addWidget(self._spinner)
        actions.addWidget(self._install_btn)
        actions.addWidget(self._update_btn)
        actions.addWidget(self._installed_badge)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(16)
        root.addLayout(info, stretch=1)
        root.addLayout(actions)

    # ---- API publique ----------------------------------------------------

    @property
    def package(self) -> WingetPackage:
        return self._package

    def set_already_installed(self, installed: bool, upgradable: bool = False) -> None:
        self.setProperty("installed", installed)
        self.style().unpolish(self)
        self.style().polish(self)

        self._installed_badge.setVisible(installed and not upgradable)
        self._install_btn.setVisible(not installed)
        self._update_btn.setVisible(installed and upgradable)
        self._add_btn.setVisible(True)

    def set_bundle_state(self, in_bundle: bool) -> None:
        # éviter une boucle si on synchronise depuis l'extérieur
        self._add_btn.blockSignals(True)
        self._add_btn.setChecked(in_bundle)
        self._add_btn.setText("✓ Sélectionné" if in_bundle else "+ Ajouter")
        self._add_btn.blockSignals(False)

    def mark_installing(self) -> None:
        self._install_btn.hide()
        self._spinner.show()
        self._spinner.start()

    def mark_install_result(self, success: bool) -> None:
        self._spinner.stop()
        self._spinner.hide()
        if success:
            self.set_already_installed(True)
            self.set_bundle_state(False)
        else:
            self._install_btn.show()
            self._install_btn.setEnabled(True)
            self._install_btn.setText("Réessayer")

    def mark_updating(self) -> None:
        self._update_btn.hide()
        self._spinner.show()
        self._spinner.start()

    def mark_update_result(self, success: bool) -> None:
        self._spinner.stop()
        self._spinner.hide()
        if success:
            self.set_already_installed(True, upgradable=False)
        else:
            self._update_btn.show()
            self._update_btn.setEnabled(True)
            self._update_btn.setText("Réessayer")

    # ---- callbacks internes ----------------------------------------------

    def _on_bundle_toggled(self, checked: bool) -> None:
        self._add_btn.setText("✓ Sélectionné" if checked else "+ Ajouter")
        self.bundle_toggled.emit(self._package, checked)

    def _emit_install(self) -> None:
        self.mark_installing()
        self.install_requested.emit(self._package)

    def _emit_update(self) -> None:
        self.mark_updating()
        self.update_requested.emit(self._package)

    def _emit_detail(self) -> None:
        self.detail_requested.emit(self._package)
