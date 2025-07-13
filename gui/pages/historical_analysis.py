"""
历史分析页面模块
"""
import streamlit as st
from gui.state_manager import state_manager
from gui.ui_components import ui_components
from gui_utils import get_available_analysis_dates, load_historical_analysis


class HistoricalAnalysisPage:
    """历史分析页面"""
    
    def render_sidebar_controls(self):
        """渲染侧边栏控制面板"""
        st.divider()
        st.subheader("📋 历史记录选择")
        
        # 刷新按钮
        if st.button("🔄 刷新历史数据", use_container_width=True):
            self._refresh_historical_data()
            st.success("历史数据已刷新")
            # 移除st.rerun()调用，让状态自然更新
        
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
            if (selected_ticker and selected_date and 
                selected_ticker != "暂无历史数据" and 
                selected_date not in ["请先选择股票", "该股票暂无分析记录"]):
                
                if self._load_historical_analysis(selected_ticker, selected_date):
                    st.success(f"✅ 已加载 {selected_ticker} 在 {selected_date} 的分析结果")
                    # 移除st.rerun()调用，让状态自然更新
                else:
                    st.error("❌ 加载失败，请检查数据完整性")
            else:
                st.error("请选择有效的股票和日期")
    
    def _refresh_historical_data(self):
        """刷新历史数据"""
        from gui_utils import get_all_available_tickers, get_all_analysis_results
        try:
            tickers = get_all_available_tickers()
            analysis_data = get_all_analysis_results()
            # 使用state_manager统一管理历史数据
            state_manager.update_historical_data(tickers, analysis_data)
        except Exception as e:
            st.error(f"❌ 加载历史分析数据失败: {e}")
            # 使用state_manager设置空数据
            state_manager.update_historical_data([], {})
    
    def _load_historical_analysis(self, ticker: str, date: str) -> bool:
        """加载历史分析数据"""
        if not ticker or not date:
            return False
        
        try:
            historical_results = load_historical_analysis(ticker, date)
            if not historical_results:
                return False
            
            # 加载历史数据到分离的历史状态
            state_manager.load_historical_report_sections(historical_results)
            state_manager.set_historical_analysis_data(ticker, date)
            
            return True
            
        except Exception as e:
            st.error(f"加载历史分析失败: {str(e)}")
            return False
    
    def render_main_content(self):
        """渲染主内容区域"""
        st.header("📚 历史分析")
        
        # 如果没有查看历史记录，显示提示
        if not st.session_state.is_viewing_historical:
            st.info("👈 请在左侧控制面板中选择要查看的历史分析记录")
        
        # 主内容区域 - 显示历史数据概览
        ui_components.render_historical_overview()
        
        # 显示已加载的历史分析结果
        if st.session_state.is_viewing_historical and st.session_state.historical_ticker:
            self._render_historical_results()
    
    def _render_historical_results(self):
        """渲染历史分析结果"""
        st.header("📈 历史分析结果")
        
        # 添加历史分析摘要
        with st.container():
            ui_components.render_analysis_summary_metrics(historical=True)
        
        st.divider()
        
        # 使用选项卡展示历史报告
        ui_components.render_report_tabs(historical=True)


# 全局历史分析页面实例
historical_analysis_page = HistoricalAnalysisPage()