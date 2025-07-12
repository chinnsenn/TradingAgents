"""
TradingAgents Streamlit 应用专用工具函数
提供缓存优化和 Streamlit 特定的功能
"""

import streamlit as st
import datetime
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

# 导入原有工具函数
from gui_utils import (
    validate_ticker, validate_date, validate_api_keys,
    format_currency, format_percentage, format_number,
    save_analysis_results, load_previous_analysis,
    get_analysis_history, format_analysis_summary,
    get_all_available_tickers, get_available_analysis_dates,
    load_historical_analysis, get_all_analysis_results
)

@st.cache_data(ttl=300)  # 缓存5分钟
def cached_get_all_available_tickers() -> List[str]:
    """缓存版本的获取所有可用股票代码"""
    return get_all_available_tickers()

@st.cache_data(ttl=300)
def cached_get_available_analysis_dates(ticker: str) -> List[str]:
    """缓存版本的获取分析日期"""
    return get_available_analysis_dates(ticker)

@st.cache_data(ttl=300)
def cached_get_all_analysis_results() -> Dict[str, List[Dict[str, Any]]]:
    """缓存版本的获取所有分析结果"""
    return get_all_analysis_results()

@st.cache_data(ttl=600)  # 缓存10分钟
def cached_load_historical_analysis(ticker: str, analysis_date: str) -> Optional[Dict[str, Any]]:
    """缓存版本的加载历史分析"""
    return load_historical_analysis(ticker, analysis_date)

def clear_cache():
    """清空所有缓存"""
    st.cache_data.clear()

def show_loading_spinner(message: str = "处理中..."):
    """显示加载动画"""
    return st.spinner(message)

def show_success_message(message: str, icon: str = "✅"):
    """显示成功消息"""
    st.success(f"{icon} {message}")

def show_error_message(message: str, icon: str = "❌"):
    """显示错误消息"""
    st.error(f"{icon} {message}")

def show_warning_message(message: str, icon: str = "⚠️"):
    """显示警告消息"""
    st.warning(f"{icon} {message}")

def show_info_message(message: str, icon: str = "ℹ️"):
    """显示信息消息"""
    st.info(f"{icon} {message}")

def create_progress_bar(value: float, text: str = "") -> None:
    """创建进度条"""
    progress_bar = st.progress(value / 100.0)
    if text:
        st.text(text)
    return progress_bar

def create_metric_cards(metrics: List[Dict[str, Any]]) -> None:
    """创建指标卡片"""
    cols = st.columns(len(metrics))
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(
                label=metric.get("label", ""),
                value=metric.get("value", ""),
                delta=metric.get("delta", None)
            )

def create_status_badge(status: str) -> str:
    """创建状态徽章"""
    status_colors = {
        "等待中": "🔵",
        "进行中": "🟡", 
        "已完成": "🟢",
        "失败": "🔴",
        "停止": "⏸️"
    }
    return status_colors.get(status, "⚪")

def format_analysis_duration(start_time: datetime.datetime, end_time: Optional[datetime.datetime] = None) -> str:
    """格式化分析持续时间"""
    if end_time is None:
        end_time = datetime.datetime.now()
    
    duration = end_time - start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{int(hours)}小时{int(minutes)}分钟"
    elif minutes > 0:
        return f"{int(minutes)}分钟{int(seconds)}秒"
    else:
        return f"{int(seconds)}秒"

def create_agent_status_grid(agent_statuses: Dict[str, str]) -> None:
    """创建代理状态网格显示"""
    # 分组显示代理状态
    agent_groups = {
        "📊 分析师团队": ["市场分析师", "社交分析师", "新闻分析师", "基本面分析师"],
        "🔬 研究团队": ["牛市研究员", "熊市研究员", "研究经理"],
        "💼 交易团队": ["交易员"],
        "⚠️ 风险管理团队": ["激进分析师", "中性分析师", "保守分析师"],
        "📈 投资组合管理": ["投资组合经理"]
    }
    
    for group_name, agents in agent_groups.items():
        st.subheader(group_name)
        
        # 计算组进度
        completed = sum(1 for agent in agents if agent_statuses.get(agent) == "已完成")
        total = len(agents)
        progress = completed / total if total > 0 else 0
        
        # 显示组进度条
        st.progress(progress)
        st.text(f"进度: {completed}/{total} 完成")
        
        # 显示各个代理状态
        cols = st.columns(min(len(agents), 4))  # 最多4列
        for i, agent in enumerate(agents):
            with cols[i % 4]:
                status = agent_statuses.get(agent, "等待中")
                badge = create_status_badge(status)
                st.text(f"{badge} {agent}")
                st.text(status)

