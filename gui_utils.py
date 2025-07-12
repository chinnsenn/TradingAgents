"""
TradingAgents GUI 工具函数
提供分析结果保存、历史数据管理等功能
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


def save_analysis_results(results: Dict[str, Any], ticker: str, analysis_date: str) -> str:
    """
    保存分析结果到文件
    
    Args:
        results: 分析结果字典
        ticker: 股票代码
        analysis_date: 分析日期
        
    Returns:
        保存的文件路径
    """
    # 创建结果目录
    results_dir = Path("results") / ticker.upper() / analysis_date
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存 JSON 格式的结果
    json_path = results_dir / "analysis_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    # 保存 Markdown 格式的报告
    md_path = results_dir / "analysis_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# {ticker.upper()} 交易分析报告\n\n")
        f.write(f"**分析日期**: {analysis_date}\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        section_titles = {
            "market_report": "## 🏢 市场分析\n\n",
            "sentiment_report": "## 💬 社交情绪分析\n\n",
            "news_report": "## 📰 新闻分析\n\n",
            "fundamentals_report": "## 📊 基本面分析\n\n",
            "investment_plan": "## 🎯 研究团队决策\n\n",
            "trader_investment_plan": "## 💼 交易团队计划\n\n",
            "final_trade_decision": "## 📈 最终交易决策\n\n",
        }
        
        for section_key, title in section_titles.items():
            content = results.get(section_key)
            if content:
                f.write(title)
                f.write(str(content) + "\n\n")
        
        f.write("---\n")
        f.write("*此报告由 TradingAgents 多代理LLM金融交易框架生成*\n")
    
    return str(results_dir)


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
        if ticker_dir.is_dir():
            tickers.append(ticker_dir.name)
    
    return sorted(tickers)


def get_available_analysis_dates(ticker: str) -> List[str]:
    """
    获取指定股票的可用分析日期
    
    Args:
        ticker: 股票代码
        
    Returns:
        分析日期列表
    """
    ticker_dir = Path("results") / ticker.upper()
    if not ticker_dir.exists():
        return []
    
    dates = []
    for date_dir in ticker_dir.iterdir():
        if date_dir.is_dir():
            dates.append(date_dir.name)
    
    return sorted(dates, reverse=True)


def load_historical_analysis(ticker: str, analysis_date: str) -> Optional[Dict[str, Any]]:
    """
    加载历史分析结果
    
    Args:
        ticker: 股票代码
        analysis_date: 分析日期
        
    Returns:
        分析结果字典，如果不存在则返回 None
    """
    json_path = Path("results") / ticker.upper() / analysis_date / "analysis_results.json"
    
    if not json_path.exists():
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def get_all_analysis_results() -> Dict[str, List[Dict[str, Any]]]:
    """
    获取所有分析结果的摘要
    
    Returns:
        按股票代码组织的分析结果摘要
    """
    results = {}
    results_dir = Path("results")
    
    if not results_dir.exists():
        return results
    
    for ticker_dir in results_dir.iterdir():
        if not ticker_dir.is_dir():
            continue
            
        ticker = ticker_dir.name
        results[ticker] = []
        
        for date_dir in ticker_dir.iterdir():
            if not date_dir.is_dir():
                continue
                
            analysis_date = date_dir.name
            json_path = date_dir / "analysis_results.json"
            
            if json_path.exists():
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # 创建摘要
                    summary = {
                        "date": analysis_date,
                        "ticker": ticker,
                        "has_market_report": bool(data.get("market_report")),
                        "has_sentiment_report": bool(data.get("sentiment_report")),
                        "has_news_report": bool(data.get("news_report")),
                        "has_fundamentals_report": bool(data.get("fundamentals_report")),
                        "has_investment_plan": bool(data.get("investment_plan")),
                        "has_trader_plan": bool(data.get("trader_investment_plan")),
                        "has_final_decision": bool(data.get("final_trade_decision")),
                        "file_path": str(json_path)
                    }
                    
                    results[ticker].append(summary)
                    
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
        
        # 按日期排序
        results[ticker].sort(key=lambda x: x["date"], reverse=True)
    
    return results


def validate_ticker(ticker: str) -> tuple[bool, str]:
    """
    验证股票代码格式
    
    Args:
        ticker: 股票代码
        
    Returns:
        (是否有效, 错误信息)
    """
    if not ticker or not ticker.strip():
        return False, "股票代码不能为空"
    
    ticker = ticker.strip().upper()
    
    if len(ticker) < 1 or len(ticker) > 10:
        return False, "股票代码长度应在1-10个字符之间"
    
    # 基本字符检查
    if not ticker.replace(".", "").replace("-", "").isalnum():
        return False, "股票代码只能包含字母、数字、点号和连字符"
    
    return True, ""


def validate_date(date_str: str) -> tuple[bool, str]:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串
        
    Returns:
        (是否有效, 错误信息)
    """
    if not date_str or not date_str.strip():
        return False, "日期不能为空"
    
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "日期格式应为 YYYY-MM-DD"


def format_currency(amount: float) -> str:
    """
    格式化货币显示
    
    Args:
        amount: 金额
        
    Returns:
        格式化后的货币字符串
    """
    if amount >= 1e12:
        return f"${amount/1e12:.1f}T"
    elif amount >= 1e9:
        return f"${amount/1e9:.1f}B"
    elif amount >= 1e6:
        return f"${amount/1e6:.1f}M"
    elif amount >= 1e3:
        return f"${amount/1e3:.1f}K"
    else:
        return f"${amount:.2f}"


def format_percentage(value: float) -> str:
    """
    格式化百分比显示
    
    Args:
        value: 数值
        
    Returns:
        格式化后的百分比字符串
    """
    return f"{value:.2f}%"


def format_number(number: float) -> str:
    """
    格式化数字显示
    
    Args:
        number: 数字
        
    Returns:
        格式化后的数字字符串
    """
    if abs(number) >= 1e9:
        return f"{number/1e9:.1f}B"
    elif abs(number) >= 1e6:
        return f"{number/1e6:.1f}M"
    elif abs(number) >= 1e3:
        return f"{number/1e3:.1f}K"
    else:
        return f"{number:.2f}"