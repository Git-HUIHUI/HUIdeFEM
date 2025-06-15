# SlopeFEM_2D PowerShell 构建脚本
# 优化版本，支持修复的资源路径管理

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "     SlopeFEM_2D 构建脚本 (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 第1步：清理旧的构建文件
Write-Host "[1/4] 清理旧的构建文件..." -ForegroundColor Yellow
if (Test-Path "build") {
    Write-Host "删除 build 文件夹..." -ForegroundColor Gray
    Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
}
if (Test-Path "dist") {
    Write-Host "删除 dist 文件夹..." -ForegroundColor Gray
    Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host "清理完成！" -ForegroundColor Green
Write-Host ""

# 第2步：检查Python环境
Write-Host "[2/4] 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python版本: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "错误：未找到Python环境！" -ForegroundColor Red
    Write-Host "请确保Python已安装并添加到PATH中" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查依赖
Write-Host "检查依赖包..." -ForegroundColor Gray
try {
    python -c "import PyQt6, numpy, triangle, matplotlib, vtk; print('所有依赖已安装')" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "依赖检查失败"
    }
    Write-Host "所有依赖已安装" -ForegroundColor Green
} catch {
    Write-Host "错误：缺少必要的依赖库！" -ForegroundColor Red
    Write-Host "请运行：pip install -r requirements.txt" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 1
}
Write-Host ""

# 第3步：测试资源路径
Write-Host "[3/4] 测试资源路径管理器..." -ForegroundColor Yellow
try {
    python test_resource_paths.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "警告：资源路径测试失败，但继续构建..." -ForegroundColor Yellow
    } else {
        Write-Host "资源路径测试通过！" -ForegroundColor Green
    }
} catch {
    Write-Host "警告：无法运行资源路径测试，但继续构建..." -ForegroundColor Yellow
}
Write-Host ""

# 第4步：开始构建
Write-Host "[4/4] 开始构建 SlopeFEM_2D..." -ForegroundColor Yellow
try {
    pyinstaller build.spec
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller构建失败"
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "           构建完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "可执行文件位置：dist\SlopeFEM_2D\SlopeFEM_2D.exe" -ForegroundColor Cyan
    
    # 检查生成的文件
    $exePath = "dist\SlopeFEM_2D\SlopeFEM_2D.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-Host "文件大小：$([math]::Round($fileSize, 2)) MB" -ForegroundColor Gray
    }
    
} catch {
    Write-Host ""
    Write-Host "构建失败！" -ForegroundColor Red
    Write-Host "错误信息：$_" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

Write-Host ""
Read-Host "按任意键退出"
