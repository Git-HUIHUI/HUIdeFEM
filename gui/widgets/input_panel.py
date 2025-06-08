from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QTableWidget, QComboBox,
                             QTableWidgetItem, QPushButton, QHBoxLayout, 
                             QHeaderView, QAbstractItemView, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal

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
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        
        # 创建各个选项卡页面
        vertices_widget, self.vertices_table = self._create_tab_page("定义顶点", ["ID", "X 坐标", "Y 坐标"])
        segments_widget, self.segments_table = self._create_tab_page("定义线段", ["ID", "起始点 ID", "结束点 ID"])
        regions_widget, self.regions_table = self._create_tab_page("定义区域", ["区域点 X", "区域点 Y", "材料"])
        bc_widget, self.bc_table = self._create_tab_page("边界条件", ["线段 ID", "约束类型", "荷载 Q (N/m)"])
        targets_widget, self.targets_table = self._create_tab_page("目标点", ["点名称", "X 坐标", "Y 坐标"])

        # 添加选项卡页面
        self.tab_widget.addTab(vertices_widget, "1. 顶点")
        self.tab_widget.addTab(segments_widget, "2. 线段")
        self.tab_widget.addTab(regions_widget, "3. 区域")
        self.tab_widget.addTab(bc_widget, "4. 边界")
        self.tab_widget.addTab(targets_widget, "5. 目标点")

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
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建表格
        table = QTableWidget(objectName=title)
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.itemChanged.connect(self.data_changed.emit)
        
        # 设置表格样式
        table.verticalHeader().setDefaultSectionSize(35)
        font = table.font()
        font.setPointSize(10)
        table.setFont(font)

        # 创建按钮布局
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("+ 添加", objectName="add_button")
        remove_btn = QPushButton("- 移除", objectName="remove_button")
        
        # 设置按钮样式
        for btn in [add_btn, remove_btn]:
            btn.setMinimumHeight(35)
            btn.setMinimumWidth(80)
            font = btn.font()
            font.setPointSize(10)
            btn.setFont(font)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(remove_btn)
        
        # 组装布局
        layout.addWidget(table)
        layout.addLayout(buttons_layout)
        
        return widget, table

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
            materials = self.controller.problem.materials
            mat_name_to_id = {name: mat.id for name, mat in materials.items()}
            data['regions'] = []
            for r in range(self.regions_table.rowCount()):
                mat_name = self.regions_table.cellWidget(r, 2).currentText()
                if mat_name in mat_name_to_id:
                    data['regions'].append((float(self.regions_table.item(r, 0).text()), float(self.regions_table.item(r, 1).text()), mat_name_to_id[mat_name]))
            data['constraints'], data['loads'] = {}, {}
            for r in range(self.bc_table.rowCount()):
                seg_id, const_type, load_val = int(self.bc_table.item(r, 0).text()), self.bc_table.cellWidget(r, 1).currentText(), float(self.bc_table.item(r, 2).text())
                if const_type != "无": data['constraints'][seg_id] = const_type
                if load_val != 0.0: data['loads'][seg_id] = load_val
            data['target_points'] = {self.targets_table.item(r, 0).text(): (float(self.targets_table.item(r, 1).text()), float(self.targets_table.item(r, 2).text())) for r in range(self.targets_table.rowCount())}
            return data
        except (ValueError, AttributeError, IndexError, TypeError):
            return None
    
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
                for i, region in enumerate(data['regions']):
                    self.regions_table.insertRow(i)
                    if len(region) >= 3:
                        self.regions_table.setItem(i, 0, QTableWidgetItem(str(region[0])))
                        self.regions_table.setItem(i, 1, QTableWidgetItem(str(region[1])))
                        combo = QComboBox()
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
            raise e
