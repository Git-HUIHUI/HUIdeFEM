@echo off
echo 开始打包SlopeFEM_2D...

:: 清理之前的构建文件（保留build.spec）
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo 清理完成！

:: 检查Python环境
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到Python环境，请确保Python已安装并添加到PATH中
    exit /b 1
)

:: 测试资源路径
echo 测试资源路径管理器...
python test_resource_paths.py
if %ERRORLEVEL% neq 0 (
    echo 警告: 资源路径测试失败，但继续构建...
)

:: 检查依赖（不自动安装，避免意外更新）
echo 检查依赖包...
python -c "import PyQt6, numpy, triangle, matplotlib, vtk; print('所有依赖已安装')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 缺少必要的依赖库！
    echo 请运行：pip install -r requirements.txt
    pause
    exit /b 1
)

:: 使用PyInstaller打包
echo 开始打包...
pyinstaller build.spec
if %ERRORLEVEL% neq 0 (
    echo 错误: 打包失败
    exit /b 1
)

echo 打包完成！可执行文件位于 dist/SlopeFEM_2D/ 目录中
pause
