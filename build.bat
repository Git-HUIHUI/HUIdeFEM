@echo off
echo 开始打包SlopeFEM_2D...

:: 清理之前的构建文件
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

:: 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

:: 使用PyInstaller打包
echo 开始打包...
pyinstaller build.spec

echo 打包完成！可执行文件位于 dist/SlopeFEM_2D/ 目录中
pause