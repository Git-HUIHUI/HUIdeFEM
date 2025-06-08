from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any
import numpy as np

@dataclass
class Material:
    """
    定义一种材料及其物理属性。
    """
    id: int = 0
    name: str = "Default Material"
    elastic_modulus: float = 2.0e7  # 弹性模量 E, 单位: 帕斯卡 (Pa)
    poisson_ratio: float = 0.3      # 泊松比 ν, 无量纲
    unit_weight: float = 18000.0    # 重度, 单位: 牛顿/立方米 (N/m³)

@dataclass
class ProblemDefinition:
    """
    一个数据容器，持有用户定义的完整有限元问题信息。
    它将在GUI和核心计算模块之间传递。
    """
    # 1. 几何骨架 (Geometry Skeleton)
    # 顶点列表: 存储每个顶点的 (x, y) 坐标
    vertices: List[Tuple[float, float]] = field(default_factory=list)
    # 线段列表: 存储每个线段的 (起始顶点ID, 结束顶点ID)
    segments: List[Tuple[int, int]] = field(default_factory=list)

    # 2. 物理定义 (Physics Definition)
    # 材料库: 存储所有已定义的材料, key为材料名称
    materials: Dict[str, Material] = field(default_factory=dict)
    # 区域列表: 存储用于定义材料区域的代表点 (x, y, material_id)
    regions: List[Tuple[float, float, int]] = field(default_factory=list)

    # 3. 边界条件 (Boundary Conditions)
    # 约束字典: 将线段ID映射到约束类型 (例如: "Fixed", "Roller_X")
    constraints: Dict[int, str] = field(default_factory=dict)
    # 荷载字典: 将线段ID映射到荷载值 (例如: 均布荷载 N/m)
    loads: Dict[int, float] = field(default_factory=dict)
    # 目标点位移: 需要输出位移的目标点
    target_points: Dict[str, Tuple[float, float]] = field(default_factory=dict)

@dataclass
class FemResult:
    """
    一个数据容器，持有有限元分析计算出的所有结果。
    """
    # 从 'triangle' 库得到的原始网格数据
    mesh: Dict[str, Any] = field(default_factory=dict)

    # 节点位移向量, 形状: (节点数 * 2, 1)
    displacements: np.ndarray = field(default_factory=lambda: np.array([]))

    # 单元应力 (例如: 冯·米塞斯应力), 形状: (单元数,)
    stresses: np.ndarray = field(default_factory=lambda: np.array([]))
    
    # 节点位移 (水平)
    displacements_x: np.ndarray = field(default_factory=lambda: np.array([]))

    # 目标点的位移结果
    target_displacements: Dict[str, Tuple[float, float]] = field(default_factory=dict)

    # 可以在此处添加其他需要输出的结果
