import sys
import os

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和打包环境"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_icon_path(icon_name):
    """获取图标文件路径"""
    return get_resource_path(os.path.join('resources', 'icons', icon_name))

def get_example_path(example_name):
    """获取示例文件路径"""
    return get_resource_path(os.path.join('examples', example_name))