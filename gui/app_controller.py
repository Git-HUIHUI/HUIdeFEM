from PyQt6.QtCore import QObject, pyqtSignal
from core.fem_model import ProblemDefinition, FemResult
from core.preprocessor import create_mesh
from core.solver import FemSolver
from core.postprocessor import PostProcessor

class AppController(QObject):
    """
    应用程序的控制器。继承自QObject以使用信号。
    """
    # 定义信号
    computation_started = pyqtSignal()
    computation_finished = pyqtSignal(bool, str) # success: bool, message: str
    
    def __init__(self):
        super().__init__()
        self.problem = ProblemDefinition()
        self.result = FemResult()

    def update_problem_from_dict(self, data):
        if data:
            self.problem.vertices = data.get('vertices', [])
            self.problem.segments = data.get('segments', [])
            self.problem.regions = data.get('regions', [])
            self.problem.constraints = data.get('constraints', {})
            self.problem.loads = data.get('loads', {})
            self.problem.target_points = data.get('target_points', {})

    def update_materials(self, materials_dict):
        self.problem.materials = materials_dict

    def run_analysis(self):
        """
        执行完整的有限元分析流程。
        """
        self.computation_started.emit()
        
        # 1. 网格剖分
        mesh = create_mesh(self.problem, 'pq30a1') # 'a1'表示最大单元面积为1
        if mesh is None:
            self.computation_finished.emit(False, "网格生成失败，请检查几何定义。")
            return
        self.result.mesh = mesh
        
        # 2. 求解
        solver = FemSolver(self.problem, mesh)
        displacements_vec = solver.solve()
        if displacements_vec is None:
            self.computation_finished.emit(False, "求解失败，请检查约束是否充分。")
            return
        self.result.displacements = displacements_vec.reshape(-1, 2)
        
        # 3. 后处理
        post_proc = PostProcessor(self.problem, mesh, displacements_vec)
        stresses, target_displacements = post_proc.calculate_results()
        self.result.stresses = stresses
        self.result.target_displacements = target_displacements
        
        self.computation_finished.emit(True, "计算成功完成！")
