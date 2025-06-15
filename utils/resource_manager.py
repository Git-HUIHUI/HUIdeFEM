import sys
import os

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和打包环境"""
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境 - 使用脚本所在目录的父目录作为基础路径
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_icon_path(icon_name):
    """获取图标文件路径"""
    return get_resource_path(os.path.join('resources', 'icons', icon_name))

def get_example_path(example_name):
    """获取示例文件路径"""
    return get_resource_path(os.path.join('examples', example_name))

def safe_get_icon_path(icon_name):
    """安全获取图标路径，如果文件不存在返回None"""
    icon_path = get_icon_path(icon_name)
    return icon_path if os.path.exists(icon_path) else None

def safe_get_example_path(example_name):
    """安全获取示例文件路径，如果文件不存在返回None"""
    example_path = get_example_path(example_name)
    return example_path if os.path.exists(example_path) else None