#!/usr/bin/env python3
"""
简化的性能测试脚本
"""

import time
import datetime
from gradio_utils import parse_and_validate_date, validate_ticker
from streaming_handler import StreamingHandler

def test_date_parsing():
    """测试日期解析性能"""
    print("🧪 测试日期解析性能...")
    
    test_dates = [
        datetime.datetime.now(),
        "2024-01-15",
        "2024-01-15T10:30:00",
        "invalid_date"
    ]
    
    start_time = time.time()
    for i in range(100):
        for date_input in test_dates:
            is_valid, date_str, error_msg = parse_and_validate_date(date_input)
    end_time = time.time()
    
    print(f"   ✅ 日期解析测试完成: {(end_time - start_time) * 1000:.2f}毫秒")
    return end_time - start_time

def test_streaming_handler():
    """测试 StreamingHandler 性能"""
    print("🧪 测试 StreamingHandler 性能...")
    
    handler = StreamingHandler()
    handler.set_analysis_params("NVDA", "2024-01-15")
    
    start_time = time.time()
    for i in range(100):
        handler.add_message("info", f"Test message {i}")
        handler.update_agent_status("Market Analyst", "running")
        summary = handler.get_agent_status_summary()
    end_time = time.time()
    
    print(f"   ✅ StreamingHandler测试完成: {(end_time - start_time) * 1000:.2f}毫秒")
    return end_time - start_time

def test_ticker_validation():
    """测试股票代码验证性能"""
    print("🧪 测试股票代码验证性能...")
    
    test_tickers = ["NVDA", "AAPL", "INVALID", ""]
    
    start_time = time.time()
    for i in range(100):
        for ticker in test_tickers:
            is_valid = validate_ticker(ticker)
    end_time = time.time()
    
    print(f"   ✅ 股票代码验证测试完成: {(end_time - start_time) * 1000:.2f}毫秒")
    return end_time - start_time

def run_tests():
    """运行所有测试"""
    print("🚀 开始性能测试...")
    print("=" * 50)
    
    total_time = 0
    total_time += test_date_parsing()
    total_time += test_streaming_handler()
    total_time += test_ticker_validation()
    
    print()
    print("📊 测试汇总:")
    print(f"   总耗时: {total_time * 1000:.2f}毫秒")
    print("✅ 性能测试完成!")

if __name__ == "__main__":
    run_tests()