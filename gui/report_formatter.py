"""
报告格式化模块 - 统一处理各种报告的格式化逻辑
"""
import streamlit as st
from typing import Dict, Any, Optional


class ReportFormatter:
    """报告格式化器 - 统一处理报告格式化逻辑"""
    
    # 报告部分标题配置
    SECTION_TITLES = {
        "market_report": "🏢 市场分析",
        "sentiment_report": "💬 社交情绪分析", 
        "news_report": "📰 新闻分析",
        "fundamentals_report": "📊 基本面分析",
        "investment_plan": "🎯 研究团队决策",
        "trader_investment_plan": "💼 交易团队计划",
        "final_trade_decision": "📈 最终交易决策",
    }
    
    # 代理组配置
    AGENT_GROUPS = {
        "📊 分析师团队": ["市场分析师", "社交分析师", "新闻分析师", "基本面分析师"],
        "🔬 研究团队": ["牛市研究员", "熊市研究员", "研究经理"],
        "💼 交易团队": ["交易员"],
        "⚠️ 风险管理团队": ["激进分析师", "中性分析师", "保守分析师"],
        "📈 投资组合管理": ["投资组合经理"]
    }
    
    def format_report_section(self, section_key: str, title: str, 
                            report_sections: Dict[str, Any] = None, 
                            historical: bool = False) -> str:
        """格式化单个报告部分
        
        Args:
            section_key: 报告部分的键名
            title: 报告标题
            report_sections: 报告数据字典，默认使用session_state
            historical: 是否为历史报告
        """
        if report_sections is None:
            if historical:
                report_sections = st.session_state.historical_report_sections
            else:
                report_sections = st.session_state.report_sections
        
        content = report_sections.get(section_key)
        if not content:
            return f"## {title}\\n\\n暂无{title}结果"
        return f"## {title}\\n\\n{content}"
    
    def format_final_report(self, historical: bool = False) -> str:
        """格式化完整报告
        
        Args:
            historical: 是否为历史报告
        """
        if historical:
            report_sections = st.session_state.historical_report_sections
            report_title = "📊 历史分析报告"
            empty_message = "暂无历史分析结果"
        else:
            report_sections = st.session_state.report_sections
            report_title = "📊 完整分析报告"
            empty_message = "暂无分析结果"
        
        if not any(report_sections.values()):
            return f"## {report_title}\\n\\n{empty_message}"
        
        report_text = f"## {report_title}\\n\\n"
        
        # 分析师团队报告
        analyst_sections = ["market_report", "sentiment_report", "news_report", "fundamentals_report"]
        has_analyst_reports = any(report_sections.get(section) for section in analyst_sections)
        
        if has_analyst_reports:
            report_text += "### 🔍 分析师团队报告\\n\\n"
            for section in analyst_sections:
                content = report_sections.get(section)
                if content:
                    title = self.SECTION_TITLES[section]
                    report_text += f"#### {title}\\n{content}\\n\\n"
        
        # 研究团队报告
        if report_sections.get("investment_plan"):
            report_text += f"### 🎯 研究团队决策\\n\\n{report_sections['investment_plan']}\\n\\n"
        
        # 交易团队报告
        if report_sections.get("trader_investment_plan"):
            report_text += f"### 💼 交易团队计划\\n\\n{report_sections['trader_investment_plan']}\\n\\n"
        
        # 最终决策
        if report_sections.get("final_trade_decision"):
            report_text += f"### 📈 最终交易决策\\n\\n{report_sections['final_trade_decision']}\\n\\n"
        
        return report_text
    
    def format_agent_status_display(self) -> str:
        """格式化代理状态显示"""
        status_text = "## 🤖 代理执行状态\\n\\n"
        
        for group_name, agents in self.AGENT_GROUPS.items():
            completed = sum(1 for agent in agents if st.session_state.agent_statuses.get(agent) == "已完成")
            in_progress = sum(1 for agent in agents if st.session_state.agent_statuses.get(agent) == "进行中")
            total = len(agents)
            
            if completed == total:
                status_emoji = "✅"
            elif in_progress > 0:
                status_emoji = "🔄"
            else:
                status_emoji = "⏸️"
            
            status_text += f"### {group_name}\\n"
            status_text += f"{status_emoji} **进度**: {completed}/{total} 完成\\n"
            
            # 显示各个代理状态
            for agent in agents:
                status = st.session_state.agent_statuses.get(agent, "等待中")
                if status == "已完成":
                    emoji = "✅"
                elif status == "进行中":
                    emoji = "🔄"
                else:
                    emoji = "⏸️"
                status_text += f"- {emoji} {agent}\\n"
            status_text += "\\n"
        
        return status_text
    
    def format_api_logs(self) -> str:
        """格式化API日志为显示文本"""
        if not st.session_state.api_logs:
            return "暂无日志记录"
        
        log_text = ""
        for log in st.session_state.api_logs[-50:]:  # 只显示最近50条
            timestamp = log["timestamp"].strftime("%H:%M:%S")
            log_type = log["type"]
            message = log["message"]
            
            # 根据类型添加图标和颜色
            icon_mapping = {
                "api_call": "🔵",
                "response": "🟢",
                "error": "🔴",
                "warning": "🟡",
                "info": "ℹ️"
            }
            icon = icon_mapping.get(log_type, "ℹ️")
            
            log_text += f"`{timestamp}` {icon} **{log_type.upper()}**: {message}\\n\\n"
        
        return log_text
    
    def create_report_status_data(self) -> list:
        """创建报告状态数据"""
        report_status_data = []
        
        for section_key, title in self.SECTION_TITLES.items():
            content = st.session_state.report_sections.get(section_key)
            status = "✅ 已生成" if content else "❌ 未生成"
            length = len(content) if content else 0
            report_status_data.append({
                "报告类型": title,
                "状态": status,
                "内容长度": f"{length} 字符"
            })
        
        return report_status_data
    
    def get_analysis_summary_metrics(self, historical: bool = False) -> Dict[str, Any]:
        """获取分析摘要指标
        
        Args:
            historical: 是否为历史报告
            
        Returns:
            包含各种指标的字典
        """
        if historical:
            report_sections = st.session_state.historical_report_sections
            ticker = st.session_state.historical_ticker
            date = st.session_state.historical_date
        else:
            report_sections = st.session_state.report_sections
            ticker = st.session_state.current_ticker
            date = st.session_state.current_date
        
        completed_reports = sum(1 for content in report_sections.values() if content)
        total_reports = len(report_sections)
        total_content = sum(len(str(content)) for content in report_sections.values() if content)
        
        return {
            "completed_reports": completed_reports,
            "total_reports": total_reports,
            "total_content": total_content,
            "ticker": ticker or "无",
            "date": date or "无"
        }


# 全局报告格式化器实例
report_formatter = ReportFormatter()