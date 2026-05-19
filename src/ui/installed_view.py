from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QVBoxLayout, QWidget,
)

from src.ui.spinner import SpinnerWithLabel
from src.winget import WingetPackage


class InstalledCard(QFrame):
    """Carte d'un paquet installé : actions Mettre à jour / Désinstaller."""

    update_requested    = Signal(WingetPackage)
    uninstall_requested = Signal(WingetPackage)

    def __init__(self, package: WingetPackage, upgradable: bool, parent=None):
        super().__init__(parent)
        self._package = package
        self._upgradable = upgradable
        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setProperty("installed", True)
        self._build_layout(upgradable)

    def _build_layout(self, upgradable: bool) -> None:
        name = QLabel(self._package.name)
        name.setObjectName("cardName")
        name.setWordWrap(True)

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
        if upgradable:
            up_badge = QLabel("Mise à jour disponible")
            up_badge.setObjectName("upgradeBadge")
            meta_row.addWidget(up_badge)
        meta_row.addStretch()

        info = QVBoxLayout()
        info.setSpacing(4)
        info.addWidget(name)
        info.addWidget(pkg_id)
        info.addSpacing(4)
        info.addLayout(meta_row)

        self._update_btn = QPushButton("Mettre à jour")
        self._update_btn.setObjectName("primary")
        self._update_btn.setCursor(Qt.PointingHandCursor)
        self._update_btn.clicked.connect(self._emit_update)
        self._update_btn.setVisible(upgradable)

        self._uninstall_btn = QPushButton("Désinstaller")
        self._uninstall_btn.setObjectName("danger")
        self._uninstall_btn.setCursor(Qt.PointingHandCursor)
        self._uninstall_btn.clicked.connect(self._emit_uninstall)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self._update_btn)
        actions.addWidget(self._uninstall_btn)

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(16)
        root.addLayout(info, stretch=1)
        root.addLayout(actions)

    @property
    def package(self) -> WingetPackage:
        return self._package

    def mark_busy(self, label: str) -> None:
        self._update_btn.setEnabled(False)
        self._uninstall_btn.setEnabled(False)
        self._update_btn.setText(label)

    def mark_result(self, success: bool, action: str) -> None:
        self._update_btn.setEnabled(True)
        self._uninstall_btn.setEnabled(True)
        self._update_btn.setText("Mettre à jour")
        self._update_btn.setVisible(self._upgradable and not success
                                    if action == "Mise à jour"
                                    else self._upgradable)
        if not success:
            self._update_btn.setVisible(True)
            self._update_btn.setText(f"{action} échoué")

    def _emit_update(self) -> None:
        self.mark_busy("Mise à jour…")
        self.update_requested.emit(self._package)

    def _emit_uninstall(self) -> None:
        self.mark_busy("Désinstallation…")
        self.uninstall_requested.emit(self._package)


