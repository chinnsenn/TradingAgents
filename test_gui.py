#!/usr/bin/env python3
"""
TradingAgents GUI测试脚本
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试导入功能"""
    print("🔍 测试导入功能...")
    
    try:
        import gradio as gr
        print("✅ Gradio导入成功")
    except ImportError as e:
        print(f"❌ Gradio导入失败：{e}")
        return False
    
    try:
        from gui_app import TradingAgentsGUI
        print("✅ TradingAgentsGUI导入成功")
    except ImportError as e:
        print(f"❌ TradingAgentsGUI导入失败：{e}")
        return False
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        print("✅ TradingAgentsGraph导入成功")
    except ImportError as e:
        print(f"❌ TradingAgentsGraph导入失败：{e}")
        return False
    
    return True

def test_gui_creation():
    """测试GUI创建"""
    print("🔍 测试GUI创建...")
    
    try:
        from gui_app import TradingAgentsGUI
        gui = TradingAgentsGUI()
        print("✅ GUI实例创建成功")
        
        # 测试基础方法
        analyst_choices = gui.get_analyst_choices()
        print(f"✅ 分析师选择：{len(analyst_choices)}个选项")
        
        llm_providers = gui.get_llm_providers()
        print(f"✅ LLM提供商：{len(llm_providers)}个选项")
        
        # 测试状态格式化
        status_display = gui.format_status_display()
        print("✅ 状态显示格式化成功")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI创建失败：{e}")
        return False

def test_interface_creation():
    """测试界面创建"""
    print("🔍 测试界面创建...")
    
    try:
        from gui_app import TradingAgentsGUI
        gui = TradingAgentsGUI()
        demo = gui.create_interface()
        print("✅ Gradio界面创建成功")
        return True
        
    except Exception as e:
        print(f"❌ 界面创建失败：{e}")
        return False

def test_core_functionality():
    """测试核心功能"""
    print("🔍 测试核心功能...")
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 创建配置
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = 1
        config["online_tools"] = False  # 使用离线模式测试
        
        # 尝试创建图
        graph = TradingAgentsGraph(
            selected_analysts=["market"],
            config=config,
            debug=True
        )
        print("✅ 交易图创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 核心功能测试失败：{e}")
        return False

def test_api_keys():
    """测试API密钥配置"""
    print("🔍 测试API密钥配置...")
    
    api_keys = {
        'ANTHROPIC_API_KEY': 'Anthropic',
        'GOOGLE_API_KEY': 'Google',
        'FINNHUB_API_KEY': 'Finnhub'
    }
    
    configured_keys = []
    missing_keys = []
    
    for key, name in api_keys.items():
        if os.getenv(key):
            configured_keys.append(name)
        else:
            missing_keys.append(name)
    
    if configured_keys:
        print(f"✅ 已配置的API密钥：{', '.join(configured_keys)}")
    
    if missing_keys:
        print(f"⚠️  缺少的API密钥：{', '.join(missing_keys)}")
        print("   部分功能可能无法使用")
    
    return len(configured_keys) > 0

def main():
    """主测试函数"""
    print("🧪 TradingAgents GUI测试")
    print("=" * 50)
    
    tests = [
        ("导入功能", test_imports),
        ("GUI创建", test_gui_creation),
        ("界面创建", test_interface_creation),
        ("核心功能", test_core_functionality),
        ("API密钥", test_api_keys)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}测试")
        print("-" * 30)
        
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name}测试通过")
            else:
                print(f"❌ {test_name}测试失败")
        except Exception as e:
            print(f"❌ {test_name}测试异常：{e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果：{passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！GUI已准备就绪")
        print("\n🚀 启动GUI请运行：python launch_gui.py")
    else:
        print("⚠️  部分测试失败，请检查配置")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)