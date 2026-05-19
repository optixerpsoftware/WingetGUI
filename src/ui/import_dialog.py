from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QFrame, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from src.winget import Winget


class _NameResolverWorker(QThread):
    """Résout en arrière-plan les noms des paquets non installés via winget search."""

    name_resolved = Signal(str, str)  # id, name

    def __init__(self, ids: list[str], winget: Winget, parent=None):
        super().__init__(parent)
        self._ids = ids
        self._winget = winget
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        for pid in self._ids:
            if self._cancelled:
                return
            results = self._winget.search(pid)
            for pkg in results:
                if pkg.id == pid:
                    self.name_resolved.emit(pid, pkg.name)
                    break


class ImportSelectionDialog(QDialog):
    """Dialogue de sélection des paquets à installer depuis un import.

    Affiche la liste détaillée des paquets, permet d'en exclure individuellement.
    Les paquets déjà installés sont marqués et désélectionnés par défaut.
    Les noms des paquets non installés sont résolus en arrière-plan.
    """

    def __init__(self, ids: list[str], name_by_id: dict[str, str],
                 installed_ids: set[str], winget: Winget | None = None,
                 parent=None):
        super().__init__(parent)
        self.setWindowTitle("Importer une configuration")
        self.resize(640, 560)
        self.setModal(True)

        self._checks: dict[str, QCheckBox] = {}
        self._name_labels: dict[str, QLabel] = {}
        self._id_labels: dict[str, QLabel] = {}
        self._name_by_id = dict(name_by_id)
        self._installed_ids = installed_ids
        self._winget = winget
        self._resolver: _NameResolverWorker | None = None

        self._build_ui(ids)
        self._start_resolver(ids)

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
        name = self._name_by_id.get(pid, "")

        check = QCheckBox()
        check.setChecked(not already_installed)
        check.toggled.connect(self._update_ok_label)
        self._checks[pid] = check

        name_label = QLabel(name if name else "Résolution du nom…")
        name_label.setObjectName("importName")
        name_label.setWordWrap(True)
        if not name:
            name_label.setProperty("pending", True)
        self._name_labels[pid] = name_label

        id_label = QLabel(pid)
        id_label.setObjectName("importId")
        id_label.setWordWrap(True)
        self._id_labels[pid] = id_label

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.addWidget(name_label)
        text_col.addWidget(id_label)

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setSpacing(10)
        row_layout.addWidget(check)
        row_layout.addLayout(text_col, stretch=1)

        if already_installed:
            badge = QLabel("Déjà installé")
            badge.setObjectName("installedBadge")
            row_layout.addWidget(badge)

        row = QFrame()
        row.setObjectName("card")
        row.setLayout(row_layout)
        return row

    def _start_resolver(self, ids: list[str]) -> None:
        if not self._winget:
            return
        unknown = [pid for pid in ids if pid not in self._name_by_id]
        if not unknown:
            return
        self._resolver = _NameResolverWorker(unknown, self._winget, self)
        self._resolver.name_resolved.connect(self._on_name_resolved)
        self._resolver.start()

    def _on_name_resolved(self, pid: str, name: str) -> None:
        self._name_by_id[pid] = name
        label = self._name_labels.get(pid)
        if label:
            label.setText(name)
            label.setProperty("pending", False)
            label.style().unpolish(label)
            label.style().polish(label)

    def closeEvent(self, event) -> None:  # noqa: N802
        if self._resolver:
            self._resolver.cancel()
        super().closeEvent(event)

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
