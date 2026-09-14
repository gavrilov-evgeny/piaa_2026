from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QVBoxLayout,
)

HINT_COLOR = "gray"


class ChoiceBoard(QGroupBox):
    """Поля ручного ввода для алгоритма Ахо — Корасик."""

    def __init__(self, parent=None):
        super().__init__("Входные данные", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        hint = QLabel("Введите текст и шаблоны для поиска.")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()

        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("hisher")
        self.text_edit.setClearButtonEnabled(True)
        form.addRow("Текст:", self.text_edit)

        self.patterns_edit = QPlainTextEdit()
        self.patterns_edit.setPlaceholderText("he\nshe\nhers")
        self.patterns_edit.setMinimumHeight(150)
        form.addRow("Шаблоны:", self.patterns_edit)

        layout.addLayout(form)

        note = QLabel("Один шаблон на строчку")
        note.setStyleSheet(f"color: {HINT_COLOR};")
        layout.addWidget(note)

    def get_input(self) -> tuple[str, list[str]]:
        text = self.text_edit.text()
        patterns = [
            line.strip()
            for line in self.patterns_edit.toPlainText().splitlines()
            if line.strip()
        ]
        return text, patterns
