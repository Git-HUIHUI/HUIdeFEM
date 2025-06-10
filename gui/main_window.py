from PyQt6.QtWidgets import (QMainWindow, QSplitter, QMessageBox, QWidget,
                             QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel,
                             QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import json
import os

from gui.widgets.input_panel import InputPanel
from gui.widgets.canvas_widget import CanvasWidget
from gui.widgets.results_panel import ResultsPanel
from gui.dialogs.material_dialog import MaterialDialog
from core.fem_model import ProblemDefinition, FemResult

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
        self._update_window_title()  # 设置初始窗口标题
        self._update_all()

    def _create_actions(self):
        # 文件操作
        self.new_action = QAction("新建项目", self)
        self.open_action = QAction("打开项目...", self)
        self.save_action = QAction("保存项目", self)
        self.save_as_action = QAction("另存为...", self)
        self.load_example_action = QAction("加载预设案例", self)
        self.exit_action = QAction("退出", self)
        
        # 导出功能已移至选项卡页面，不再需要菜单动作
        
        # 设置图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'icons')
        if os.path.exists(os.path.join(icon_path, 'open_file.png')):
            self.open_action.setIcon(QIcon(os.path.join(icon_path, 'open_file.png')))
        if os.path.exists(os.path.join(icon_path, 'save_file.png')):
            self.save_action.setIcon(QIcon(os.path.join(icon_path, 'save_file.png')))
            self.save_as_action.setIcon(QIcon(os.path.join(icon_path, 'save_file.png')))
        if os.path.exists(os.path.join(icon_path, 'calculate.png')):
            self.calc_action = QAction("计算", self)
            self.calc_action.setIcon(QIcon(os.path.join(icon_path, 'calculate.png')))
        else:
            self.calc_action = QAction("计算", self)
        
        # 其他操作
        self.material_action = QAction("材料库...", self)
        self.about_action = QAction("关于", self)
        
        # 设置快捷键
        self.new_action.setShortcut("Ctrl+N")
        self.open_action.setShortcut("Ctrl+O")
        self.save_action.setShortcut("Ctrl+S")
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        
        # 当前文件路径
        self.current_file_path = None

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        file_menu.addAction(self.new_action)
        file_menu.addSeparator()
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        # 移除导出菜单，导出功能已移至选项卡页面
        file_menu.addSeparator()
        file_menu.addAction(self.load_example_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # 定义菜单
        define_menu = menu_bar.addMenu("定义")
        define_menu.addAction(self.material_action)
        
        # 运行菜单
        run_menu = menu_bar.addMenu("运行")
        run_menu.addAction(self.calc_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        help_menu.addAction(self.about_action)

    def _create_tool_bar(self):
        toolbar = self.addToolBar("主要工具")
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
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
        self.plot_selector.addItems([
            "模型预览", 
            "Von Mises 应力", 
            "水平位移 (原始)", 
            "竖直位移 (原始)",
            "水平位移 (放大)", 
            "竖直位移 (放大)"
        ])
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
        # 数据和界面更新
        self.input_panel.data_changed.connect(self._update_all)
        self.plot_selector.currentTextChanged.connect(self._update_plot_view)
        
        # 文件操作
        self.new_action.triggered.connect(self._new_project)
        self.open_action.triggered.connect(self._open_project)
        self.save_action.triggered.connect(self._save_project)
        self.save_as_action.triggered.connect(self._save_project_as)
        # 导出功能已移至输入面板的导出选项卡，不再需要这些连接
        self.load_example_action.triggered.connect(self._load_example_case)
        self.exit_action.triggered.connect(self.close)
        
        # 计算和分析
        self.calc_action.triggered.connect(self._run_analysis)
        self.controller.computation_started.connect(lambda: self.statusBar().showMessage("正在计算，请稍候..."))
        self.controller.computation_finished.connect(self._on_computation_finished)
        
        # 其他操作
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
            
            # 启用导出功能（在输入面板的导出选项卡中）
            self.input_panel.enable_export_buttons()
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
            plot_map = { 
                "Von Mises 应力": "stress", 
                "水平位移 (原始)": "disp_x_original", 
                "竖直位移 (原始)": "disp_y_original",
                "水平位移 (放大)": "disp_x", 
                "竖直位移 (放大)": "disp_y" 
            }
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
            
            # 先加载到输入面板
            self.input_panel.load_data_from_dict(case_data)
            
            # 更新界面（这会调用update_problem_from_dict）
            self._update_all()
            
            # 最后加载材料数据，确保不被覆盖
            if 'materials' in case_data:
                from core.fem_model import Material
                materials_dict = {}
                for name, mat_data in case_data['materials'].items():
                    material = Material(
                        id=mat_data['id'],
                        name=name,
                        elastic_modulus=mat_data['elastic_modulus'],
                        poisson_ratio=mat_data['poisson_ratio'],
                        unit_weight=mat_data.get('unit_weight', 18000.0)
                    )
                    materials_dict[name] = material
                self.controller.update_materials(materials_dict)
            
            # 清除之前的计算结果
            self.controller.result = FemResult()
            self.results_panel.clear()
            
            # 禁用导出功能（在输入面板的导出选项卡中）
            self.input_panel.disable_export_buttons()
            
            self.statusBar().showMessage("预设案例加载成功！")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载预设案例失败：{str(e)}")
    
    def _new_project(self):
        """新建项目"""
        reply = QMessageBox.question(self, "新建项目", 
                                   "是否新建项目？这将清除当前所有数据。",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清除所有数据
            self.input_panel.clear_all_data()
            self.controller.problem = ProblemDefinition()
            self.controller.result = FemResult()
            self.results_panel.clear()
            
            # 禁用导出功能（在输入面板的导出选项卡中）
            self.input_panel.disable_export_buttons()
            
            self.current_file_path = None
            self._update_window_title()
            self._update_all()
            self.statusBar().showMessage("新项目已创建")
    
    def _open_project(self):
        """打开项目文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目文件", "", "JSON文件 (*.json);;所有文件 (*.*)")
        
        if file_path:
            self._load_project_file(file_path)
    
    def _save_project(self):
        """保存项目"""
        if self.current_file_path:
            self._save_project_to_file(self.current_file_path)
        else:
            self._save_project_as()
    
    def _save_project_as(self):
        """另存为项目文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存项目文件", "", "JSON文件 (*.json);;所有文件 (*.*)")
        
        if file_path:
            # 确保文件扩展名为.json
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
            self._save_project_to_file(file_path)
    
    def _load_project_file(self, file_path):
        """从文件加载项目数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # 确认是否加载
            project_name = project_data.get('name', os.path.basename(file_path))
            reply = QMessageBox.question(self, "打开项目", 
                                       f"是否打开项目：{project_name}？\n\n"
                                       f"文件：{file_path}\n\n"
                                       "这将清除当前所有数据。",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # 加载数据到输入面板
            self.input_panel.load_data_from_dict(project_data)
            
            # 更新界面
            self._update_all()
            
            # 加载材料数据
            if 'materials' in project_data:
                from core.fem_model import Material
                materials_dict = {}
                for name, mat_data in project_data['materials'].items():
                    material = Material(
                        id=mat_data['id'],
                        name=name,
                        elastic_modulus=mat_data['elastic_modulus'],
                        poisson_ratio=mat_data['poisson_ratio'],
                        unit_weight=mat_data.get('unit_weight', 18000.0)
                    )
                    materials_dict[name] = material
                self.controller.update_materials(materials_dict)
            
            # 清除之前的计算结果
            self.controller.result = FemResult()
            self.results_panel.clear()
            
            # 禁用导出功能（在输入面板的导出选项卡中）
            self.input_panel.disable_export_buttons()
            
            # 更新当前文件路径和窗口标题
            self.current_file_path = file_path
            self._update_window_title()
            self.statusBar().showMessage(f"项目文件加载成功：{os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载项目文件失败：{str(e)}")
    
    def _save_project_to_file(self, file_path):
        """保存项目数据到文件"""
        try:
            # 获取当前所有数据
            all_data = self.input_panel.get_all_data()
            if not all_data:
                all_data = {}
            
            # 添加材料数据
            if self.controller.problem.materials:
                materials_data = {}
                for name, material in self.controller.problem.materials.items():
                    materials_data[name] = {
                        'id': material.id,
                        'elastic_modulus': material.elastic_modulus,
                        'poisson_ratio': material.poisson_ratio,
                        'unit_weight': material.unit_weight
                    }
                all_data['materials'] = materials_data
            
            # 添加项目信息
            if 'name' not in all_data:
                all_data['name'] = os.path.splitext(os.path.basename(file_path))[0]
            if 'description' not in all_data:
                all_data['description'] = "SlopeFEM_2D项目文件"
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            # 更新当前文件路径和窗口标题
            self.current_file_path = file_path
            self._update_window_title()
            self.statusBar().showMessage(f"项目文件保存成功：{os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存项目文件失败：{str(e)}")
    
    def _update_window_title(self):
        """更新窗口标题"""
        base_title = "SlopeFEM_2D - 二维边坡有限元分析程序"
        if self.current_file_path:
            file_name = os.path.basename(self.current_file_path)
            self.setWindowTitle(f"{base_title} - {file_name}")
        else:
            self.setWindowTitle(f"{base_title} - 未保存的项目")
    
    # 导出功能已移至输入面板的导出选项卡，不再需要这些方法
