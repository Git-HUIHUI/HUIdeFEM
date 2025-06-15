# GitHub 同步指南

本文档指导您如何将 SlopeFEM_2D 项目同步到 GitHub。

## 📋 准备工作

### 1. 检查文件状态
确保所有必要的文件都已准备好：

```bash
# 检查项目文件
ls -la

# 应该包含以下文件：
# .gitignore          - Git 忽略文件
# .gitattributes      - Git 属性文件
# README.md           - 项目说明
# LICENSE             - 许可证文件
# CONTRIBUTING.md     - 贡献指南
# CHANGELOG.md        - 更新日志
# requirements.txt    - Python 依赖
# build.spec          - PyInstaller 配置
```

### 2. 清理不需要的文件
删除构建产生的临时文件：

```bash
# 删除构建文件夹（如果存在）
rm -rf build dist

# 删除 Python 缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete
```

## 🚀 GitHub 同步步骤

### 1. 初始化 Git 仓库

```bash
# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 检查状态
git status

# 首次提交
git commit -m "Initial commit: SlopeFEM_2D v1.0.0

- 完整的二维边坡有限元分析软件
- 基于 PyQt6 的现代化 GUI
- 双引擎可视化系统 (Matplotlib + VTK)
- 完整的前后处理工作流
- 支持 PyInstaller 打包
- 修复所有路径问题，支持打包部署"
```

### 2. 在 GitHub 上创建仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `SlopeFEM_2D`
   - **Description**: `二维边坡有限元分析软件 - 基于Python的专业边坡稳定性分析工具`
   - **Visibility**: Public（推荐）或 Private
   - **不要**勾选 "Add a README file"（我们已经有了）
   - **不要**勾选 "Add .gitignore"（我们已经有了）
   - **License**: MIT（我们已经有了）

### 3. 连接本地仓库到 GitHub

```bash
# 添加远程仓库（替换为您的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/SlopeFEM_2D.git

# 验证远程仓库
git remote -v

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 4. 验证同步结果

访问您的 GitHub 仓库页面，确认：
- [ ] 所有文件都已上传
- [ ] README.md 正确显示
- [ ] 许可证信息正确
- [ ] 项目描述完整

## 🔧 后续维护

### 日常提交流程

```bash
# 查看修改状态
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "描述您的修改"

# 推送到 GitHub
git push
```

### 创建发布版本

```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

### 分支管理

```bash
# 创建开发分支
git checkout -b develop

# 创建功能分支
git checkout -b feature/new-feature

# 合并分支
git checkout main
git merge feature/new-feature

# 删除已合并的分支
git branch -d feature/new-feature
```

## 📝 GitHub 仓库设置建议

### 1. 仓库设置
- 启用 Issues（问题跟踪）
- 启用 Wiki（如果需要详细文档）
- 设置分支保护规则（对于团队开发）

### 2. 添加主题标签
在仓库页面添加相关标签：
- `finite-element-analysis`
- `slope-stability`
- `python`
- `pyqt6`
- `engineering`
- `geotechnical`
- `visualization`
- `vtk`
- `matplotlib`

### 3. 设置仓库描述
```
二维边坡有限元分析软件 - 基于Python的专业边坡稳定性分析工具，支持完整的前后处理工作流和双引擎可视化
```

### 4. 添加网站链接
如果有项目主页或文档站点，在仓库设置中添加。

## 🎯 推广建议

1. **完善文档**：确保 README.md 包含清晰的安装和使用说明
2. **添加截图**：在 README.md 中添加软件界面截图
3. **创建示例**：提供更多使用示例和教程
4. **社区互动**：及时回复 Issues 和 Pull Requests
5. **版本发布**：定期发布新版本并编写发布说明

## ⚠️ 注意事项

1. **敏感信息**：确保没有提交密码、API 密钥等敏感信息
2. **大文件**：避免提交大型二进制文件，考虑使用 Git LFS
3. **许可证**：确保所有代码都符合 MIT 许可证要求
4. **依赖管理**：保持 requirements.txt 更新

完成以上步骤后，您的 SlopeFEM_2D 项目就成功同步到 GitHub 了！🎉