def create_report_summary_cards(report_sections: Dict[str, Any]) -> None:
    """创建报告摘要卡片"""
    section_titles = {
        "market_report": ("🏢", "市场分析"),
        "sentiment_report": ("💬", "社交情绪"),
        "news_report": ("📰", "新闻分析"),
        "fundamentals_report": ("📊", "基本面"),
        "investment_plan": ("🎯", "研究决策"),
        "trader_investment_plan": ("💼", "交易计划"),
        "final_trade_decision": ("📈", "最终决策"),
    }
    
    # 创建4列布局
    cols = st.columns(4)
    
    for i, (section_key, (icon, title)) in enumerate(section_titles.items()):
        with cols[i % 4]:
            content = report_sections.get(section_key)
            if content:
                st.success(f"{icon} {title}")
                # 显示内容长度
                content_length = len(content) if isinstance(content, str) else 0
                st.caption(f"{content_length} 字符")
            else:
                st.warning(f"{icon} {title}")
                st.caption("未生成")

def save_session_state() -> Dict[str, Any]:
    """保存会话状态到字典"""
    return {
        "analysis_running": st.session_state.get("analysis_running", False),
        "analysis_progress": st.session_state.get("analysis_progress", 0.0),
        "current_status": st.session_state.get("current_status", ""),
        "agent_statuses": st.session_state.get("agent_statuses", {}),
        "report_sections": st.session_state.get("report_sections", {}),
        "current_ticker": st.session_state.get("current_ticker", None),
        "current_date": st.session_state.get("current_date", None),
    }

def load_session_state(state_data: Dict[str, Any]) -> None:
    """从字典加载会话状态"""
    for key, value in state_data.items():
        st.session_state[key] = value

def export_analysis_report(report_sections: Dict[str, Any], ticker: str, analysis_date: str) -> str:
    """导出分析报告为Markdown格式"""
    markdown_content = f"# {ticker} 交易分析报告\n\n"
    markdown_content += f"**分析日期**: {analysis_date}\n"
    markdown_content += f"**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
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
        content = report_sections.get(section_key)
        if content:
            markdown_content += title
            markdown_content += content + "\n\n"
    
    markdown_content += "---\n"
    markdown_content += "*此报告由 TradingAgents 多代理LLM金融交易框架生成*\n"
    
    return markdown_content

def create_download_button(content: str, filename: str, label: str = "下载", mime_type: str = "text/plain") -> None:
    """创建下载按钮"""
    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime=mime_type,
        key=f"download_{filename}_{int(time.time())}"
    )

def validate_analysis_inputs(ticker: str, analysis_date: str, selected_analysts: List[str]) -> Tuple[bool, str]:
    """验证分析输入参数"""
    # 验证股票代码
    ticker_valid, ticker_error = validate_ticker(ticker)
    if not ticker_valid:
        return False, ticker_error
    
    # 验证日期
    date_valid, date_error = validate_date(analysis_date)
    if not date_valid:
        return False, date_error
    
    # 验证分析师选择
    if not selected_analysts:
        return False, "请选择至少一个分析师"
    
    return True, ""

def get_system_info_display() -> Dict[str, Any]:
    """获取系统信息用于显示"""
    import platform
    import sys
    
    try:
        import psutil
        memory_info = f"{psutil.virtual_memory().total / (1024**3):.1f} GB"
        cpu_info = f"{psutil.cpu_count()} 核心"
    except ImportError:
        memory_info = "未知"
        cpu_info = "未知"
    
    return {
        "操作系统": platform.system() + " " + platform.release(),
        "Python版本": sys.version.split()[0],
        "处理器": platform.processor() or "未知",
        "架构": platform.machine(),
        "内存": memory_info,
        "CPU": cpu_info,
        "Streamlit版本": st.__version__
    }

def create_system_info_display() -> None:
    """创建系统信息显示"""
    system_info = get_system_info_display()
    
    # 创建两列显示
    col1, col2 = st.columns(2)
    
    with col1:
        for key, value in list(system_info.items())[:4]:
            st.text(f"{key}: {value}")
    
    with col2:
        for key, value in list(system_info.items())[4:]:
            st.text(f"{key}: {value}")

def check_dependencies() -> Dict[str, bool]:
    """检查依赖包是否正确安装"""
    dependencies = {
        "streamlit": False,
        "langchain": False,
        "pandas": False,
        "yfinance": False,
        "gradio": False
    }
    
    for package in dependencies.keys():
        try:
            __import__(package)
            dependencies[package] = True
        except ImportError:
            dependencies[package] = False
    
    return dependencies

