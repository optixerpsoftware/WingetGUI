from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)


class ImportSelectionDialog(QDialog):
    """Dialogue de sélection des paquets à installer depuis un import.

    Affiche la liste détaillée des paquets, permet d'en exclure individuellement.
    Les paquets déjà installés sont marqués et désélectionnés par défaut.
    """

    def __init__(self, ids: list[str], installed_ids: set[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importer une configuration")
        self.resize(640, 560)
        self.setModal(True)

        self._checks: dict[str, QCheckBox] = {}
        self._installed_ids = installed_ids
        self._build_ui(ids)

    def _build_ui(self, ids: list[str]) -> None:
        title = QLabel(f"{len(ids)} paquet(s) trouvé(s) dans le fichier")
        title.setObjectName("title")

        n_already = sum(1 for pid in ids if pid in self._installed_ids)
        subtitle = QLabel(
            f"Décochez les paquets que vous ne voulez pas installer."
            + (f" {n_already} déjà installé(s)." if n_already else "")
        )
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)

        select_all_btn = QPushButton("Tout cocher")
        select_all_btn.setObjectName("ghost")
        select_all_btn.setCursor(Qt.PointingHandCursor)
        select_all_btn.clicked.connect(lambda: self._set_all(True))

        select_none_btn = QPushButton("Tout décocher")
        select_none_btn.setObjectName("ghost")
        select_none_btn.setCursor(Qt.PointingHandCursor)
        select_none_btn.clicked.connect(lambda: self._set_all(False))

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        toolbar.addWidget(select_all_btn)
        toolbar.addWidget(select_none_btn)
        toolbar.addStretch()

        # liste des paquets
        list_host = QWidget()
        list_layout = QVBoxLayout(list_host)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(6)

        for pid in ids:
            list_layout.addWidget(self._build_row(pid))
        list_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(list_host)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Installer la sélection")
        buttons.button(QDialogButtonBox.Ok).setObjectName("primary")
        buttons.button(QDialogButtonBox.Cancel).setText("Annuler")
        buttons.button(QDialogButtonBox.Cancel).setObjectName("ghost")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._buttons = buttons
        self._update_ok_label()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 16)
        root.setSpacing(10)
        root.addWidget(title)
        root.addWidget(subtitle)
        root.addLayout(toolbar)
        root.addWidget(scroll, stretch=1)
        root.addWidget(buttons)

    def _build_row(self, pid: str) -> QFrame:
        already_installed = pid in self._installed_ids

        check = QCheckBox(pid)
        check.setChecked(not already_installed)
        check.toggled.connect(self._update_ok_label)
        self._checks[pid] = check

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setSpacing(10)
        row_layout.addWidget(check, stretch=1)

        if already_installed:
            badge = QLabel("Déjà installé")
            badge.setObjectName("installedBadge")
            row_layout.addWidget(badge)

        row = QFrame()
        row.setObjectName("card")
        row.setLayout(row_layout)
        return row

    def _set_all(self, checked: bool) -> None:
        for check in self._checks.values():
            check.setChecked(checked)

    def _update_ok_label(self) -> None:
        n = sum(1 for c in self._checks.values() if c.isChecked())
        ok = self._buttons.button(QDialogButtonBox.Ok)
        ok.setEnabled(n > 0)
        ok.setText(f"Installer la sélection ({n})" if n else "Installer la sélection")

    def selected_ids(self) -> list[str]:
        return [pid for pid, c in self._checks.items() if c.isChecked()]
