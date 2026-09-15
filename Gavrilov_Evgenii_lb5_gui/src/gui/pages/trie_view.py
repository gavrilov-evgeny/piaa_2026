import math
from algo.AhoCorasick import TrieNode

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QVBoxLayout,
    QWidget,
)

NODE_RADIUS = 20
HORIZONTAL_GAP = 100
VERTICAL_GAP = 100
FIT_MARGIN = 35

NODE_COLOR = QColor("white")
TERMINAL_COLOR = QColor("darkGray")
TREE_COLOR = QColor("black")
SUFFIX_COLOR = QColor("darkGray")
EXIT_COLOR = QColor("darkRed")
SCENE_COLOR = QColor("whitesmoke")
TREE_LINE_WIDTH = 2


class StaticGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setInteractive(False)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def fit_content(self):
        self.resetTransform()
        rect = self.scene().itemsBoundingRect()
        if rect.isNull():
            return
        rect.adjust(-FIT_MARGIN, -FIT_MARGIN, FIT_MARGIN, FIT_MARGIN)
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_content()

    def wheelEvent(self, event):
        event.accept()


class TrieView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(SCENE_COLOR)
        self.view = StaticGraphicsView(self.scene)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)

    def set_trie(self, trie) -> None:
        self.scene.clear()
        positions: dict[TrieNode, QPointF] = {}
        next_leaf = 0

        def place(node, depth: int) -> float:
            nonlocal next_leaf
            children = list(node.children.values())
            if children:
                child_x = [place(child, depth + 1) for child in children]
                x = sum(child_x) / len(child_x)
            else:
                x = next_leaf * HORIZONTAL_GAP
                next_leaf += 1
            positions[node] = QPointF(x, depth * VERTICAL_GAP)
            return x

        place(trie.root, 0)

        for node, start in positions.items():
            if node is trie.root:
                continue
            if node.suff is not None:
                self._draw_link(
                    start,
                    positions[node.suff],
                    SUFFIX_COLOR,
                    Qt.PenStyle.DashLine,
                    28,
                )
            if node.exit is not None:
                self._draw_link(
                    start,
                    positions[node.exit],
                    EXIT_COLOR,
                    Qt.PenStyle.DashDotLine,
                    -28,
                )

        for node, parent_pos in positions.items():
            for char, child in node.children.items():
                self._draw_edge(parent_pos, positions[child], char)

        for node, pos in positions.items():
            self._draw_node(
                pos,
                is_terminal=node.isTerminal,
            )

        self.view.fit_content()

    def _draw_edge(self, start: QPointF, end: QPointF, char: str) -> None:
        edge_start, edge_end = self._edge_points(start, end)
        line = QGraphicsLineItem(
            edge_start.x(),
            edge_start.y(),
            edge_end.x(),
            edge_end.y(),
        )
        line.setPen(QPen(TREE_COLOR, TREE_LINE_WIDTH))
        self.scene.addItem(line)

        label = QGraphicsSimpleTextItem(char)
        label.setBrush(QBrush(TREE_COLOR))
        label.setFont(QFont("Sans Serif", 8, QFont.Weight.DemiBold))
        midpoint = line.line().pointAt(0.5)
        bounds = label.boundingRect()
        label.setPos(midpoint.x() - bounds.width() / 2 + 7, midpoint.y() - 10)
        label.setZValue(2)
        self.scene.addItem(label)

    def _draw_link(
        self,
        start: QPointF,
        end: QPointF,
        color: QColor,
        style: Qt.PenStyle,
        curve_offset: float,
    ) -> None:
        edge_start, edge_end = self._edge_points(start, end)
        dx = edge_end.x() - edge_start.x()
        dy = edge_end.y() - edge_start.y()
        distance = math.hypot(dx, dy)
        if distance == 0:
            return

        control = QPointF(
            (edge_start.x() + edge_end.x()) / 2 - dy / distance * curve_offset,
            (edge_start.y() + edge_end.y()) / 2 + dx / distance * curve_offset,
        )
        path = QPainterPath(edge_start)
        path.quadTo(control, edge_end)

        link = QGraphicsPathItem(path)
        link.setPen(QPen(color, 1.8, style))
        link.setZValue(-2)
        self.scene.addItem(link)

        angle = math.atan2(edge_end.y() - control.y(), edge_end.x() - control.x())
        arrow_size = 8
        arrow = QPolygonF(
            [
                edge_end,
                QPointF(
                    edge_end.x() - arrow_size * math.cos(angle - 0.5),
                    edge_end.y() - arrow_size * math.sin(angle - 0.5),
                ),
                QPointF(
                    edge_end.x() - arrow_size * math.cos(angle + 0.5),
                    edge_end.y() - arrow_size * math.sin(angle + 0.5),
                ),
            ]
        )
        arrow_item = QGraphicsPolygonItem(arrow)
        arrow_item.setBrush(QBrush(color))
        arrow_item.setPen(QPen(color))
        arrow_item.setZValue(-1)
        self.scene.addItem(arrow_item)

    @staticmethod
    def _edge_points(start: QPointF, end: QPointF) -> tuple[QPointF, QPointF]:
        dx = end.x() - start.x()
        dy = end.y() - start.y()
        distance = math.hypot(dx, dy)
        if distance == 0:
            return start, end

        ux = dx / distance
        uy = dy / distance
        return (
            QPointF(start.x() + ux * NODE_RADIUS, start.y() + uy * NODE_RADIUS),
            QPointF(end.x() - ux * NODE_RADIUS, end.y() - uy * NODE_RADIUS),
        )

    def _draw_node(
        self,
        center: QPointF,
        is_terminal: bool,
    ) -> None:
        if is_terminal:
            color = TERMINAL_COLOR
        else:
            color = NODE_COLOR

        diameter = NODE_RADIUS * 2
        node = QGraphicsEllipseItem(
            center.x() - NODE_RADIUS,
            center.y() - NODE_RADIUS,
            diameter,
            diameter,
        )
        node.setBrush(QBrush(color))
        node.setPen(QPen(TREE_COLOR, TREE_LINE_WIDTH))
        node.setZValue(1)
        self.scene.addItem(node)
