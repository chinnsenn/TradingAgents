#!/usr/bin/env python3
"""
LLM Provider 配置验证脚本
用于确认 llm_provider.json 被正确读取和使用
"""

import json
import sys
from pathlib import Path

def test_config_loading():
    """测试配置文件加载"""
    print("🔍 测试配置文件加载...")
    try:
        from config_utils import load_llm_providers
        config = load_llm_providers()
        providers_count = len(config.get("Providers", []))
        print(f"✅ 配置文件加载成功，找到 {providers_count} 个提供商")
        return True
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return False

def test_provider_functions():
    """测试提供商相关函数"""
    print("\n🔍 测试提供商相关函数...")
    try:
        from config_utils import get_provider_names, get_provider_models, get_provider_info
        
        providers = get_provider_names()
        print(f"✅ 获取提供商列表: {providers}")
        
        for provider in providers:
            models = get_provider_models(provider)
            info = get_provider_info(provider)
            print(f"✅ {provider}: {len(models)} 个模型, API: {info['api_base_url']}")
        
        return True
    except Exception as e:
        print(f"❌ 提供商函数测试失败: {e}")
        return False

def test_cli_integration():
    """测试CLI集成"""
    print("\n🔍 测试CLI集成...")
    try:
        from cli.utils import get_all_providers, get_provider_models
        
        providers = get_all_providers()
        print(f"✅ CLI 获取到 {len(providers)} 个提供商")
        
        for provider in providers:
            name = provider['name']
            models = get_provider_models(name)
            print(f"✅ CLI {name}: {len(models)} 个模型")
        
        return True
    except Exception as e:
        print(f"❌ CLI集成测试失败: {e}")
        return False

def test_gui_integration():
    """测试GUI集成"""
    print("\n🔍 测试GUI集成...")
    try:
        from config_utils import get_provider_names, get_provider_models
        
        providers = get_provider_names()
        print(f"✅ GUI 获取到 {len(providers)} 个提供商")
        
        for provider in providers:
            models = get_provider_models(provider)
            print(f"✅ GUI {provider}: {len(models)} 个模型")
        
        return True
    except Exception as e:
        print(f"❌ GUI集成测试失败: {e}")
        return False

def test_gui_styles():
    """测试GUI样式配置"""
    print("\n🔍 测试GUI样式配置...")
    try:
        from gui_styles import get_default_gui_config, DEFAULT_GUI_CONFIG
        
        config = get_default_gui_config()
        print(f"✅ GUI动态配置: provider={config['llm_provider']}, models={config['deep_model']}/{config['quick_model']}")
        
        return True
    except Exception as e:
        print(f"❌ GUI样式配置测试失败: {e}")
        return False

def test_configuration_completeness():
    """测试配置完整性"""
    print("\n🔍 测试配置完整性...")
    try:
        # 检查配置文件存在
        config_file = Path("llm_provider.json")
        if not config_file.exists():
            print("❌ llm_provider.json 文件不存在")
            return False
        
        # 检查JSON格式
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查必需字段
        if "Providers" not in config:
            print("❌ 配置文件缺少 'Providers' 字段")
            return False
        
        providers = config["Providers"]
        if not providers:
            print("❌ 配置文件中没有提供商")
            return False
        
        # 检查每个提供商的必需字段
        required_fields = ["name", "api_base_url", "models"]
        for i, provider in enumerate(providers):
            for field in required_fields:
                if field not in provider:
                    print(f"❌ 提供商 {i+1} 缺少必需字段: {field}")
                    return False
            
            if not provider["models"]:
                print(f"❌ 提供商 '{provider['name']}' 没有配置模型")
                return False
        
        print(f"✅ 配置完整性检查通过，{len(providers)} 个提供商配置正确")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 配置完整性检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 LLM Provider 配置验证开始...")
    print("=" * 50)
    
    tests = [
        test_configuration_completeness,
        test_config_loading,
        test_provider_functions,
        test_cli_integration,
        test_gui_integration,
        test_gui_styles
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！llm_provider.json 配置正确！")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置")
        return 1

if __name__ == "__main__":
    sys.exit(main())