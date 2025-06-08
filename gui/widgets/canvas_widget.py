from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# 设置matplotlib中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.ax = None
        self.colorbar = None
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._create_axes()
        self._setup_plot()

    def _create_axes(self):
        """创建固定布局的坐标轴"""
        self.figure.clear()
        # 使用GridSpec创建固定布局，为colorbar预留空间
        gs = GridSpec(1, 2, figure=self.figure, width_ratios=[1, 0.05], wspace=0.1)
        self.ax = self.figure.add_subplot(gs[0])
        self.cbar_ax = self.figure.add_subplot(gs[1])
        self.cbar_ax.set_visible(False)  # 初始时隐藏colorbar轴
        self.colorbar = None

    def _setup_plot(self, title="模型预览"):
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.set_title(title)
        self.ax.set_xlabel("X 坐标 (m)")
        self.ax.set_ylabel("Y 坐标 (m)")
        self.figure.tight_layout()

    def plot_problem(self, problem_def):
        self.ax.clear()
        self.cbar_ax.set_visible(False)  # 隐藏colorbar轴
        if self.colorbar is not None:
            self.colorbar = None
            
        verts, segs = np.array(problem_def.vertices), problem_def.segments
        if verts.size > 0:
            self.ax.plot(verts[:, 0], verts[:, 1], 'bo', label='顶点', markersize=4, zorder=5)
            for i, (x, y) in enumerate(verts): self.ax.text(x, y, f' {i}', c='blue', fontsize=8)
        if segs:
            for i, seg in enumerate(segs):
                if max(seg) < len(verts):
                    p1, p2 = verts[seg[0]], verts[seg[1]]
                    self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r-')
        if problem_def.regions:
            region_points = np.array([r[:2] for r in problem_def.regions])
            self.ax.scatter(region_points[:, 0], region_points[:, 1], marker='x', c='g', s=80, label='区域点')
        if problem_def.constraints:
            for seg_id, const_type in problem_def.constraints.items():
                if seg_id < len(segs) and max(segs[seg_id]) < len(verts):
                    p1, p2 = verts[segs[seg_id][0]], verts[segs[seg_id][1]]
                    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
                    if "固定" in const_type: self.ax.plot(mid[0], mid[1], 'ks', ms=7)
                    elif "X向" in const_type: self.ax.plot(mid[0], mid[1], 'k>', ms=7)
                    elif "Y向" in const_type: self.ax.plot(mid[0], mid[1], 'k^', ms=7)
        
        # 绘制荷载箭头（匀布荷载形式）
        if problem_def.loads:
            self._draw_distributed_loads(problem_def, verts, segs)
            
        # 绘制目标点
        if problem_def.target_points:
            for name, (x, y) in problem_def.target_points.items():
                self.ax.plot(x, y, 'ro', markersize=8, markeredgecolor='black', markeredgewidth=1, label='目标点' if name == list(problem_def.target_points.keys())[0] else "", zorder=6)
                self.ax.text(x, y, f' {name}', c='red', fontsize=10, fontweight='bold')
            
        self._setup_plot()
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
