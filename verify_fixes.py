#!/usr/bin/env python3
"""
验证路径修复的脚本
检查所有修复是否正确应用
"""

import os
import sys
import ast
import re

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_file_for_old_patterns(file_path):
    """检查文件中是否还有旧的路径模式"""
    old_patterns = [
        r'os\.path\.dirname\(os\.path\.dirname\(__file__\)\)',
        r'os\.path\.dirname\(os\.path\.dirname\(os\.path\.dirname\(__file__\)\)\)',
        r'os\.path\.abspath\("\."',
        r'os\.path\.join\(.*dirname.*__file__.*resources',
        r'os\.path\.join\(.*dirname.*__file__.*icons',
    ]
    
    issues = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        for i, line in enumerate(lines, 1):
            for pattern in old_patterns:
                if re.search(pattern, line):
                    issues.append(f"第{i}行: {line.strip()}")
    except Exception as e:
        issues.append(f"读取文件失败: {e}")
    
    return issues

def check_imports(file_path):
    """检查是否正确导入了资源管理器"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否导入了资源管理器
        has_resource_import = (
            'from utils.resource_manager import' in content or
            'import utils.resource_manager' in content
        )
        
        # 检查是否使用了资源管理器函数
        uses_resource_functions = any(func in content for func in [
            'get_icon_path', 'safe_get_icon_path', 'get_example_path', 'safe_get_example_path'
        ])
        
        return has_resource_import, uses_resource_functions
    except Exception:
        return False, False

def main():
    print("=" * 60)
    print("验证路径修复")
    print("=" * 60)
    
    # 需要检查的文件
    files_to_check = [
        'gui/main_window.py',
        'gui/widgets/input_panel.py',
        'gui/widgets/enhanced_canvas_widget.py',
        'gui/widgets/vtk_canvas_widget.py',
        'gui/widgets/results_panel.py',
        'gui/widgets/canvas_widget.py',
        'utils/resource_manager.py'
    ]
    
    print("\n1. 检查旧路径模式:")
    total_issues = 0
    for file_path in files_to_check:
        if os.path.exists(file_path):
            issues = check_file_for_old_patterns(file_path)
            if issues:
                print(f"   ❌ {file_path}:")
                for issue in issues:
                    print(f"      {issue}")
                total_issues += len(issues)
            else:
                print(f"   ✅ {file_path}: 无问题")
        else:
            print(f"   ⚠️  {file_path}: 文件不存在")
    
    print(f"\n   总计发现 {total_issues} 个问题")
    
    print("\n2. 检查资源管理器导入:")
    gui_files = [f for f in files_to_check if f.startswith('gui/')]
    for file_path in gui_files:
        if os.path.exists(file_path):
            has_import, uses_functions = check_imports(file_path)
            if has_import and uses_functions:
                print(f"   ✅ {file_path}: 正确导入和使用")
            elif has_import:
                print(f"   ⚠️  {file_path}: 已导入但未使用")
            elif uses_functions:
                print(f"   ❌ {file_path}: 使用了函数但未导入")
            else:
                print(f"   ❌ {file_path}: 未导入也未使用")
    
    print("\n3. 测试资源管理器功能:")
    try:
        from utils.resource_manager import (
            get_resource_path, get_icon_path, get_example_path,
            safe_get_icon_path, safe_get_example_path
        )
        
        # 测试基础功能
        base_path = get_resource_path("")
        print(f"   基础路径: {base_path}")
        print(f"   基础路径存在: {os.path.exists(base_path)}")
        
        # 测试图标路径
        icon_path = safe_get_icon_path('计算.png')
        print(f"   图标路径测试: {'✅ 成功' if icon_path else '❌ 失败'}")
        
        # 测试示例路径
        example_path = safe_get_example_path('slope_problem.json')
        print(f"   示例路径测试: {'✅ 成功' if example_path else '❌ 失败'}")
        
    except Exception as e:
        print(f"   ❌ 资源管理器测试失败: {e}")
    
    print("\n4. 检查build.spec配置:")
    if os.path.exists('build.spec'):
        with open('build.spec', 'r', encoding='utf-8') as f:
            spec_content = f.read()
        
        checks = [
            ("包含resources", "('resources', 'resources')" in spec_content),
            ("包含examples", "('examples', 'examples')" in spec_content),
            ("包含utils", "('utils', 'utils')" in spec_content),
            ("设置pathex", "pathex=" in spec_content),
        ]
        
        for check_name, result in checks:
            print(f"   {'✅' if result else '❌'} {check_name}")
    else:
        print("   ❌ build.spec文件不存在")
    
    print("\n5. 检查构建脚本:")
    build_files = ['build.bat', 'build.ps1']
    for build_file in build_files:
        if os.path.exists(build_file):
            print(f"   ✅ {build_file}: 存在")
        else:
            print(f"   ❌ {build_file}: 不存在")
    
    print("\n" + "=" * 60)
    if total_issues == 0:
        print("🎉 所有路径问题已修复！可以安全进行打包。")
    else:
        print(f"⚠️  发现 {total_issues} 个问题，建议修复后再打包。")
    print("=" * 60)

if __name__ == "__main__":
    main()
