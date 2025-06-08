import numpy as np
from .utils import get_d_matrix, get_b_matrix

class PostProcessor:
    """
    后处理器类，用于计算和提取结果。
    """
    def __init__(self, problem, mesh, displacements):
        self.problem = problem
        self.mesh = mesh
        self.nodes = mesh['vertices']
        self.elements = mesh['triangles']
        # 将位移向量重塑为 (节点数, 2) 的形式，方便索引
        self.displacements = displacements.reshape(-1, 2)

    def calculate_results(self):
        """计算所有后处理结果。"""
        print("开始计算单元应力...")
        stresses = self._calculate_element_stresses()
        
        print("开始提取目标点位移...")
        target_displacements = self._get_target_displacements()
        
        return stresses, target_displacements

    def _calculate_element_stresses(self):
        """计算每个单元的应力和冯·米塞斯(Von Mises)等效应力。"""
        mat_id_map = {mat.id: mat for mat in self.problem.materials.values()}
        von_mises_stresses = np.zeros(len(self.elements))

        for i, element in enumerate(self.elements):
            node_ids = element
            p1, p2, p3 = self.nodes[node_ids[0]], self.nodes[node_ids[1]], self.nodes[node_ids[2]]
            
            # 获取材料和D矩阵
            # 获取材料和D矩阵
            if i >= len(self.mesh['element_attributes']) or len(self.mesh['element_attributes'][i]) == 0:
                # 如果没有材料属性，使用第一个可用材料
                if mat_id_map:
                    material = list(mat_id_map.values())[0]
                else:
                    raise ValueError(f"单元 {i} 没有材料属性，且没有定义任何材料。")
            else:
                element_attr = self.mesh['element_attributes'][i][0]
                material = mat_id_map.get(int(element_attr))
                if not material:
                    raise ValueError(f"单元 {i} 的材料ID {element_attr} 无效。")
            D = get_d_matrix(material.elastic_modulus, material.poisson_ratio)
            
            # 获取B矩阵
            B = get_b_matrix(p1, p2, p3)
            if B is None:
                continue

            # 获取单元的节点位移向量 [u1, v1, u2, v2, u3, v3]^T
            element_disp = self.displacements[node_ids].flatten()

            # 计算应力 {sigma} = [D] * [B] * {u_e}
            sigma = D @ B @ element_disp
            sigma_x, sigma_y, tau_xy = sigma[0], sigma[1], sigma[2]

            # 计算冯·米塞斯等效应力
            # sigma_v = sqrt(sigma_x^2 - sigma_x*sigma_y + sigma_y^2 + 3*tau_xy^2)
            # 对于平面应变，还需考虑 sigma_z = nu * (sigma_x + sigma_y)
            sigma_z = material.poisson_ratio * (sigma_x + sigma_y)
            term1 = ((sigma_x - sigma_y)**2 + (sigma_y - sigma_z)**2 + (sigma_z - sigma_x)**2) / 2
            term2 = 3 * tau_xy**2
            von_mises_stresses[i] = np.sqrt(term1 + term2)
            
        return von_mises_stresses

    def _get_target_displacements(self):
        """找到距离目标点最近的节点的位移。"""
        target_results = {}
        if not self.problem.target_points:
            return target_results
            
        nodes_array = np.array(self.nodes)
        
        for name, point in self.problem.target_points.items():
            # 计算所有节点到目标点的距离
            distances = np.linalg.norm(nodes_array - np.array(point), axis=1)
            # 找到最近节点的索引
            nearest_node_id = np.argmin(distances)
            # 提取该节点的位移
            disp = self.displacements[nearest_node_id]
            target_results[name] = (disp[0], disp[1]) # (水平位移, 竖直位移)
            
        return target_results
