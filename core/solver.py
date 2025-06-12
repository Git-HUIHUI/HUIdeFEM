import numpy as np
from scipy.sparse import lil_matrix
from .utils import get_d_matrix, get_b_matrix, is_point_on_segment

class FemSolver:
    """
    有限元求解器类。
    """
    def __init__(self, problem, mesh):
        self.problem = problem
        self.mesh = mesh
        self.nodes = mesh['vertices']
        self.elements = mesh['triangles']
        self.num_nodes = len(self.nodes)
        self.total_dof = self.num_nodes * 2  # 每个节点2个自由度 (x, y)

        # 全局刚度矩阵 (K) 和 全局荷载向量 (F)
        self.K = lil_matrix((self.total_dof, self.total_dof))
        self.F = np.zeros((self.total_dof, 1))
        
        # 罚函数法使用的大数
        self.penalty_value = 1.0e20

    def solve(self):
        """
        执行有限元分析全过程。
        """
        print("开始组装全局刚度矩阵...")
        self._assemble_global_stiffness()
        
        print("开始施加边界条件...")
        self._apply_boundary_conditions()
        
        print("开始组装荷载向量...")
        self._assemble_load_vector()
        
        print("开始求解线性方程组...")
        # 将稀疏矩阵转换为更适合求解的CSR格式
        K_csr = self.K.tocsr()
        
        try:
            displacements = np.linalg.solve(K_csr.toarray(), self.F)
            print("求解成功！")
            return displacements
        except np.linalg.LinAlgError as e:
            print(f"求解失败：矩阵为奇异矩阵。请检查约束是否足够。错误: {e}")
            return None

    def _assemble_global_stiffness(self):
        """组装全局刚度矩阵。"""
        mat_id_map = {mat.id: mat for mat in self.problem.materials.values()}
        
        for i, element in enumerate(self.elements):
            node_ids = element
            p1, p2, p3 = self.nodes[node_ids[0]], self.nodes[node_ids[1]], self.nodes[node_ids[2]]
            
            # 获取单元的材料属性
            if i >= len(self.mesh['element_attributes']) or len(self.mesh['element_attributes'][i]) == 0:
                # 如果没有材料属性，使用第一个可用材料
                if mat_id_map:
                    material = list(mat_id_map.values())[0]
                    print(f"警告: 单元 {i} 没有材料属性，使用默认材料 {material.name}")
                else:
                    raise ValueError(f"单元 {i} 没有材料属性，且没有定义任何材料。")
            else:
                element_attr = self.mesh['element_attributes'][i][0]
                material = mat_id_map.get(int(element_attr))
                if not material:
                    raise ValueError(f"单元 {i} 的材料ID {element_attr} 无效。")

            # 计算D矩阵和B矩阵
            D = get_d_matrix(material.elastic_modulus, material.poisson_ratio)
            B = get_b_matrix(p1, p2, p3)
            
            if B is None: continue # 忽略面积为0的单元

            # 计算单元面积
            area = 0.5 * np.linalg.det(np.array([[1, p1[0], p1[1]], [1, p2[0], p2[1]], [1, p3[0], p3[1]]]))

            # 计算单元刚度矩阵 ke = B^T * D * B * area * t (厚度t=1)
            ke = B.T @ D @ B * area
            
            # 组装到全局刚度矩阵
            dof_indices = [node_ids[0]*2, node_ids[0]*2+1,
                           node_ids[1]*2, node_ids[1]*2+1,
                           node_ids[2]*2, node_ids[2]*2+1]
            
            for r in range(6):
                for c in range(6):
                    self.K[dof_indices[r], dof_indices[c]] += ke[r, c]

    def _apply_boundary_conditions(self):
        """使用罚函数法施加位移边界条件。"""
        constrained_nodes = self._find_constrained_nodes()
        
        for node_id, constraints in constrained_nodes.items():
            if 'x' in constraints:
                dof = node_id * 2
                self.K[dof, dof] += self.penalty_value
            if 'y' in constraints:
                dof = node_id * 2 + 1
                self.K[dof, dof] += self.penalty_value

    def _assemble_load_vector(self):
        """组装等效节点荷载向量。"""
        if not self.problem.loads:
            return
            
        # 使用字典记录每个节点应该承受的总荷载，避免重复施加
        node_loads = {}  # {node_id: total_load}
        
        loaded_nodes = self._find_loaded_nodes()
        
        for seg_id, node_ids in loaded_nodes.items():
            load_val = self.problem.loads[seg_id]
            p1, p2 = self.problem.vertices[self.problem.segments[seg_id][0]], self.problem.vertices[self.problem.segments[seg_id][1]]
            seg_length = np.linalg.norm(np.array(p1) - np.array(p2))
            
            # 计算该线段上每个节点应该承受的荷载
            if len(node_ids) == 0:
                continue
            elif len(node_ids) == 1:
                # 如果线段上只有一个节点（不太可能，但为了健壮性）
                nodal_force = seg_length * load_val
                node_id = node_ids[0]
                if node_id not in node_loads:
                    node_loads[node_id] = 0.0
                node_loads[node_id] += nodal_force
            else:
                # 线段上有多个节点，需要按照节点间距离分配荷载
                # 对于均布荷载，可以按照节点在线段上的分布来分配
                
                # 获取线段上所有节点的坐标
                seg_nodes = [(node_id, self.nodes[node_id]) for node_id in node_ids]
                
                # 按照在线段上的位置排序
                seg_vector = np.array(p2) - np.array(p1)
                seg_nodes.sort(key=lambda x: np.dot(np.array(x[1]) - np.array(p1), seg_vector))
                
                # 为每个节点分配荷载
                for i, (node_id, node_coord) in enumerate(seg_nodes):
                    if i == 0:  # 第一个节点
                        if len(seg_nodes) == 1:
                            segment_length = seg_length
                        else:
                            next_coord = seg_nodes[i+1][1]
                            segment_length = np.linalg.norm(np.array(next_coord) - np.array(node_coord)) / 2
                    elif i == len(seg_nodes) - 1:  # 最后一个节点
                        prev_coord = seg_nodes[i-1][1]
                        segment_length = np.linalg.norm(np.array(node_coord) - np.array(prev_coord)) / 2
                    else:  # 中间节点
                        prev_coord = seg_nodes[i-1][1]
                        next_coord = seg_nodes[i+1][1]
                        segment_length = (np.linalg.norm(np.array(node_coord) - np.array(prev_coord)) + 
                                        np.linalg.norm(np.array(next_coord) - np.array(node_coord))) / 2
                    
                    nodal_force = segment_length * load_val
                    
                    if node_id not in node_loads:
                        node_loads[node_id] = 0.0
                    node_loads[node_id] += nodal_force
        
        # 将计算出的节点荷载施加到全局荷载向量中
        for node_id, total_load in node_loads.items():
            dof = node_id * 2 + 1  # Y方向自由度
            self.F[dof] -= total_load  # 荷载向下为负

    def _find_constrained_nodes(self):
        """在网格中找到所有被约束的节点。"""
        constrained_nodes = {}
        for seg_id, const_type in self.problem.constraints.items():
            p1 = self.problem.vertices[self.problem.segments[seg_id][0]]
            p2 = self.problem.vertices[self.problem.segments[seg_id][1]]
            
            for node_id, node_coord in enumerate(self.nodes):
                if is_point_on_segment(node_coord, p1, p2):
                    if node_id not in constrained_nodes:
                        constrained_nodes[node_id] = set()
                    
                    if "固定" in const_type:
                        constrained_nodes[node_id].update(['x', 'y'])
                    elif "X向" in const_type:
                        constrained_nodes[node_id].add('x')
                    elif "Y向" in const_type:
                        constrained_nodes[node_id].add('y')
        return constrained_nodes
        
    def _find_loaded_nodes(self):
        """在网格中找到所有施加了荷载的节点。"""
        loaded_nodes_on_segs = {}
        for seg_id in self.problem.loads.keys():
            p1 = self.problem.vertices[self.problem.segments[seg_id][0]]
            p2 = self.problem.vertices[self.problem.segments[seg_id][1]]
            
            nodes_on_this_seg = []
            for node_id, node_coord in enumerate(self.nodes):
                if is_point_on_segment(node_coord, p1, p2):
                    nodes_on_this_seg.append(node_id)
            loaded_nodes_on_segs[seg_id] = nodes_on_this_seg
        return loaded_nodes_on_segs

