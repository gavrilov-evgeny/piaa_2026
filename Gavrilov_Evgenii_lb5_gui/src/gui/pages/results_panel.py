from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QPlainTextEdit


class ResultsPanel(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Результаты", parent)
        self._setup_ui()
        self.clear()

    def _setup_ui(self):
        form = QFormLayout(self)

        self.nodes_label = QLabel()
        form.addRow("Вершин в боре:", self.nodes_label)

        self.count_label = QLabel()
        form.addRow("Совпадений:", self.count_label)

        self.matches_edit = QPlainTextEdit()
        self.matches_edit.setReadOnly(True)
        self.matches_edit.setMaximumHeight(180)
        form.addRow("Позиции:", self.matches_edit)

    def clear(self):
        self.nodes_label.setText("-")
        self.count_label.setText("-")
        self.matches_edit.setPlainText("-")

    def update_results(
        self,
        trie,
        patterns: list[str],
        matches: list[tuple[int, int]],
    ):
        self.nodes_label.setText(str(self._count_nodes(trie.root)))
        self.count_label.setText(str(len(matches)))

        if not matches:
            self.matches_edit.setPlainText("Совпадений не найдено")
            return

        self.matches_edit.setPlainText(
            "\n".join(
                f"{position} — шаблон {pattern_index} «{patterns[pattern_index - 1]}»"
                for position, pattern_index in matches
            )
        )

    @staticmethod
    def _count_nodes(root) -> int:
        count = 0
        stack = [root]
        while stack:
            node = stack.pop()
            count += 1
            stack.extend(node.children.values())
        return count
