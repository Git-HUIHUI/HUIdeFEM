# -*- mode: python ; coding: utf-8 -*-
"""
SlopeFEM_2D PyInstaller 构建配置文件
优化后的配置，支持修复的资源路径管理
"""

import os

block_cipher = None

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[project_root],  # 添加项目根目录到路径
    binaries=[],
    datas=[
        ('resources', 'resources'),  # 包含资源文件夹
        ('examples', 'examples'),    # 包含示例文件
        ('utils', 'utils'),          # 确保utils模块被包含
    ],
    # 在hiddenimports中添加VTK相关模块
    hiddenimports=[
        'triangle',
        'scipy.spatial.qhull',
        'scipy.sparse.csgraph._validation',
        'vtk',
        'vtk.qt',
        'vtk.qt.QVTKRenderWindowInteractor',
        'vtkmodules',
        'vtkmodules.all',
        'vtkmodules.qt',
        'vtkmodules.qt.QVTKRenderWindowInteractor',
        'vtkmodules.util',
        'vtkmodules.util.numpy_support',
        'vtkmodules.numpy_interface',
        'vtkmodules.numpy_interface.dataset_adapter',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtSvg',
        'PyQt6.QtPrintSupport',
    ],
    hookspath=[],
    hooksconfig={
        'matplotlib': {'backends': ['QtAgg', 'SVG']},
    },
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SlopeFEM_2D',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 设置为False隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/计算.png'  # 设置应用图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SlopeFEM_2D'
)
