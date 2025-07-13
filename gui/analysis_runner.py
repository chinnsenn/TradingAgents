"""
分析执行模块 - 处理分析流程的执行逻辑
"""
import streamlit as st
import time
from typing import List, Dict, Any
from error_handler import with_error_handling, print_exception_details
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from config_utils import get_provider_info
from gui_utils import save_analysis_results
from gui.state_manager import state_manager


class AnalysisRunner:
    """分析执行器 - 处理分析流程的核心逻辑"""
    
    def __init__(self):
        self.graph = None
        self.init_state = None
        self.args = None
    
    @with_error_handling
    def run_analysis(self, ticker: str, analysis_date: str, selected_analysts: List[str], 
                    research_depth: int, llm_provider: str, deep_model: str, quick_model: str) -> bool:
        """执行完整的分析流程"""
        try:
            # 初始化分析环境
            if not self._initialize_analysis(ticker, analysis_date, selected_analysts, 
                                           research_depth, llm_provider, deep_model, quick_model):
                return False
            
            # 执行分析流程
            success = self._execute_analysis_stream()
            
            if success and not st.session_state.stop_analysis:
                # 完成分析
                self._finalize_analysis()
                return True
            else:
                self._handle_analysis_stopped()
                return False
                
        except Exception as e:
            self._handle_analysis_error(e)
            return False
        finally:
            self._cleanup_analysis()
    
    def _initialize_analysis(self, ticker: str, analysis_date: str, selected_analysts: List[str], 
                           research_depth: int, llm_provider: str, deep_model: str, quick_model: str) -> bool:
        """初始化分析环境"""
        # 设置分析参数
        state_manager.set_analysis_params(ticker, analysis_date)
        
        # 清空之前的日志和状态
        state_manager.clear_api_logs()
        state_manager.add_api_log_with_container_update("info", f"开始分析 {ticker.upper()} ({analysis_date})")
        
        # 重置状态 - 使用state_manager统一管理
        state_manager.set_stop_analysis(False)
        state_manager.set_analysis_progress(0.0)
        # 不在此重置 analysis_starting，保持按钮状态正确
        
        # 创建进度显示
        progress_placeholder = st.empty()
        
        try:
            with progress_placeholder.container():
                st.info("🚀 正在初始化分析系统...")
                init_progress = st.progress(0.0)
                init_status = st.empty()
            
            # 步骤1: 解析分析师配置
            analyst_types = self._parse_analyst_selection(selected_analysts)
            init_status.text("📋 解析分析师配置...")
            init_progress.progress(0.1)
            state_manager.add_api_log_with_container_update("info", f"配置分析师: {', '.join(analyst_types)}")
            
            # 步骤2: 创建配置
            config = self._create_analysis_config(research_depth, llm_provider, deep_model, quick_model)
            init_status.text("⚙️ 配置LLM提供商...")
            init_progress.progress(0.2)
            state_manager.add_api_log_with_container_update("info", f"LLM提供商: {llm_provider}, 深度模型: {deep_model}, 快速模型: {quick_model}")
            
            # 步骤3: 初始化图
            if not self._initialize_trading_graph(analyst_types, config):
                return False
            init_status.text("🤖 初始化TradingAgents图...")
            init_progress.progress(0.5)
            
            # 步骤4: 创建初始状态
            if not self._create_initial_state(ticker, analysis_date):
                return False
            init_status.text("📊 创建初始分析状态...")
            init_progress.progress(0.8)
            
            init_status.text("✅ 初始化完成，开始分析...")
            init_progress.progress(1.0)
            time.sleep(0.5)
            
            # 初始化完成后，从 starting 状态转换到 running 状态
            state_manager.transition_to_running()
            
            # 清空初始化显示
            progress_placeholder.empty()
            return True
            
        except Exception as e:
            progress_placeholder.empty()
            # 如果初始化失败，使用state_manager重置状态
            state_manager.set_analysis_starting(False)
            state_manager.set_analysis_running(False)
            raise e
    
    def _parse_analyst_selection(self, selected_analysts: List[str]) -> List[str]:
        """解析分析师选择"""
        analyst_types = []
        for choice in selected_analysts:
            analyst_type = choice.split(" - ")[0]
            analyst_types.append(analyst_type)
        return analyst_types
    
    def _create_analysis_config(self, research_depth: int, llm_provider: str, 
                              deep_model: str, quick_model: str) -> Dict[str, Any]:
        """创建分析配置"""
        config = DEFAULT_CONFIG.copy()
        config["max_debate_rounds"] = research_depth
        config["max_risk_discuss_rounds"] = research_depth
        config["deep_think_llm"] = deep_model
        config["quick_think_llm"] = quick_model
        config["llm_provider"] = llm_provider.lower()
        
        # 获取提供商信息
        provider_info = get_provider_info(llm_provider)
        if provider_info:
            config["backend_url"] = provider_info["api_base_url"]
            config["api_key"] = provider_info["api_key"]
            state_manager.add_api_log("api_call", f"连接到API: {provider_info['api_base_url']}")
        else:
            raise Exception(f"未找到提供商配置: {llm_provider}")
        
        config["online_tools"] = True
        return config
    
    def _initialize_trading_graph(self, analyst_types: List[str], config: Dict[str, Any]) -> bool:
        """初始化TradingAgents图"""
        try:
            print(f"[DEBUG] 开始初始化TradingAgentsGraph...")
            print(f"[DEBUG] 分析师类型: {analyst_types}")
            print(f"[DEBUG] 配置参数: {config}")
            
            self.graph = TradingAgentsGraph(
                selected_analysts=analyst_types,
                config=config,
                debug=True
            )
            
            print(f"[DEBUG] TradingAgentsGraph初始化成功")
            state_manager.add_api_log_with_container_update("response", "交易代理系统初始化成功")
            return True
            
        except Exception as e:
            print(f"[DEBUG] TradingAgentsGraph初始化失败: {str(e)}")
            print(f"[DEBUG] 错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            state_manager.add_api_log_with_container_update("error", f"初始化TradingAgentsGraph失败: {str(e)}")
            raise e
    
    def _create_initial_state(self, ticker: str, analysis_date: str) -> bool:
        """创建初始分析状态"""
        try:
            print(f"[DEBUG] 开始创建初始状态...")
            print(f"[DEBUG] 股票代码: {ticker}, 分析日期: {analysis_date}")
            
            self.init_state = self.graph.propagator.create_initial_state(ticker, analysis_date)
            self.args = self.graph.propagator.get_graph_args()
            
            print(f"[DEBUG] 初始状态创建成功")
            print(f"[DEBUG] 初始状态内容: {list(self.init_state.keys()) if hasattr(self.init_state, 'keys') else type(self.init_state)}")
            print(f"[DEBUG] 图参数: {self.args}")
            state_manager.add_api_log_with_container_update("response", "初始分析状态创建成功")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 创建初始状态失败: {str(e)}")
            print(f"[DEBUG] 错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            state_manager.add_api_log_with_container_update("error", f"创建初始状态失败: {str(e)}")
            raise e
    
    def _execute_analysis_stream(self) -> bool:
        """执行分析流"""
        # 让右侧状态监控面板处理所有进度显示
        status_placeholder = st.empty()
        progress_placeholder = st.empty()
        
        step_count = 0
        total_expected_steps = 50
        last_update_time = time.time()
        
        try:
            print(f"[DEBUG] 开始流式分析处理...")
            state_manager.add_api_log_with_container_update("info", "开始流式分析处理...")
            
            stream_count = 0
            for chunk in self.graph.graph.stream(self.init_state, **self.args):
                if st.session_state.stop_analysis:
                    print(f"[DEBUG] 分析被用户停止")
                    state_manager.add_api_log_with_container_update("warning", "分析被用户停止")
                    break
                
                stream_count += 1
                step_count += 1
                
                # 处理数据块
                self._process_stream_chunk(chunk, step_count)
                
                # 更新进度 - 使用state_manager
                progress = min((step_count / total_expected_steps) * 95, 95)
                state_manager.set_analysis_progress(progress)
                
                # 所有进度信息由右侧状态监控面板处理
                current_time = time.time()
                if current_time - last_update_time > 2.0:  # 每2秒更新一次状态，但不显示UI
                    # 状态更新由右侧面板管理
                    last_update_time = current_time
                
                # 限制UI更新频率
                self._update_ui_if_needed(step_count, last_update_time)
            
            print(f"[DEBUG] 流式分析完成，总共处理 {step_count} 步，流数据块: {stream_count}")
            state_manager.add_api_log("response", f"流式分析完成，总共处理 {step_count} 步")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 分析流处理失败: {str(e)}")
            state_manager.add_api_log("error", f"分析流处理失败: {str(e)}")
            raise e
    
    def _process_stream_chunk(self, chunk: Dict[str, Any], step_count: int):
        """处理流数据块"""
        print(f"[DEBUG] 接收到流数据块 #{step_count}: {list(chunk.keys()) if hasattr(chunk, 'keys') else type(chunk)}")
        
        # 更新报告部分
        try:
            self._update_reports_from_chunk(chunk)
        except Exception as e:
            print(f"[DEBUG] 更新报告部分失败: {str(e)}")
        
        # 更新代理状态
        try:
            self._update_agent_status_from_chunk(chunk)
        except Exception as e:
            print(f"[DEBUG] 更新代理状态失败: {str(e)}")
        
        # 记录进度
        if step_count % 10 == 0:
            progress = min((step_count / 50) * 95, 95)
            state_manager.add_api_log("info", f"处理步骤 {step_count}, 进度 {progress:.1f}%")
    
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
                state_manager.update_report_section(report_key, chunk[chunk_key])
        
        # 处理投资辩论状态
        if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
            debate_state = chunk["investment_debate_state"]
            if "judge_decision" in debate_state and debate_state["judge_decision"]:
                state_manager.update_report_section("investment_plan", debate_state["judge_decision"])
    
    def _update_agent_status_from_chunk(self, chunk: Dict[str, Any]):
        """从数据块更新代理状态"""
        # 检测正在进行的分析
        if "market_analysis" in chunk or any(key.startswith("market") for key in chunk.keys()):
            if not chunk.get("market_report"):
                state_manager.update_agent_status_with_refresh("市场分析师", "进行中")
                state_manager.add_api_log_with_container_update("api_call", "市场分析师开始分析")
        
        if "sentiment_analysis" in chunk or any(key.startswith("sentiment") for key in chunk.keys()):
            if not chunk.get("sentiment_report"):
                state_manager.update_agent_status_with_refresh("社交分析师", "进行中")
                state_manager.add_api_log_with_container_update("api_call", "社交分析师开始分析")
        
        if "news_analysis" in chunk or any(key.startswith("news") for key in chunk.keys()):
            if not chunk.get("news_report"):
                state_manager.update_agent_status_with_refresh("新闻分析师", "进行中")
                state_manager.add_api_log_with_container_update("api_call", "新闻分析师开始分析")
        
        if "fundamentals_analysis" in chunk or any(key.startswith("fundamentals") for key in chunk.keys()):
            if not chunk.get("fundamentals_report"):
                state_manager.update_agent_status_with_refresh("基本面分析师", "进行中")
                state_manager.add_api_log_with_container_update("api_call", "基本面分析师开始分析")
        
        # 检测完成的分析
        if "market_report" in chunk and chunk["market_report"]:
            state_manager.update_agent_status_with_refresh("市场分析师", "已完成")
            state_manager.add_api_log_with_container_update("response", "市场分析完成")
        
        if "sentiment_report" in chunk and chunk["sentiment_report"]:
            state_manager.update_agent_status_with_refresh("社交分析师", "已完成")
            state_manager.add_api_log_with_container_update("response", "社交情绪分析完成")
        
        if "news_report" in chunk and chunk["news_report"]:
            state_manager.update_agent_status_with_refresh("新闻分析师", "已完成")
            state_manager.add_api_log_with_container_update("response", "新闻分析完成")
        
        if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
            state_manager.update_agent_status_with_refresh("基本面分析师", "已完成")
            state_manager.add_api_log_with_container_update("response", "基本面分析完成")
        
        if "investment_debate_state" in chunk and chunk["investment_debate_state"]:
            debate_state = chunk["investment_debate_state"]
            if "judge_decision" in debate_state and debate_state["judge_decision"]:
                state_manager.update_agent_status_with_refresh("研究经理", "已完成")
                state_manager.add_api_log_with_container_update("response", "研究团队决策完成")
        
        if "trader_investment_plan" in chunk and chunk["trader_investment_plan"]:
            state_manager.update_agent_status_with_refresh("交易员", "已完成")
            state_manager.add_api_log_with_container_update("response", "交易计划制定完成")
        
        if "final_trade_decision" in chunk and chunk["final_trade_decision"]:
            state_manager.update_agent_status_with_refresh("投资组合经理", "已完成")
            state_manager.add_api_log_with_container_update("response", "最终交易决策完成")
    
    def _update_ui_if_needed(self, step_count: int, last_update_time: float):
        """在需要时更新UI"""
        current_time = time.time()
        if current_time - last_update_time > 1.0:
            print(f"[DEBUG] 更新UI状态信息...")
            info = f"步骤 {step_count} | {st.session_state.current_status}"
            state_manager.set_last_step_info(info)
            
            # 移除st.rerun()调用，避免中断分析流程
            # 状态更新会通过session_state自然反映到UI上
    
    def _finalize_analysis(self):
        """完成分析"""
        # 使用state_manager完成分析
        state_manager.finalize_analysis_success()
        
        # 使用容器显示完成状态，避免st.rerun()
        completion_placeholder = st.empty()
        with completion_placeholder.container():
            st.progress(1.0)
            st.success("🎉 分析成功完成！")
        
        # 保存分析结果
        self._save_analysis_results()
    
    def _save_analysis_results(self):
        """保存分析结果"""
        try:
            saved_path = save_analysis_results(
                results=st.session_state.report_sections,
                ticker=st.session_state.current_ticker,
                analysis_date=st.session_state.current_date
            )
            
            # 使用容器显示保存结果
            results_placeholder = st.empty()
            with results_placeholder.container():
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
                    st.metric("分析时长", "已完成")
                    
        except Exception as e:
            error_placeholder = st.empty()
            with error_placeholder.container():
                st.warning(f"⚠️ 保存分析结果时发生错误: {str(e)}")
    
    def _handle_analysis_stopped(self):
        """处理分析停止"""
        stop_placeholder = st.empty()
        with stop_placeholder.container():
            st.warning("⏹️ 分析已被用户停止")
    
    def _handle_analysis_error(self, e: Exception):
        """处理分析错误"""
        # 使用state_manager处理错误状态
        state_manager.finalize_analysis_failure(str(e))
        
        # 使用容器显示错误信息，避免st.rerun()
        error_placeholder = st.empty()
        with error_placeholder.container():
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
    
    def _cleanup_analysis(self):
        """清理分析资源"""
        print(f"[DEBUG] 分析线程的finally块已执行")
        # 使用state_manager清理分析状态
        state_manager.cleanup_analysis()


# 全局分析运行器实例
analysis_runner = AnalysisRunner()