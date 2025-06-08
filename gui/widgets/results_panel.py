from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QGridLayout
from PyQt6.QtCore import Qt

class ResultsPanel(QWidget):
    """
    用于显示数值计算结果的面板。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件。"""
        main_layout = QVBoxLayout(self)
        group = QGroupBox("数值结果")
        self.grid_layout = QGridLayout()
        group.setLayout(self.grid_layout)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

        # 初始提示信息
        self.info_label = QLabel("请先运行计算...")
        self.grid_layout.addWidget(self.info_label, 0, 0, 1, 4)

    def update_results(self, result):
        """
        用计算结果更新面板显示。

        Args:
            result (FemResult): 包含所有计算结果的数据对象。
        """
        # 清除旧内容
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not result or not result.target_displacements:
            self.grid_layout.addWidget(QLabel("计算失败或无目标点结果。"), 0, 0)
            return

        # 创建表头
        headers = ["点名称", "水平位移 (m)", "竖直位移 (m)"]
        for col, header in enumerate(headers):
            self.grid_layout.addWidget(QLabel(f"<b>{header}</b>"), 0, col)

        # 填充数据
        row = 1
        for name, (dx, dy) in result.target_displacements.items():
            self.grid_layout.addWidget(QLabel(name), row, 0)
            # 使用科学记数法格式化输出
            self.grid_layout.addWidget(QLabel(f"{dx:.4e}"), row, 1)
            self.grid_layout.addWidget(QLabel(f"{dy:.4e}"), row, 2)
            row += 1

    def clear(self):
        """清除显示，恢复到初始状态。"""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.info_label = QLabel("请先运行计算...")
        self.grid_layout.addWidget(self.info_label, 0, 0, 1, 4)

