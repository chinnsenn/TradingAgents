"""
TradingAgents GUI应用程序的实用工具函数
"""

import os
import json
import datetime
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def validate_ticker(ticker: str) -> Tuple[bool, str]:
    """
    验证股票代码格式
    
    Args:
        ticker: 股票代码
        
    Returns:
        (是否有效, 错误消息)
    """
    if not ticker:
        return False, "股票代码不能为空"
    
    # 基本格式验证
    ticker = ticker.upper().strip()
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        return False, "股票代码格式无效，应为1-5个大写字母"
    
    return True, ""

def validate_date(date_str: str) -> Tuple[bool, str]:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串
        
    Returns:
        (是否有效, 错误消息)
    """
    if not date_str:
        return False, "日期不能为空"
    
    try:
        # 验证日期格式
        analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        
        # 检查是否为未来日期
        if analysis_date.date() > datetime.datetime.now().date():
            return False, "分析日期不能是未来日期"
        
        # 检查是否太久远
        min_date = datetime.datetime.now() - datetime.timedelta(days=365*5)  # 5年前
        if analysis_date < min_date:
            return False, "分析日期不能超过5年前"
        
        return True, ""
        
    except ValueError:
        return False, "日期格式无效，请使用YYYY-MM-DD格式"

def validate_api_keys() -> Tuple[bool, List[str]]:
    """
    验证API密钥配置
    
    Returns:
        (是否有效, 缺失的密钥列表)
    """
    required_keys = {
        "FINNHUB_API_KEY": "Finnhub API密钥"
    }
    
    missing_keys = []
    for key, description in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(description)
    
    return len(missing_keys) == 0, missing_keys

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    格式化货币显示
    
    Args:
        amount: 金额
        currency: 货币类型
        
    Returns:
        格式化后的货币字符串
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_percentage(percentage: float) -> str:
    """
    格式化百分比显示
    
    Args:
        percentage: 百分比值
        
    Returns:
        格式化后的百分比字符串
    """
    return f"{percentage:.2f}%"

def format_number(number: float, decimals: int = 2) -> str:
    """
    格式化数字显示
    
    Args:
        number: 数字
        decimals: 小数位数
        
    Returns:
        格式化后的数字字符串
    """
    return f"{number:,.{decimals}f}"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def extract_decision_from_text(text: str) -> Dict[str, Any]:
    """
    从文本中提取交易决策信息
    
    Args:
        text: 包含决策的文本
        
    Returns:
        决策信息字典
    """
    decision = {
        "action": "持有",  # 买入、卖出、持有
        "confidence": 0.5,  # 置信度 0-1
        "reasoning": text[:200],  # 推理过程
        "risk_level": "中等",  # 风险水平
        "target_price": None,  # 目标价格
        "stop_loss": None  # 止损价格
    }
    
    # 简单的关键词匹配
    text_lower = text.lower()
    
    # 判断交易动作
    if any(word in text_lower for word in ["买入", "购买", "buy", "long"]):
        decision["action"] = "买入"
    elif any(word in text_lower for word in ["卖出", "抛售", "sell", "short"]):
        decision["action"] = "卖出"
    
    # 判断置信度
    if any(word in text_lower for word in ["强烈推荐", "highly recommend", "strong buy"]):
        decision["confidence"] = 0.9
    elif any(word in text_lower for word in ["推荐", "recommend", "buy"]):
        decision["confidence"] = 0.7
    elif any(word in text_lower for word in ["谨慎", "cautious", "weak"]):
        decision["confidence"] = 0.3
    
    # 判断风险水平
    if any(word in text_lower for word in ["高风险", "high risk", "risky"]):
        decision["risk_level"] = "高"
    elif any(word in text_lower for word in ["低风险", "low risk", "conservative"]):
        decision["risk_level"] = "低"
    
    return decision

def save_analysis_results(results: Dict[str, Any], ticker: str, analysis_date: str) -> str:
    """
    保存分析结果到文件
    
    Args:
        results: 分析结果
        ticker: 股票代码
        analysis_date: 分析日期
        
    Returns:
        保存的文件路径
    """
    # 创建结果目录
    results_dir = Path("results") / ticker / analysis_date
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建reports子目录
    reports_dir = results_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存各个报告为独立的.md文件到reports目录
    for section_key, content in results.items():
        if content:
            report_file = reports_dir / f"{section_key}.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(content)
    
    # 保存完整的JSON格式结果
    json_file = results_dir / "analysis_results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 保存综合Markdown报告
    md_file = results_dir / "analysis_report.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(f"# {ticker} 分析报告\n\n")
        f.write(f"**分析日期**: {analysis_date}\n\n")
        
        # 写入各部分报告
        report_sections = {
            "market_report": "市场分析",
            "sentiment_report": "情绪分析",
            "news_report": "新闻分析", 
            "fundamentals_report": "基本面分析",
            "investment_plan": "投资计划",
            "trader_investment_plan": "交易计划",
            "final_trade_decision": "最终决策"
        }
        
        for section_key, section_title in report_sections.items():
            if section_key in results and results[section_key]:
                f.write(f"## {section_title}\n\n")
                f.write(f"{results[section_key]}\n\n")
    
    # 保存日志文件
    log_file = results_dir / "message_tool.log"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"GUI分析日志 - {ticker} - {analysis_date}\n")
        f.write(f"分析时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"分析完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("报告生成状态:\n")
        for section, content in results.items():
            status = "已生成" if content else "未生成"
            f.write(f"  {section}: {status}\n")
        
        f.write(f"\n保存位置: {results_dir}\n")
        f.write(f"JSON文件: {json_file}\n")
        f.write(f"Markdown文件: {md_file}\n")
        f.write(f"报告目录: {reports_dir}\n")
    
    return str(results_dir)

def load_previous_analysis(ticker: str, analysis_date: str) -> Optional[Dict[str, Any]]:
    """
    加载之前的分析结果
    
    Args:
        ticker: 股票代码
        analysis_date: 分析日期
        
    Returns:
        之前的分析结果，如果不存在则返回None
    """
    results_file = Path("results") / ticker / analysis_date / "analysis_results.json"
    
    if results_file.exists():
        try:
            with open(results_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    
    return None

def get_analysis_history(ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取股票的分析历史
    
    Args:
        ticker: 股票代码
        limit: 最大返回数量
        
    Returns:
        分析历史列表
    """
    results_dir = Path("results") / ticker
    if not results_dir.exists():
        return []
    
    history = []
    for date_dir in sorted(results_dir.iterdir(), reverse=True):
        if date_dir.is_dir():
            json_file = date_dir / "analysis_results.json"
            if json_file.exists():
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        history.append({
                            "date": date_dir.name,
                            "ticker": ticker,
                            "summary": data.get("final_trade_decision", "")[:100]
                        })
                except Exception:
                    continue
        
        if len(history) >= limit:
            break
    
    return history