class InstalledView(QWidget):
    """Vue des paquets installés avec actions de mise à jour et désinstallation."""

    refresh_requested   = Signal()
    update_requested    = Signal(WingetPackage)
    uninstall_requested = Signal(WingetPackage)
    upgrade_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: dict[str, InstalledCard] = {}
        self._packages: list[WingetPackage] = []
        self._upgradable: set[str] = set()
        self._filter_text: str = ""
        self._only_upgradable: bool = False
        self._build_ui()

    def _build_ui(self) -> None:
        title = QLabel("Paquets installés")
        title.setObjectName("title")

        subtitle = QLabel("Mettez à jour ou désinstallez les paquets présents sur le système")
        subtitle.setObjectName("subtitle")

        self._refresh_btn = QPushButton("🔄  Actualiser")
        self._refresh_btn.setObjectName("ghost")
        self._refresh_btn.setCursor(Qt.PointingHandCursor)
        self._refresh_btn.clicked.connect(self.refresh_requested.emit)

        self._only_upgradable_btn = QPushButton("Mises à jour disponibles")
        self._only_upgradable_btn.setObjectName("ghost")
        self._only_upgradable_btn.setCheckable(True)
        self._only_upgradable_btn.setCursor(Qt.PointingHandCursor)
        self._only_upgradable_btn.toggled.connect(self._on_only_upgradable_toggled)

        self._upgrade_all_btn = QPushButton("Tout mettre à jour")
        self._upgrade_all_btn.setObjectName("primary")
        self._upgrade_all_btn.setCursor(Qt.PointingHandCursor)
        self._upgrade_all_btn.setEnabled(False)
        self._upgrade_all_btn.clicked.connect(self.upgrade_all_requested.emit)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        toolbar.addWidget(self._refresh_btn)
        toolbar.addWidget(self._only_upgradable_btn)
        toolbar.addStretch()
        toolbar.addWidget(self._upgrade_all_btn)

        self._filter = QLineEdit()
        self._filter.setObjectName("search")
        self._filter.setPlaceholderText("Filtrer la liste des paquets installés…")
        self._filter.textChanged.connect(self._on_filter_changed)

        self._results_host = QWidget()
        self._results_layout = QVBoxLayout(self._results_host)
        self._results_layout.setContentsMargins(0, 0, 0, 0)
        self._results_layout.setSpacing(10)
        self._results_layout.addStretch()

        self._placeholder = QLabel("Chargement…")
        self._placeholder.setObjectName("subtitle")
        self._placeholder.setAlignment(Qt.AlignCenter)
        self._results_layout.insertWidget(0, self._placeholder)

        self._loading = SpinnerWithLabel("Analyse des paquets installés…")
        self._loading.hide()
        self._results_layout.insertWidget(1, self._loading)

        scroll = QScrollArea()
        scroll.setWidget(self._results_host)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 16)
        root.setSpacing(12)
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addSpacing(4)
        root.addLayout(toolbar)
        root.addWidget(self._filter)
        root.addSpacing(4)
        root.addWidget(scroll, stretch=1)

    # ---- API publique ----------------------------------------------------

    def set_loading(self, loading: bool) -> None:
        self._refresh_btn.setEnabled(not loading)
        self._refresh_btn.setText("Chargement…" if loading else "🔄  Actualiser")
        if loading:
            self._clear_cards()
            self._placeholder.hide()
            self._loading.start()
        else:
            self._loading.stop()

    def show_packages(self, packages: list[WingetPackage], upgradable: set[str]) -> None:
        self._packages = packages
        self._upgradable = upgradable
        self._upgrade_all_btn.setEnabled(len(upgradable) > 0)
        if upgradable:
            self._upgrade_all_btn.setText(f"Tout mettre à jour ({len(upgradable)})")
            self._only_upgradable_btn.setText(f"Mises à jour disponibles ({len(upgradable)})")
            self._only_upgradable_btn.setEnabled(True)
        else:
            self._upgrade_all_btn.setText("Tout mettre à jour")
            self._only_upgradable_btn.setText("Mises à jour disponibles")
            # rien à filtrer : on désactive et on relâche le bouton
            self._only_upgradable_btn.setChecked(False)
            self._only_upgradable_btn.setEnabled(False)
        self._render()

    def show_error(self, message: str) -> None:
        self._clear_cards()
        self._placeholder.setText(f"Erreur : {message}")
        self._placeholder.show()

    def mark_action_result(self, package: WingetPackage, success: bool, action: str) -> None:
        card = self._cards.get(package.id)
        if card:
            card.mark_result(success, action)

    @property
    def upgradable_ids(self) -> set[str]:
        return self._upgradable

    @property
    def packages(self) -> list[WingetPackage]:
        return self._packages

    # ---- interne ---------------------------------------------------------

    def _on_filter_changed(self, text: str) -> None:
        self._filter_text = text.strip().lower()
        self._render()

    def _on_only_upgradable_toggled(self, checked: bool) -> None:
        self._only_upgradable = checked
        self._render()

    def _render(self) -> None:
        self._clear_cards()
        filtered = [
            p for p in self._packages
            if (not self._only_upgradable or p.id in self._upgradable)
            and (not self._filter_text
                 or self._filter_text in p.name.lower()
                 or self._filter_text in p.id.lower())
        ]
        if not filtered:
            if not self._packages:
                msg = "Aucun paquet installé."
            elif self._only_upgradable:
                msg = "Aucune mise à jour disponible."
            else:
                msg = "Aucun paquet ne correspond au filtre."
            self._placeholder.setText(msg)
            self._placeholder.show()
            return

        self._placeholder.hide()
        for pkg in filtered:
            card = InstalledCard(pkg, pkg.id in self._upgradable)
            card.update_requested.connect(self.update_requested.emit)
            card.uninstall_requested.connect(self.uninstall_requested.emit)
            self._cards[pkg.id] = card
            self._results_layout.insertWidget(self._results_layout.count() - 1, card)

    def _clear_cards(self) -> None:
        for card in self._cards.values():
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()
