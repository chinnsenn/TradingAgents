"""
TradingAgents 主程序入口
包含完整的错误跟踪功能
"""

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from error_handler import setup_error_handling, with_error_handling, print_exception_details
import os
from datetime import datetime


@with_error_handling
def main():
    """主函数 - 运行TradingAgents分析"""
    # 启用全局错误处理
    setup_error_handling(enable_debug=True)
    
    print("🚀 TradingAgents 分析系统启动")
    print("=" * 50)
    
    try:
        # Create a custom config
        config = DEFAULT_CONFIG.copy()

        # Use environment variables or defaults for configuration
        config["llm_provider"] = os.getenv("LLM_PROVIDER", "google")
        config["backend_url"] = os.getenv("BACKEND_URL", "https://generativelanguage.googleapis.com/v1")
        config["deep_think_llm"] = os.getenv("DEEP_THINK_LLM", "gemini-2.0-flash")
        config["quick_think_llm"] = os.getenv("QUICK_THINK_LLM", "gemini-2.0-flash")
        config["max_debate_rounds"] = int(os.getenv("MAX_DEBATE_ROUNDS", "1"))
        config["online_tools"] = os.getenv("ONLINE_TOOLS", "True").lower() == "true"

        print(f"📊 配置信息:")
        print(f"  - LLM提供商: {config['llm_provider']}")
        print(f"  - 深度思考模型: {config['deep_think_llm']}")
        print(f"  - 快速思考模型: {config['quick_think_llm']}")
        print(f"  - 最大辩论轮数: {config['max_debate_rounds']}")
        print(f"  - 在线工具: {config['online_tools']}")

        # Initialize with custom config
        print("\n🤖 正在初始化TradingAgents...")
        ta = TradingAgentsGraph(debug=True, config=config)

        # Use environment variables for demonstration ticker and date
        demo_ticker = os.getenv("DEMO_TICKER", "NVDA")
        demo_date = os.getenv("DEMO_DATE", "2024-05-10")

        print(f"\n📈 开始分析 {demo_ticker} ({demo_date})...")

        # forward propagate
        _, decision = ta.propagate(demo_ticker, demo_date)
        
        print("\n" + "=" * 50)
        print("✅ 分析完成!")
        print(f"📊 交易决策: {decision}")
        print("=" * 50)

        # Memorize mistakes and reflect (commented out for demo)
        # ta.reflect_and_remember(1000) # parameter is the position returns
        
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")
        print_exception_details(e, "主程序执行")
        raise


if __name__ == "__main__":
    main()
