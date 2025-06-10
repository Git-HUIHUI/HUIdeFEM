import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, 
    QTableWidgetItem, QPushButton, QComboBox, QLabel, QSpinBox, 
    QDoubleSpinBox, QCheckBox, QHeaderView, QFormLayout, QLineEdit  # 添加 QFormLayout 和 QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class InputPanel(QWidget):
    """
    用于用户输入所有模型数据的面板。
    当任何数据发生变化时，会发出信号。
    """
    data_changed = pyqtSignal()

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._init_ui()

    def _init_ui(self):
        """初始化UI组件。"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-bottom: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                min-width: 80px;
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1976d2;
                border-bottom: 2px solid #1976d2;
                font-weight: bold;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e3f2fd;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
        """)
        
        # 获取图标路径
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icons')
        
        # 创建各个选项卡页面
        vertices_widget, self.vertices_table = self._create_tab_page("定义顶点", ["ID", "X 坐标", "Y 坐标"])
        segments_widget, self.segments_table = self._create_tab_page("定义线段", ["ID", "起始点 ID", "结束点 ID"])
        regions_widget, self.regions_table = self._create_tab_page("定义区域", ["区域点 X", "区域点 Y", "材料"])
        bc_widget, self.bc_table = self._create_tab_page("边界条件", ["线段 ID", "约束类型", "荷载 Q (N/m)"])
        targets_widget, self.targets_table = self._create_tab_page("目标点", ["点名称", "X 坐标", "Y 坐标"])
        mesh_widget = self._create_mesh_settings_page()
        export_widget = self._create_export_page()
        
        # 添加选项卡页面并设置图标
        self.tab_widget.addTab(vertices_widget, "1. 顶点")
        if os.path.exists(os.path.join(icon_path, '顶点.png')):
            self.tab_widget.setTabIcon(0, QIcon(os.path.join(icon_path, '顶点.png')))
            
        self.tab_widget.addTab(segments_widget, "2. 线段")
        if os.path.exists(os.path.join(icon_path, '线段.png')):
            self.tab_widget.setTabIcon(1, QIcon(os.path.join(icon_path, '线段.png')))
            
        self.tab_widget.addTab(regions_widget, "3. 区域")
        if os.path.exists(os.path.join(icon_path, '区域.png')):
            self.tab_widget.setTabIcon(2, QIcon(os.path.join(icon_path, '区域.png')))
            
        self.tab_widget.addTab(bc_widget, "4. 边界")
        if os.path.exists(os.path.join(icon_path, '边界.png')):
            self.tab_widget.setTabIcon(3, QIcon(os.path.join(icon_path, '边界.png')))
            
        self.tab_widget.addTab(targets_widget, "5. 目标点")
        if os.path.exists(os.path.join(icon_path, '目标点.png')):
            self.tab_widget.setTabIcon(4, QIcon(os.path.join(icon_path, '目标点.png')))
            
        self.tab_widget.addTab(mesh_widget, "6. 网格设置")
        if os.path.exists(os.path.join(icon_path, '网格设置.png')):
            self.tab_widget.setTabIcon(5, QIcon(os.path.join(icon_path, '网格设置.png')))
            
        self.tab_widget.addTab(export_widget, "7. 导出结果")
        if os.path.exists(os.path.join(icon_path, '导出结果.png')):
            self.tab_widget.setTabIcon(6, QIcon(os.path.join(icon_path, '导出结果.png')))

        # 连接按钮事件
        vertices_widget.findChild(QPushButton, "add_button").clicked.connect(self._add_vertex_row)
        vertices_widget.findChild(QPushButton, "remove_button").clicked.connect(lambda: self._remove_generic_row(self.vertices_table, True))
        
        segments_widget.findChild(QPushButton, "add_button").clicked.connect(self._add_segment_row)
        segments_widget.findChild(QPushButton, "remove_button").clicked.connect(lambda: self._remove_generic_row(self.segments_table, True))
        
        regions_widget.findChild(QPushButton, "add_button").clicked.connect(self._add_region_row)
        regions_widget.findChild(QPushButton, "remove_button").clicked.connect(lambda: self._remove_generic_row(self.regions_table, False))
        
        bc_widget.findChild(QPushButton, "add_button").clicked.connect(self._add_bc_row)
        bc_widget.findChild(QPushButton, "remove_button").clicked.connect(lambda: self._remove_generic_row(self.bc_table, False))
        
        targets_widget.findChild(QPushButton, "add_button").clicked.connect(self._add_target_row)
        targets_widget.findChild(QPushButton, "remove_button").clicked.connect(lambda: self._remove_generic_row(self.targets_table, False))

        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def _create_tab_page(self, title, headers):
        """创建选项卡页面，包含表格和按钮。"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建表格
        table = QTableWidget(objectName=title)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # 设置表格行高
        table.verticalHeader().setDefaultSectionSize(50)  # 设置默认行高为50像素
        table.verticalHeader().setMinimumSectionSize(45)  # 设置最小行高为45像素
        
        # 设置表格列宽调整模式
        header = table.horizontalHeader()
        from PyQt6.QtWidgets import QHeaderView
        
        # 根据不同的表格设置不同的列宽策略
        if title == "定义区域":
            # 区域表格：X坐标、Y坐标列固定宽度，材料列拉伸填充
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            table.setColumnWidth(0, 100)  # X坐标列宽度
            table.setColumnWidth(1, 100)  # Y坐标列宽度
        elif title == "边界条件":
            # 边界条件表格：线段ID列固定，约束类型列拉伸，荷载列固定
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            table.setColumnWidth(0, 80)   # 线段ID列宽度
            table.setColumnWidth(2, 120)  # 荷载列宽度
        else:
            # 其他表格使用默认的拉伸模式
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                gridline-color: #f0f0f0;
                selection-background-color: #e3f2fd;
            }
            
            QTableWidget::item {
                padding: 15px 8px;  /* 进一步增加垂直内边距 */
                border: none;
                min-height: 30px;   /* 增加最小高度 */
            }
            
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QHeaderView::section {
                background-color: #f8f9fa;
                border: none;
                border-bottom: 1px solid #e0e0e0;
                border-right: 1px solid #e0e0e0;
                padding: 15px 10px;  /* 增加表头内边距 */
                font-weight: bold;
                color: #555555;
                min-height: 35px;    /* 增加表头最小高度 */
            }
        """)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        add_button = QPushButton("添加行")
        add_button.setObjectName("add_button")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        
        remove_button = QPushButton("删除行")
        remove_button.setObjectName("remove_button")
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addStretch()
        
        layout.addWidget(table)
        layout.addLayout(button_layout)
        
        return widget, table  # 返回元组而不是单个widget

    # --- 为每个“添加”按钮设置的专用槽函数 ---
    def _add_vertex_row(self):
        row = self.vertices_table.rowCount()
        self.vertices_table.insertRow(row)
        self._set_uneditable_id_cell(self.vertices_table, row)
        self.vertices_table.setItem(row, 1, QTableWidgetItem("0.0"))
        self.vertices_table.setItem(row, 2, QTableWidgetItem("0.0"))
        self.data_changed.emit()

    def _add_segment_row(self):
        row = self.segments_table.rowCount()
        self.segments_table.insertRow(row)
        self._set_uneditable_id_cell(self.segments_table, row)
        self.segments_table.setItem(row, 1, QTableWidgetItem("0"))
        self.segments_table.setItem(row, 2, QTableWidgetItem("1"))
        self.data_changed.emit()

    def _add_region_row(self):
        row = self.regions_table.rowCount()
        self.regions_table.insertRow(row)
        self.regions_table.setItem(row, 0, QTableWidgetItem("0.0"))
        self.regions_table.setItem(row, 1, QTableWidgetItem("0.0"))
        combo = QComboBox()
        self.update_material_options_for_combo(combo)
        self.regions_table.setCellWidget(row, 2, combo)
        combo.currentIndexChanged.connect(self.data_changed.emit)
        self.data_changed.emit()
    
    def _add_bc_row(self):
        row = self.bc_table.rowCount()
        self.bc_table.insertRow(row)
        self.bc_table.setItem(row, 0, QTableWidgetItem("0"))
        self.bc_table.setItem(row, 2, QTableWidgetItem("0.0"))
        combo = QComboBox()
        combo.addItems(["无", "固定约束 (Fixed)", "X向约束 (Roller)", "Y向约束 (Roller)"])
        self.bc_table.setCellWidget(row, 1, combo)
        combo.currentIndexChanged.connect(self.data_changed.emit)
        self.data_changed.emit()

    def _add_target_row(self):
        row = self.targets_table.rowCount()
        self.targets_table.insertRow(row)
        self.targets_table.setItem(row, 0, QTableWidgetItem("A"))
        self.targets_table.setItem(row, 1, QTableWidgetItem("0.0"))
        self.targets_table.setItem(row, 2, QTableWidgetItem("0.0"))
        self.data_changed.emit()

    def _set_uneditable_id_cell(self, table, row):
        """辅助函数，用于创建不可编辑的ID单元格。"""
        id_item = QTableWidgetItem(str(row))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        table.setItem(row, 0, id_item)

    def _remove_generic_row(self, table, has_id_col):
        selected_row = table.currentRow()
        if selected_row >= 0:
            table.removeRow(selected_row)
            if has_id_col: self._update_table_ids(table)
            self.data_changed.emit()

    def _update_table_ids(self, table):
        for row in range(table.rowCount()):
            self._set_uneditable_id_cell(table, row)
            
    def update_material_options_for_combo(self, combo):
        material_names = list(self.controller.problem.materials.keys())
        current_selection = combo.currentText()
        combo.clear()
        if material_names:
            combo.addItems(material_names)
            if current_selection in material_names:
                combo.setCurrentText(current_selection)

    def update_all_material_options(self):
        for row in range(self.regions_table.rowCount()):
            combo = self.regions_table.cellWidget(row, 2)
            if combo: self.update_material_options_for_combo(combo)

    def get_all_data(self):
        data = {}
        try:
            data['vertices'] = [(float(self.vertices_table.item(r, 1).text()), float(self.vertices_table.item(r, 2).text())) for r in range(self.vertices_table.rowCount())]
            data['segments'] = [(int(self.segments_table.item(r, 1).text()), int(self.segments_table.item(r, 2).text())) for r in range(self.segments_table.rowCount())]
            data['regions'] = []
            for r in range(self.regions_table.rowCount()):
                mat_name = self.regions_table.cellWidget(r, 2).currentText()
                # 保持材料名称而不是转换为ID，让preprocessor处理转换
                data['regions'].append((float(self.regions_table.item(r, 0).text()), float(self.regions_table.item(r, 1).text()), mat_name))
            data['constraints'], data['loads'] = {}, {}
            for r in range(self.bc_table.rowCount()):
                seg_id, const_type, load_val = int(self.bc_table.item(r, 0).text()), self.bc_table.cellWidget(r, 1).currentText(), float(self.bc_table.item(r, 2).text())
                if const_type != "无": data['constraints'][seg_id] = const_type
                if load_val != 0.0: data['loads'][seg_id] = load_val
            data['target_points'] = {self.targets_table.item(r, 0).text(): (float(self.targets_table.item(r, 1).text()), float(self.targets_table.item(r, 2).text())) for r in range(self.targets_table.rowCount())}
            return data
        except (ValueError, AttributeError, IndexError, TypeError):
            return None
    
    def clear_all_data(self):
        """清除所有输入数据"""
        self.vertices_table.setRowCount(0)
        self.segments_table.setRowCount(0)
        self.regions_table.setRowCount(0)
        self.bc_table.setRowCount(0)
        self.targets_table.setRowCount(0)
        
        # 重置网格设置为默认值
        if hasattr(self, 'mesh_area_input'):
            self.mesh_area_input.setText("10")
        if hasattr(self, 'mesh_quality_input'):
            self.mesh_quality_input.setText("30")
        
        # 发出数据变化信号
        self.data_changed.emit()
    
    def load_data_from_dict(self, data):
        """从字典数据加载到输入面板的各个表格中"""
        try:
            # 清空所有表格
            self.vertices_table.setRowCount(0)
            self.segments_table.setRowCount(0)
            self.regions_table.setRowCount(0)
            self.bc_table.setRowCount(0)
            self.targets_table.setRowCount(0)
            
            # 加载顶点数据
            if 'vertices' in data:
                for i, (x, y) in enumerate(data['vertices']):
                    self.vertices_table.insertRow(i)
                    self._set_uneditable_id_cell(self.vertices_table, i)
                    self.vertices_table.setItem(i, 1, QTableWidgetItem(str(x)))
                    self.vertices_table.setItem(i, 2, QTableWidgetItem(str(y)))
            
            # 加载线段数据
            if 'segments' in data:
                for i, (start_id, end_id) in enumerate(data['segments']):
                    self.segments_table.insertRow(i)
                    self._set_uneditable_id_cell(self.segments_table, i)
                    self.segments_table.setItem(i, 1, QTableWidgetItem(str(start_id)))
                    self.segments_table.setItem(i, 2, QTableWidgetItem(str(end_id)))
            
            # 加载区域数据
            if 'regions' in data:
                # 如果数据中包含材料信息，先临时获取材料名称列表
                material_names = []
                if 'materials' in data:
                    material_names = list(data['materials'].keys())
                
                for i, region in enumerate(data['regions']):
                    self.regions_table.insertRow(i)
                    if len(region) >= 3:
                        self.regions_table.setItem(i, 0, QTableWidgetItem(str(region[0])))
                        self.regions_table.setItem(i, 1, QTableWidgetItem(str(region[1])))
                        combo = QComboBox()
                        # 如果有材料名称列表，先添加到combo中
                        if material_names:
                            combo.addItems(material_names)
                        else:
                            self.update_material_options_for_combo(combo)
                        # 如果region[2]是材料名称字符串，直接设置
                        if isinstance(region[2], str):
                            combo.setCurrentText(region[2])
                        self.regions_table.setCellWidget(i, 2, combo)
                        combo.currentIndexChanged.connect(self.data_changed.emit)
            
            # 加载边界条件数据
            constraints = data.get('constraints', {})
            loads = data.get('loads', {})
            all_bc_segments = set(constraints.keys()) | set(loads.keys())
            
            for i, seg_id in enumerate(sorted(all_bc_segments, key=lambda x: int(x))):
                self.bc_table.insertRow(i)
                self.bc_table.setItem(i, 0, QTableWidgetItem(str(seg_id)))
                
                # 设置约束类型
                combo = QComboBox()
                combo.addItems(["无", "固定约束 (Fixed)", "X向约束 (Roller)", "Y向约束 (Roller)"])
                constraint_type = constraints.get(seg_id, "无")
                combo.setCurrentText(constraint_type)
                self.bc_table.setCellWidget(i, 1, combo)
                combo.currentIndexChanged.connect(self.data_changed.emit)
                
                # 设置荷载值
                load_value = loads.get(seg_id, 0.0)
                self.bc_table.setItem(i, 2, QTableWidgetItem(str(load_value)))
            
            # 加载目标点数据
            if 'target_points' in data:
                for i, (name, (x, y)) in enumerate(data['target_points'].items()):
                    self.targets_table.insertRow(i)
                    self.targets_table.setItem(i, 0, QTableWidgetItem(str(name)))
                    self.targets_table.setItem(i, 1, QTableWidgetItem(str(x)))
                    self.targets_table.setItem(i, 2, QTableWidgetItem(str(y)))
            
            # 发出数据变化信号
            self.data_changed.emit()
            
        except Exception as e:
            print(f"加载数据时出错: {e}")
    
    def _create_mesh_settings_page(self):
        """创建网格设置页面。"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # 网格面积设置
        self.mesh_area_input = QLineEdit()
        self.mesh_area_input.setText("10")  # 默认值
        self.mesh_area_input.setPlaceholderText("输入最大单元面积 (例如: 10)")
        self.mesh_area_input.textChanged.connect(self.data_changed.emit)
        
        # 添加说明标签
        area_label = QLabel("最大单元面积:")
        area_help = QLabel("较小的值会生成更密的网格，计算更精确但耗时更长")
        area_help.setStyleSheet("color: gray; font-size: 9pt;")
        
        form_layout.addRow(area_label, self.mesh_area_input)
        form_layout.addRow("", area_help)
        
        # 质量设置
        self.mesh_quality_input = QLineEdit()
        self.mesh_quality_input.setText("30")  # 默认值
        self.mesh_quality_input.setPlaceholderText("输入最小角度 (例如: 30)")
        self.mesh_quality_input.textChanged.connect(self.data_changed.emit)
        
        quality_label = QLabel("最小角度 (度):")
        quality_help = QLabel("控制网格质量，建议值为20-35度")
        quality_help.setStyleSheet("color: gray; font-size: 9pt;")
        
        form_layout.addRow(quality_label, self.mesh_quality_input)
        form_layout.addRow("", quality_help)
        
        layout.addLayout(form_layout)
        layout.addStretch()  # 添加弹性空间
        
        return widget
    
    def get_mesh_options(self):
        """获取用户设置的网格参数。"""
        try:
            area = float(self.mesh_area_input.text()) if hasattr(self, 'mesh_area_input') and self.mesh_area_input.text() else 10.0
            quality = int(self.mesh_quality_input.text()) if hasattr(self, 'mesh_quality_input') and self.mesh_quality_input.text() else 30
            # 添加'A'标志来启用区域属性生成
            return f'pq{quality}a{area}A'
        except ValueError:
            # 如果输入无效，返回默认值
            return 'pq30a10A'  # 也要添加A标志
            raise e
    
    def _create_export_page(self):
        """创建导出页面"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 页面标题
        title_label = QLabel("导出分析结果")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # 导出说明
        info_label = QLabel("选择需要导出的数据格式：")
        info_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #666666;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(info_label)
        
        # 添加导出状态标签
        self.export_status_label = QLabel("请先运行计算以生成结果数据")
        self.export_status_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #e74c3c;
                font-style: italic;
                margin-bottom: 15px;
                padding: 10px;
                background-color: #fdf2f2;
                border: 1px solid #f5c6cb;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.export_status_label)
        
        # 导出按钮容器
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)
        
        # 创建导出按钮
        export_buttons = [
            ("导出为CSV格式", "将数据导出为CSV文件，便于在Excel等软件中查看", "#4caf50"),
            ("导出为Excel格式", "将数据导出为Excel文件，包含多个工作表", "#2196f3"),
            ("导出为PNG图像", "将当前视图导出为高质量PNG图像", "#ff9800"),
            ("导出为PDF文档", "将分析报告导出为PDF文档", "#9c27b0")
        ]
        
        for button_text, description, color in export_buttons:
            button_widget = self._create_export_button(button_text, description, color)
            buttons_layout.addWidget(button_widget)
        
        layout.addWidget(buttons_container)
        layout.addStretch()
        
        return widget
    
    def _create_export_button(self, text, description, color):
        """创建单个导出按钮"""
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                background-color: #ffffff;
                border: 2px solid {color};
                border-radius: 10px;
                padding: 15px;
            }}
            QWidget:hover {{
                background-color: {color}15;
                border-color: {color};
            }}
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 按钮图标区域 - 使用实际图标文件
        icon_label = QLabel()
        
        # 根据按钮类型选择对应的图标文件
        icon_path = ""
        if "CSV" in text:
            icon_path = "d:/SlopeFEM_2D/resources/icons/csv.png"
        elif "Excel" in text:
            icon_path = "d:/SlopeFEM_2D/resources/icons/Excel.png"
        elif "PNG" in text:
            icon_path = "d:/SlopeFEM_2D/resources/icons/png.png"
        elif "PDF" in text:
            icon_path = "d:/SlopeFEM_2D/resources/icons/pdf.png"
        
        # 加载并设置图标
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            # 缩放图标到合适大小
            scaled_pixmap = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            # 如果图标文件不存在，使用默认emoji
            icon_label.setText("📄")
            icon_label.setStyleSheet(f"""
                QLabel {{
                    font-size: 24pt;
                    color: {color};
                }}
            """)
        
        icon_label.setStyleSheet(f"""
            QLabel {{
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }}
        """)
        
        # 文本区域
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(5)
        
        title_label = QLabel(text)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12pt;
                font-weight: bold;
                color: {color};
            }}
        """)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 9pt;
                color: #666666;
            }
        """)
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        # 导出按钮
        export_btn = QPushButton("导出")
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 25px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
        """)
        
        layout.addWidget(icon_label)
        layout.addWidget(text_widget, 1)
        layout.addWidget(export_btn)
        
        # 连接按钮事件
        if "CSV" in text:
            export_btn.clicked.connect(self._export_csv)
        elif "Excel" in text:
            export_btn.clicked.connect(self._export_excel)
        elif "PNG" in text:
            export_btn.clicked.connect(self._export_png)
        elif "PDF" in text:
            export_btn.clicked.connect(self._export_pdf)
        
        return container
    
    def enable_export_buttons(self):
        """启用导出按钮（当有计算结果时调用）"""
        if hasattr(self, 'export_csv_btn'):
            self.export_csv_btn.setEnabled(True)
        if hasattr(self, 'export_excel_btn'):
            self.export_excel_btn.setEnabled(True)
        if hasattr(self, 'export_png_btn'):
            self.export_png_btn.setEnabled(True)
        if hasattr(self, 'export_pdf_btn'):
            self.export_pdf_btn.setEnabled(True)
        if hasattr(self, 'export_status_label'):
            self.export_status_label.setText("计算结果已准备就绪，可以导出")
            self.export_status_label.setStyleSheet("color: #27ae60; font-style: italic;")
    
    def disable_export_buttons(self):
        """禁用导出按钮（当没有计算结果时调用）"""
        if hasattr(self, 'export_csv_btn'):
            self.export_csv_btn.setEnabled(False)
        if hasattr(self, 'export_excel_btn'):
            self.export_excel_btn.setEnabled(False)
        if hasattr(self, 'export_png_btn'):
            self.export_png_btn.setEnabled(False)
        if hasattr(self, 'export_pdf_btn'):
            self.export_pdf_btn.setEnabled(False)
        if hasattr(self, 'export_status_label'):
            self.export_status_label.setText("请先运行计算以生成结果数据")
            self.export_status_label.setStyleSheet("color: #e74c3c; font-style: italic;")
    
    def _export_csv(self):
        """导出CSV格式"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not self.controller.result or not hasattr(self.controller.result, 'mesh') or not self.controller.result.mesh:
            QMessageBox.warning(self, "警告", "没有可导出的计算结果，请先运行计算。")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出结果为CSV", "", "CSV文件 (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self._export_to_csv(file_path)
            QMessageBox.information(self, "成功", f"结果已成功导出到：{file_path}")
            self.export_status_label.setText(f"已导出到：{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出CSV文件时发生错误：{str(e)}")
    
    def _export_excel(self):
        """导出Excel格式"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not self.controller.result or not hasattr(self.controller.result, 'mesh') or not self.controller.result.mesh:
            QMessageBox.warning(self, "警告", "没有可导出的计算结果，请先运行计算。")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出结果为Excel", "", "Excel文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            self._export_to_excel(file_path)
            QMessageBox.information(self, "成功", f"结果已成功导出到：{file_path}")
            self.export_status_label.setText(f"已导出到：{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出Excel文件时发生错误：{str(e)}")
    
    def _export_to_csv(self, file_path):
        """将结果数据导出为CSV格式"""
        import csv
        from PyQt6.QtCore import QDateTime
        
        result = self.controller.result
        
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入标题
            writer.writerow(['SlopeFEM_2D 计算结果导出'])
            writer.writerow(['导出时间:', QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')])
            writer.writerow([])
            
            # 目标点位移结果
            if result.target_displacements:
                writer.writerow(['目标点位移结果'])
                writer.writerow(['点名称', '水平位移 (m)', '竖直位移 (m)'])
                for name, (dx, dy) in result.target_displacements.items():
                    writer.writerow([name, f'{dx:.6e}', f'{dy:.6e}'])
                writer.writerow([])
            
            # 节点位移结果
            if len(result.displacements) > 0:
                writer.writerow(['节点位移结果'])
                writer.writerow(['节点ID', 'X坐标 (m)', 'Y坐标 (m)', '水平位移 (m)', '竖直位移 (m)'])
                displacements_2d = result.displacements.reshape(-1, 2)
                for i, (node, disp) in enumerate(zip(result.mesh['vertices'], displacements_2d)):
                    writer.writerow([i, f'{node[0]:.6f}', f'{node[1]:.6f}', f'{disp[0]:.6e}', f'{disp[1]:.6e}'])
                writer.writerow([])
            
            # 单元应力结果
            if len(result.stresses) > 0:
                writer.writerow(['单元应力结果'])
                writer.writerow(['单元ID', '冯·米塞斯应力 (Pa)'])
                for i, stress in enumerate(result.stresses):
                    writer.writerow([i, f'{stress:.6e}'])
    
    def _export_to_excel(self, file_path):
        """将结果数据导出为Excel格式"""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("需要安装pandas库才能导出Excel文件。请运行：pip install pandas openpyxl")
        
        result = self.controller.result
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 目标点位移结果
            if result.target_displacements:
                target_data = []
                for name, (dx, dy) in result.target_displacements.items():
                    target_data.append({
                        '点名称': name,
                        '水平位移 (m)': dx,
                        '竖直位移 (m)': dy
                    })
                df_targets = pd.DataFrame(target_data)
                df_targets.to_excel(writer, sheet_name='目标点位移', index=False)
            
            # 节点位移结果
            if len(result.displacements) > 0:
                node_data = []
                displacements_2d = result.displacements.reshape(-1, 2)
                for i, (node, disp) in enumerate(zip(result.mesh['vertices'], displacements_2d)):
                    node_data.append({
                        '节点ID': i,
                        'X坐标 (m)': node[0],
                        'Y坐标 (m)': node[1],
                        '水平位移 (m)': disp[0],
                        '竖直位移 (m)': disp[1]
                    })
                df_nodes = pd.DataFrame(node_data)
                df_nodes.to_excel(writer, sheet_name='节点位移', index=False)
            
            # 单元应力结果
            if len(result.stresses) > 0:
                stress_data = []
                for i, stress in enumerate(result.stresses):
                    stress_data.append({
                        '单元ID': i,
                        '冯·米塞斯应力 (Pa)': stress
                    })
                df_stress = pd.DataFrame(stress_data)
                df_stress.to_excel(writer, sheet_name='单元应力', index=False)
    
    def _export_png(self):
        """导出PNG格式图像 - 导出所有结果类型"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os
        
        if not self.controller.result or not hasattr(self.controller.result, 'mesh') or not self.controller.result.mesh:
            QMessageBox.warning(self, "警告", "没有可导出的计算结果，请先运行计算。")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出所有结果图像为PNG", "", "PNG图像文件 (*.png)"
        )
        
        if not file_path:
            return
        
        try:
            exported_files = self._export_all_results_to_images(file_path, 'png')
            file_list = "\n".join(exported_files)
            QMessageBox.information(self, "成功", f"所有结果图像已成功导出：\n{file_list}")
            self.export_status_label.setText(f"已导出{len(exported_files)}个PNG文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出PNG文件时发生错误：{str(e)}")
    
    def _export_pdf(self):
        """导出PDF格式文档 - 导出所有结果类型到多页PDF"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        if not self.controller.result or not hasattr(self.controller.result, 'mesh') or not self.controller.result.mesh:
            QMessageBox.warning(self, "警告", "没有可导出的计算结果，请先运行计算。")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出所有结果为PDF", "", "PDF文档文件 (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            self._export_all_results_to_pdf(file_path)
            QMessageBox.information(self, "成功", f"所有结果已成功导出到多页PDF：{file_path}")
            self.export_status_label.setText(f"已导出到：{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出PDF文件时发生错误：{str(e)}")
    
    def _export_all_results_to_images(self, base_file_path, format_type):
        """导出所有结果类型为单独的图像文件"""
        import os
        
        # 定义所有结果类型
        result_types = [
            ('stress', 'Von_Mises应力'),
            ('disp_x_original', '水平位移_原始'),
            ('disp_y_original', '竖直位移_原始'),
            ('disp_x', '水平位移_放大'),
            ('disp_y', '竖直位移_放大')
        ]
        
        # 获取主窗口的画布组件
        main_window = self.window()
        if not hasattr(main_window, 'canvas'):
            raise Exception("无法访问画布组件")
        
        canvas_widget = main_window.canvas
        exported_files = []
        
        # 获取文件路径的目录和基础名称
        base_dir = os.path.dirname(base_file_path)
        base_name = os.path.splitext(os.path.basename(base_file_path))[0]
        
        # 设置高分辨率参数
        dpi = 300 if format_type == 'png' else 150
        
        for plot_type, type_name in result_types:
            # 绘制当前结果类型
            canvas_widget.plot_result(self.controller.result, plot_type)
            
            # 生成文件名
            file_name = f"{base_name}_{type_name}.{format_type}"
            file_path = os.path.join(base_dir, file_name)
            
            # 保存图像
            canvas_widget.figure.savefig(
                file_path,
                format=format_type,
                dpi=dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            
            exported_files.append(file_path)
        
        return exported_files
    
    def _export_all_results_to_pdf(self, file_path):
        """导出所有结果类型到多页PDF文件"""
        from matplotlib.backends.backend_pdf import PdfPages
        
        # 定义所有结果类型
        result_types = [
            ('stress', 'Von Mises应力'),
            ('disp_x_original', '水平位移_原始'),
            ('disp_y_original', '竖直位移_原始'),
            ('disp_x', '水平位移_放大'),
            ('disp_y', '竖直位移_放大')
        ]
        
        # 获取主窗口的画布组件
        main_window = self.window()
        if not hasattr(main_window, 'canvas'):
            raise Exception("无法访问画布组件")
        
        canvas_widget = main_window.canvas
        
        # 创建多页PDF
        with PdfPages(file_path) as pdf:
            for plot_type, type_name in result_types:
                # 绘制当前结果类型
                canvas_widget.plot_result(self.controller.result, plot_type)
                
                # 保存当前页面到PDF
                pdf.savefig(
                    canvas_widget.figure,
                    dpi=150,
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
