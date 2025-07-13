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
            st.session_state.stop_analysis = True
            st.session_state.analysis_running = False
            st.session_state.analysis_starting = False
            st.warning("分析已停止")
            st.rerun()
    
    def _start_analysis(self, ticker: str, analysis_date: str, selected_analysts: List[str], 
                       research_depth: int, llm_provider: str, deep_model: str, quick_model: str):
        """开始分析"""
        # 设置分析触发器
        st.session_state.analysis_starting = True
        st.session_state.analysis_running = True
        
        # 执行分析
        try:
            success = analysis_runner.run_analysis(
                ticker, analysis_date, selected_analysts, 
                research_depth, llm_provider, deep_model, quick_model
            )
            
            if success:
                st.balloons()  # 庆祝动画
                st.success("🎉 分析成功完成！")
            else:
                st.error("❌ 分析失败，请检查配置和网络连接")
                
        except Exception as e:
            st.error(f"❌ 分析过程中发生错误: {str(e)}")
        
        st.rerun()
    
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
        st.header("📊 实时状态监控")
        
        # 分析进度概览
        with st.container():
            ui_components.render_progress_panel()
        
        # 当前活跃代理
        with st.container():
            ui_components.render_current_agent_panel()
        
        # 分析参数信息
        ui_components.render_analysis_params_panel()
        
        # 代理状态详情
        ui_components.render_agent_status_details()
        
        # 实时日志
        ui_components.render_realtime_logs()
    
    def _render_analysis_content(self):
        """渲染分析内容"""
        # 如果没有开始分析，显示提示信息
        if (state_manager.get_analysis_progress() == 0 and 
            not state_manager.is_analysis_running() and 
            not state_manager.is_analysis_starting()):
            st.info("👈 请在左侧控制面板中配置分析参数并开始分析")
            return
        
        # 如果正在启动，显示启动状态
        elif state_manager.is_analysis_starting() and not state_manager.is_analysis_running():
            st.warning("⏳ 分析正在启动中，请稍候...")
            with st.spinner("正在初始化分析系统..."):
                st.info("🚀 系统正在准备分析环境，这可能需要几秒钟时间")
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
            # 如果没有分析结果，显示占位信息
            st.info("📊 分析结果将在分析完成后显示在此处")


# 全局新建分析页面实例
new_analysis_page = NewAnalysisPage()