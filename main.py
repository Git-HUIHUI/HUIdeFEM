import sys
from PyQt6.QtWidgets import QApplication

# 导入主窗口和控制器
from gui.main_window import MainWindow
from gui.app_controller import AppController

def main():
    """
    主函数，用于创建和启动应用程序。
    """
    # 初始化PyQt6应用
    app = QApplication(sys.argv)
    
    # 1. 创建控制器实例
    # 控制器是连接UI和后端逻辑的桥梁。它继承自QObject以使用信号。
    controller = AppController()

    # 2. 创建主窗口实例
    # 将控制器实例传递给主窗口，以便UI可以与之交互。
    window = MainWindow(controller)
    
    # 3. 显示主窗口
    window.show()

    # 启动Qt事件循环
    sys.exit(app.exec())


if __name__ == '__main__':
    # 确保此脚本作为主程序运行时才执行main函数
    main()
