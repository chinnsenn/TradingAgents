"""
新建分析页面模块
"""
import streamlit as st
import datetime
from typing import List
from gui.state_manager import state_manager
from gui.ui_components import ui_components
from gui.analysis_runner import analysis_runner
from config_utils import get_provider_names, get_provider_models, get_default_provider


class NewAnalysisPage:
    """新建分析页面"""
    
    @staticmethod
    def get_analyst_choices() -> List[str]:
        """获取分析师选择选项"""
        return [
            "market - 市场分析师",
            "social - 社交分析师", 
            "news - 新闻分析师",
            "fundamentals - 基本面分析师"
        ]
    
    def render_sidebar_controls(self):
        """渲染侧边栏控制面板"""
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
            self.get_analyst_choices(),
            default=self.get_analyst_choices()
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
        
        available_providers = get_provider_names()
        default_provider = get_default_provider() or available_providers[0]
        
        llm_provider = st.selectbox(
            "LLM提供商",
            available_providers,
            index=available_providers.index(default_provider) if default_provider in available_providers else 0
        )
        
        default_models = get_provider_models(llm_provider)
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
        
        self._render_control_buttons(ticker, analysis_date, selected_analysts, 
                                   research_depth, llm_provider, deep_model, quick_model)
    
    def _render_control_buttons(self, ticker: str, analysis_date: str, selected_analysts: List[str], 
                               research_depth: int, llm_provider: str, deep_model: str, quick_model: str):
        """渲染控制按钮"""
        # 检查是否可以开始分析
        can_start_analysis = (
            not state_manager.is_analysis_running() and
            not state_manager.is_analysis_starting() and
            state_manager.get_analysis_progress() == 0
        )
        
        # 动态按钮文本和状态
        if state_manager.is_analysis_running():
            button_text = "🔄 分析进行中..."
            button_disabled = True
        elif state_manager.is_analysis_starting():
            button_text = "⏳ 正在启动..."
            button_disabled = True
        else:
            button_text = "🚀 开始分析"
            button_disabled = False
        
        # 开始分析按钮
        if st.button(button_text, type="primary", disabled=button_disabled, use_container_width=True):
            if not ticker.strip():
                st.error("请输入股票代码")
            elif not analysis_date.strip():
                st.error("请输入分析日期")
            elif not selected_analysts:
                st.error("请选择至少一个分析师")
            else:
                self._start_analysis(ticker, analysis_date, selected_analysts, 
                                   research_depth, llm_provider, deep_model, quick_model)
        
        # 停止分析按钮
        stop_button_disabled = not state_manager.is_analysis_running()
        if st.button("⏹️ 停止分析", disabled=stop_button_disabled, use_container_width=True):
            # 使用state_manager统一处理停止逻辑并刷新UI
            state_manager.stop_analysis_with_refresh()
            st.warning("分析已停止")
    
    def _start_analysis(self, ticker: str, analysis_date: str, selected_analysts: List[str], 
                       research_depth: int, llm_provider: str, deep_model: str, quick_model: str):
        """开始分析"""
        # 设置分析参数到session state，避免阻塞UI
        st.session_state.analysis_params = {
            'ticker': ticker,
            'analysis_date': analysis_date,
            'selected_analysts': selected_analysts,
            'research_depth': research_depth,
            'llm_provider': llm_provider,
            'deep_model': deep_model,
            'quick_model': quick_model
        }
        
        # 使用state_manager原子性地启动分析并触发UI刷新
        state_manager.start_analysis_atomic_with_refresh(ticker, analysis_date)
        
        # 立即重新运行以开始分析
        # 移除st.rerun()调用，让状态自然更新
    
    def render_main_content(self):
        """渲染主内容区域"""
        st.header("🆕 新建分析")
        
        # 创建左右分栏布局
        main_col, status_col = st.columns([2, 1])
        
        # 右侧状态面板
        with status_col:
            self.render_status_panel()
        
        # 左侧主内容区域
        with main_col:
            self._render_analysis_content()
    
    def render_status_panel(self):
        """渲染状态监控面板"""
        # 添加CSS类标识
        st.markdown('<div class="status-panel">', unsafe_allow_html=True)
        
        st.header("📊 实时状态监控")
        
        # 使用动态容器实现实时更新
        # 创建持久化的动态容器
        if 'progress_container' not in st.session_state:
            st.session_state.progress_container = st.empty()
        if 'agent_container' not in st.session_state:
            st.session_state.agent_container = st.empty()
        if 'details_container' not in st.session_state:
            st.session_state.details_container = st.empty()
        if 'logs_container' not in st.session_state:
            st.session_state.logs_container = st.empty()
        
        # 使用动态容器渲染各个面板
        with st.session_state.progress_container.container():
            ui_components.render_progress_panel()
        
        with st.session_state.agent_container.container():
            ui_components.render_current_agent_panel()
        
        with st.session_state.details_container.container():
            ui_components.render_agent_status_details()
        
        with st.session_state.logs_container.container():
            ui_components.render_realtime_logs()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 处理刷新标志（但不在此处重新渲染）
        if (st.session_state.get('ui_needs_refresh', False) or
            st.session_state.get('status_needs_refresh', False) or
            st.session_state.get('completion_needs_refresh', False)):
            
            # 清除各类刷新标志
            st.session_state.ui_needs_refresh = False
            st.session_state.status_needs_refresh = False
            st.session_state.completion_needs_refresh = False
            
            # 标记需要在下次渲染时自动刷新，而不是立即重新渲染
            # 这避免了在同一个渲染周期内重复渲染组件
    
    def _render_analysis_content(self):
        """渲染分析内容"""
        # 检查是否需要执行分析（非阻塞方式）
        if state_manager.is_analysis_triggered():
            state_manager.clear_analysis_trigger()
            params = st.session_state.get('analysis_params', {})
            if params:
                # 在后台执行分析，不阻塞UI
                self._execute_analysis_async(params)
        
        # 检查分析完成状态
        if st.session_state.get('analysis_completed', False):
            st.balloons()  # 庆祝动画
            state_manager.set_analysis_completed(False)  # 重置状态
        
        # 检查分析失败状态
        if st.session_state.get('analysis_failed', False):
            st.error("❌ 分析失败或被中断")
            state_manager.set_analysis_failed(False)  # 重置状态
        
        # 只有在没有开始分析时才显示提示信息
        if (state_manager.get_analysis_progress() == 0 and 
            not state_manager.is_analysis_running() and 
            not state_manager.is_analysis_starting()):
            st.info("👈 请在左侧控制面板中配置分析参数并开始分析")
            return
        
        # 分析结果展示区域
        if any(st.session_state.report_sections.values()):
            st.header("📈 分析结果")
            
            # 添加分析摘要卡片
            with st.container():
                ui_components.render_analysis_summary_metrics(historical=False)
            
            st.divider()
            
            # 使用选项卡展示不同报告
            ui_components.render_report_tabs(historical=False)
        else:
            # 当分析已经启动但没完成时，左侧保持空白
            # 所有进度信息都在右侧的「实时状态监控」中显示
            pass
    
    def _execute_analysis_async(self, params: dict):
        """异步执行分析（避免阻塞UI）"""
        try:
            # 避免重复执行分析
            if st.session_state.get('analysis_executed', False):
                return
                
            state_manager.set_analysis_executed(True)
            
            # 执行分析（这里会是一个长时间运行的过程）
            success = analysis_runner.run_analysis(
                params['ticker'], params['analysis_date'], params['selected_analysts'], 
                params['research_depth'], params['llm_provider'], 
                params['deep_model'], params['quick_model']
            )
            
            # 分析完成后的处理
            if success:
                # 不使用st.rerun()，让状态自然更新
                state_manager.set_analysis_completed(True)
                state_manager.add_api_log("response", "🎉 分析成功完成！")
            else:
                state_manager.set_analysis_failed(True)
                state_manager.add_api_log("error", "❌ 分析失败，请检查配置和网络连接")
            
            # 清理参数
            state_manager.clear_analysis_params()
            state_manager.set_analysis_executed(False)
            
        except Exception as e:
            state_manager.set_analysis_failed(True)
            state_manager.add_api_log("error", f"❌ 分析过程中发生错误: {str(e)}")
            state_manager.clear_analysis_params()
            state_manager.set_analysis_executed(False)


# 全局新建分析页面实例
new_analysis_page = NewAnalysisPage()