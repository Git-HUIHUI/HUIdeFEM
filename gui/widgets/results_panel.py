from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont  # 确保QFont已导入
import os

class ResultsPanel(QWidget):
    """用于显示数值计算结果的面板。"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)  # 增加最小高度
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件。"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)  # 增加间距
        
        # 获取图标路径
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icons')
        
        # 设置字体
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        
        content_font = QFont()
        content_font.setPointSize(10)
        
        # 创建带图标的标题布局
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        # 添加图标标签
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(os.path.join(icon_path, '数值结果.png')).pixmap(24, 24))  # 放大图标
        title_layout.addWidget(icon_label)
        
        # 添加标题文本
        title_label = QLabel("数值结果")
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        
        # 创建结果显示区域
        group = QGroupBox()
        group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(8)  # 增加网格间距
        group.setLayout(self.grid_layout)
        main_layout.addWidget(group)
        self.setLayout(main_layout)

        # 初始提示信息
        self.info_label = QLabel("请先运行计算...")
        self.info_label.setFont(content_font)
        self.grid_layout.addWidget(self.info_label, 0, 0, 1, 4)

    def update_results(self, result):
        """用计算结果更新面板显示。"""
        # 清除旧内容
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not result or not result.target_displacements:
            error_label = QLabel("计算失败或无目标点结果。")
            error_label.setFont(QFont("Arial", 10))
            self.grid_layout.addWidget(error_label, 0, 0)
            return

        # 设置字体
        header_font = QFont()
        header_font.setPointSize(10)
        header_font.setBold(True)
        
        content_font = QFont()
        content_font.setPointSize(9)

        # 创建表头
        headers = ["点名称", "水平位移 (m)", "竖直位移 (m)"]
        for col, header in enumerate(headers):
            header_label = QLabel(f"<b>{header}</b>")
            header_label.setFont(header_font)
            header_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
            self.grid_layout.addWidget(header_label, 0, col)

        # 填充数据
        row = 1
        for name, (dx, dy) in result.target_displacements.items():
            name_label = QLabel(name)
            name_label.setFont(content_font)
            name_label.setStyleSheet("padding: 3px;")
            self.grid_layout.addWidget(name_label, row, 0)
            
            dx_label = QLabel(f"{dx:.4e}")
            dx_label.setFont(content_font)
            dx_label.setStyleSheet("padding: 3px;")
            self.grid_layout.addWidget(dx_label, row, 1)
            
            dy_label = QLabel(f"{dy:.4e}")
            dy_label.setFont(content_font)
            dy_label.setStyleSheet("padding: 3px;")
            self.grid_layout.addWidget(dy_label, row, 2)
            
            row += 1

    def clear(self):
        """清除显示，恢复到初始状态。"""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.info_label = QLabel("请先运行计算...")
        self.grid_layout.addWidget(self.info_label, 0, 0, 1, 4)