def format_analysis_summary(results: Dict[str, Any]) -> str:
    """
    格式化分析摘要
    
    Args:
        results: 分析结果
        
    Returns:
        格式化后的摘要
    """
    if not results:
        return "暂无分析结果"
    
    summary = "## 📊 分析摘要\n\n"
    
    # 提取决策信息
    if "final_trade_decision" in results:
        decision = extract_decision_from_text(results["final_trade_decision"])
        summary += f"**交易建议**: {decision['action']}\n"
        summary += f"**置信度**: {decision['confidence']:.0%}\n"
        summary += f"**风险水平**: {decision['risk_level']}\n\n"
    
    # 添加关键发现
    if "market_report" in results:
        summary += "**市场分析**: " + truncate_text(results["market_report"], 100) + "\n\n"
    
    if "sentiment_report" in results:
        summary += "**情绪分析**: " + truncate_text(results["sentiment_report"], 100) + "\n\n"
    
    return summary

def check_system_requirements() -> Dict[str, bool]:
    """
    检查系统要求
    
    Returns:
        系统要求检查结果
    """
    requirements = {
        "python_version": False,
        "required_packages": False,
        "api_keys": False,
        "disk_space": False,
        "memory": False
    }
    
    # 检查Python版本
    import sys
    if sys.version_info >= (3, 8):
        requirements["python_version"] = True
    
    # 检查必需包
    try:
        import gradio
        import langchain
        import pandas
        requirements["required_packages"] = True
    except ImportError:
        pass
    
    # 检查API密钥
    api_keys_valid, _ = validate_api_keys()
    requirements["api_keys"] = api_keys_valid
    
    # 检查磁盘空间 (至少需要1GB)
    import shutil
    try:
        _, _, free = shutil.disk_usage(".")
        requirements["disk_space"] = free > 1024 * 1024 * 1024  # 1GB
    except Exception:
        pass
    
    # 检查内存 (至少需要4GB)
    try:
        import psutil
        requirements["memory"] = psutil.virtual_memory().available > 4 * 1024 * 1024 * 1024  # 4GB
    except Exception:
        pass
    
    return requirements

def get_system_info() -> Dict[str, str]:
    """
    获取系统信息
    
    Returns:
        系统信息字典
    """
    import platform
    import sys
    
    info = {
        "操作系统": platform.system() + " " + platform.release(),
        "Python版本": sys.version.split()[0],
        "处理器": platform.processor(),
        "架构": platform.machine(),
    }
    
    try:
        import psutil
        info["内存"] = f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
        info["CPU核心"] = str(psutil.cpu_count())
    except ImportError:
        pass
    
    return info

