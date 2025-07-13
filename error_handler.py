"""
错误处理模块 - 提供完整的堆栈跟踪输出
"""

import sys
import traceback
import logging
from typing import Optional
from functools import wraps


def setup_error_handling(enable_debug: bool = True):
    """
    配置全局错误处理，启用完整的堆栈跟踪输出
    
    Args:
        enable_debug: 是否启用调试模式
    """
    # 配置Python异常处理
    def exception_handler(exc_type, exc_value, exc_traceback):
        """全局异常处理器"""
        if issubclass(exc_type, KeyboardInterrupt):
            # 对于Ctrl+C中断，不显示堆栈跟踪
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print("\n" + "="*80)
        print("❌ 程序遇到错误，完整错误信息如下：")
        print("="*80)
        
        # 打印完整的堆栈跟踪
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        print("="*80)
        print("💡 调试建议：")
        print("1. 检查上述堆栈跟踪中的错误源头")
        print("2. 验证配置文件是否正确")
        print("3. 确认网络连接和API密钥")
        print("4. 如果问题持续，请提供完整的错误日志")
        print("="*80)
    
    # 设置全局异常处理器
    sys.excepthook = exception_handler
    
    # 如果启用调试模式，配置详细日志
    if enable_debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )


def with_error_handling(func):
    """
    装饰器：为函数添加错误处理和堆栈跟踪
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"\n❌ 函数 {func.__name__} 执行失败:")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            print("\n📋 完整堆栈跟踪:")
            traceback.print_exc()
            raise
    return wrapper


def print_exception_details(e: Exception, context: Optional[str] = None):
    """
    打印详细的异常信息和堆栈跟踪
    
    Args:
        e: 异常对象
        context: 可选的上下文信息
    """
    print("\n" + "="*60)
    if context:
        print(f"❌ {context}")
    else:
        print("❌ 发生错误")
    print("="*60)
    
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {str(e)}")
    
    print("\n📋 完整堆栈跟踪:")
    traceback.print_exc()
    
    print("="*60)


def safe_execute(func, *args, context: str = None, **kwargs):
    """
    安全执行函数，自动处理异常并显示完整堆栈跟踪
    
    Args:
        func: 要执行的函数
        *args: 函数参数
        context: 上下文描述
        **kwargs: 函数关键字参数
    
    Returns:
        函数执行结果，如果出错则返回None
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print_exception_details(e, context)
        return None