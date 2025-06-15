#!/usr/bin/env python3
"""
测试资源路径管理器的脚本
用于验证在开发环境和打包环境中资源文件路径是否正确
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from utils.resource_manager import (
    get_resource_path, 
    get_icon_path, 
    get_example_path,
    safe_get_icon_path,
    safe_get_example_path
)

def test_resource_paths():
    """测试资源路径函数"""
    print("=" * 60)
    print("测试资源路径管理器")
    print("=" * 60)
    
    # 测试基础路径函数
    print("\n1. 测试基础路径函数:")
    base_path = get_resource_path("")
    print(f"   基础路径: {base_path}")
    print(f"   基础路径存在: {os.path.exists(base_path)}")
    
    # 测试图标路径
    print("\n2. 测试图标路径:")
    test_icons = [
        '计算.png', '新建项目.png', '打开项目.png', '保存项目.png',
        '材料库.png', '顶点.png', '线段.png', '区域.png', '边界.png',
        '目标点.png', '网格设置.png', '导出结果.png'
    ]
    
    for icon in test_icons:
        icon_path = get_icon_path(icon)
        safe_icon_path = safe_get_icon_path(icon)
        exists = os.path.exists(icon_path)
        print(f"   {icon:20} -> 存在: {exists:5} | 路径: {icon_path}")
        if not exists:
            print(f"   {'':20}    安全路径: {safe_icon_path}")
    
    # 测试示例文件路径
    print("\n3. 测试示例文件路径:")
    example_file = 'slope_problem.json'
    example_path = get_example_path(example_file)
    safe_example_path = safe_get_example_path(example_file)
    exists = os.path.exists(example_path)
    print(f"   {example_file:20} -> 存在: {exists:5} | 路径: {example_path}")
    if not exists:
        print(f"   {'':20}    安全路径: {safe_example_path}")
    
    # 测试资源文件夹结构
    print("\n4. 测试资源文件夹结构:")
    resources_path = get_resource_path('resources')
    if os.path.exists(resources_path):
        print(f"   resources文件夹: {resources_path}")
        icons_path = os.path.join(resources_path, 'icons')
        if os.path.exists(icons_path):
            icon_files = [f for f in os.listdir(icons_path) if f.endswith('.png')]
            print(f"   找到 {len(icon_files)} 个图标文件")
        else:
            print("   icons文件夹不存在")
    else:
        print("   resources文件夹不存在")
    
    examples_path = get_resource_path('examples')
    if os.path.exists(examples_path):
        print(f"   examples文件夹: {examples_path}")
        example_files = [f for f in os.listdir(examples_path) if f.endswith('.json')]
        print(f"   找到 {len(example_files)} 个示例文件")
    else:
        print("   examples文件夹不存在")
    
    # 检查是否在打包环境中
    print("\n5. 环境检测:")
    if hasattr(sys, '_MEIPASS'):
        print(f"   运行环境: PyInstaller打包环境")
        print(f"   临时路径: {sys._MEIPASS}")
    else:
        print(f"   运行环境: 开发环境")
        print(f"   工作目录: {os.getcwd()}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_resource_paths()
