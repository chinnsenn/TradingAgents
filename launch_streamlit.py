#!/usr/bin/env python3
"""
TradingAgents Streamlit 应用启动脚本
替代 Gradio 版本的 launch_gui.py
"""

import subprocess
import sys
import os
from pathlib import Path

def check_streamlit_installation():
    """检查 Streamlit 是否已安装"""
    try:
        import streamlit
        print(f"✅ Streamlit 已安装，版本: {streamlit.__version__}")
        return True
    except ImportError:
        print("❌ Streamlit 未安装")
        return False

def install_dependencies():
    """安装依赖包"""
    print("📦 正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖包安装失败: {e}")
        return False

def check_config_files():
    """检查必要的配置文件"""
    config_files = {
        "llm_provider.json": "LLM 提供商配置文件",
        ".env": "环境变量配置文件（可选）"
    }
    
    missing_files = []
    for file_path, description in config_files.items():
        if not Path(file_path).exists():
            if file_path == "llm_provider.json":
                missing_files.append(f"{file_path} ({description})")
            else:
                print(f"⚠️  {file_path} 不存在，但这是可选的")
    
    if missing_files:
        print("❌ 缺少必要的配置文件:")
        for file in missing_files:
            print(f"   - {file}")
        print("\n💡 请确保创建 llm_provider.json 配置文件")
        print("   示例: cp llm_provider.json.example llm_provider.json")
        return False
    
    print("✅ 配置文件检查通过")
    return True

def launch_streamlit_app():
    """启动 Streamlit 应用"""
    print("🚀 正在启动 TradingAgents Streamlit 应用...")
    print("📡 应用将在浏览器中自动打开")
    print("🔗 默认地址: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止应用")
    print("-" * 50)
    
    try:
        # 启动 Streamlit 应用
        cmd = [
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"
        ]
        
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动 Streamlit 应用失败: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  应用已停止")
        return True
    
    return True

def main():
    """主函数"""
    print("🚀 TradingAgents Streamlit 启动器")
    print("=" * 50)
    
    # 检查当前工作目录
    current_dir = Path.cwd()
    app_file = current_dir / "streamlit_app.py"
    
    if not app_file.exists():
        print(f"❌ 在当前目录找不到 streamlit_app.py 文件")
        print(f"📁 当前目录: {current_dir}")
        print("💡 请确保在 TradingAgents 项目根目录运行此脚本")
        sys.exit(1)
    
    # 检查 Streamlit 安装
    if not check_streamlit_installation():
        print("📦 正在安装 Streamlit...")
        if not install_dependencies():
            print("❌ 无法安装依赖包，请手动安装:")
            print("   pip install streamlit")
            sys.exit(1)
    
    # 检查配置文件
    if not check_config_files():
        print("\n💡 配置文件设置指南:")
        print("1. 复制示例配置文件:")
        print("   cp llm_provider.json.example llm_provider.json")
        print("2. 编辑 llm_provider.json 配置您的 LLM 提供商")
        print("3. (可选) 创建 .env 文件设置 API 密钥")
        
        response = input("\n是否忽略配置检查继续启动? (y/N): ").strip().lower()
        if response != 'y' and response != 'yes':
            print("❌ 启动已取消")
            sys.exit(1)
        print("⚠️  忽略配置检查，继续启动...")
    
    # 显示启动信息
    print("\n📋 启动信息:")
    print(f"📁 工作目录: {current_dir}")
    print(f"🐍 Python 版本: {sys.version.split()[0]}")
    print(f"📱 应用文件: {app_file}")
    
    # 启动应用
    print("\n" + "="*50)
    success = launch_streamlit_app()
    
    if success:
        print("\n✅ 应用已成功启动和停止")
    else:
        print("\n❌ 应用启动失败")
        sys.exit(1)

if __name__ == "__main__":
    main()