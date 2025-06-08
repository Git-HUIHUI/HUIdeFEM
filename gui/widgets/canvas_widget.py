import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import numpy as np

class CanvasWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.colorbar = None  # 用于跟踪当前的colorbar
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self._setup_plot()

    def _setup_plot(self, title="模型预览"):
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.ax.set_title(title)
        self.ax.set_xlabel("X 坐标 (m)")
        self.ax.set_ylabel("Y 坐标 (m)")
        self.figure.tight_layout()

    def plot_problem(self, problem_def):
        self.ax.clear()
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
        self._setup_plot()
        self.canvas.draw()
    
    def plot_result(self, result, plot_type='stress'):
        self.ax.clear()
        # 清除之前的colorbar
        if self.colorbar is not None:
            try:
                self.colorbar.remove()
            except (AttributeError, ValueError):
                pass  # 忽略移除colorbar时的错误
            self.colorbar = None
            
        mesh = result.mesh
        nodes = mesh['vertices']
        elements = mesh['triangles']
        
        title, values, unit = "", None, ""
        if plot_type == 'stress':
            title, values, unit = "Von Mises 应力云图", result.stresses, "Pa"
        elif plot_type == 'disp_x':
            title, values, unit = "水平位移 (X)", result.displacements[:, 0], "m"
        elif plot_type == 'disp_y':
            title, values, unit = "竖直位移 (Y)", result.displacements[:, 1], "m"
        
        # 绘制云图
        if values is not None:
            if values.ndim == 1 and len(values) == len(elements): # 单元数据
                cax = self.ax.tripcolor(nodes[:, 0], nodes[:, 1], elements, facecolors=values, cmap='jet')
            elif values.ndim == 1 and len(values) == len(nodes): # 节点数据
                cax = self.ax.tricontourf(nodes[:, 0], nodes[:, 1], elements, values, cmap='jet', levels=20)
            self.colorbar = self.figure.colorbar(cax, ax=self.ax, label=f"{title} ({unit})")
        
        # 叠加网格
        self.ax.triplot(nodes[:, 0], nodes[:, 1], elements, 'k-', linewidth=0.5, alpha=0.5)

        self._setup_plot(title=title)
        self.canvas.draw()

    def clear_plot(self):
        self.ax.clear()
        # 清除colorbar
        if self.colorbar is not None:
            try:
                self.colorbar.remove()
            except (AttributeError, ValueError):
                pass  # 忽略移除colorbar时的错误
            self.colorbar = None
        self._setup_plot()
        self.canvas.draw()
