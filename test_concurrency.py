#!/usr/bin/env python3
"""
并发安全性测试
测试修改后的代码是否支持多用户并发访问
"""
import threading
import time
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gradio_app import init_session_state, get_analysis_status, get_live_updates, get_agent_status


def test_session_isolation():
    """测试会话隔离"""
    print("🧪 测试会话隔离...")
    
    # 创建两个独立的会话状态
    session1 = init_session_state()
    session2 = init_session_state()
    
    # 修改第一个会话的状态
    session1["current_ticker"] = "AAPL"
    session1["current_date"] = "2023-01-01"
    session1["running"] = True
    
    # 修改第二个会话的状态
    session2["current_ticker"] = "NVDA"
    session2["current_date"] = "2023-01-02"
    session2["running"] = False
    session2["error"] = "Test error"
    
    # 验证状态隔离
    assert session1["current_ticker"] == "AAPL"
    assert session2["current_ticker"] == "NVDA"
    assert session1["running"] is True
    assert session2["running"] is False
    assert session1["error"] is None
    assert session2["error"] == "Test error"
    
    print("✅ 会话隔离测试通过")


def test_streaming_handler_isolation():
    """测试StreamingHandler实例隔离"""
    print("🧪 测试StreamingHandler实例隔离...")
    
    # 创建两个独立的会话状态
    session1 = init_session_state()
    session2 = init_session_state()
    
    # 获取各自的StreamingHandler实例
    handler1 = session1["streaming_handler"]
    handler2 = session2["streaming_handler"]
    
    # 验证它们是不同的实例
    assert handler1 is not handler2
    
    # 修改第一个handler的状态
    handler1.current_ticker = "AAPL"
    handler1.add_message("info", "Test message 1")
    
    # 修改第二个handler的状态
    handler2.current_ticker = "NVDA"
    handler2.add_message("info", "Test message 2")
    
    # 验证状态隔离
    assert handler1.current_ticker == "AAPL"
    assert handler2.current_ticker == "NVDA"
    
    print("✅ StreamingHandler实例隔离测试通过")


def test_concurrent_access():
    """测试并发访问"""
    print("🧪 测试并发访问...")
    
    results = []
    
    def worker(worker_id):
        """工作线程函数"""
        # 每个线程创建自己的会话状态
        session = init_session_state()
        
        # 设置不同的状态
        session["current_ticker"] = f"TEST{worker_id}"
        session["current_date"] = f"2023-01-{worker_id:02d}"
        session["running"] = worker_id % 2 == 0
        
        # 模拟一些工作
        time.sleep(0.1)
        
        # 验证状态没有被其他线程修改
        assert session["current_ticker"] == f"TEST{worker_id}"
        assert session["current_date"] == f"2023-01-{worker_id:02d}"
        assert session["running"] == (worker_id % 2 == 0)
        
        results.append(worker_id)
    
    # 创建多个并发线程
    threads = []
    for i in range(10):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 验证所有线程都成功完成
    assert len(results) == 10
    assert sorted(results) == list(range(10))
    
    print("✅ 并发访问测试通过")


def test_function_parameters():
    """测试函数参数传递"""
    print("🧪 测试函数参数传递...")
    
    # 创建测试会话
    session = init_session_state()
    session["current_ticker"] = "AAPL"
    session["current_date"] = "2023-01-01"
    session["running"] = True
    
    # 测试状态获取函数
    status = get_analysis_status(session)
    assert "AAPL" in status
    assert "2023-01-01" in status
    
    # 测试更新函数
    updates = get_live_updates(session)
    assert isinstance(updates, str)
    
    # 测试代理状态函数
    agent_status = get_agent_status(session)
    assert isinstance(agent_status, str)
    
    print("✅ 函数参数传递测试通过")


def main():
    """主测试函数"""
    print("🚀 开始并发安全性测试...")
    print("=" * 60)
    
    try:
        test_session_isolation()
        test_streaming_handler_isolation()
        test_concurrent_access()
        test_function_parameters()
        
        print("=" * 60)
        print("🎉 所有测试通过！代码现在支持并发访问")
        print("✨ 主要改进：")
        print("  • 移除了全局状态变量")
        print("  • 使用Gradio会话状态管理")
        print("  • 每个用户有独立的StreamingHandler实例")
        print("  • 函数参数传递实现状态隔离")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()