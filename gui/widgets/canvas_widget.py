from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 使用 constrained_layout 替代 tight_layout 来避免警告
        self.figure = Figure(figsize=(10, 8), constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.ax = None
        self.colorbar = None
        
        # 初始化缩放相关属性
        self.original_xlim = None
        self.original_ylim = None
        
        # 初始化平移相关属性
        self.pan_start = None
        self.is_panning = False
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._create_axes()
        self._setup_plot()
        
        # 启用鼠标交互功能
        self._setup_mouse_interaction()

    def _setup_mouse_interaction(self):
        """设置鼠标交互功能（缩放和平移）"""
        # 连接鼠标事件
        self.canvas.mpl_connect('scroll_event', self._on_scroll)
        self.canvas.mpl_connect('button_press_event', self._on_mouse_press)
        self.canvas.mpl_connect('button_release_event', self._on_mouse_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)

    def _on_scroll(self, event):
        """处理鼠标滚轮事件（缩放）"""
        if event.inaxes != self.ax:
            return
            
        # 获取当前坐标轴范围
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        # 获取鼠标位置
        xdata = event.xdata
        ydata = event.ydata
        
        if xdata is None or ydata is None:
            return
            
        # 设置缩放因子
        if event.button == 'up':
            # 向上滚动，放大
            scale_factor = 0.9
        elif event.button == 'down':
            # 向下滚动，缩小
            scale_factor = 1.1
        else:
            return
            
        # 计算新的坐标轴范围
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
        
        # 以鼠标位置为中心进行缩放
        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
        
        new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
        new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]
        
        # 应用新的坐标轴范围
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        
        # 重新绘制
        self.canvas.draw()

    def _on_mouse_press(self, event):
        """处理鼠标按下事件"""
        if event.inaxes != self.ax:
            return
            
        if event.button == 1:  # 左键
            self.is_panning = True
            self.pan_start = (event.xdata, event.ydata)
            # 改变鼠标光标为移动状态
            self.canvas.setCursor(Qt.CursorShape.ClosedHandCursor)

    def _on_mouse_release(self, event):
        """处理鼠标释放事件"""
        if event.button == 1:  # 左键
            self.is_panning = False
            self.pan_start = None
            # 恢复鼠标光标
            self.canvas.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_mouse_move(self, event):
        """处理鼠标移动事件（平移）"""
        if not self.is_panning or self.pan_start is None:
            return
            
        if event.inaxes != self.ax:
            return
            
        if event.xdata is None or event.ydata is None:
            return
            
        # 计算移动距离
        dx = self.pan_start[0] - event.xdata
        dy = self.pan_start[1] - event.ydata
        
        # 获取当前坐标轴范围
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        
        # 应用平移
        new_xlim = [cur_xlim[0] + dx, cur_xlim[1] + dx]
        new_ylim = [cur_ylim[0] + dy, cur_ylim[1] + dy]
        
        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        
        # 重新绘制
        self.canvas.draw()

    def _create_axes(self):
        """创建坐标轴"""
        self.figure.clear()
        
        # 创建GridSpec布局，为colorbar预留空间
        from matplotlib.gridspec import GridSpec
        gs = GridSpec(1, 2, width_ratios=[20, 1], wspace=0.05)
        
        # 设置现代化的图形样式
        self.figure.patch.set_facecolor('#ffffff')
        
        # 创建主绘图区域
        self.ax = self.figure.add_subplot(gs[0])
        
        # 设置坐标轴样式
        self.ax.set_facecolor('#fafafa')
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
        self.ax.set_axisbelow(True)
        
        # 设置坐标轴标签样式
        self.ax.set_xlabel('X 坐标 (m)', fontsize=10, fontweight='bold', color='#333333')
        self.ax.set_ylabel('Y 坐标 (m)', fontsize=10, fontweight='bold', color='#333333')
        
        # 设置刻度样式
        self.ax.tick_params(axis='both', which='major', labelsize=9, colors='#666666')
        
        # 设置边框样式
        for spine in self.ax.spines.values():
            spine.set_color('#cccccc')
            spine.set_linewidth(1)
        
        # 创建colorbar区域（初始时隐藏）
        self.cbar_ax = self.figure.add_subplot(gs[1])
        self.cbar_ax.set_visible(False)  # 初始时隐藏colorbar轴
        self.colorbar = None
        
        # 移除 tight_layout 调用，因为使用了 constrained_layout

    def _setup_plot(self, title="模型预览"):
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.set_title(title)
        self.ax.set_xlabel("X 坐标 (m)")
        self.ax.set_ylabel("Y 坐标 (m)")
        # 移除 tight_layout 调用

    def reset_zoom(self):
        """重置缩放到初始视图"""
        if self.original_xlim is not None and self.original_ylim is not None:
            self.ax.set_xlim(self.original_xlim)
            self.ax.set_ylim(self.original_ylim)
            self.canvas.draw()

    def plot_problem(self, problem_def):
        self.ax.clear()
        self.cbar_ax.set_visible(False)  # 隐藏colorbar轴
        if self.colorbar is not None:
            self.colorbar = None
            
        verts, segs = np.array(problem_def.vertices), problem_def.segments
        
        # 绘制顶点
        if verts.size > 0:
            self.ax.plot(verts[:, 0], verts[:, 1], 'bo', label='顶点', markersize=4, zorder=5)
            for i, (x, y) in enumerate(verts): 
                self.ax.text(x, y, f' {i}', c='blue', fontsize=8)
        
        # 绘制线段
        if segs:
            for i, seg in enumerate(segs):
                if max(seg) < len(verts):
                    p1, p2 = verts[seg[0]], verts[seg[1]]
                    self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-')
        
        # 绘制区域点
        if problem_def.regions:
            region_points = np.array([r[:2] for r in problem_def.regions])
            self.ax.scatter(region_points[:, 0], region_points[:, 1], marker='x', c='g', s=80, label='区域点')
        
        # 绘制约束
        if problem_def.constraints:
            for seg_id, const_type in problem_def.constraints.items():
                if seg_id < len(segs) and max(segs[seg_id]) < len(verts):
                    p1, p2 = verts[segs[seg_id][0]], verts[segs[seg_id][1]]
                    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
                    if "固定" in const_type: 
                        self.ax.plot(mid[0], mid[1], 'ks', ms=7)
                    elif "X向" in const_type: 
                        self.ax.plot(mid[0], mid[1], 'k>', ms=7)
                    elif "Y向" in const_type: 
                        self.ax.plot(mid[0], mid[1], 'k^', ms=7)
        
        # 绘制荷载箭头（匀布荷载形式）
        if problem_def.loads:
            self._draw_distributed_loads(problem_def, verts, segs)
            
        # 绘制目标点
        if problem_def.target_points:
            for name, (x, y) in problem_def.target_points.items():
                self.ax.plot(x, y, 'ro', markersize=8, markeredgecolor='black', markeredgewidth=1, 
                           label='目标点' if name == list(problem_def.target_points.keys())[0] else "", zorder=6)
                self.ax.text(x, y, f' {name}', c='red', fontsize=10, fontweight='bold')
            
        self._setup_plot()
        
        # 保存初始视图范围
        self.original_xlim = self.ax.get_xlim()
        self.original_ylim = self.ax.get_ylim()
        
        self.canvas.draw()

    def plot_result(self, result, plot_type='stress'):
        # 清除主坐标轴内容
        self.ax.clear()
        
        # 清除colorbar
        if self.colorbar is not None:
            self.colorbar = None
        self.cbar_ax.clear()
        self.cbar_ax.set_visible(False)
            
        mesh = result.mesh
        nodes = mesh['vertices']
        elements = mesh['triangles']
        
        # 判断是否需要放大显示
        use_deformation = plot_type in ['disp_x', 'disp_y', 'disp_x_original', 'disp_y_original']
        use_scale = plot_type in ['disp_x', 'disp_y']  # 只有非原始模式才放大
        
        # 计算变形放大系数
        scale_factor = 1.0
        if use_deformation and use_scale and len(result.displacements) > 0:
            max_displacement = np.max(np.abs(result.displacements))
            if max_displacement > 0:
                # 根据模型尺寸自动计算放大系数
                model_size = max(np.max(nodes[:, 0]) - np.min(nodes[:, 0]), 
                               np.max(nodes[:, 1]) - np.min(nodes[:, 1]))
                scale_factor = model_size * 0.1 / max_displacement  # 变形显示为模型尺寸的10%
        
        # 计算变形后的节点坐标
        if use_deformation and len(result.displacements) > 0:
            deformed_nodes = nodes + scale_factor * result.displacements
        else:
            deformed_nodes = nodes
        
        title, values, unit = "", None, ""
        if plot_type == 'stress':
            title, values, unit = "Von Mises 应力云图", result.stresses, "Pa"
        elif plot_type == 'disp_x':
            title, values, unit = f"水平位移 (X) [放大{scale_factor:.0f}倍]", result.displacements[:, 0], "m"
        elif plot_type == 'disp_y':
            title, values, unit = f"竖直位移 (Y) [放大{scale_factor:.0f}倍]", result.displacements[:, 1], "m"
        elif plot_type == 'disp_x_original':
            title, values, unit = "水平位移 (X) [原始尺寸]", result.displacements[:, 0], "m"
        elif plot_type == 'disp_y_original':
            title, values, unit = "竖直位移 (Y) [原始尺寸]", result.displacements[:, 1], "m"
        
        # 绘制云图
        if values is not None:
            if values.ndim == 1 and len(values) == len(elements): # 单元数据
                cax = self.ax.tripcolor(deformed_nodes[:, 0], deformed_nodes[:, 1], elements, facecolors=values, cmap='jet')
            elif values.ndim == 1 and len(values) == len(nodes): # 节点数据
                cax = self.ax.tricontourf(deformed_nodes[:, 0], deformed_nodes[:, 1], elements, values, cmap='jet', levels=20)
            
            # 在固定的colorbar轴上创建colorbar
            self.cbar_ax.set_visible(True)
            self.colorbar = self.figure.colorbar(cax, cax=self.cbar_ax, label=f"{title} ({unit})")
        
        # 叠加网格 - 显示变形后的形状
        self.ax.triplot(deformed_nodes[:, 0], deformed_nodes[:, 1], elements, 'k-', linewidth=0.5, alpha=0.5)
        
        # 如果是放大位移图，额外显示原始形状作为对比
        if use_deformation and use_scale and scale_factor > 1:
            self.ax.triplot(nodes[:, 0], nodes[:, 1], elements, color='gray', linewidth=0.3, alpha=0.3, linestyle='--')

        self._setup_plot(title=title)
        self.canvas.draw()

    def clear_plot(self):
        # 清除所有内容并重新创建布局
        self._create_axes()
        self._setup_plot()
        self.canvas.draw()

    def _draw_distributed_loads(self, problem_def, verts, segs):
        """绘制匀布荷载箭头"""
        for seg_id, load_value in problem_def.loads.items():
            if seg_id < len(segs) and max(segs[seg_id]) < len(verts):
                p1, p2 = verts[segs[seg_id][0]], verts[segs[seg_id][1]]
                
                # 计算线段的方向向量和法向量
                seg_vec = np.array(p2) - np.array(p1)
                seg_length = np.linalg.norm(seg_vec)
                seg_unit = seg_vec / seg_length
                
                # 计算垂直于线段的单位法向量（向上为正）
                normal_vec = np.array([-seg_unit[1], seg_unit[0]])
                
                # 根据荷载值确定箭头方向和长度
                # 负荷载向下，正荷载向上
                arrow_direction = -np.sign(load_value) * normal_vec
                
                # 计算箭头长度（基于荷载大小和模型尺寸）
                model_size = max(np.max(verts[:, 0]) - np.min(verts[:, 0]), 
                               np.max(verts[:, 1]) - np.min(verts[:, 1]))
                max_arrow_length = model_size * 0.1  # 最大箭头长度为模型尺寸的10%
                
                # 根据荷载值计算箭头长度（可以根据需要调整比例）
                arrow_length = min(abs(load_value) / 10000.0, max_arrow_length)
                if arrow_length < model_size * 0.02:  # 最小箭头长度
                    arrow_length = model_size * 0.02
                
                # 沿线段均匀分布箭头
                num_arrows = max(3, int(seg_length / (model_size * 0.05)))  # 根据线段长度确定箭头数量
                
                for i in range(num_arrows):
                    # 计算箭头起点位置
                    t = (i + 0.5) / num_arrows  # 在线段上的参数位置
                    arrow_start = np.array(p1) + t * seg_vec
                    
                    # 计算箭头终点位置
                    arrow_end = arrow_start + arrow_direction * arrow_length
                    
                    # 绘制箭头
                    self.ax.annotate('', xy=arrow_end, xytext=arrow_start,
                                   arrowprops=dict(arrowstyle='->', color='orange', lw=1.5),
                                   zorder=4)
# 在现有的导入中添加
from PyQt6.QtGui import QIcon
import os

# 在 setup_ui 方法中修改结果显示控制面板部分
def setup_ui(self):
    # ... existing code ...
    
    # 获取图标路径
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'resources', 'icons')
    
    # 结果显示控制面板
    result_control_panel = QHBoxLayout()
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
    result_control_panel.addWidget(self.result_type_combo)
    
    result_control_panel.addWidget(QLabel("显示内容:"))
    self.result_type_combo = QComboBox()
    self.result_type_combo.addItems(["应力", "水平位移", "竖直位移"])
    self.result_type_combo.currentTextChanged.connect(self.change_result_type)
    # 为显示内容添加图标
    for i in range(self.result_type_combo.count()):
        self.result_type_combo.setItemIcon(i, QIcon(os.path.join(icon_path, '显示内容.png')))
