import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
from PyQt6.QtCore import Qt, QSize  # 添加QSize导入
from PyQt6.QtGui import QIcon, QFont  # 添加QFont导入
import numpy as np
import os

# 保留抽象基类定义，但不用于继承
from abc import ABC, abstractmethod

class BaseVisualizationWidget(ABC):
    """可视化组件的抽象基类（仅作为接口参考）"""
    
    @abstractmethod
    def plot_problem(self, problem_def):
        pass
    
    @abstractmethod
    def plot_result(self, result, plot_type='stress'):
        pass
    
    @abstractmethod
    def clear_plot(self):
        pass

class VTKCanvasWidget(QWidget):
    """基于VTK的高级3D可视化组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_vtk()
        
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 获取图标路径
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icons')
        
        # 设置字体
        font = QFont()
        font.setPointSize(10)
        
        # 控制面板
        control_panel = QHBoxLayout()
        control_panel.setSpacing(15)  # 增加间距
        
        # 视图模式选择
        view_icon = QLabel()
        view_icon.setPixmap(QIcon(os.path.join(icon_path, '视图模式.png')).pixmap(24, 24))  # 放大图标
        control_panel.addWidget(view_icon)
        
        view_label = QLabel("视图模式:")
        view_label.setFont(font)
        control_panel.addWidget(view_label)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["2D平面视图", "3D透视视图", "等轴测视图"])
        self.view_combo.currentTextChanged.connect(self.change_view_mode)
        self.view_combo.setMinimumHeight(30)
        self.view_combo.setFont(font)
        control_panel.addWidget(self.view_combo)
        
        # 渲染质量选择
        quality_icon = QLabel()
        quality_icon.setPixmap(QIcon(os.path.join(icon_path, '渲染质量.png')).pixmap(24, 24))  # 放大图标
        control_panel.addWidget(quality_icon)
        
        quality_label = QLabel("渲染质量:")
        quality_label.setFont(font)
        control_panel.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["高质量", "标准", "快速预览"])
        self.quality_combo.currentTextChanged.connect(self.change_render_quality)
        self.quality_combo.setMinimumHeight(30)
        self.quality_combo.setFont(font)
        control_panel.addWidget(self.quality_combo)
        
        # 重置视图按钮
        reset_btn = QPushButton("重置视图")
        reset_btn.setIcon(QIcon(os.path.join(icon_path, '重置视图.png')))
        reset_btn.setIconSize(QSize(20, 20))  # 设置按钮图标大小
        reset_btn.setMinimumHeight(35)  # 增加按钮高度
        reset_btn.setFont(font)
        reset_btn.clicked.connect(self.reset_camera)
        control_panel.addWidget(reset_btn)
        
        control_panel.addStretch()
        layout.addLayout(control_panel)
        
        # VTK渲染窗口
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        layout.addWidget(self.vtk_widget)
        
    def setup_vtk(self):
        """设置VTK渲染管线"""
        # 创建渲染器
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.95, 0.95, 0.95)  # 浅灰色背景
        
        # 设置渲染窗口
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        
        # 设置交互器
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        
        # 设置交互样式
        style = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(style)
        
        # 添加坐标轴
        self.add_coordinate_axes()
        
        # 初始化相机
        self.setup_camera()
        
    def add_coordinate_axes(self):
        """添加坐标轴"""
        # 创建坐标轴
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(1, 1, 0.1)  # 设置轴长度
        axes.SetShaftType(0)  # 圆柱形轴
        axes.SetAxisLabels(1)  # 显示标签
        
        # 设置标签
        axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
        
        # 添加到渲染器
        self.renderer.AddActor(axes)
        
    def setup_camera(self):
        """设置相机"""
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(10, 10, 10)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 0, 1)
        self.renderer.ResetCamera()
        
    def plot_problem(self, problem_def):
        """绘制问题定义"""
        # 清除现有内容
        self.clear_plot()
        
        # 重新添加坐标轴
        self.add_coordinate_axes()
        
        verts = np.array(problem_def.vertices)
        segs = problem_def.segments
        
        if len(verts) == 0:
            return
            
        # 创建顶点
        self.add_vertices(verts)
        
        # 创建线段
        if segs:
            self.add_segments(verts, segs)
            
        # 添加约束可视化
        if problem_def.constraints:
            self.add_constraints(verts, segs, problem_def.constraints)
            
        # 添加荷载可视化
        if problem_def.loads:
            self.add_loads(verts, segs, problem_def.loads)
            
        # 添加目标点
        if problem_def.target_points:
            self.add_target_points(problem_def.target_points)
            
        # 更新渲染
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
    def add_vertices(self, vertices):
        """添加顶点可视化"""
        points = vtk.vtkPoints()
        for i, (x, y) in enumerate(vertices):
            points.InsertNextPoint(x, y, 0)
            
        # 创建顶点数据
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        
        # 创建顶点
        vertex_filter = vtk.vtkVertexGlyphFilter()
        vertex_filter.SetInputData(polydata)
        
        # 创建映射器
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(vertex_filter.GetOutputPort())
        
        # 创建演员
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 0, 1)  # 蓝色
        actor.GetProperty().SetPointSize(8)
        
        self.renderer.AddActor(actor)
        
    def add_segments(self, vertices, segments):
        """添加线段可视化"""
        points = vtk.vtkPoints()
        lines = vtk.vtkCellArray()
        
        for x, y in vertices:
            points.InsertNextPoint(x, y, 0)
            
        for seg in segments:
            if max(seg) < len(vertices):
                line = vtk.vtkLine()
                line.GetPointIds().SetId(0, seg[0])
                line.GetPointIds().SetId(1, seg[1])
                lines.InsertNextCell(line)
                
        # 创建多边形数据
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(lines)
        
        # 创建映射器
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        
        # 创建演员
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1, 0, 0)  # 红色
        actor.GetProperty().SetLineWidth(2)
        
        self.renderer.AddActor(actor)
        
    def add_constraints(self, vertices, segments, constraints):
        """添加约束可视化"""
        for seg_id, const_type in constraints.items():
            if seg_id < len(segments) and max(segments[seg_id]) < len(vertices):
                p1, p2 = vertices[segments[seg_id][0]], vertices[segments[seg_id][1]]
                mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                
                # 创建约束符号（立方体）
                cube = vtk.vtkCubeSource()
                cube.SetXLength(0.2)
                cube.SetYLength(0.2)
                cube.SetZLength(0.2)
                cube.SetCenter(mid_x, mid_y, 0)
                
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(cube.GetOutputPort())
                
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                
                if "固定" in const_type:
                    actor.GetProperty().SetColor(0, 0, 0)  # 黑色
                elif "X向" in const_type:
                    actor.GetProperty().SetColor(0.5, 0.5, 0.5)  # 灰色
                elif "Y向" in const_type:
                    actor.GetProperty().SetColor(0.7, 0.7, 0.7)  # 浅灰色
                    
                self.renderer.AddActor(actor)
                
    def add_loads(self, vertices, segments, loads):
        """添加荷载可视化（箭头）"""
        for seg_id, load_value in loads.items():
            if seg_id < len(segments) and max(segments[seg_id]) < len(vertices):
                p1, p2 = vertices[segments[seg_id][0]], vertices[segments[seg_id][1]]
                
                # 计算线段中点和法向量
                mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                seg_vec = np.array(p2) - np.array(p1)
                normal_vec = np.array([-seg_vec[1], seg_vec[0]])
                normal_vec = normal_vec / np.linalg.norm(normal_vec)
                
                # 创建箭头
                arrow = vtk.vtkArrowSource()
                arrow.SetTipLength(0.3)
                arrow.SetTipRadius(0.1)
                arrow.SetShaftRadius(0.03)
                
                # 计算箭头方向和位置
                arrow_length = abs(load_value) / 10000.0
                arrow_dir = -np.sign(load_value) * normal_vec
                
                # 变换箭头
                transform = vtk.vtkTransform()
                transform.Translate(mid_x, mid_y, 0)
                transform.Scale(arrow_length, arrow_length, arrow_length)
                
                # 计算旋转角度
                angle = np.arctan2(arrow_dir[1], arrow_dir[0]) * 180 / np.pi
                transform.RotateZ(angle)
                
                transform_filter = vtk.vtkTransformPolyDataFilter()
                transform_filter.SetInputConnection(arrow.GetOutputPort())
                transform_filter.SetTransform(transform)
                
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(transform_filter.GetOutputPort())
                
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(1, 0.5, 0)  # 橙色
                
                self.renderer.AddActor(actor)
                
    def add_target_points(self, target_points):
        """添加目标点可视化"""
        for name, (x, y) in target_points.items():
            # 创建球体
            sphere = vtk.vtkSphereSource()
            sphere.SetCenter(x, y, 0)
            sphere.SetRadius(0.1)
            sphere.SetPhiResolution(20)
            sphere.SetThetaResolution(20)
            
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphere.GetOutputPort())
            
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(1, 0, 0)  # 红色
            
            self.renderer.AddActor(actor)
            
    def plot_result(self, result, plot_type='stress'):
        """绘制分析结果"""
        # 清除现有内容
        self.clear_plot()
        
        mesh = result.mesh
        nodes = mesh['vertices']
        elements = mesh['triangles']
        
        # 创建网格可视化
        scale_factor = self.create_mesh_visualization(nodes, elements, result, plot_type)
        
        # 更新渲染
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
        return scale_factor  # 返回放大系数供颜色条使用
        
    def create_mesh_visualization(self, nodes, elements, result, plot_type):
        """创建网格可视化"""
        # 创建点
        points = vtk.vtkPoints()
        
        # 判断是否需要变形显示 - 与Matplotlib保持一致
        use_deformation = plot_type in ['disp_x', 'disp_y', 'disp_x_original', 'disp_y_original']
        use_scale = plot_type in ['disp_x', 'disp_y']  # 只有非原始模式才放大
        
        # 计算变形放大系数 - 与Matplotlib完全一致
        scale_factor = 1.0
        if use_deformation and use_scale and len(result.displacements) > 0:
            max_displacement = np.max(np.abs(result.displacements))
            if max_displacement > 0:
                # 根据模型尺寸自动计算放大系数
                model_size = max(np.max(nodes[:, 0]) - np.min(nodes[:, 0]), 
                               np.max(nodes[:, 1]) - np.min(nodes[:, 1]))
                scale_factor = model_size * 0.1 / max_displacement  # 变形显示为模型尺寸的10%
        
        # 添加节点（可能包含变形）
        for i, (x, y) in enumerate(nodes):
            if use_deformation and i < len(result.displacements):
                dx, dy = result.displacements[i] * scale_factor
                points.InsertNextPoint(x + dx, y + dy, 0)
            else:
                points.InsertNextPoint(x, y, 0)
        
        # 创建三角形单元
        triangles = vtk.vtkCellArray()
        for element in elements:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, element[0])
            triangle.GetPointIds().SetId(1, element[1])
            triangle.GetPointIds().SetId(2, element[2])
            triangles.InsertNextCell(triangle)
            
        # 创建多边形数据
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(triangles)
        
        # 添加标量数据
        scalars = vtk.vtkFloatArray()
        scalars.SetName("Values")
        
        if plot_type == 'stress' and hasattr(result, 'stresses'):
            for stress in result.stresses:
                scalars.InsertNextValue(stress)
            polydata.GetCellData().SetScalars(scalars)
        elif plot_type in ['disp_x', 'disp_y'] and hasattr(result, 'displacements'):
            idx = 0 if plot_type == 'disp_x' else 1
            for disp in result.displacements[:, idx]:
                scalars.InsertNextValue(disp)
            polydata.GetPointData().SetScalars(scalars)
            
        # 创建映射器
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)
        mapper.SetScalarModeToUseCellData() if plot_type == 'stress' else mapper.SetScalarModeToUsePointData()
        
        # 设置颜色映射 - 完全匹配Matplotlib的jet颜色映射
        # 设置颜色映射 - 红色表示大值，蓝色表示小值
        lut = vtk.vtkLookupTable()
        # 反转颜色映射：红色到蓝色（大值到小值）
        lut.SetHueRange(0.0, 0.667)  # 红色到蓝色，反转后红色表示大值
        lut.SetSaturationRange(1.0, 1.0)
        lut.SetValueRange(1.0, 1.0)
        lut.SetNumberOfTableValues(256)
        
        # 确保数值范围与Matplotlib完全一致
        if plot_type == 'stress' and hasattr(result, 'stresses'):
            values = result.stresses
            min_val, max_val = np.min(values), np.max(values)
            lut.SetTableRange(min_val, max_val)
            mapper.SetScalarRange(min_val, max_val)
            for i, stress in enumerate(result.stresses):
                scalars.InsertNextValue(stress)
            polydata.GetCellData().SetScalars(scalars)
            mapper.SetScalarModeToUseCellData()
        elif plot_type in ['disp_x', 'disp_y'] and hasattr(result, 'displacements'):
            idx = 0 if plot_type == 'disp_x' else 1
            values = result.displacements[:, idx]
            min_val, max_val = np.min(values), np.max(values)
            lut.SetTableRange(min_val, max_val)
            mapper.SetScalarRange(min_val, max_val)
            for disp in values:
                scalars.InsertNextValue(disp)
            polydata.GetPointData().SetScalars(scalars)
            mapper.SetScalarModeToUsePointData()
        elif plot_type in ['disp_x_original', 'disp_y_original'] and hasattr(result, 'displacements'):
            idx = 0 if plot_type == 'disp_x_original' else 1
            values = result.displacements[:, idx]
            min_val, max_val = np.min(values), np.max(values)
            lut.SetTableRange(min_val, max_val)
            mapper.SetScalarRange(min_val, max_val)
            for disp in values:
                scalars.InsertNextValue(disp)
            polydata.GetPointData().SetScalars(scalars)
            mapper.SetScalarModeToUsePointData()
        
        lut.Build()
        mapper.SetLookupTable(lut)
        
        # 创建演员
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        
        self.renderer.AddActor(actor)
        
        # 添加颜色条
        self.add_colorbar(mapper, plot_type)
        
        # 添加网格线
        self.add_wireframe(polydata)
        
    def add_colorbar(self, mapper, plot_type, scale_factor=1.0):
        """添加颜色条"""
        colorbar = vtk.vtkScalarBarActor()
        colorbar.SetLookupTable(mapper.GetLookupTable())
        
        # 设置标题 - 完全匹配Matplotlib的格式
        titles = {
            'stress': 'Von Mises 应力云图 (Pa)',
            'disp_x': f'水平位移 (X) [放大{scale_factor:.0f}倍] (m)' if scale_factor > 1 else '水平位移 (X) (m)',
            'disp_y': f'竖直位移 (Y) [放大{scale_factor:.0f}倍] (m)' if scale_factor > 1 else '竖直位移 (Y) (m)',
            'disp_x_original': '水平位移 (X) [原始尺寸] (m)',
            'disp_y_original': '竖直位移 (Y) [原始尺寸] (m)'
        }
        colorbar.SetTitle(titles.get(plot_type, '数值'))
        
        # 设置颜色条的数值格式 - 与Matplotlib一致
        colorbar.SetLabelFormat("%.2e")  # 科学计数法格式
        colorbar.SetNumberOfLabels(5)   # 显示5个标签
        
        # 设置位置和大小
        colorbar.SetPosition(0.85, 0.1)
        colorbar.SetWidth(0.1)
        colorbar.SetHeight(0.8)
        
        self.renderer.AddActor2D(colorbar)
        
    def add_wireframe(self, polydata):
        """添加网格线"""
        # 提取边缘
        edges = vtk.vtkExtractEdges()
        edges.SetInputData(polydata)
        
        # 创建映射器
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(edges.GetOutputPort())
        
        # 创建演员
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 0, 0)  # 黑色
        actor.GetProperty().SetLineWidth(1)
        actor.GetProperty().SetOpacity(0.3)
        
        self.renderer.AddActor(actor)
        
    def add_original_wireframe(self, nodes, elements):
        """添加原始形状的网格线作为对比"""
        # 创建原始形状的点
        points = vtk.vtkPoints()
        for x, y in nodes:
            points.InsertNextPoint(x, y, 0)
        
        # 创建三角形单元
        triangles = vtk.vtkCellArray()
        for element in elements:
            triangle = vtk.vtkTriangle()
            triangle.GetPointIds().SetId(0, element[0])
            triangle.GetPointIds().SetId(1, element[1])
            triangle.GetPointIds().SetId(2, element[2])
            triangles.InsertNextCell(triangle)
        
        # 创建多边形数据
        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetPolys(triangles)
        
        # 提取边缘
        edges = vtk.vtkExtractEdges()
        edges.SetInputData(polydata)
        
        # 创建映射器
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(edges.GetOutputPort())
        
        # 创建演员 - 灰色虚线，与Matplotlib一致
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.5, 0.5, 0.5)  # 灰色
        actor.GetProperty().SetLineWidth(1)
        actor.GetProperty().SetOpacity(0.3)
        actor.GetProperty().SetLineStipplePattern(0xAAAA)  # 虚线模式
        actor.GetProperty().SetLineStippleRepeatFactor(1)
        
        self.renderer.AddActor(actor)
        
    def change_view_mode(self, mode):
        """改变视图模式"""
        camera = self.renderer.GetActiveCamera()
        
        if mode == "2D平面视图":
            camera.SetPosition(0, 0, 10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 1, 0)
            camera.ParallelProjectionOn()
        elif mode == "3D透视视图":
            camera.SetPosition(10, 10, 10)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOff()
        elif mode == "等轴测视图":
            camera.SetPosition(5, 5, 5)
            camera.SetFocalPoint(0, 0, 0)
            camera.SetViewUp(0, 0, 1)
            camera.ParallelProjectionOn()
            
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
    def change_render_quality(self, quality):
        """改变渲染质量"""
        render_window = self.vtk_widget.GetRenderWindow()
        
        if quality == "高质量":
            render_window.SetMultiSamples(8)
            self.renderer.SetUseFXAA(True)
        elif quality == "标准":
            render_window.SetMultiSamples(4)
            self.renderer.SetUseFXAA(False)
        else:  # 快速预览
            render_window.SetMultiSamples(0)
            self.renderer.SetUseFXAA(False)
            
        render_window.Render()
        
    def reset_camera(self):
        """重置相机视图"""
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()
        
    def clear_plot(self):
        """清除绘图"""
        self.renderer.RemoveAllViewProps()
        self.vtk_widget.GetRenderWindow().Render()