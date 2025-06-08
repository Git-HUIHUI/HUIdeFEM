from PyQt6.QtWidgets import (QMainWindow, QSplitter, QMessageBox, QWidget,
                             QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import json
import os

from gui.widgets.input_panel import InputPanel
from gui.widgets.canvas_widget import CanvasWidget
from gui.widgets.results_panel import ResultsPanel
from gui.dialogs.material_dialog import MaterialDialog

class MainWindow(QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("SlopeFEM_2D - 二维边坡有限元分析程序")
        self.setGeometry(100, 100, 1800, 1000)
        self._create_actions()
        self._create_menu_bar()
        self._create_tool_bar()
        self._create_status_bar()
        self._create_central_widget()
        self._create_connections()
        self._update_all()

    def _create_actions(self):
        self.calc_action = QAction("计算", self)
        self.load_example_action = QAction("加载预设案例", self)
        self.exit_action = QAction("退出", self)
        self.material_action = QAction("材料库...", self)
        self.about_action = QAction("关于", self)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("文件")
        file_menu.addAction(self.load_example_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        define_menu = menu_bar.addMenu("定义")
        define_menu.addAction(self.material_action)
        run_menu = menu_bar.addMenu("运行")
        run_menu.addAction(self.calc_action)
        help_menu = menu_bar.addMenu("帮助")
        help_menu.addAction(self.about_action)

    def _create_tool_bar(self):
        toolbar = self.addToolBar("主要工具")
        toolbar.addAction(self.load_example_action)
        toolbar.addSeparator()
        toolbar.addAction(self.material_action)
        toolbar.addAction(self.calc_action)

    def _create_status_bar(self):
        self.statusBar().showMessage("准备就绪。")

    def _create_central_widget(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧面板 (仅输入面板)
        self.input_panel = InputPanel(self.controller)

        # 右侧面板 (画布和结果)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 绘图控制
        plot_controls = QHBoxLayout()
        self.plot_selector = QComboBox()
        self.plot_selector.addItems(["模型预览", "Von Mises 应力", "水平位移", "竖直位移"])
        plot_controls.addWidget(QLabel("显示内容:"))
        plot_controls.addWidget(self.plot_selector)
        plot_controls.addStretch()
        
        # 画布和结果面板
        self.canvas = CanvasWidget()
        self.results_panel = ResultsPanel()
        
        right_layout.addLayout(plot_controls)
        right_layout.addWidget(self.canvas)
        right_layout.addWidget(self.results_panel)
        right_layout.setStretch(1, 3)  # canvas占更多空间
        right_layout.setStretch(2, 1)  # results panel占较少空间

        splitter.addWidget(self.input_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 1200])
        main_layout.addWidget(splitter)

    def _create_connections(self):
        self.input_panel.data_changed.connect(self._update_all)
        self.calc_action.triggered.connect(self._run_analysis)
        self.load_example_action.triggered.connect(self._load_example_case)
        self.controller.computation_started.connect(lambda: self.statusBar().showMessage("正在计算，请稍候..."))
        self.controller.computation_finished.connect(self._on_computation_finished)
        self.plot_selector.currentTextChanged.connect(self._update_plot_view)
        self.exit_action.triggered.connect(self.close)
        self.material_action.triggered.connect(self._open_material_dialog)
        self.about_action.triggered.connect(lambda: QMessageBox.about(self, "关于", "SlopeFEM_2D v1.0"))

    def _update_all(self):
        all_data = self.input_panel.get_all_data()
        if all_data:
            self.controller.update_problem_from_dict(all_data)
        self.plot_selector.setCurrentIndex(0) # 切换回模型预览
        self._update_plot_view()
        self.results_panel.clear()

    def _run_analysis(self):
        self._update_all() # 确保使用最新的数据
        self.controller.run_analysis()

    def _on_computation_finished(self, success, message):
        self.statusBar().showMessage(message)
        if success:
            QMessageBox.information(self, "成功", message)
            self.results_panel.update_results(self.controller.result)
            self.plot_selector.setCurrentIndex(1) # 默认显示应力云图
            self._update_plot_view()
        else:
            QMessageBox.critical(self, "错误", message)

    def _update_plot_view(self):
        plot_type_text = self.plot_selector.currentText()
        if plot_type_text == "模型预览":
            self.canvas.plot_problem(self.controller.problem)
        else:
            if not self.controller.result.mesh:
                self.canvas.clear_plot()
                return
            plot_map = { "Von Mises 应力": "stress", "水平位移": "disp_x", "竖直位移": "disp_y" }
            self.canvas.plot_result(self.controller.result, plot_map.get(plot_type_text))

    def _open_material_dialog(self):
        dialog = MaterialDialog(self.controller.problem.materials, self)
        if dialog.exec():
            self.controller.update_materials(dialog.get_materials())
            self.input_panel.update_all_material_options()
            self._update_all()
    
    def _load_example_case(self):
        """加载预设的边坡分析案例"""
        try:
            # 获取例题文件路径
            example_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'examples', 'slope_problem.json')
            
            if not os.path.exists(example_file):
                QMessageBox.warning(self, "警告", "预设案例文件不存在！")
                return
            
            # 读取JSON文件
            with open(example_file, 'r', encoding='utf-8') as f:
                case_data = json.load(f)
            
            # 确认是否加载
            reply = QMessageBox.question(self, "加载预设案例", 
                                       f"是否加载预设案例：{case_data.get('name', '未命名案例')}？\n\n"
                                       f"描述：{case_data.get('description', '无描述')}\n\n"
                                       "这将清除当前所有输入数据。",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # 加载材料数据
            if 'materials' in case_data:
                from core.fem_model import Material
                materials_dict = {}
                for name, mat_data in case_data['materials'].items():
                    material = Material(
                        id=mat_data['id'],
                        name=name,
                        elastic_modulus=mat_data['elastic_modulus'],
                        poisson_ratio=mat_data['poisson_ratio']
                    )
                    materials_dict[name] = material
                self.controller.update_materials(materials_dict)
            
            # 加载到输入面板
            self.input_panel.load_data_from_dict(case_data)
            
            # 更新界面
            self._update_all()
            self.statusBar().showMessage("预设案例加载成功！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载预设案例失败：{str(e)}")
