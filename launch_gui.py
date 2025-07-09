#!/usr/bin/env python3
"""
TradingAgents GUI启动脚本
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui_app import TradingAgentsGUI


def check_requirements():
    """检查系统要求"""
    print("🔍 检查系统要求...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误：需要Python 3.8或更高版本")
        return False
    
    # 检查必需的包
    required_packages = [
        'gradio',
        'langchain',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 错误：缺少必需的包：{', '.join(missing_packages)}")
        print("请运行：pip install -r requirements.txt")
        return False
    
    # 检查配置文件
    config_file = project_root / "llm_provider.json"
    if not config_file.exists():
        print("⚠️  警告：未找到 llm_provider.json 配置文件")
        print("部分功能可能无法正常使用")
    
    # 检查环境变量
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  警告：未找到 .env 文件")
        print("请创建 .env 文件并配置 FINNHUB_API_KEY")
    else:
        if not os.getenv("FINNHUB_API_KEY"):
            print("⚠️  警告：FINNHUB_API_KEY 未配置")
            print("请在 .env 文件中设置 FINNHUB_API_KEY")
    
    print("✅ 系统要求检查完成")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='TradingAgents GUI - 多代理LLM金融交易框架'
    )
    parser.add_argument(
        '--host', 
        default='0.0.0.0',
        help='服务器主机地址 (默认: 0.0.0.0)'
    )
    parser.add_argument(
        '--port', 
        type=int,
        default=7860,
        help='服务器端口 (默认: 7860)'
    )
    parser.add_argument(
        '--share', 
        action='store_true',
        help='创建公开分享链接'
    )
    parser.add_argument(
        '--debug', 
        action='store_true',
        help='启用debug模式'
    )
    parser.add_argument(
        '--skip-check', 
        action='store_true',
        help='跳过系统要求检查'
    )
    
    args = parser.parse_args()
    
    # 显示欢迎信息
    print("🚀 TradingAgents GUI - 多代理LLM金融交易框架")
    print("=" * 60)
    
    # 检查系统要求
    if not args.skip_check:
        if not check_requirements():
            sys.exit(1)
    
    # 创建GUI应用 (配置将从llm_provider.json读取)
    print("🔧 初始化GUI应用...")
    gui = TradingAgentsGUI()
    
    # 创建界面
    print("🎨 创建用户界面...")
    demo = gui.create_interface()
    
    # 启动服务器
    print(f"🌐 启动服务器 http://{args.host}:{args.port}")
    print("💡 LLM配置请在界面中通过llm_provider.json文件管理")
    print("=" * 60)
    
    try:
        demo.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            show_error=True,
            debug=args.debug
        )
    except KeyboardInterrupt:
        print("\n👋 感谢使用TradingAgents GUI!")
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()