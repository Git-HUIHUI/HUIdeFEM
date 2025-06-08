import numpy as np

def get_d_matrix(E, nu):
    """
    计算平面应变问题的弹性本构矩阵 [D]。

    Args:
        E (float): 弹性模量.
        nu (float): 泊松比.

    Returns:
        np.ndarray: 3x3的D矩阵.
    """
    factor = E / ((1 + nu) * (1 - 2 * nu))
    d_matrix = np.array([
        [1 - nu, nu, 0],
        [nu, 1 - nu, 0],
        [0, 0, (1 - 2 * nu) / 2]
    ])
    return factor * d_matrix

def get_b_matrix(p1, p2, p3):
    """
    计算常应变三角形单元(CST)的应变-位移矩阵 [B]。

    Args:
        p1, p2, p3 (tuple): 三角形单元三个顶点的(x, y)坐标。

    Returns:
        np.ndarray: 3x6的B矩阵, 或者在面积为0时返回None.
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    # 计算单元面积的两倍
    area2 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    
    if abs(area2) < 1e-12: # 避免除以零
        return None

    # 定义bi, ci等系数
    b1, b2, b3 = y2 - y3, y3 - y1, y1 - y2
    c1, c2, c3 = x3 - x2, x1 - x3, x2 - x1

    b_matrix = (1 / area2) * np.array([
        [b1, 0, b2, 0, b3, 0],
        [0, c1, 0, c2, 0, c3],
        [c1, b1, c2, b2, c3, b3]
    ])
    
    return b_matrix

def is_point_on_segment(p, a, b, tol=1e-6):
    """
    检查点p是否在线段ab上（带容差）。
    """
    p, a, b = np.array(p), np.array(a), np.array(b)
    # 检查共线性
    cross_product = np.linalg.norm(np.cross(b-a, p-a))
    if cross_product > tol:
        return False
    # 检查是否在线段范围内
    dot_product = np.dot(p-a, b-a)
    if dot_product < 0 or dot_product > np.dot(b-a, b-a):
        return False
    return True
