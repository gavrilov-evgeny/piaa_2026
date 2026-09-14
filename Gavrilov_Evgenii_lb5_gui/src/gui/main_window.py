from PySide6.QtWidgets import QMainWindow

from gui.pages.dashboard_page import DashboardPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Алгоритм Ахо — Корасик")
        self.setMinimumSize(1100, 650)
        self.setCentralWidget(DashboardPage())
