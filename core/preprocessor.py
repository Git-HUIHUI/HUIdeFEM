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
        regions_for_tri = []
        for r in problem.regions:
            # r[2] 是材料名称，需要转换为材料ID
            material_name = r[2]
            if material_name in problem.materials:
                material_id = problem.materials[material_name].id
                regions_for_tri.append([r[0], r[1], material_id, -1])
            else:
                print(f"警告: 区域中的材料 '{material_name}' 未在材料库中找到")
                # 使用第一个可用材料的ID，如果没有材料则使用1
                if problem.materials:
                    default_material = list(problem.materials.values())[0]
                    default_id = default_material.id
                else:
                    default_id = 1
                regions_for_tri.append([r[0], r[1], default_id, -1])
        geom['regions'] = regions_for_tri

    print(f"正在使用选项 '{mesh_opts}' 生成网格...")
    try:
        mesh = tr.triangulate(geom, mesh_opts)
        print("网格生成成功！")
        # 在网格生成后添加
        print(f"调试: 定义的区域数据: {regions_for_tri}")
        triangle_attrs = mesh.get('triangle_attributes', [])
        print(f"调试: triangle生成的属性数量: {len(triangle_attrs)}")
        if len(triangle_attrs) > 0:
            print(f"调试: 前10个单元的属性: {triangle_attrs[:10]}")
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

# 将 'pq30a10.0' 改为 'pq30a10.0A'
mesh_opts = 'pq30a10.0A'  # A标志启用区域属性
