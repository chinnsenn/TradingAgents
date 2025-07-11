import gradio as gr
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from config_utils import (
    get_provider_names, 
    get_provider_models, 
    get_default_provider, 
    get_default_model,
    get_provider_info
)
from gui_utils import (
    save_analysis_results, 
    get_all_available_tickers, 
    get_available_analysis_dates, 
    load_historical_analysis,
    get_all_analysis_results
)


class TradingAgentsGUI:
    """TradingAgents GUI应用程序"""
    
    def __init__(self):
        # 从配置文件获取默认设置
        self.default_provider = get_default_provider()
        self.default_provider_info = get_provider_info(self.default_provider) if self.default_provider else None
        
        self.analysis_status = {}
        self.current_analysis = None
        self.analysis_results = {}
        self.stop_analysis = False
        
        # 当前分析参数
        self.current_ticker = None
        self.current_date = None
        
        # 历史分析状态
        self.available_tickers = []
        self.historical_analysis = {}
        self.current_historical_ticker = None
        self.current_historical_date = None
        
        # 在初始化时加载历史分析记录
        self._load_historical_data()
        
        # 初始化状态
        self.agent_statuses = {
            "市场分析师": "等待中",
            "社交分析师": "等待中", 
            "新闻分析师": "等待中",
            "基本面分析师": "等待中",
            "牛市研究员": "等待中",
            "熊市研究员": "等待中",
            "研究经理": "等待中",
            "交易员": "等待中",
            "激进分析师": "等待中",
            "中性分析师": "等待中",
            "保守分析师": "等待中",
            "投资组合经理": "等待中",
        }
        
        # 进度跟踪
        self.total_agents = len(self.agent_statuses)
        self.current_active_agent = None
        self.current_progress = 0.0
        
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }
        
    def _load_historical_data(self):
        """加载历史分析数据"""
        try:
            self.available_tickers = get_all_available_tickers()
            self.historical_analysis = get_all_analysis_results()
            print(f"📚 已加载 {len(self.available_tickers)} 个股票的历史分析记录")
        except Exception as e:
            print(f"❌ 加载历史分析数据失败: {e}")
            self.available_tickers = []
            self.historical_analysis = {}
    
    def get_historical_ticker_choices(self) -> List[str]:
        """获取历史分析股票选择"""
        if not self.available_tickers:
            return ["暂无历史数据"]
        return self.available_tickers
    
    def get_historical_date_choices(self, ticker: str) -> List[str]:
        """获取指定股票的历史分析日期选择"""
        if not ticker or ticker == "暂无历史数据":
            return ["请先选择股票"]
        
        dates = get_available_analysis_dates(ticker)
        if not dates:
            return ["该股票暂无分析记录"]
        return dates
    
    def load_selected_historical_analysis(self, ticker: str, date: str) -> Tuple[float, str, str, str, str, str, str, str, str, str, str]:
        """加载选定的历史分析"""
        if not ticker or not date or ticker == "暂无历史数据" or date in ["请先选择股票", "该股票暂无分析记录"]:
            msg = "请选择有效的股票和日期"
            return (100.0, "📚 历史分析", msg, msg, msg, msg, msg, msg, msg, msg, msg)
        
        try:
            # 加载历史分析结果
            historical_results = load_historical_analysis(ticker, date)
            if not historical_results:
                msg = "未找到分析结果"
                return (0.0, "❌ 加载失败", msg, msg, msg, msg, msg, msg, msg, msg, msg)
            
            # 更新当前报告状态
            self.current_historical_ticker = ticker
            self.current_historical_date = date
            
            # 临时保存当前报告状态
            original_sections = self.report_sections.copy()
            
            # 加载历史数据到报告状态
            for key, value in historical_results.items():
                if key in self.report_sections:
                    self.report_sections[key] = value
            
            # 生成显示内容
            status_text = f"## 📚 历史分析记录\n\n**股票代码**: {ticker}\n**分析日期**: {date}\n\n"
            status_text += "### 📊 数据来源\n"
            
            sections_loaded = sum(1 for v in historical_results.values() if v)
            status_text += f"- 已加载 {sections_loaded} 个分析报告\n"
            status_text += f"- 数据完整性: {'完整' if sections_loaded >= 6 else '部分'}\n\n"
            
            # 添加可用报告列表
            status_text += "### 📋 可用报告\n"
            section_titles = {
                "market_report": "🏢 市场分析",
                "sentiment_report": "💬 社交情绪分析",
                "news_report": "📰 新闻分析",
                "fundamentals_report": "📊 基本面分析",
                "investment_plan": "🎯 研究团队决策",
                "trader_investment_plan": "💼 交易团队计划",
                "final_trade_decision": "📈 最终交易决策",
            }
            
            for key, title in section_titles.items():
                status = "✅" if historical_results.get(key) else "❌"
                status_text += f"- {status} {title}\n"
            
            final_report = self.format_final_report()
            market_report = self.format_market_report()
            sentiment_report = self.format_sentiment_report()
            news_report = self.format_news_report()
            fundamentals_report = self.format_fundamentals_report()
            investment_plan = self.format_investment_plan()
            trader_plan = self.format_trader_plan()
            final_decision = self.format_final_decision()
            
            # 恢复原始报告状态
            self.report_sections = original_sections
            
            return (100.0, f"📚 已加载: {ticker} ({date})", status_text, final_report, 
                   market_report, sentiment_report, news_report, fundamentals_report, 
                   investment_plan, trader_plan, final_decision)
            
        except Exception as e:
            error_msg = f"加载历史分析失败: {str(e)}"
            return (0.0, "❌ 加载失败", error_msg, error_msg, error_msg, error_msg, 
                   error_msg, error_msg, error_msg, error_msg, error_msg)
    
    def get_analyst_choices(self) -> List[str]:
        """获取分析师选择选项"""
        return [
            "market - 市场分析师",
            "social - 社交分析师", 
            "news - 新闻分析师",
            "fundamentals - 基本面分析师"
        ]
    
    def get_llm_providers(self) -> List[str]:
        """获取LLM提供商选项"""
        return get_provider_names()
    
    def get_model_choices(self, provider: str) -> List[str]:
        """根据提供商获取模型选择"""
        return get_provider_models(provider)
    
    def update_agent_status(self, agent_name: str, status: str):
        """更新代理状态"""
        self.agent_statuses[agent_name] = status
        
        # 更新当前活跃代理
        if status == "进行中":
            self.current_active_agent = agent_name
        elif status == "已完成" and self.current_active_agent == agent_name:
            self.current_active_agent = None
        
        # 重新计算进度
        self.current_progress = self.calculate_progress()
    
    def calculate_progress(self) -> float:
        """计算当前整体进度"""
        completed_count = sum(1 for status in self.agent_statuses.values() if status == "已完成")
        return (completed_count / self.total_agents) * 100
    
    def get_current_status_text(self) -> str:
        """获取当前状态文本"""
        if self.current_active_agent:
            return f"正在执行: {self.current_active_agent}"
        elif self.current_progress >= 100:
            return "✅ 所有分析已完成"
        elif self.current_progress > 0:
            return "⏸️ 等待下一个分析步骤..."
        else:
            return "⏳ 准备开始分析..."
    
    def format_progress_details(self) -> str:
        """格式化详细进度信息"""
        details = f"## 📊 详细执行状态\n\n"
        details += f"**整体进度**: {self.current_progress:.1f}%\n\n"
        
        # 分组显示代理状态
        agent_groups = {
            "📊 分析师团队": ["市场分析师", "社交分析师", "新闻分析师", "基本面分析师"],
            "🔬 研究团队": ["牛市研究员", "熊市研究员", "研究经理"],
            "💼 交易团队": ["交易员"],
            "⚠️ 风险管理团队": ["激进分析师", "中性分析师", "保守分析师"],
            "📈 投资组合管理": ["投资组合经理"]
        }
        
        for group_name, agents in agent_groups.items():
            completed = sum(1 for agent in agents if self.agent_statuses.get(agent) == "已完成")
            in_progress = sum(1 for agent in agents if self.agent_statuses.get(agent) == "进行中")
            total = len(agents)
            
            if completed == total:
                status_emoji = "✅"
            elif in_progress > 0:
                status_emoji = "🔄"
            else:
                status_emoji = "⏸️"
            
            details += f"### {group_name}\n"
            details += f"{status_emoji} **进度**: {completed}/{total} 完成\n"
            
            # 显示各个代理状态
            for agent in agents:
                status = self.agent_statuses.get(agent, "等待中")
                if status == "已完成":
                    emoji = "✅"
                elif status == "进行中":
                    emoji = "🔄"
                else:
                    emoji = "⏸️"
                details += f"- {emoji} {agent}\n"
            details += "\n"
        
        return details
        
    def format_status_display(self) -> str:
        """格式化状态显示"""
        status_text = "## 🤖 代理执行状态\n\n"
        
        # 分析师团队
        status_text += "### 📊 分析师团队\n"
        analyst_agents = ["市场分析师", "社交分析师", "新闻分析师", "基本面分析师"]
        for agent in analyst_agents:
            status = self.agent_statuses.get(agent, "等待中")
            emoji = "🟢" if status == "已完成" else "🟡" if status == "进行中" else "⚪"
            status_text += f"- {emoji} {agent}: {status}\n"
        
        # 研究团队
        status_text += "\n### 🔬 研究团队\n"
        research_agents = ["牛市研究员", "熊市研究员", "研究经理"]
        for agent in research_agents:
            status = self.agent_statuses.get(agent, "等待中")
            emoji = "🟢" if status == "已完成" else "🟡" if status == "进行中" else "⚪"
            status_text += f"- {emoji} {agent}: {status}\n"
        
        # 交易团队
        status_text += "\n### 💼 交易团队\n"
        status = self.agent_statuses.get("交易员", "等待中")
        emoji = "🟢" if status == "已完成" else "🟡" if status == "进行中" else "⚪"
        status_text += f"- {emoji} 交易员: {status}\n"
        
        # 风险管理团队
        status_text += "\n### ⚠️ 风险管理团队\n"
        risk_agents = ["激进分析师", "中性分析师", "保守分析师"]
        for agent in risk_agents:
            status = self.agent_statuses.get(agent, "等待中")
            emoji = "🟢" if status == "已完成" else "🟡" if status == "进行中" else "⚪"
            status_text += f"- {emoji} {agent}: {status}\n"
        
        # 投资组合管理
        status_text += "\n### 📈 投资组合管理\n"
        status = self.agent_statuses.get("投资组合经理", "等待中")
        emoji = "🟢" if status == "已完成" else "🟡" if status == "进行中" else "⚪"
        status_text += f"- {emoji} 投资组合经理: {status}\n"
        
        return status_text
    
    def format_final_report(self) -> str:
        """格式化最终完整报告"""
        if not any(self.report_sections.values()):
            return "## 📊 完整分析报告\n\n暂无分析结果"
        
        report_text = "## 📊 完整分析报告\n\n"
        
        section_titles = {
            "market_report": "🏢 市场分析",
            "sentiment_report": "💬 社交情绪分析", 
            "news_report": "📰 新闻分析",
            "fundamentals_report": "📊 基本面分析",
            "investment_plan": "🎯 研究团队决策",
            "trader_investment_plan": "💼 交易团队计划",
            "final_trade_decision": "📈 最终交易决策",
        }
        
        # 分析师团队报告
        analyst_sections = ["market_report", "sentiment_report", "news_report", "fundamentals_report"]
        has_analyst_reports = any(self.report_sections.get(section) for section in analyst_sections)
        
        if has_analyst_reports:
            report_text += "### 🔍 分析师团队报告\n\n"
            for section in analyst_sections:
                content = self.report_sections.get(section)
                if content:
                    report_text += f"#### {section_titles[section]}\n{content}\n\n"
        
        # 研究团队报告
        if self.report_sections.get("investment_plan"):
            report_text += f"### 🎯 研究团队决策\n\n{self.report_sections['investment_plan']}\n\n"
        
        # 交易团队报告
        if self.report_sections.get("trader_investment_plan"):
            report_text += f"### 💼 交易团队计划\n\n{self.report_sections['trader_investment_plan']}\n\n"
        
        # 最终决策
        if self.report_sections.get("final_trade_decision"):
            report_text += f"### 📈 最终交易决策\n\n{self.report_sections['final_trade_decision']}\n\n"
        
        return report_text
    
    def format_market_report(self) -> str:
        """格式化市场分析报告"""
        content = self.report_sections.get("market_report")
        if not content:
            return "## 🏢 市场分析\n\n暂无市场分析结果"
        return f"## 🏢 市场分析\n\n{content}"
    
    def format_sentiment_report(self) -> str:
        """格式化社交情绪分析报告"""
        content = self.report_sections.get("sentiment_report")
        if not content:
            return "## 💬 社交情绪分析\n\n暂无社交情绪分析结果"
        return f"## 💬 社交情绪分析\n\n{content}"
    
    def format_news_report(self) -> str:
        """格式化新闻分析报告"""
        content = self.report_sections.get("news_report")
        if not content:
            return "## 📰 新闻分析\n\n暂无新闻分析结果"
        return f"## 📰 新闻分析\n\n{content}"
    
    def format_fundamentals_report(self) -> str:
        """格式化基本面分析报告"""
        content = self.report_sections.get("fundamentals_report")
        if not content:
            return "## 📊 基本面分析\n\n暂无基本面分析结果"
        return f"## 📊 基本面分析\n\n{content}"
    
    def format_investment_plan(self) -> str:
        """格式化研究团队决策报告"""
        content = self.report_sections.get("investment_plan")
        if not content:
            return "## 🎯 研究团队决策\n\n暂无研究团队决策结果"
        return f"## 🎯 研究团队决策\n\n{content}"
    
    def format_trader_plan(self) -> str:
        """格式化交易团队计划报告"""
        content = self.report_sections.get("trader_investment_plan")
        if not content:
            return "## 💼 交易团队计划\n\n暂无交易团队计划结果"
        return f"## 💼 交易团队计划\n\n{content}"
    
    def format_final_decision(self) -> str:
        """格式化最终交易决策报告"""
        content = self.report_sections.get("final_trade_decision")
        if not content:
            return "## 📈 最终交易决策\n\n暂无最终交易决策结果"
        return f"## 📈 最终交易决策\n\n{content}"
    
    def extract_content_string(self, content):
        """提取内容字符串"""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[工具: {item.get('name', 'unknown')}]")
                else:
                    text_parts.append(str(item))
            return ' '.join(text_parts)
        else:
            return str(content)
    
    def run_analysis(self, ticker: str, analysis_date: str, selected_analysts: List[str], 
                    research_depth: int, llm_provider: str, deep_model: str, 
                    quick_model: str, progress=gr.Progress()) -> Tuple[float, str, str, str, str, str, str, str, str, str, str]:
        """运行交易分析"""
        
        # 保存当前分析参数
        self.current_ticker = ticker.upper().strip()
        self.current_date = analysis_date
        
        # 重置状态
        self.stop_analysis = False
        self.current_progress = 0.0
        self.current_active_agent = None
        for agent in self.agent_statuses:
            self.agent_statuses[agent] = "等待中"
        for section in self.report_sections:
            self.report_sections[section] = None
        
        # 解析分析师选择
        analyst_types = []
        for choice in selected_analysts:
            analyst_type = choice.split(" - ")[0]
            analyst_types.append(analyst_type)
        
        # 创建配置
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = research_depth
        config["max_risk_discuss_rounds"] = research_depth
        config["deep_think_llm"] = deep_model
        config["quick_think_llm"] = quick_model
        config["llm_provider"] = llm_provider.lower()
        
        # 从配置获取提供商信息
        provider_info = get_provider_info(llm_provider)
        if provider_info:
            config["backend_url"] = provider_info["api_base_url"]
            config["api_key"] = provider_info["api_key"]
        
        config["online_tools"] = True
        
        try:
            # 初始化图
            if hasattr(self, 'graph') and self.graph:
                self.graph = None
            graph = TradingAgentsGraph(
                selected_analysts=analyst_types,
                config=config,
                debug=True
            )
            self.graph = graph
            
            progress(0.1, desc="初始化分析系统...")
            
            # 获取初始状态
            init_state = graph.propagator.create_initial_state(ticker, analysis_date)
            args = graph.propagator.get_graph_args()
            
            progress(0.2, desc="开始分析...")
            
            # 流式处理分析
            step_count = 0
            total_steps = 100
            
            for chunk in graph.graph.stream(init_state, **args):
                if self.stop_analysis:
                    break
                    
                step_count += 1
                progress_val = 0.2 + (step_count / total_steps) * 0.8
                progress(progress_val, desc=f"分析进行中... 步骤 {step_count}")
                
                # 更新报告部分
                self._update_reports_from_chunk(chunk)
                
                # 更新代理状态
                self._update_agent_status_from_chunk(chunk)
                
                yield (
                    self.current_progress,
                    self.get_current_status_text(),
                    self.format_progress_details(),
                    self.format_final_report(),
                    self.format_market_report(),
                    self.format_sentiment_report(),
                    self.format_news_report(),
                    self.format_fundamentals_report(),
                    self.format_investment_plan(),
                    self.format_trader_plan(),
                    self.format_final_decision()
                )
            
            if not self.stop_analysis:
                progress(1.0, desc="分析完成!")
                
                # Yield final progress update explicitly
                yield (
                    100.0,
                    self.get_current_status_text(),
                    self.format_progress_details(),
                    self.format_final_report(),
                    self.format_market_report(),
                    self.format_sentiment_report(),
                    self.format_news_report(),
                    self.format_fundamentals_report(),
                    self.format_investment_plan(),
                    self.format_trader_plan(),
                    self.format_final_decision()
                )
                
                # 标记所有代理为已完成
                for agent in self.agent_statuses:
                    self.agent_statuses[agent] = "已完成"
                
                # 使用 gui_utils 中的函数自动保存分析结果
                try:
                    saved_path = save_analysis_results(
                        results=self.report_sections,
                        ticker=self.current_ticker,
                        analysis_date=self.current_date
                    )
                    print(f"📁 分析结果已自动保存到: {saved_path}")
                except Exception as e:
                    print(f"❌ 保存分析结果时发生错误: {str(e)}")
                
                yield (
                    self.current_progress,
                    self.get_current_status_text(),
                    self.format_progress_details(),
                    self.format_final_report(),
                    self.format_market_report(),
                    self.format_sentiment_report(),
                    self.format_news_report(),
                    self.format_fundamentals_report(),
                    self.format_investment_plan(),
                    self.format_trader_plan(),
                    self.format_final_decision()
                )
                
        except Exception as e:
            error_msg = f"分析过程中发生错误: {str(e)}"
            yield (
                0.0,
                f"❌ 分析失败",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}",
                f"## ❌ 错误\n\n{error_msg}"
            )
    
    def _update_reports_from_chunk(self, chunk: Dict[str, Any]):
        """从数据块更新报告"""
        report_mappings = {
            "market_report": "market_report",
            "sentiment_report": "sentiment_report", 
            "news_report": "news_report",
            "fundamentals_report": "fundamentals_report",
            "trader_investment_plan": "trader_investment_plan",
            "final_trade_decision": "final_trade_decision"
        }
        
        for chunk_key, report_key in report_mappings.items():
            if chunk_key in chunk and chunk[chunk_key]:
                self.report_sections[report_key] = chunk[chunk_key]
        
        # 处理投资辩论状态
        if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
            debate_state = chunk["investment_debate_state"]
            if "judge_decision" in debate_state and debate_state["judge_decision"]:
                self.report_sections["investment_plan"] = debate_state["judge_decision"]
    
    def _update_agent_status_from_chunk(self, chunk: Dict[str, Any]):
        """从数据块更新代理状态"""
        # 检测正在进行的分析
        if "market_analysis" in chunk or any(key.startswith("market") for key in chunk.keys()):
            if not chunk.get("market_report"):
                self.update_agent_status("市场分析师", "进行中")
        
        if "sentiment_analysis" in chunk or any(key.startswith("sentiment") for key in chunk.keys()):
            if not chunk.get("sentiment_report"):
                self.update_agent_status("社交分析师", "进行中")
        
        if "news_analysis" in chunk or any(key.startswith("news") for key in chunk.keys()):
            if not chunk.get("news_report"):
                self.update_agent_status("新闻分析师", "进行中")
        
        if "fundamentals_analysis" in chunk or any(key.startswith("fundamentals") for key in chunk.keys()):
            if not chunk.get("fundamentals_report"):
                self.update_agent_status("基本面分析师", "进行中")
        
        # 检测完成的分析
        if "market_report" in chunk and chunk["market_report"]:
            self.update_agent_status("市场分析师", "已完成")
        
        if "sentiment_report" in chunk and chunk["sentiment_report"]:
            self.update_agent_status("社交分析师", "已完成")
        
        if "news_report" in chunk and chunk["news_report"]:
            self.update_agent_status("新闻分析师", "已完成")
        
        if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
            self.update_agent_status("基本面分析师", "已完成")
        
        if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
            debate_state = chunk["investment_debate_state"]
            if "judge_decision" in debate_state and debate_state["judge_decision"]:
                self.update_agent_status("研究经理", "已完成")
        
        if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
            self.update_agent_status("交易员", "已完成")
        
        if "final_trade_decision" in chunk and chunk["final_trade_decision"]:
            self.update_agent_status("投资组合经理", "已完成")
    
    def stop_analysis_func(self):
        """停止分析"""
        self.stop_analysis = True
        return "⏹️ 分析已停止"
    
    def create_interface(self):
        """创建Gradio界面"""
        with gr.Blocks(title="TradingAgents - 多代理LLM金融交易框架", theme=gr.themes.Soft()) as demo:
            
            # 标题
            # 获取当前配置信息
            current_providers = get_provider_names()
            config_info = ""
            if self.default_provider:
                config_info = f"- 默认提供商：{self.default_provider.upper()}\n"
                if self.default_provider_info:
                    config_info += f"- API 地址：{self.default_provider_info['api_base_url']}\n"
            
            config_info += f"- 可用提供商：{', '.join(current_providers)}\n"
            config_info += f"- 历史记录：已加载 {len(self.available_tickers)} 个股票的分析记录"
            
            gr.Markdown(f"""
            # 🚀 TradingAgents - 多代理LLM金融交易框架
            
            **专业的AI驱动金融分析系统**
            
            通过多个专业AI代理协作，为您提供全面的股票分析和交易建议。
            
            **当前配置：**
            {config_info}
            """)
            
            with gr.Row():
                # 左侧：输入参数
                with gr.Column(scale=1):
                    with gr.Tabs():
                        # 新建分析选项卡
                        with gr.TabItem("🆕 新建分析"):
                            gr.Markdown("## ⚙️ 分析参数")
                            
                            # 基础参数
                            ticker = gr.Textbox(
                                label="股票代码",
                                placeholder="请输入股票代码，如：AAPL、TSLA、NVDA",
                                value="SPY"
                            )
                            
                            analysis_date = gr.Textbox(
                                label="分析日期",
                                placeholder="YYYY-MM-DD",
                                value=datetime.datetime.now().strftime("%Y-%m-%d")
                            )
                            
                            # 分析师选择
                            selected_analysts = gr.CheckboxGroup(
                                choices=self.get_analyst_choices(),
                                label="选择分析师",
                                value=self.get_analyst_choices()
                            )
                            
                            # 研究深度
                            research_depth = gr.Slider(
                                minimum=1,
                                maximum=5,
                                step=1,
                                value=2,
                                label="研究深度（辩论轮数）"
                            )
                            
                            # LLM配置
                            gr.Markdown("### 🤖 AI模型配置")
                            
                            # 获取动态提供商和模型
                            available_providers = self.get_llm_providers()
                            default_provider = self.default_provider or available_providers[0]
                            default_models = self.get_model_choices(default_provider)
                            default_model = default_models[0]
                            
                            llm_provider = gr.Dropdown(
                                choices=available_providers,
                                label="LLM提供商",
                                value=default_provider
                            )
                            
                            deep_model = gr.Dropdown(
                                choices=default_models,
                                label="深度思考模型",
                                value=default_model
                            )
                            
                            quick_model = gr.Dropdown(
                                choices=default_models,
                                label="快速思考模型",
                                value=default_model
                            )
                            
                            # 更新模型选择
                            def update_model_choices(provider):
                                choices = self.get_model_choices(provider)
                                return gr.update(choices=choices, value=choices[0]), gr.update(choices=choices, value=choices[0])
                            
                            llm_provider.change(
                                update_model_choices,
                                inputs=[llm_provider],
                                outputs=[deep_model, quick_model]
                            )
                            
                            # 控制按钮
                            with gr.Row():
                                start_btn = gr.Button("🚀 开始分析", variant="primary", size="lg")
                                stop_btn = gr.Button("⏹️ 停止分析", variant="stop", size="lg")
                        
                        # 历史分析选项卡
                        with gr.TabItem("📚 历史分析"):
                            gr.Markdown("## 📋 历史分析记录")
                            
                            # 获取初始选择
                            initial_ticker_choices = self.get_historical_ticker_choices()
                            initial_ticker = initial_ticker_choices[0] if initial_ticker_choices and initial_ticker_choices[0] != "暂无历史数据" else None
                            
                            # 历史分析选择
                            historical_ticker = gr.Dropdown(
                                choices=initial_ticker_choices,
                                label="选择股票",
                                value=initial_ticker
                            )
                            
                            # 根据初始股票设置日期选择
                            initial_date_choices = self.get_historical_date_choices(initial_ticker) if initial_ticker else ["请先选择股票"]
                            initial_date = initial_date_choices[0] if initial_date_choices and initial_date_choices[0] not in ["请先选择股票", "该股票暂无分析记录"] else None
                            
                            historical_date = gr.Dropdown(
                                choices=initial_date_choices,
                                label="选择分析日期",
                                value=initial_date
                            )
                            
                            # 更新历史日期选择
                            def update_historical_dates(ticker):
                                dates = self.get_historical_date_choices(ticker)
                                return gr.update(choices=dates, value=dates[0] if dates and dates[0] not in ["请先选择股票", "该股票暂无分析记录"] else None)
                            
                            historical_ticker.change(
                                update_historical_dates,
                                inputs=[historical_ticker],
                                outputs=[historical_date]
                            )
                            
                            # 加载历史分析按钮
                            load_historical_btn = gr.Button("📖 加载历史分析", variant="primary", size="lg")
                            
                            # 刷新历史数据按钮
                            refresh_btn = gr.Button("🔄 刷新历史数据", variant="secondary")
                            
                            def refresh_historical_data():
                                self._load_historical_data()
                                ticker_choices = self.get_historical_ticker_choices()
                                selected_ticker = ticker_choices[0] if ticker_choices and ticker_choices[0] != "暂无历史数据" else None
                                
                                # 同时更新日期选择
                                date_choices = self.get_historical_date_choices(selected_ticker) if selected_ticker else ["请先选择股票"]
                                selected_date = date_choices[0] if date_choices and date_choices[0] not in ["请先选择股票", "该股票暂无分析记录"] else None
                                
                                return (
                                    gr.update(choices=ticker_choices, value=selected_ticker),
                                    gr.update(choices=date_choices, value=selected_date)
                                )
                            
                            refresh_btn.click(
                                refresh_historical_data,
                                outputs=[historical_ticker, historical_date]
                            )
                
                # 右侧：结果展示
                with gr.Column(scale=2):
                    with gr.Tabs():
                        with gr.TabItem("🤖 代理状态"):
                            # 进度条
                            progress_bar = gr.Slider(
                                minimum=0,
                                maximum=100,
                                value=0,
                                label="分析进度",
                                interactive=False,
                                show_label=True
                            )
                            
                            # 当前状态文本
                            current_status = gr.Textbox(
                                value="⏳ 准备开始分析...",
                                label="当前状态",
                                interactive=False
                            )
                            
                            # 详细状态信息（可折叠）
                            with gr.Accordion("详细状态", open=False):
                                detailed_status = gr.Markdown(
                                    value=self.format_progress_details(),
                                    label="详细状态"
                                )
                        with gr.TabItem("📊 完整报告"):
                            with gr.Tabs():
                                with gr.TabItem("🏢 市场分析"):
                                    market_report = gr.Markdown(
                                        value=self.format_market_report(),
                                        label="市场分析"
                                    )
                                with gr.TabItem("💬 社交情绪分析"):
                                    sentiment_report = gr.Markdown(
                                        value=self.format_sentiment_report(),
                                        label="社交情绪分析"
                                    )
                                with gr.TabItem("📰 新闻分析"):
                                    news_report = gr.Markdown(
                                        value=self.format_news_report(),
                                        label="新闻分析"
                                    )
                                with gr.TabItem("📊 基本面分析"):
                                    fundamentals_report = gr.Markdown(
                                        value=self.format_fundamentals_report(),
                                        label="基本面分析"
                                    )
                                with gr.TabItem("🎯 研究团队决策"):
                                    investment_plan = gr.Markdown(
                                        value=self.format_investment_plan(),
                                        label="研究团队决策"
                                    )
                                with gr.TabItem("💼 交易团队计划"):
                                    trader_plan = gr.Markdown(
                                        value=self.format_trader_plan(),
                                        label="交易团队计划"
                                    )
                                with gr.TabItem("📈 最终交易决策"):
                                    final_decision = gr.Markdown(
                                        value=self.format_final_decision(),
                                        label="最终交易决策"
                                    )
                                with gr.TabItem("📋 完整报告"):
                                    final_report = gr.Markdown(
                                        value=self.format_final_report(),
                                        label="完整报告"
                                    )
            
            # 绑定事件 - 新建分析
            start_btn.click(
                fn=self.run_analysis,
                inputs=[
                    ticker, analysis_date, selected_analysts, research_depth,
                    llm_provider, deep_model, quick_model
                ],
                outputs=[progress_bar, current_status, detailed_status, final_report, 
                        market_report, sentiment_report, news_report, 
                        fundamentals_report, investment_plan, trader_plan, 
                        final_decision]
            )
            
            stop_btn.click(
                fn=self.stop_analysis_func,
                outputs=[current_status]
            )
            
            # 绑定事件 - 历史分析
            load_historical_btn.click(
                fn=self.load_selected_historical_analysis,
                inputs=[historical_ticker, historical_date],
                outputs=[progress_bar, current_status, detailed_status, final_report, 
                        market_report, sentiment_report, news_report, 
                        fundamentals_report, investment_plan, trader_plan, 
                        final_decision]
            )
            
            # 底部信息
            gr.Markdown("""
            ---
            
            **使用说明：**
            1. **新建分析**：输入股票代码和参数，开始新的分析
            2. **历史分析**：查看之前完成的分析结果
            3. 分析过程可能需要几分钟时间
            4. 可以随时停止正在进行的分析
            
            **注意事项：**
            - 确保已正确配置API密钥
            - 历史分析支持从JSON或reports文件夹加载
            - 使用"刷新历史数据"按钮更新记录列表
            
            © TradingAgents - 多代理LLM金融交易框架
            """)
        
        return demo


def main():
    """主函数"""
    gui = TradingAgentsGUI()
    demo = gui.create_interface()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_tips=True,
        debug=True
    )


if __name__ == "__main__":
    main()