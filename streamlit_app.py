"""
TradingAgents Streamlit Web 应用程序
专业的多代理LLM金融交易分析框架
"""

import streamlit as st
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import time
import json

# 导入错误处理模块
from error_handler import setup_error_handling, with_error_handling, print_exception_details

# 导入核心业务逻辑
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

class TradingAgentsStreamlitApp:
    """TradingAgents Streamlit 应用程序类"""
    
    def __init__(self):
        self.initialize_session_state()
        self.load_configuration()
        
    def initialize_session_state(self):
        """初始化会话状态"""
        # 基础状态
        if 'analysis_running' not in st.session_state:
            st.session_state.analysis_running = False
        if 'analysis_starting' not in st.session_state:
            st.session_state.analysis_starting = False
        if 'analysis_progress' not in st.session_state:
            st.session_state.analysis_progress = 0.0
        if 'current_status' not in st.session_state:
            st.session_state.current_status = "⏳ 准备开始分析..."
        if 'stop_analysis' not in st.session_state:
            st.session_state.stop_analysis = False
            
        # 代理状态
        if 'agent_statuses' not in st.session_state:
            st.session_state.agent_statuses = {
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
            
        # 报告内容
        if 'report_sections' not in st.session_state:
            st.session_state.report_sections = {
                "market_report": None,
                "sentiment_report": None,
                "news_report": None,
                "fundamentals_report": None,
                "investment_plan": None,
                "trader_investment_plan": None,
                "final_trade_decision": None,
            }
            
        # 分析参数
        if 'current_ticker' not in st.session_state:
            st.session_state.current_ticker = None
        if 'current_date' not in st.session_state:
            st.session_state.current_date = None
            
        # 历史数据
        if 'available_tickers' not in st.session_state:
            st.session_state.available_tickers = []
        if 'historical_analysis' not in st.session_state:
            st.session_state.historical_analysis = {}
            
        # 历史分析状态（与当前分析分离）
        if 'historical_report_sections' not in st.session_state:
            st.session_state.historical_report_sections = {
                "market_report": None,
                "sentiment_report": None,
                "news_report": None,
                "fundamentals_report": None,
                "investment_plan": None,
                "trader_investment_plan": None,
                "final_trade_decision": None,
            }
        if 'historical_ticker' not in st.session_state:
            st.session_state.historical_ticker = None
        if 'historical_date' not in st.session_state:
            st.session_state.historical_date = None
        if 'is_viewing_historical' not in st.session_state:
            st.session_state.is_viewing_historical = False
            
        # 实时日志状态
        if 'api_logs' not in st.session_state:
            st.session_state.api_logs = []
        if 'show_logs' not in st.session_state:
            st.session_state.show_logs = True
        if 'max_log_entries' not in st.session_state:
            st.session_state.max_log_entries = 100
        
        # 步骤信息状态
        if 'last_step_info' not in st.session_state:
            st.session_state.last_step_info = ""
            
    def load_configuration(self):
        """加载配置信息"""
        self.default_provider = get_default_provider()
        self.default_provider_info = get_provider_info(self.default_provider) if self.default_provider else None
        
        # 加载历史数据
        self.load_historical_data()
        
    def load_historical_data(self):
        """加载历史分析数据"""
        try:
            st.session_state.available_tickers = get_all_available_tickers()
            st.session_state.historical_analysis = get_all_analysis_results()
        except Exception as e:
            st.error(f"❌ 加载历史分析数据失败: {e}")
            st.session_state.available_tickers = []
            st.session_state.historical_analysis = {}
    
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
    
    def add_api_log(self, log_type: str, message: str, details: dict = None):
        """添加API日志条目"""
        import datetime
        
        log_entry = {
            "timestamp": datetime.datetime.now(),
            "type": log_type,  # "info", "api_call", "response", "error", "warning"
            "message": message,
            "details": details or {}
        }
        
        # 添加到日志列表
        st.session_state.api_logs.append(log_entry)
        
        # 限制日志条目数量
        if len(st.session_state.api_logs) > st.session_state.max_log_entries:
            st.session_state.api_logs = st.session_state.api_logs[-st.session_state.max_log_entries:]
    
    def clear_api_logs(self):
        """清空API日志"""
        st.session_state.api_logs = []
    
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
            if log_type == "api_call":
                icon = "🔵"
            elif log_type == "response":
                icon = "🟢"
            elif log_type == "error":
                icon = "🔴"
            elif log_type == "warning":
                icon = "🟡"
            else:
                icon = "ℹ️"
            
            log_text += f"`{timestamp}` {icon} **{log_type.upper()}**: {message}\n\n"
        
        return log_text
    
    def update_agent_status(self, agent_name: str, status: str):
        """更新代理状态"""
        st.session_state.agent_statuses[agent_name] = status
        
        # 重新计算进度
        completed_count = sum(1 for status in st.session_state.agent_statuses.values() if status == "已完成")
        total_agents = len(st.session_state.agent_statuses)
        st.session_state.analysis_progress = (completed_count / total_agents) * 100
        
        # 更新状态文本
        if status == "进行中":
            st.session_state.current_status = f"正在执行: {agent_name}"
        elif st.session_state.analysis_progress >= 100:
            st.session_state.current_status = "✅ 所有分析已完成"
        elif st.session_state.analysis_progress > 0:
            st.session_state.current_status = "⏸️ 等待下一个分析步骤..."
        else:
            st.session_state.current_status = "⏳ 准备开始分析..."
    
    def format_agent_status_display(self) -> str:
        """格式化代理状态显示"""
        status_text = "## 🤖 代理执行状态\n\n"
        
        # 分组显示代理状态
        agent_groups = {
            "📊 分析师团队": ["市场分析师", "社交分析师", "新闻分析师", "基本面分析师"],
            "🔬 研究团队": ["牛市研究员", "熊市研究员", "研究经理"],
            "💼 交易团队": ["交易员"],
            "⚠️ 风险管理团队": ["激进分析师", "中性分析师", "保守分析师"],
            "📈 投资组合管理": ["投资组合经理"]
        }
        
        for group_name, agents in agent_groups.items():
            completed = sum(1 for agent in agents if st.session_state.agent_statuses.get(agent) == "已完成")
            in_progress = sum(1 for agent in agents if st.session_state.agent_statuses.get(agent) == "进行中")
            total = len(agents)
            
            if completed == total:
                status_emoji = "✅"
            elif in_progress > 0:
                status_emoji = "🔄"
            else:
                status_emoji = "⏸️"
            
            status_text += f"### {group_name}\n"
            status_text += f"{status_emoji} **进度**: {completed}/{total} 完成\n"
            
            # 显示各个代理状态
            for agent in agents:
                status = st.session_state.agent_statuses.get(agent, "等待中")
                if status == "已完成":
                    emoji = "✅"
                elif status == "进行中":
                    emoji = "🔄"
                else:
                    emoji = "⏸️"
                status_text += f"- {emoji} {agent}\n"
            status_text += "\n"
        
        return status_text
    
    def format_report_section(self, section_key: str, title: str) -> str:
        """格式化报告部分"""
        content = st.session_state.report_sections.get(section_key)
        if not content:
            return f"## {title}\n\n暂无{title}结果"
        return f"## {title}\n\n{content}"
    
    def format_historical_report_section(self, section_key: str, title: str) -> str:
        """格式化历史报告部分"""
        content = st.session_state.historical_report_sections.get(section_key)
        if not content:
            return f"## {title}\n\n暂无{title}结果"
        return f"## {title}\n\n{content}"
    
    def format_final_report(self) -> str:
        """格式化最终完整报告"""
        if not any(st.session_state.report_sections.values()):
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
        has_analyst_reports = any(st.session_state.report_sections.get(section) for section in analyst_sections)
        
        if has_analyst_reports:
            report_text += "### 🔍 分析师团队报告\n\n"
            for section in analyst_sections:
                content = st.session_state.report_sections.get(section)
                if content:
                    report_text += f"#### {section_titles[section]}\n{content}\n\n"
        
        # 研究团队报告
        if st.session_state.report_sections.get("investment_plan"):
            report_text += f"### 🎯 研究团队决策\n\n{st.session_state.report_sections['investment_plan']}\n\n"
        
        # 交易团队报告
        if st.session_state.report_sections.get("trader_investment_plan"):
            report_text += f"### 💼 交易团队计划\n\n{st.session_state.report_sections['trader_investment_plan']}\n\n"
        
        # 最终决策
        if st.session_state.report_sections.get("final_trade_decision"):
            report_text += f"### 📈 最终交易决策\n\n{st.session_state.report_sections['final_trade_decision']}\n\n"
        
        return report_text
    
    def format_historical_final_report(self) -> str:
        """格式化历史完整报告"""
        if not any(st.session_state.historical_report_sections.values()):
            return "## 📊 历史分析报告\n\n暂无历史分析结果"
        
        report_text = "## 📊 历史分析报告\n\n"
        
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
        has_analyst_reports = any(st.session_state.historical_report_sections.get(section) for section in analyst_sections)
        
        if has_analyst_reports:
            report_text += "### 🔍 分析师团队报告\n\n"
            for section in analyst_sections:
                content = st.session_state.historical_report_sections.get(section)
                if content:
                    report_text += f"#### {section_titles[section]}\n{content}\n\n"
        
        # 研究团队报告
        if st.session_state.historical_report_sections.get("investment_plan"):
            report_text += f"### 🎯 研究团队决策\n\n{st.session_state.historical_report_sections['investment_plan']}\n\n"
        
        # 交易团队报告
        if st.session_state.historical_report_sections.get("trader_investment_plan"):
            report_text += f"### 💼 交易团队计划\n\n{st.session_state.historical_report_sections['trader_investment_plan']}\n\n"
        
        # 最终决策
        if st.session_state.historical_report_sections.get("final_trade_decision"):
            report_text += f"### 📈 最终交易决策\n\n{st.session_state.historical_report_sections['final_trade_decision']}\n\n"
        
        return report_text
    
    @with_error_handling
    def run_analysis_sync(self, ticker: str, analysis_date: str, selected_analysts: List[str], 
                         research_depth: int, llm_provider: str, deep_model: str, quick_model: str):
        """同步运行分析（避免多线程上下文问题）"""
        
        # 保存当前分析参数
        st.session_state.current_ticker = ticker.upper().strip()
        st.session_state.current_date = analysis_date
        
        # 清空之前的日志
        self.clear_api_logs()
        self.add_api_log("info", f"开始分析 {ticker.upper()} ({analysis_date})")
        
        # 重置状态
        st.session_state.stop_analysis = False
        st.session_state.analysis_progress = 0.0
        st.session_state.analysis_starting = False  # 清除启动状态
        for agent in st.session_state.agent_statuses:
            st.session_state.agent_statuses[agent] = "等待中"
        for section in st.session_state.report_sections:
            st.session_state.report_sections[section] = None
        
        # 创建主要的进度显示容器
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        details_placeholder = st.empty()
        
        try:
            with progress_placeholder.container():
                st.info("🚀 正在初始化分析系统...")
                init_progress = st.progress(0.0)
                init_status = st.empty()
            
            # 解析分析师选择
            analyst_types = []
            for choice in selected_analysts:
                analyst_type = choice.split(" - ")[0]
                analyst_types.append(analyst_type)
            
            init_status.text("📋 解析分析师配置...")
            init_progress.progress(0.1)
            self.add_api_log("info", f"配置分析师: {', '.join(analyst_types)}")
            
            # 创建配置
            config = DEFAULT_CONFIG.copy()
            config["max_debate_rounds"] = research_depth
            config["max_risk_discuss_rounds"] = research_depth
            config["deep_think_llm"] = deep_model
            config["quick_think_llm"] = quick_model
            config["llm_provider"] = llm_provider.lower()
            
            init_status.text("⚙️ 配置LLM提供商...")
            init_progress.progress(0.2)
            self.add_api_log("info", f"LLM提供商: {llm_provider}, 深度模型: {deep_model}, 快速模型: {quick_model}")
            
            # 从配置获取提供商信息
            provider_info = get_provider_info(llm_provider)
            if provider_info:
                config["backend_url"] = provider_info["api_base_url"]
                config["api_key"] = provider_info["api_key"]
                self.add_api_log("api_call", f"连接到API: {provider_info['api_base_url']}")
            else:
                raise Exception(f"未找到提供商配置: {llm_provider}")
            
            config["online_tools"] = True
            
            init_status.text("🤖 初始化TradingAgents图...")
            init_progress.progress(0.5)
            self.add_api_log("info", "正在初始化交易代理系统...")
            
            # 初始化图
            try:
                print(f"[DEBUG] 开始初始化TradingAgentsGraph...")
                print(f"[DEBUG] 分析师类型: {analyst_types}")
                print(f"[DEBUG] 配置参数: {config}")
                graph = TradingAgentsGraph(
                    selected_analysts=analyst_types,
                    config=config,
                    debug=True
                )
                print(f"[DEBUG] TradingAgentsGraph初始化成功")
                self.add_api_log("response", "交易代理系统初始化成功")
            except Exception as e:
                print(f"[DEBUG] TradingAgentsGraph初始化失败: {str(e)}")
                print(f"[DEBUG] 错误类型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                self.add_api_log("error", f"初始化TradingAgentsGraph失败: {str(e)}")
                raise e
            
            init_status.text("📊 创建初始分析状态...")
            init_progress.progress(0.8)
            
            # 获取初始状态
            try:
                print(f"[DEBUG] 开始创建初始状态...")
                print(f"[DEBUG] 股票代码: {ticker}, 分析日期: {analysis_date}")
                init_state = graph.propagator.create_initial_state(ticker, analysis_date)
                args = graph.propagator.get_graph_args()
                print(f"[DEBUG] 初始状态创建成功")
                print(f"[DEBUG] 初始状态内容: {list(init_state.keys()) if hasattr(init_state, 'keys') else type(init_state)}")
                print(f"[DEBUG] 图参数: {args}")
                self.add_api_log("response", "初始分析状态创建成功")
            except Exception as e:
                print(f"[DEBUG] 创建初始状态失败: {str(e)}")
                print(f"[DEBUG] 错误类型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                self.add_api_log("error", f"创建初始状态失败: {str(e)}")
                raise e
            
            init_status.text("✅ 初始化完成，开始分析...")
            init_progress.progress(1.0)
            time.sleep(0.5)  # 短暂暂停让用户看到完成状态
            
            # 清空初始化显示，开始实际分析
            progress_placeholder.empty()
            
            # 创建简化的分析过程显示容器
            with status_placeholder.container():
                st.success("🔄 分析正在进行中...")
                st.info("💡 实时状态和详细信息请查看右侧状态面板")
            
            # 流式处理分析
            step_count = 0
            total_expected_steps = 50  # 估计的总步数
            last_update_time = time.time()
            
            try:
                print(f"[DEBUG] 开始流式分析处理...")
                self.add_api_log("info", "开始流式分析处理...")
                
                stream_count = 0
                for chunk in graph.graph.stream(init_state, **args):
                    stream_count += 1
                    print(f"[DEBUG] 接收到流数据块 #{stream_count}: {list(chunk.keys()) if hasattr(chunk, 'keys') else type(chunk)}")
                    
                    # 详细记录每个chunk的内容长度
                    if hasattr(chunk, 'keys'):
                        for key, value in chunk.items():
                            if isinstance(value, str):
                                print(f"[DEBUG]   - {key}: {len(value)} 字符")
                            elif value is not None:
                                print(f"[DEBUG]   - {key}: {type(value).__name__}")
                            else:
                                print(f"[DEBUG]   - {key}: None")
                    
                    if st.session_state.stop_analysis:
                        print(f"[DEBUG] 分析被用户停止")
                        self.add_api_log("warning", "分析被用户停止")
                        break
                        
                    step_count += 1
                    print(f"[DEBUG] 处理步骤 {step_count} 开始")
                    
                    # 记录流处理步骤
                    if step_count % 10 == 0:  # 每10步记录一次
                        print(f"[DEBUG] 处理步骤 {step_count}, 总流数据块: {stream_count}")
                        self.add_api_log("info", f"处理步骤 {step_count}, 进度 {min((step_count / total_expected_steps) * 95, 95):.1f}%")
                    
                    print(f"[DEBUG] 开始更新报告部分...")
                    # 更新报告部分
                    try:
                        self._update_reports_from_chunk(chunk)
                        print(f"[DEBUG] 报告部分更新完成")
                    except Exception as e:
                        print(f"[DEBUG] 更新报告部分失败: {str(e)}")
                        import traceback
                        traceback.print_exc()
                    
                    print(f"[DEBUG] 开始更新代理状态...")
                    # 更新代理状态
                    try:
                        self._update_agent_status_from_chunk(chunk)
                        print(f"[DEBUG] 代理状态更新完成")
                    except Exception as e:
                        print(f"[DEBUG] 更新代理状态失败: {str(e)}")
                        import traceback
                        traceback.print_exc()
                    
                    # 计算进度（最多到95%，留5%给最终处理）
                    progress = min((step_count / total_expected_steps) * 95, 95)
                    st.session_state.analysis_progress = progress
                    print(f"[DEBUG] 进度更新为: {progress:.1f}%")
                    
                    # 限制状态更新频率（每1秒更新一次，减少UI刷新频率）
                    current_time = time.time()
                    if current_time - last_update_time > 1.0:
                        print(f"[DEBUG] 更新UI状态信息...")
                        # 触发右侧面板的状态更新（通过session state变化）
                        st.session_state.last_step_info = f"步骤 {step_count} | {st.session_state.current_status}"
                        
                        # 强制页面重新渲染以更新右侧状态面板
                        if step_count % 5 == 0:  # 每5步更新一次UI
                            # print(f"[DEBUG] 触发页面重新渲染 (st.rerun)")
                            pass # st.rerun()
                        
                        last_update_time = current_time
                        print(f"[DEBUG] UI状态信息更新完成")
                    
                    print(f"[DEBUG] 处理步骤 {step_count} 完成，等待下一个流数据块...")
                
                print(f"[DEBUG] 流式分析循环结束")
                print(f"[DEBUG] 流式分析完成，总共处理 {step_count} 步，流数据块: {stream_count}")
                self.add_api_log("response", f"流式分析完成，总共处理 {step_count} 步")
                
            except Exception as e:
                print(f"[DEBUG] 分析流处理失败: {str(e)}")
                print(f"[DEBUG] 错误类型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                self.add_api_log("error", f"分析流处理失败: {str(e)}")
                raise e
            
            if not st.session_state.stop_analysis:
                # 标记所有代理为已完成
                for agent in st.session_state.agent_statuses:
                    st.session_state.agent_statuses[agent] = "已完成"
                
                st.session_state.analysis_progress = 100.0
                st.session_state.current_status = "✅ 所有分析已完成"
                
                # 最终状态更新
                with status_placeholder.container():
                    st.progress(1.0)
                    st.success("🎉 分析成功完成！")
                
                # 保存分析结果
                try:
                    saved_path = save_analysis_results(
                        results=st.session_state.report_sections,
                        ticker=st.session_state.current_ticker,
                        analysis_date=st.session_state.current_date
                    )
                    
                    with details_placeholder.container():
                        st.success(f"📁 分析结果已保存到: {saved_path}")
                        
                        # 显示分析摘要
                        completed_reports = sum(1 for content in st.session_state.report_sections.values() if content)
                        total_reports = len(st.session_state.report_sections)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("生成报告", f"{completed_reports}/{total_reports}")
                        with col2:
                            total_content = sum(len(str(content)) for content in st.session_state.report_sections.values() if content)
                            st.metric("总内容", f"{total_content:,} 字符")
                        with col3:
                            st.metric("分析时长", f"{step_count} 步骤")
                        
                except Exception as e:
                    with details_placeholder.container():
                        st.warning(f"⚠️ 保存分析结果时发生错误: {str(e)}")
                
                return True
            else:
                with status_placeholder.container():
                    st.warning("⏹️ 分析已被用户停止")
                return False
                
        except Exception as e:
            st.session_state.current_status = f"❌ 分析失败: {str(e)}"
            st.session_state.analysis_progress = 0.0
            
            with status_placeholder.container():
                st.error(f"❌ 分析过程中发生错误: {str(e)}")
                
                # 提供错误详情和建议
                with st.expander("🔍 错误详情和解决建议", expanded=True):
                    st.text(f"错误类型: {type(e).__name__}")
                    st.text(f"错误信息: {str(e)}")
                    
                    # 在控制台显示完整堆栈跟踪
                    print_exception_details(e, "Streamlit分析过程")
                    
                    st.markdown("**可能的解决方案:**")
                    st.markdown("1. 检查网络连接")
                    st.markdown("2. 验证LLM API密钥配置")
                    st.markdown("3. 确认`llm_provider.json`文件格式正确")
                    st.markdown("4. 检查股票代码是否有效")
                    st.markdown("5. 尝试使用较少的分析师或较低的研究深度")
                    st.markdown("6. 查看终端控制台获取完整错误堆栈信息")
            
            return False
        finally:
            print(f"[DEBUG] 分析线程的finally块已执行")
            st.session_state.analysis_running = False
            st.session_state.analysis_starting = False
    
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
                st.session_state.report_sections[report_key] = chunk[chunk_key]
        
        # 处理投资辩论状态
        if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
            debate_state = chunk["investment_debate_state"]
            if "judge_decision" in debate_state and debate_state["judge_decision"]:
                st.session_state.report_sections["investment_plan"] = debate_state["judge_decision"]
    
    def _update_agent_status_from_chunk(self, chunk: Dict[str, Any]):
        """从数据块更新代理状态"""
        # 检测正在进行的分析
        if "market_analysis" in chunk or any(key.startswith("market") for key in chunk.keys()):
            if not chunk.get("market_report"):
                self.update_agent_status("市场分析师", "进行中")
                self.add_api_log("api_call", "市场分析师开始分析")
        
        if "sentiment_analysis" in chunk or any(key.startswith("sentiment") for key in chunk.keys()):
            if not chunk.get("sentiment_report"):
                self.update_agent_status("社交分析师", "进行中")
                self.add_api_log("api_call", "社交分析师开始分析")
        
        if "news_analysis" in chunk or any(key.startswith("news") for key in chunk.keys()):
            if not chunk.get("news_report"):
                self.update_agent_status("新闻分析师", "进行中")
                self.add_api_log("api_call", "新闻分析师开始分析")
        
        if "fundamentals_analysis" in chunk or any(key.startswith("fundamentals") for key in chunk.keys()):
            if not chunk.get("fundamentals_report"):
                self.update_agent_status("基本面分析师", "进行中")
                self.add_api_log("api_call", "基本面分析师开始分析")
        
        # 检测完成的分析
        if "market_report" in chunk and chunk["market_report"]:
            self.update_agent_status("市场分析师", "已完成")
            self.add_api_log("response", "市场分析完成")
        
        if "sentiment_report" in chunk and chunk["sentiment_report"]:
            self.update_agent_status("社交分析师", "已完成")
            self.add_api_log("response", "社交情绪分析完成")
        
        if "news_report" in chunk and chunk["news_report"]:
            self.update_agent_status("新闻分析师", "已完成")
            self.add_api_log("response", "新闻分析完成")
        
        if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
            self.update_agent_status("基本面分析师", "已完成")
            self.add_api_log("response", "基本面分析完成")
        
        if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
            debate_state = chunk["investment_debate_state"]
            if "judge_decision" in debate_state and debate_state["judge_decision"]:
                self.update_agent_status("研究经理", "已完成")
                self.add_api_log("response", "研究团队决策完成")
        
        if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
            self.update_agent_status("交易员", "已完成")
            self.add_api_log("response", "交易计划制定完成")
        
        if "final_trade_decision" in chunk and chunk["final_trade_decision"]:
            self.update_agent_status("投资组合经理", "已完成")
            self.add_api_log("response", "最终交易决策完成")
    
    def load_historical_analysis_data(self, ticker: str, date: str) -> bool:
        """加载历史分析数据到分离的历史状态"""
        if not ticker or not date:
            return False
        
        try:
            historical_results = load_historical_analysis(ticker, date)
            if not historical_results:
                return False
            
            # 加载历史数据到分离的历史状态
            for key, value in historical_results.items():
                if key in st.session_state.historical_report_sections:
                    st.session_state.historical_report_sections[key] = value
            
            # 设置历史分析状态
            st.session_state.historical_ticker = ticker
            st.session_state.historical_date = date
            st.session_state.is_viewing_historical = True
            
            # 历史分析的状态标识
            st.session_state.current_status = f"📚 已加载历史: {ticker} ({date})"
            
            return True
            
        except Exception as e:
            st.error(f"加载历史分析失败: {str(e)}")
            return False

def main():
    """主函数 - 创建 Streamlit 应用"""
    # 启用全局错误处理
    setup_error_handling(enable_debug=True)
    
    st.set_page_config(
        page_title="TradingAgents - 多代理LLM金融交易框架",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 添加自定义CSS样式
    st.markdown("""
    <style>
    /* 右侧状态面板样式 */
    .stColumns > div:last-child {
        padding-left: 1rem;
        border-left: 2px solid #f0f2f6;
    }
    
    /* 状态面板标题样式 */
    .status-panel-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* 进度条容器样式 */
    .progress-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .stColumns > div:last-child {
            border-left: none;
            border-top: 2px solid #f0f2f6;
            padding-left: 0;
            padding-top: 1rem;
            margin-top: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 初始化应用
    app = TradingAgentsStreamlitApp()
    
    # 主标题和配置信息
    st.title("🚀 TradingAgents - 多代理LLM金融交易框架")
    st.markdown("**专业的AI驱动金融分析系统**")
    
    # 显示配置信息
    current_providers = app.get_llm_providers()
    config_info = ""
    if app.default_provider:
        config_info = f"- 默认提供商：{app.default_provider.upper()}\n"
        if app.default_provider_info:
            config_info += f"- API 地址：{app.default_provider_info['api_base_url']}\n"
    
    config_info += f"- 可用提供商：{', '.join(current_providers)}\n"
    config_info += f"- 历史记录：已加载 {len(st.session_state.available_tickers)} 个股票的分析记录"
    
    with st.expander("📊 当前配置", expanded=False):
        st.markdown(config_info)
    
    # 侧边栏 - 控制面板
    with st.sidebar:
        st.header("🎛️ 控制面板")
        
        # 页面选择
        page = st.selectbox(
            "选择功能",
            ["🆕 新建分析", "📚 历史分析", "🤖 系统状态"]
        )
        
        # 如果是新建分析页面，显示分析参数控件
        if page == "🆕 新建分析":
            st.divider()
            st.subheader("⚙️ 分析参数")
            
            # 基础参数
            ticker = st.text_input(
                "股票代码",
                value="SPY",
                placeholder="AAPL、TSLA、NVDA..."
            )
            
            analysis_date = st.text_input(
                "分析日期",
                value=datetime.datetime.now().strftime("%Y-%m-%d"),
                placeholder="YYYY-MM-DD"
            )
            
            # 分析师选择
            selected_analysts = st.multiselect(
                "选择分析师",
                app.get_analyst_choices(),
                default=app.get_analyst_choices()
            )
            
            # 研究深度
            research_depth = st.slider(
                "研究深度（辩论轮数）",
                min_value=1,
                max_value=5,
                value=2,
                step=1
            )
            
            # AI模型配置
            st.divider()
            st.subheader("🤖 AI模型配置")
            
            available_providers = app.get_llm_providers()
            default_provider = app.default_provider or available_providers[0]
            
            llm_provider = st.selectbox(
                "LLM提供商",
                available_providers,
                index=available_providers.index(default_provider) if default_provider in available_providers else 0
            )
            
            default_models = app.get_model_choices(llm_provider)
            default_model = default_models[0] if default_models else "gpt-3.5-turbo"
            
            deep_model = st.selectbox(
                "深度思考模型",
                default_models,
                index=0
            )
            
            quick_model = st.selectbox(
                "快速思考模型",
                default_models,
                index=0
            )
            
            # 控制按钮
            st.divider()
            st.subheader("🚀 执行控制")
            
            # 检查是否可以开始分析（防重复点击和状态检查）
            can_start_analysis = (
                not st.session_state.analysis_running and
                not st.session_state.get('analysis_starting', False) and
                st.session_state.analysis_progress == 0
            )
            
            # 动态按钮文本和状态
            if st.session_state.analysis_running:
                button_text = "🔄 分析进行中..."
                button_disabled = True
            elif st.session_state.get('analysis_starting', False):
                button_text = "⏳ 正在启动..."
                button_disabled = True
            else:
                button_text = "🚀 开始分析"
                button_disabled = False
            
            # 添加隐藏字段来处理分析触发
            if 'analysis_trigger' not in st.session_state:
                st.session_state.analysis_trigger = False
            
            if st.button(button_text, type="primary", disabled=button_disabled, use_container_width=True):
                if not ticker.strip():
                    st.error("请输入股票代码")
                elif not analysis_date.strip():
                    st.error("请输入分析日期")
                elif not selected_analysts:
                    st.error("请选择至少一个分析师")
                else:
                    # 设置分析触发器
                    st.session_state.analysis_trigger = True
                    st.session_state.analysis_starting = True
                    st.session_state.analysis_running = True
                    st.session_state.analysis_params = {
                        'ticker': ticker,
                        'analysis_date': analysis_date,
                        'selected_analysts': selected_analysts,
                        'research_depth': research_depth,
                        'llm_provider': llm_provider,
                        'deep_model': deep_model,
                        'quick_model': quick_model
                    }
                    st.rerun()
            
            # 在页面渲染时检查是否需要执行分析
            if st.session_state.get('analysis_trigger', False):
                st.session_state.analysis_trigger = False
                params = st.session_state.get('analysis_params', {})
                if params:
                    success = app.run_analysis_sync(
                        params['ticker'], params['analysis_date'], params['selected_analysts'], 
                        params['research_depth'], params['llm_provider'], 
                        params['deep_model'], params['quick_model']
                    )
                    
                    if success:
                        st.balloons()  # 庆祝动画
                        st.success("🎉 分析成功完成！")
                    else:
                        st.error("❌ 分析失败，请检查配置和网络连接")
                    
                    # 清理参数
                    st.session_state.analysis_params = {}
                    st.rerun()
            
            # 停止分析按钮
            stop_button_disabled = not st.session_state.analysis_running
            if st.button("⏹️ 停止分析", disabled=stop_button_disabled, use_container_width=True):
                st.session_state.stop_analysis = True
                st.session_state.analysis_running = False
                st.session_state.analysis_starting = False
                st.warning("分析已停止")
                st.rerun()
        
        # 历史分析页面的侧边栏控件
        elif page == "📚 历史分析":
            st.divider()
            st.subheader("📋 历史记录选择")
            
            # 刷新按钮
            if st.button("🔄 刷新历史数据", use_container_width=True):
                app.load_historical_data()
                st.success("历史数据已刷新")
                st.rerun()
            
            # 股票选择
            ticker_choices = st.session_state.available_tickers if st.session_state.available_tickers else ["暂无历史数据"]
            selected_ticker = st.selectbox(
                "选择股票",
                ticker_choices,
                index=0
            )
            
            # 日期选择
            if selected_ticker and selected_ticker != "暂无历史数据":
                date_choices = get_available_analysis_dates(selected_ticker)
                if not date_choices:
                    date_choices = ["该股票暂无分析记录"]
            else:
                date_choices = ["请先选择股票"]
            
            selected_date = st.selectbox(
                "选择分析日期",
                date_choices,
                index=0
            )
            
            # 加载按钮
            if st.button("📖 加载历史分析", type="primary", use_container_width=True):
                if selected_ticker and selected_date and selected_ticker != "暂无历史数据" and selected_date not in ["请先选择股票", "该股票暂无分析记录"]:
                    if app.load_historical_analysis_data(selected_ticker, selected_date):
                        st.success(f"✅ 已加载 {selected_ticker} 在 {selected_date} 的分析结果")
                        st.rerun()
                    else:
                        st.error("❌ 加载失败，请检查数据完整性")
                else:
                    st.error("请选择有效的股票和日期")
    
    # 页面状态管理 - 检测页面切换并重置状态
    if 'current_page' not in st.session_state:
        st.session_state.current_page = page
    
    # 如果从历史分析切换到新建分析，重置分析状态
    if st.session_state.current_page != page:
        if st.session_state.current_page == "📚 历史分析" and page == "🆕 新建分析":
            # 重置新建分析的状态
            st.session_state.analysis_progress = 0.0
            st.session_state.current_status = "⏳ 准备开始分析..."
            st.session_state.analysis_running = False
            st.session_state.analysis_starting = False
            st.session_state.stop_analysis = False
            st.session_state.is_viewing_historical = False
            
            # 重置代理状态为等待中
            for agent in st.session_state.agent_statuses:
                st.session_state.agent_statuses[agent] = "等待中"
            
            # 清空当前分析的报告内容（保留历史数据在分离状态）
            for section in st.session_state.report_sections:
                st.session_state.report_sections[section] = None
            
            # 清空当前分析参数和日志
            st.session_state.current_ticker = None
            st.session_state.current_date = None
            st.session_state.api_logs = []
            
        elif st.session_state.current_page == "🆕 新建分析" and page == "📚 历史分析":
            # 从新建分析切换到历史分析时，不重置历史状态
            st.session_state.is_viewing_historical = True if st.session_state.historical_ticker else False
            
        st.session_state.current_page = page
    
    # 主内容区域
    if page == "🆕 新建分析":
        render_new_analysis_page(app)
    elif page == "📚 历史分析":
        render_historical_analysis_page(app)
    else:  # 系统状态
        render_system_status_page(app)

def render_new_analysis_page(app):
    """渲染新建分析页面"""
    st.header("🆕 新建分析")
    
    # 创建左右分栏布局
    main_col, status_col = st.columns([2, 1])
    
    # 右侧状态面板 - 始终显示
    with status_col:
        render_status_panel(app)
    
    # 左侧主内容区域
    with main_col:
        # 如果没有开始分析，显示提示信息
        if st.session_state.analysis_progress == 0 and not st.session_state.analysis_running and not st.session_state.get('analysis_starting', False):
            st.info("👈 请在左侧控制面板中配置分析参数并开始分析")
            return
        
        # 如果正在启动，显示启动状态
        elif st.session_state.get('analysis_starting', False) and not st.session_state.analysis_running:
            st.warning("⏳ 分析正在启动中，请稍候...")
            with st.spinner("正在初始化分析系统..."):
                # 显示启动提示
                st.info("🚀 系统正在准备分析环境，这可能需要几秒钟时间")
            return
        
        # 分析结果展示区域
        if any(st.session_state.report_sections.values()):
            st.header("📈 分析结果")
            
            # 添加分析摘要卡片
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    completed_reports = sum(1 for content in st.session_state.report_sections.values() if content)
                    total_reports = len(st.session_state.report_sections)
                    st.metric("生成报告", f"{completed_reports}/{total_reports}")
                
                with col2:
                    total_content = sum(len(str(content)) for content in st.session_state.report_sections.values() if content)
                    st.metric("总内容", f"{total_content:,} 字符")
                
                with col3:
                    if st.session_state.current_ticker:
                        st.metric("分析股票", st.session_state.current_ticker)
                    else:
                        st.metric("分析股票", "无")
                
                with col4:
                    if st.session_state.current_date:
                        st.metric("分析日期", st.session_state.current_date)
                    else:
                        st.metric("分析日期", "无")
            
            st.divider()
            
            # 使用选项卡展示不同报告
            tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
                "🏢 市场分析", "💬 社交情绪", "📰 新闻分析", "📊 基本面",
                "🎯 研究决策", "💼 交易计划", "📈 最终决策", "📋 完整报告"
            ])
            
            with tab1:
                st.markdown(app.format_report_section("market_report", "🏢 市场分析"))
            
            with tab2:
                st.markdown(app.format_report_section("sentiment_report", "💬 社交情绪分析"))
            
            with tab3:
                st.markdown(app.format_report_section("news_report", "📰 新闻分析"))
            
            with tab4:
                st.markdown(app.format_report_section("fundamentals_report", "📊 基本面分析"))
            
            with tab5:
                st.markdown(app.format_report_section("investment_plan", "🎯 研究团队决策"))
            
            with tab6:
                st.markdown(app.format_report_section("trader_investment_plan", "💼 交易团队计划"))
            
            with tab7:
                st.markdown(app.format_report_section("final_trade_decision", "📈 最终交易决策"))
            
            with tab8:
                st.markdown(app.format_final_report())
        else:
            # 如果没有分析结果，显示占位信息
            st.info("📊 分析结果将在分析完成后显示在此处")

def render_historical_analysis_page(app):
    """渲染历史分析页面"""
    st.header("📚 历史分析")
    
    # 如果没有查看历史记录，显示提示
    if not st.session_state.is_viewing_historical:
        st.info("👈 请在左侧控制面板中选择要查看的历史分析记录")
    
    # 主内容区域 - 显示历史数据概览
    st.subheader("📊 历史数据概览")
    
    if st.session_state.available_tickers:
        # 创建统计指标卡片
        col1, col2, col3 = st.columns(3)
        
        # 计算统计数据
        total_analyses = 0
        for ticker in st.session_state.available_tickers:
            dates = get_available_analysis_dates(ticker)
            total_analyses += len(dates)
        
        with col1:
            st.metric("股票数量", len(st.session_state.available_tickers))
        
        with col2:
            st.metric("总分析记录", total_analyses)
        
        with col3:
            avg_analyses = total_analyses / len(st.session_state.available_tickers) if st.session_state.available_tickers else 0
            st.metric("平均记录数", f"{avg_analyses:.1f}")
        
        # 显示最近的分析记录
        st.subheader("🕒 最近分析记录")
        
        recent_analyses = []
        for ticker in st.session_state.available_tickers:
            dates = get_available_analysis_dates(ticker)
            if dates:
                # 添加最新的分析记录
                recent_analyses.append({
                    "股票": ticker,
                    "最新分析日期": dates[0],
                    "总记录数": len(dates)
                })
        
        # 按日期排序并显示
        if recent_analyses:
            import pandas as pd
            df = pd.DataFrame(recent_analyses)
            df = df.sort_values("最新分析日期", ascending=False).head(10)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("暂无分析记录")
            
    else:
        st.info("暂无历史分析数据")
        st.markdown("""
        **如何创建历史分析数据：**
        1. 切换到「🆕 新建分析」页面
        2. 配置分析参数并运行分析
        3. 分析完成后会自动保存到历史记录
        """)
    
    # 显示已加载的历史分析结果
    if st.session_state.is_viewing_historical and st.session_state.historical_ticker:
        st.header("📈 历史分析结果")
        
        # 添加历史分析摘要
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            
            completed_reports = sum(1 for content in st.session_state.historical_report_sections.values() if content)
            total_reports = len(st.session_state.historical_report_sections)
            
            with col1:
                st.metric("加载报告", f"{completed_reports}/{total_reports}")
            
            with col2:
                total_content = sum(len(str(content)) for content in st.session_state.historical_report_sections.values() if content)
                st.metric("总内容", f"{total_content:,} 字符")
            
            with col3:
                st.metric("股票代码", st.session_state.historical_ticker or "无")
            
            with col4:
                st.metric("分析日期", st.session_state.historical_date or "无")
        
        st.divider()
        
        # 使用选项卡展示历史报告
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "🏢 市场分析", "💬 社交情绪", "📰 新闻分析", "📊 基本面",
            "🎯 研究决策", "💼 交易计划", "📈 最终决策", "📋 完整报告"
        ])
        
        with tab1:
            st.markdown(app.format_historical_report_section("market_report", "🏢 市场分析"))
        
        with tab2:
            st.markdown(app.format_historical_report_section("sentiment_report", "💬 社交情绪分析"))
        
        with tab3:
            st.markdown(app.format_historical_report_section("news_report", "📰 新闻分析"))
        
        with tab4:
            st.markdown(app.format_historical_report_section("fundamentals_report", "📊 基本面分析"))
        
        with tab5:
            st.markdown(app.format_historical_report_section("investment_plan", "🎯 研究团队决策"))
        
        with tab6:
            st.markdown(app.format_historical_report_section("trader_investment_plan", "💼 交易团队计划"))
        
        with tab7:
            st.markdown(app.format_historical_report_section("final_trade_decision", "📈 最终交易决策"))
        
        with tab8:
            st.markdown(app.format_historical_final_report())

def render_status_panel(app):
    """渲染右侧状态监控面板"""
    st.header("📊 实时状态监控")
    
    # 分析进度概览
    with st.container():
        st.subheader("🚀 分析进度")
        
        # 进度条
        progress_value = st.session_state.analysis_progress / 100.0
        st.progress(progress_value)
        
        # 当前状态和步骤信息
        if st.session_state.current_status:
            st.caption(st.session_state.current_status)
        
        # 显示步骤信息（如果存在）
        if hasattr(st.session_state, 'last_step_info') and st.session_state.last_step_info:
            st.info(st.session_state.last_step_info)
        
        # 进度指标
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "分析进度", 
                f"{st.session_state.analysis_progress:.1f}%"
            )
        with col2:
            completed_agents = sum(1 for status in st.session_state.agent_statuses.values() if status == "已完成")
            total_agents = len(st.session_state.agent_statuses)
            st.metric(
                "已完成代理", 
                f"{completed_agents}/{total_agents}"
            )
    
    # 当前活跃代理
    with st.container():
        st.subheader("🤖 当前代理")
        active_agent = next(
            (agent for agent, status in st.session_state.agent_statuses.items() if status == "进行中"),
            "无"
        )
        if active_agent != "无":
            st.success(f"🔄 {active_agent}")
        else:
            # 根据分析状态显示不同信息
            if st.session_state.get('analysis_starting', False):
                st.warning("⏳ 正在启动分析系统...")
            elif st.session_state.analysis_running:
                st.info("🔄 正在进行分析...")
            elif st.session_state.analysis_progress > 0:
                st.success("✅ 分析已完成")
            else:
                st.info("⏸️ 等待开始分析")
    
    # 分析参数信息（如果有的话）
    if st.session_state.current_ticker or st.session_state.current_date:
        with st.container():
            st.subheader("📋 分析参数")
            if st.session_state.current_ticker:
                st.text(f"📈 股票代码: {st.session_state.current_ticker}")
            if st.session_state.current_date:
                st.text(f"📅 分析日期: {st.session_state.current_date}")
    
    # 代理状态详情
    with st.expander("📋 详细代理状态", expanded=False):
        st.markdown(app.format_agent_status_display())
    
    # 实时日志
    if st.session_state.get('show_logs', True):
        with st.expander("📋 实时日志", expanded=False):
            # 日志控制
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ 清空日志", key="status_panel_clear_logs"):
                    app.clear_api_logs()
                    st.rerun()
            with col2:
                log_count = len(st.session_state.api_logs)
                st.caption(f"📊 日志: {log_count} 条")
            
            # 日志内容
            if st.session_state.api_logs:
                log_text = app.format_api_logs()
                st.markdown(log_text)
            else:
                st.info("暂无日志记录")

def render_system_status_page(app):
    """渲染系统状态页面"""
    st.header("🤖 系统状态")
    
    # 当前分析状态
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 当前分析状态")
        
        # 进度信息
        st.metric("分析进度", f"{st.session_state.analysis_progress:.1f}%")
        st.info(st.session_state.current_status)
        
        # 当前分析参数
        if st.session_state.current_ticker:
            st.write(f"**股票代码**: {st.session_state.current_ticker}")
            st.write(f"**分析日期**: {st.session_state.current_date}")
        
        # 分析状态控制
        if st.session_state.get('analysis_starting', False):
            st.warning("⏳ 分析正在启动中...")
        elif st.session_state.analysis_running:
            st.warning("🔄 分析正在进行中...")
            if st.button("⏹️ 强制停止分析"):
                st.session_state.stop_analysis = True
                st.session_state.analysis_running = False
                st.session_state.analysis_starting = False
                st.success("分析已停止")
                st.rerun()
        else:
            st.success("✅ 系统空闲")
    
    with col2:
        st.subheader("🔧 系统配置")
        
        # LLM配置信息
        if app.default_provider:
            st.write(f"**默认LLM提供商**: {app.default_provider.upper()}")
            if app.default_provider_info:
                st.write(f"**API地址**: {app.default_provider_info['api_base_url']}")
        
        available_providers = app.get_llm_providers()
        st.write(f"**可用提供商**: {', '.join(available_providers)}")
        
        # 数据统计
        st.write(f"**历史股票数**: {len(st.session_state.available_tickers)}")
        
        total_analyses = 0
        for ticker in st.session_state.available_tickers:
            dates = get_available_analysis_dates(ticker)
            total_analyses += len(dates)
        st.write(f"**总分析记录**: {total_analyses}")
    
    # 详细代理状态
    st.subheader("🤖 详细代理状态")
    st.markdown(app.format_agent_status_display())
    
    # 报告状态概览
    st.subheader("📊 报告状态概览")
    
    report_status_data = []
    section_titles = {
        "market_report": "🏢 市场分析",
        "sentiment_report": "💬 社交情绪分析",
        "news_report": "📰 新闻分析",
        "fundamentals_report": "📊 基本面分析",
        "investment_plan": "🎯 研究团队决策",
        "trader_investment_plan": "💼 交易团队计划",
        "final_trade_decision": "📈 最终交易决策",
    }
    
    for section_key, title in section_titles.items():
        content = st.session_state.report_sections.get(section_key)
        status = "✅ 已生成" if content else "❌ 未生成"
        length = len(content) if content else 0
        report_status_data.append({
            "报告类型": title,
            "状态": status,
            "内容长度": f"{length} 字符"
        })
    
    # 显示报告状态表格
    import pandas as pd
    df = pd.DataFrame(report_status_data)
    st.dataframe(df, use_container_width=True)
    
    # 系统操作
    st.subheader("🔧 系统操作")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ 清空当前分析"):
            # 重置所有状态
            for section in st.session_state.report_sections:
                st.session_state.report_sections[section] = None
            for agent in st.session_state.agent_statuses:
                st.session_state.agent_statuses[agent] = "等待中"
            st.session_state.analysis_progress = 0.0
            st.session_state.analysis_running = False
            st.session_state.analysis_starting = False
            st.session_state.stop_analysis = False
            st.session_state.current_status = "⏳ 准备开始分析..."
            st.session_state.current_ticker = None
            st.session_state.current_date = None
            st.session_state.api_logs = []  # 清空日志
            st.success("当前分析已清空")
            st.rerun()
    
    with col2:
        if st.button("🔄 刷新历史数据"):
            app.load_historical_data()
            st.success("历史数据已刷新")
            st.rerun()
    
    with col3:
        if st.button("💾 导出当前状态"):
            # 导出当前状态为JSON
            export_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "analysis_progress": st.session_state.analysis_progress,
                "current_status": st.session_state.current_status,
                "current_ticker": st.session_state.current_ticker,
                "current_date": st.session_state.current_date,
                "agent_statuses": st.session_state.agent_statuses,
                "report_sections": st.session_state.report_sections
            }
            
            st.download_button(
                label="📥 下载状态文件",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"trading_agents_status_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

if __name__ == "__main__":
    main()