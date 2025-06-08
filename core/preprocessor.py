import triangle as tr
from core.fem_model import ProblemDefinition

def create_mesh(problem: ProblemDefinition, mesh_opts='pq30a0.1'):
    """
    使用 'triangle' 库为给定的问题定义生成网格。

    Args:
        problem (ProblemDefinition): 包含顶点、线段、区域等信息的对象。
        mesh_opts (str): 'triangle' 库的剖分选项。
                         'p': PSLG (平面直线图)
                         'q30': 最小角度为30度的质量约束
                         'a': 施加最大面积约束

    Returns:
        dict: triangle库生成的网格字典, 如果失败则返回None。
    """
    if not problem.vertices or not problem.segments:
        print("错误: 无法生成网格，顶点或线段未定义。")
        return None

    # 将问题定义打包成triangle库所需的格式
    geom = {
        'vertices': problem.vertices,
        'segments': problem.segments
    }
    if problem.regions:
        # triangle需要区域属性，这里我们将材料ID作为属性
        # triangle区域格式: [x, y, attribute, max_area]
        # 我们暂时不使用最大面积约束，所以设为-1
        regions_for_tri = [[r[0], r[1], r[2], -1] for r in problem.regions]
        geom['regions'] = regions_for_tri

    print(f"正在使用选项 '{mesh_opts}' 生成网格...")
    try:
        mesh = tr.triangulate(geom, mesh_opts)
        print("网格生成成功！")
        # 为每个单元附加材料属性
        if 'regions' in geom:
            # triangle的'triangle_attributes'字段存储了每个单元的区域属性
            mesh['element_attributes'] = mesh.get('triangle_attributes', [])
        else:
            # 如果没有定义区域，为所有单元分配默认材料ID (假设为第一个材料的ID)
            num_elements = len(mesh['triangles'])
            default_material_id = list(problem.materials.keys())[0] if problem.materials else "default"
            # 获取材料的ID值
            if problem.materials:
                default_id = list(problem.materials.values())[0].id
            else:
                default_id = 1  # 默认材料ID
            mesh['element_attributes'] = [[default_id] for _ in range(num_elements)]
        return mesh
    except Exception as e:
        print(f"网格生成失败: {e}")
        return None
