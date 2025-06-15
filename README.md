# SlopeFEM_2D

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

**SlopeFEM_2D** 是一个基于有限元方法的二维边坡稳定性分析软件，采用 Python 开发，具有直观的图形用户界面。

## ✨ 项目简介

SlopeFEM_2D 是一个专业的二维有限元分析软件，专门用于边坡稳定性分析。该软件采用 PyQt6 构建现代化图形用户界面，集成 Matplotlib 和 VTK 双引擎进行可视化，使用 Triangle 库进行高质量网格剖分，提供从几何建模到结果分析的完整工作流。

## 🚀 主要功能

### 核心功能
- 🎯 **几何建模**：支持顶点、线段定义，实时可视化几何模型
- 🔧 **材料定义**：多材料支持，可定义弹性模量、泊松比、重度等参数
- ⚙️ **边界条件**：支持固定约束、滚动约束和分布荷载
- 🕸️ **网格剖分**：基于 Triangle 库的高质量自动网格生成
- 🧮 **有限元求解**：平面应变问题求解，计算节点位移和单元应力

### 双引擎可视化系统
- 📊 **Matplotlib (2D)**：传统2D可视化，快速响应，适合实时交互
- 🎨 **VTK (3D专业)**：专业3D可视化，支持多种视角和高质量渲染
- 🌈 **丰富的结果展示**：
  - Von Mises 应力云图
  - 位移云图（X方向、Y方向）
  - 变形图（可选放大显示）
  - 材料区域彩色显示
  - 目标点位移结果

### 高级功能
- 🎯 **目标点监测**：指定关键点的位移输出
- 📸 **高质量图像导出**：支持PNG、JPEG、TIFF、EPS等多种格式
- 💾 **项目管理**：支持项目保存/加载，预设案例导入
- 📋 **多格式导出**：支持CSV、Excel、PDF等格式的数据导出
- 📦 **一键打包**：支持打包为独立可执行文件

## 🛠️ 安装与运行

### 环境要求
- Python 3.8 或更高版本
- Windows 10/11（推荐）或 Linux/macOS

### 快速开始

```bash
# 克隆项目
git clone https://github.com/your-username/SlopeFEM_2D.git
cd SlopeFEM_2D

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 依赖库
- **PyQt6**: 图形用户界面框架
- **NumPy**: 数值计算基础库
- **Matplotlib**: 2D 绘图和可视化
- **VTK**: 3D 可视化工具包
- **Triangle**: 三角网格生成
- **SciPy**: 科学计算库
- **Pandas**: 数据处理（可选，用于 Excel 导出）
- **ReportLab**: PDF 生成（可选）

## 性能说明

### 渲染性能

- **2D可视化 (Matplotlib)**：响应速度快，适合实时交互和快速预览
- **3D可视化 (VTK)**：提供专业级可视化效果，但渲染时间较长
  - 高质量渲染模式下可能需要几秒钟的处理时间
  - 复杂模型的3D渲染和图像导出需要更多时间
  - 建议在需要高质量输出时使用，日常操作可使用2D模式

### 优化计划

当前版本优先保证功能完整性和结果准确性。渲染性能优化将在后续版本中进行，包括：
- 渲染管线优化
- 多线程渲染支持
- 渐进式渲染
- 缓存机制改进

## 使用建议

- 对于日常建模和快速分析，推荐使用Matplotlib (2D)模式
- 对于演示、报告和高质量输出，使用VTK (3D专业)模式
- 大型模型建议先在2D模式下完成建模和初步分析，最后切换到3D模式进行最终可视化

## 联系作者

如果您在使用过程中遇到问题、有建议或需要帮助，欢迎联系作者：

- 项目主页：[SlopeFEM_2D 项目主页](https://github.com/Git-HUIHUI/HUIdeFEM)
- 作者常用邮箱：3415023708@qq.com
感谢您的参与和支持！
