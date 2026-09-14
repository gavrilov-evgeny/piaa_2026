from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from algo.AhoCorasick import Trie
from gui.pages.choice_board import ChoiceBoard
from gui.pages.results_panel import ResultsPanel
from gui.pages.trie_view import (
    EXIT_COLOR,
    SUFFIX_COLOR,
    TERMINAL_COLOR,
    TrieView,
)


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.choice_board = ChoiceBoard()
        left_layout.addWidget(self.choice_board)

        run_button = QPushButton("Построить бор и найти вхождения")
        run_button.clicked.connect(self._on_run_clicked)
        left_layout.addWidget(run_button)

        self.result_panel = ResultsPanel()
        left_layout.addWidget(self.result_panel)
        left_layout.addStretch()

        left_widget.setMinimumWidth(320)
        left_widget.setMaximumWidth(430)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Trie")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(title)

        legend = QLabel(
            f"<span style='color:{TERMINAL_COLOR.name()}'>● конец шаблона</span> "
            f"&nbsp; <span style='color:{SUFFIX_COLOR.name()}'>--> suff</span> "
            f"&nbsp; <span style='color:{EXIT_COLOR.name()}'>--> exit</span>"
        )
        legend.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(legend)

        self.trie_view = TrieView()
        right_layout.addWidget(self.trie_view, 1)
        splitter.addWidget(right_widget)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def _on_run_clicked(self):
        text, patterns = self.choice_board.get_input()
        if not text:
            QMessageBox.warning(self, "Нет текста", "Введите текст для поиска.")
            return
        if not patterns:
            QMessageBox.warning(self, "Нет шаблонов", "Введите хотя бы один шаблон.")
            return
        if len(set(patterns)) != len(patterns):
            QMessageBox.warning(
                self,
                "Повторяющиеся шаблоны",
                "Каждый шаблон должен встречаться в списке один раз.",
            )
            return

        trie = Trie(patterns)
        matches = trie.search(text)

        matches.sort()
        self.trie_view.set_trie(trie)
        self.result_panel.update_results(trie, patterns, matches)
