# 贡献指南

感谢您对 SlopeFEM_2D 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题
- 使用 [GitHub Issues](https://github.com/your-username/SlopeFEM_2D/issues) 报告 bug
- 提供详细的问题描述和复现步骤
- 包含您的操作系统、Python 版本等环境信息

### 提出功能请求
- 在 Issues 中描述您希望添加的功能
- 解释为什么这个功能对项目有价值
- 如果可能，提供实现思路

### 代码贡献

#### 开发环境设置
```bash
# 1. Fork 并克隆项目
git clone https://github.com/your-username/SlopeFEM_2D.git
cd SlopeFEM_2D

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装开发依赖
pip install pytest flake8 black isort
```

#### 开发流程
1. 创建新分支：`git checkout -b feature/your-feature-name`
2. 进行开发并确保代码质量
3. 运行测试：`python -m pytest tests/`
4. 运行验证：`python verify_fixes.py`
5. 提交更改：`git commit -m "Add: your feature description"`
6. 推送分支：`git push origin feature/your-feature-name`
7. 创建 Pull Request

#### 代码规范
- 遵循 PEP 8 Python 代码风格
- 使用 `black` 进行代码格式化
- 使用 `isort` 整理导入语句
- 添加适当的注释和文档字符串
- 为新功能编写测试

#### 提交信息规范
使用清晰的提交信息：
- `Add: 新功能描述`
- `Fix: 修复问题描述`
- `Update: 更新内容描述`
- `Refactor: 重构内容描述`
- `Docs: 文档更新描述`

## 📋 开发指南

### 项目结构
```
SlopeFEM_2D/
├── core/          # 核心计算模块
├── gui/           # 图形用户界面
├── utils/         # 工具模块
├── resources/     # 资源文件
├── examples/      # 示例文件
└── tests/         # 测试文件
```

### 添加新功能
1. 在相应模块中添加功能代码
2. 更新相关的 GUI 组件
3. 添加单元测试
4. 更新文档

### 修复 Bug
1. 创建测试用例重现问题
2. 修复代码
3. 确保测试通过
4. 验证修复效果

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试
python -m pytest tests/test_solver.py -v

# 运行验证脚本
python verify_fixes.py

# 测试资源路径
python test_resource_paths.py
```

### 编写测试
- 为新功能编写单元测试
- 测试文件放在 `tests/` 目录下
- 使用 `pytest` 框架
- 确保测试覆盖主要功能路径

## 📝 文档

### 更新文档
- 更新 README.md 中的功能描述
- 添加新功能的使用说明
- 更新 API 文档（如果适用）

### 代码注释
- 为复杂算法添加详细注释
- 使用中文注释（项目主要面向中文用户）
- 为公共 API 添加文档字符串

## 🎯 优先级

当前项目的开发优先级：

1. **Bug 修复** - 修复现有功能中的问题
2. **性能优化** - 提升渲染和计算性能
3. **用户体验** - 改进界面和交互
4. **新功能** - 添加新的分析功能
5. **文档完善** - 改进文档和示例

## 📞 联系方式

如有疑问，请通过以下方式联系：
- GitHub Issues
- 邮箱：3415023708@qq.com

感谢您的贡献！🎉