def get_all_available_tickers() -> List[str]:
    """
    获取所有可用的股票代码
    
    Returns:
        股票代码列表
    """
    results_dir = Path("results")
    if not results_dir.exists():
        return []
    
    tickers = []
    for ticker_dir in results_dir.iterdir():
        if ticker_dir.is_dir() and ticker_dir.name != "__pycache__":
            tickers.append(ticker_dir.name)
    
    return sorted(tickers)

def get_available_analysis_dates(ticker: str) -> List[str]:
    """
    获取指定股票的分析日期
    
    Args:
        ticker: 股票代码
        
    Returns:
        分析日期列表
    """
    ticker_dir = Path("results") / ticker
    if not ticker_dir.exists():
        return []
    
    dates = []
    for date_dir in ticker_dir.iterdir():
        if date_dir.is_dir():
            # 检查是否有分析结果
            json_file = date_dir / "analysis_results.json"
            reports_dir = date_dir / "reports"
            if json_file.exists() or (reports_dir.exists() and any(reports_dir.iterdir())):
                dates.append(date_dir.name)
    
    return sorted(dates, reverse=True)

def load_historical_analysis(ticker: str, analysis_date: str) -> Optional[Dict[str, Any]]:
    """
    加载历史分析结果
    
    Args:
        ticker: 股票代码
        analysis_date: 分析日期
        
    Returns:
        分析结果，如果不存在则返回None
    """
    # 首先尝试从JSON文件加载
    json_file = Path("results") / ticker / analysis_date / "analysis_results.json"
    if json_file.exists():
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON文件失败: {e}")
    
    # 如果JSON不存在，尝试从reports文件夹生成
    reports_dir = Path("results") / ticker / analysis_date / "reports"
    if reports_dir.exists() and any(reports_dir.iterdir()):
        return generate_json_from_reports_folder(str(reports_dir))
    
    return None

def generate_json_from_reports_folder(reports_path: str) -> Dict[str, Any]:
    """
    从reports文件夹生成JSON格式的分析结果
    
    Args:
        reports_path: reports文件夹路径
        
    Returns:
        分析结果字典
    """
    reports_dir = Path(reports_path)
    if not reports_dir.exists():
        return {}
    
    results = {}
    
    # 定义文件映射关系
    file_mappings = {
        "market_report.md": "market_report",
        "sentiment_report.md": "sentiment_report",
        "news_report.md": "news_report",
        "fundamentals_report.md": "fundamentals_report",
        "investment_plan.md": "investment_plan",
        "trader_investment_plan.md": "trader_investment_plan",
        "final_trade_decision.md": "final_trade_decision"
    }
    
    # 读取各个报告文件
    for filename, key in file_mappings.items():
        file_path = reports_dir / filename
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        results[key] = content
            except Exception as e:
                print(f"读取文件 {filename} 失败: {e}")
    
    return results

def get_all_analysis_results() -> Dict[str, List[Dict[str, Any]]]:
    """
    获取所有分析结果
    
    Returns:
        按股票代码分组的分析结果
    """
    results_dir = Path("results")
    if not results_dir.exists():
        return {}
    
    all_results = {}
    
    for ticker_dir in results_dir.iterdir():
        if ticker_dir.is_dir() and ticker_dir.name != "__pycache__":
            ticker = ticker_dir.name
            ticker_results = []
            
            for date_dir in sorted(ticker_dir.iterdir(), reverse=True):
                if date_dir.is_dir():
                    # 检查是否有分析结果
                    json_file = date_dir / "analysis_results.json"
                    reports_dir = date_dir / "reports"
                    
                    if json_file.exists() or (reports_dir.exists() and any(reports_dir.iterdir())):
                        analysis_info = {
                            "date": date_dir.name,
                            "ticker": ticker,
                            "has_json": json_file.exists(),
                            "has_reports": reports_dir.exists() and any(reports_dir.iterdir())
                        }
                        
                        # 尝试加载摘要信息
                        try:
                            if json_file.exists():
                                with open(json_file, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                    analysis_info["summary"] = data.get("final_trade_decision", "")[:100] + "..."
                            else:
                                # 从final_trade_decision.md获取摘要
                                final_decision_file = reports_dir / "final_trade_decision.md"
                                if final_decision_file.exists():
                                    with open(final_decision_file, "r", encoding="utf-8") as f:
                                        content = f.read().strip()
                                        analysis_info["summary"] = content[:100] + "..."
                                else:
                                    analysis_info["summary"] = "无摘要信息"
                        except Exception:
                            analysis_info["summary"] = "加载摘要失败"
                        
                        ticker_results.append(analysis_info)
            
            if ticker_results:
                all_results[ticker] = ticker_results
    
    return all_results