from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize  # 添加QSize导入
from PyQt6.QtGui import QIcon, QFont  # 添加QFont导入
import os
from .canvas_widget import CanvasWidget
from .vtk_canvas_widget import VTKCanvasWidget, BaseVisualizationWidget

class EnhancedCanvasWidget(QWidget):
    """增强的画布组件，支持matplotlib和VTK双引擎"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_engine = 'matplotlib'
        self.setup_ui()
    
    @property
    def figure(self):
        """兼容性属性：返回matplotlib的figure对象"""
        if hasattr(self.matplotlib_widget, 'figure'):
            return self.matplotlib_widget.figure
        else:
            # 如果matplotlib_widget没有figure属性，返回None或抛出异常
            raise AttributeError("当前可视化引擎不支持figure属性")
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 获取图标路径
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icons')
        
        # 引擎选择面板
        engine_panel = QHBoxLayout()
        engine_panel.setSpacing(10)  # 增加间距
        
        # 添加可视化引擎图标和标签
        engine_icon = QLabel()
        engine_icon.setPixmap(QIcon(os.path.join(icon_path, '可视化引擎.png')).pixmap(24, 24))  # 放大图标
        engine_panel.addWidget(engine_icon)
        
        engine_label = QLabel("可视化引擎:")
        # 设置字体大小
        font = QFont()
        font.setPointSize(10)
        engine_label.setFont(font)
        engine_panel.addWidget(engine_label)
        
        self.engine_combo = QComboBox()
        self.engine_combo.addItems(["Matplotlib (2D)", "VTK (3D专业)"])
        self.engine_combo.currentTextChanged.connect(self.switch_engine)
        # 设置下拉框大小和字体
        self.engine_combo.setMinimumHeight(30)
        self.engine_combo.setFont(font)
        engine_panel.addWidget(self.engine_combo)
        
        engine_panel.addStretch()
        
        # 导出按钮
        export_btn = QPushButton("导出高质量图像")
        export_btn.setIcon(QIcon(os.path.join(icon_path, '导出高质量图像.png')))
        export_btn.setIconSize(QSize(20, 20))  # 设置按钮图标大小
        export_btn.setMinimumHeight(35)  # 增加按钮高度
        export_btn.setFont(font)
        export_btn.clicked.connect(self.export_high_quality_image)
        engine_panel.addWidget(export_btn)
        
        layout.addLayout(engine_panel)
        
        # 创建两个可视化组件
        self.matplotlib_widget = CanvasWidget()
        self.vtk_widget = VTKCanvasWidget()
        
        # 添加到布局
        layout.addWidget(self.matplotlib_widget)
        layout.addWidget(self.vtk_widget)
        
        # 初始状态：显示matplotlib，隐藏VTK
        self.vtk_widget.hide()
        
    def switch_engine(self, engine_text):
        """切换可视化引擎"""
        if "Matplotlib" in engine_text:
            self.current_engine = 'matplotlib'
            self.matplotlib_widget.show()
            self.vtk_widget.hide()
        else:
            self.current_engine = 'vtk'
            self.matplotlib_widget.hide()
            self.vtk_widget.show()
            
    def get_current_widget(self) -> BaseVisualizationWidget:
        """获取当前活动的可视化组件"""
        if self.current_engine == 'matplotlib':
            return self.matplotlib_widget
        else:
            return self.vtk_widget
            
    def plot_problem(self, problem_def):
        """绘制问题定义"""
        self.get_current_widget().plot_problem(problem_def)
        
    def plot_result(self, result, plot_type='stress'):
        """绘制分析结果"""
        self.get_current_widget().plot_result(result, plot_type)
        
    def clear_plot(self):
        """清除绘图"""
        self.get_current_widget().clear_plot()
        
    def reset_zoom(self):
        """重置缩放"""
        if hasattr(self.get_current_widget(), 'reset_zoom'):
            self.get_current_widget().reset_zoom()
        elif hasattr(self.get_current_widget(), 'reset_camera'):
            self.get_current_widget().reset_camera()
            
    def export_high_quality_image(self):
        """导出高质量图像"""
        from PyQt6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "导出图像", "", 
            "PNG图像 (*.png);;JPEG图像 (*.jpg);;TIFF图像 (*.tiff);;EPS矢量图 (*.eps)"
        )
        
        if filename:
            if self.current_engine == 'vtk':
                self.export_vtk_image(filename)
            else:
                self.export_matplotlib_image(filename)
                
    def export_vtk_image(self, filename):
        """导出VTK高质量图像"""
        # 设置高质量渲染
        render_window = self.vtk_widget.vtk_widget.GetRenderWindow()
        render_window.SetMultiSamples(8)
        
        # 创建窗口到图像过滤器
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(render_window)
        w2if.SetScale(3)  # 3倍超采样
        w2if.SetInputBufferTypeToRGBA()
        w2if.ReadFrontBufferOff()
        w2if.Update()
        
        # 写入文件
        if filename.lower().endswith('.png'):
            writer = vtk.vtkPNGWriter()
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            writer = vtk.vtkJPEGWriter()
        elif filename.lower().endswith('.tiff'):
            writer = vtk.vtkTIFFWriter()
        else:
            writer = vtk.vtkPNGWriter()
            
        writer.SetFileName(filename)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()
        
    def export_matplotlib_image(self, filename):
        """导出Matplotlib高质量图像"""
        # 使用现有的matplotlib导出功能
        dpi = 300 if filename.lower().endswith('.eps') else 300
        if hasattr(self.matplotlib_widget, 'figure'):
            self.matplotlib_widget.figure.savefig(filename, dpi=dpi, bbox_inches='tight')
        else:
            raise AttributeError("Matplotlib组件没有figure属性")