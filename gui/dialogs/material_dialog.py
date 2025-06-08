from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QAbstractItemView,
                             QTableWidgetItem, QHBoxLayout, QPushButton, QDialogButtonBox,
                             QHeaderView)
from PyQt6.QtCore import Qt

from core.fem_model import Material

class MaterialDialog(QDialog):
    """
    一个用于创建、编辑和管理材料库的对话框。
    """
    def __init__(self, materials_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("材料库编辑器")
        self.setMinimumSize(500, 300)
        
        # 这是此对话框将返回的数据
        self.materials = materials_data
        
        self._init_ui()
        self._populate_table()

    def _init_ui(self):
        """初始化UI组件。"""
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "材料名称", "弹性模量 (E / Pa)", "泊松比 (ν)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("+ 添加材料")
        remove_btn = QPushButton("- 移除选中")
        buttons_layout.addStretch()
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(remove_btn)
        
        # 标准的 OK/Cancel 按钮
        dialog_buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        
        layout.addWidget(self.table)
        layout.addLayout(buttons_layout)
        layout.addWidget(dialog_buttons)

        # 连接信号
        add_btn.clicked.connect(self._add_row)
        remove_btn.clicked.connect(self._remove_row)
        dialog_buttons.accepted.connect(self.accept)
        dialog_buttons.rejected.connect(self.reject)

    def _populate_table(self):
        """用传入的材料数据填充表格。"""
        for i, mat in enumerate(self.materials.values()):
            self.table.insertRow(i)
            self._set_row_data(i, mat)

    def _add_row(self):
        """添加一个新行并使用默认值。"""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        new_material = Material(id=row_count, name=f"新材料-{row_count}")
        self._set_row_data(row_count, new_material)

    def _remove_row(self):
        """移除选中的行。"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            # 更新ID
            for row in range(self.table.rowCount()):
                 self.table.item(row, 0).setText(str(row))

    def _set_row_data(self, row_index, material):
        """在指定行设置材料数据。"""
        id_item = QTableWidgetItem(str(material.id))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        
        self.table.setItem(row_index, 0, id_item)
        self.table.setItem(row_index, 1, QTableWidgetItem(material.name))
        self.table.setItem(row_index, 2, QTableWidgetItem(str(material.elastic_modulus)))
        self.table.setItem(row_index, 3, QTableWidgetItem(str(material.poisson_ratio)))

    def get_materials(self):
        """当对话框被接受时，从表格中读取数据并返回。"""
        updated_materials = {}
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 1).text()
            E = float(self.table.item(row, 2).text())
            nu = float(self.table.item(row, 3).text())
            mat = Material(id=row, name=name, elastic_modulus=E, poisson_ratio=nu)
            updated_materials[name] = mat
        return updated_materials