def create_dependency_status_display() -> None:
    """创建依赖状态显示"""
    dependencies = check_dependencies()
    
    st.subheader("📦 依赖包状态")
    
    for package, installed in dependencies.items():
        if installed:
            st.success(f"✅ {package}")
        else:
            st.error(f"❌ {package}")

def auto_refresh_page(interval_seconds: int = 5) -> None:
    """自动刷新页面"""
    if st.session_state.get("analysis_running", False):
        time.sleep(interval_seconds)
        st.rerun()

@st.cache_data
def get_sample_analysis_data() -> Dict[str, Any]:
    """获取示例分析数据用于演示"""
    return {
        "ticker": "AAPL",
        "date": "2024-01-01",
        "market_report": "苹果公司股票表现强劲，技术指标显示上升趋势...",
        "sentiment_report": "社交媒体对苹果公司持乐观态度，正面评论占70%...",
        "news_report": "最新产品发布获得市场积极响应...",
        "fundamentals_report": "财务状况良好，营收增长稳定...",
        "investment_plan": "建议增持苹果股票...",
        "trader_investment_plan": "分批建仓，设置止损位...",
        "final_trade_decision": "买入推荐，目标价位180美元..."
    }

def format_large_number(number: float) -> str:
    """格式化大数字显示（如市值）"""
    if number >= 1e12:
        return f"{number/1e12:.1f}T"
    elif number >= 1e9:
        return f"{number/1e9:.1f}B"
    elif number >= 1e6:
        return f"{number/1e6:.1f}M"
    elif number >= 1e3:
        return f"{number/1e3:.1f}K"
    else:
        return f"{number:.0f}"

def create_analysis_timeline(agent_statuses: Dict[str, str]) -> None:
    """创建分析时间线显示"""
    st.subheader("📅 分析时间线")
    
    # 定义分析流程顺序
    analysis_flow = [
        ("📊 数据收集", ["市场分析师", "社交分析师", "新闻分析师", "基本面分析师"]),
        ("🔬 研究分析", ["牛市研究员", "熊市研究员", "研究经理"]),
        ("💼 交易策略", ["交易员"]),
        ("⚠️ 风险评估", ["激进分析师", "中性分析师", "保守分析师"]),
        ("📈 最终决策", ["投资组合经理"])
    ]
    
    for phase_name, agents in analysis_flow:
        # 计算阶段完成度
        completed = sum(1 for agent in agents if agent_statuses.get(agent) == "已完成")
        in_progress = sum(1 for agent in agents if agent_statuses.get(agent) == "进行中")
        total = len(agents)
        
        # 确定阶段状态
        if completed == total:
            phase_icon = "✅"
            phase_status = "已完成"
        elif in_progress > 0 or completed > 0:
            phase_icon = "🔄"
            phase_status = "进行中"
        else:
            phase_icon = "⏸️"
            phase_status = "等待中"
        
        # 显示阶段信息
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                st.write(f"{phase_icon} **{phase_name}**")
            with col2:
                progress = completed / total if total > 0 else 0
                st.progress(progress)
            with col3:
                st.write(f"{completed}/{total}")
            
            # 显示该阶段的代理详情
            agent_details = []
            for agent in agents:
                status = agent_statuses.get(agent, "等待中")
                badge = create_status_badge(status)
                agent_details.append(f"{badge} {agent}")
            
            st.caption(" | ".join(agent_details))

def create_analysis_summary_metrics(report_sections: Dict[str, Any]) -> None:
    """创建分析摘要指标"""
    # 计算报告完成度
    total_sections = len(report_sections)
    completed_sections = sum(1 for content in report_sections.values() if content)
    completion_rate = (completed_sections / total_sections) * 100 if total_sections > 0 else 0
    
    # 计算总内容长度
    total_content_length = sum(len(str(content)) for content in report_sections.values() if content)
    
    # 显示指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("完成度", f"{completion_rate:.0f}%")
    
    with col2:
        st.metric("已完成报告", f"{completed_sections}/{total_sections}")
    
    with col3:
        st.metric("总内容长度", format_large_number(total_content_length))
    
    with col4:
        # 估算分析质量（基于内容长度）
        if total_content_length > 10000:
            quality = "详细"
            quality_color = "normal"
        elif total_content_length > 5000:
            quality = "中等"
            quality_color = "normal"
        elif total_content_length > 1000:
            quality = "简要"
            quality_color = "inverse"
        else:
            quality = "初步"
            quality_color = "off"
        
        st.metric("分析质量", quality)