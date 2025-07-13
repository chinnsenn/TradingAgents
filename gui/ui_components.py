"""
UI组件模块 - 可复用的Streamlit界面组件
"""
import streamlit as st
import datetime
import json
from typing import List, Dict, Any
from gui.state_manager import state_manager
from gui.report_formatter import report_formatter


class UIComponents:
    """UI组件集合"""
    
    def render_analysis_summary_metrics(self, historical: bool = False):
        """渲染分析摘要指标卡片"""
        metrics = report_formatter.get_analysis_summary_metrics(historical)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if historical:
                st.metric("加载报告", f"{metrics['completed_reports']}/{metrics['total_reports']}")
            else:
                st.metric("生成报告", f"{metrics['completed_reports']}/{metrics['total_reports']}")
        
        with col2:
            st.metric("总内容", f"{metrics['total_content']:,} 字符")
        
        with col3:
            if historical:
                st.metric("股票代码", metrics['ticker'])
            else:
                st.metric("分析股票", metrics['ticker'])
        
        with col4:
            st.metric("分析日期", metrics['date'])
    
    def render_report_tabs(self, historical: bool = False):
        """渲染报告选项卡"""
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "🏢 市场分析", "💬 社交情绪", "📰 新闻分析", "📊 基本面",
            "🎯 研究决策", "💼 交易计划", "📈 最终决策", "📋 完整报告"
        ])
        
        with tab1:
            st.markdown(report_formatter.format_report_section("market_report", "🏢 市场分析", historical=historical))
        
        with tab2:
            st.markdown(report_formatter.format_report_section("sentiment_report", "💬 社交情绪分析", historical=historical))
        
        with tab3:
            st.markdown(report_formatter.format_report_section("news_report", "📰 新闻分析", historical=historical))
        
        with tab4:
            st.markdown(report_formatter.format_report_section("fundamentals_report", "📊 基本面分析", historical=historical))
        
        with tab5:
            st.markdown(report_formatter.format_report_section("investment_plan", "🎯 研究团队决策", historical=historical))
        
        with tab6:
            st.markdown(report_formatter.format_report_section("trader_investment_plan", "💼 交易团队计划", historical=historical))
        
        with tab7:
            st.markdown(report_formatter.format_report_section("final_trade_decision", "📈 最终交易决策", historical=historical))
        
        with tab8:
            st.markdown(report_formatter.format_final_report(historical=historical))
    
    def render_progress_panel(self):
        """渲染进度面板"""
        st.subheader("🚀 分析进度")
        
        # 进度条
        progress_value = state_manager.get_analysis_progress() / 100.0
        st.progress(progress_value)
        
        # 当前状态和步骤信息
        current_status = state_manager.get_current_status()
        if current_status:
            st.caption(current_status)
        
        # 显示步骤信息（如果存在）
        if hasattr(st.session_state, 'last_step_info') and st.session_state.last_step_info:
            st.info(st.session_state.last_step_info)
        
        # 进度指标
        col1, col2 = st.columns(2)
        with col1:
            st.metric("分析进度", f"{state_manager.get_analysis_progress():.1f}%")
        with col2:
            completed, total = state_manager.get_completed_agents_count()
            st.metric("已完成代理", f"{completed}/{total}")
    
    def render_current_agent_panel(self):
        """渲染当前代理面板"""
        st.subheader("🤖 当前代理")
        active_agent = state_manager.get_active_agent()
        
        if active_agent != "无":
            st.success(f"🔄 {active_agent}")
        else:
            # 根据分析状态显示不同信息
            if state_manager.is_analysis_starting():
                st.warning("⏳ 正在启动分析系统...")
            elif state_manager.is_analysis_running():
                st.info("🔄 正在进行分析...")
            elif state_manager.get_analysis_progress() > 0:
                st.success("✅ 分析已完成")
            else:
                st.info("⏸️ 等待开始分析")
    
    def render_analysis_params_panel(self):
        """渲染分析参数面板"""
        if st.session_state.current_ticker or st.session_state.current_date:
            st.subheader("📋 分析参数")
            if st.session_state.current_ticker:
                st.text(f"📈 股票代码: {st.session_state.current_ticker}")
            if st.session_state.current_date:
                st.text(f"📅 分析日期: {st.session_state.current_date}")
    
    def render_agent_status_details(self):
        """渲染代理状态详情"""
        with st.expander("📋 详细代理状态", expanded=False):
            st.markdown(report_formatter.format_agent_status_display())
    
    def render_realtime_logs(self):
        """渲染实时日志"""
        if st.session_state.get('show_logs', True):
            with st.expander("📋 实时日志", expanded=False):
                # 日志控制
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ 清空日志", key="ui_components_clear_logs"):
                        state_manager.clear_api_logs()
                        st.rerun()
                with col2:
                    log_count = len(st.session_state.api_logs)
                    st.caption(f"📊 日志: {log_count} 条")
                
                # 日志内容
                if st.session_state.api_logs:
                    log_text = report_formatter.format_api_logs()
                    st.markdown(log_text)
                else:
                    st.info("暂无日志记录")
    
    def render_historical_overview(self):
        """渲染历史数据概览"""
        st.subheader("📊 历史数据概览")
        
        if st.session_state.available_tickers:
            # 创建统计指标卡片
            col1, col2, col3 = st.columns(3)
            
            # 计算统计数据
            from gui_utils import get_available_analysis_dates
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
            self._render_recent_analyses()
            
        else:
            st.info("暂无历史分析数据")
            st.markdown("""
            **如何创建历史分析数据：**
            1. 切换到「🆕 新建分析」页面
            2. 配置分析参数并运行分析
            3. 分析完成后会自动保存到历史记录
            """)
    
    def _render_recent_analyses(self):
        """渲染最近分析记录"""
        st.subheader("🕒 最近分析记录")
        
        from gui_utils import get_available_analysis_dates
        recent_analyses = []
        for ticker in st.session_state.available_tickers:
            dates = get_available_analysis_dates(ticker)
            if dates:
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
    
    def render_system_status_overview(self):
        """渲染系统状态概览"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 当前分析状态")
            
            # 进度信息
            st.metric("分析进度", f"{state_manager.get_analysis_progress():.1f}%")
            st.info(state_manager.get_current_status())
            
            # 当前分析参数
            if st.session_state.current_ticker:
                st.write(f"**股票代码**: {st.session_state.current_ticker}")
                st.write(f"**分析日期**: {st.session_state.current_date}")
            
            # 分析状态控制
            self._render_analysis_control()
        
        with col2:
            st.subheader("🔧 系统配置")
            self._render_system_config()
    
    def _render_analysis_control(self):
        """渲染分析控制面板"""
        if state_manager.is_analysis_starting():
            st.warning("⏳ 分析正在启动中...")
        elif state_manager.is_analysis_running():
            st.warning("🔄 分析正在进行中...")
            if st.button("⏹️ 强制停止分析"):
                st.session_state.stop_analysis = True
                st.session_state.analysis_running = False
                st.session_state.analysis_starting = False
                st.success("分析已停止")
                st.rerun()
        else:
            st.success("✅ 系统空闲")
    
    def _render_system_config(self):
        """渲染系统配置信息"""
        from config_utils import get_default_provider, get_provider_info, get_provider_names
        from gui_utils import get_available_analysis_dates
        
        # LLM配置信息
        default_provider = get_default_provider()
        if default_provider:
            st.write(f"**默认LLM提供商**: {default_provider.upper()}")
            provider_info = get_provider_info(default_provider)
            if provider_info:
                st.write(f"**API地址**: {provider_info['api_base_url']}")
        
        available_providers = get_provider_names()
        st.write(f"**可用提供商**: {', '.join(available_providers)}")
        
        # 数据统计
        st.write(f"**历史股票数**: {len(st.session_state.available_tickers)}")
        
        total_analyses = 0
        for ticker in st.session_state.available_tickers:
            dates = get_available_analysis_dates(ticker)
            total_analyses += len(dates)
        st.write(f"**总分析记录**: {total_analyses}")
    
    def render_report_status_table(self):
        """渲染报告状态表格"""
        st.subheader("📊 报告状态概览")
        
        report_status_data = report_formatter.create_report_status_data()
        
        # 显示报告状态表格
        import pandas as pd
        df = pd.DataFrame(report_status_data)
        st.dataframe(df, use_container_width=True)
    
    def render_system_operations(self):
        """渲染系统操作面板"""
        st.subheader("🔧 系统操作")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🗑️ 清空当前分析"):
                state_manager.reset_analysis_state()
                st.success("当前分析已清空")
                st.rerun()
        
        with col2:
            if st.button("🔄 刷新历史数据"):
                from gui_utils import get_all_available_tickers, get_all_analysis_results
                try:
                    st.session_state.available_tickers = get_all_available_tickers()
                    st.session_state.historical_analysis = get_all_analysis_results()
                    st.success("历史数据已刷新")
                except Exception as e:
                    st.error(f"刷新失败: {e}")
                st.rerun()
        
        with col3:
            if st.button("💾 导出当前状态"):
                self._export_current_state()
    
    def _export_current_state(self):
        """导出当前状态"""
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


# 全局UI组件实例
ui_components = UIComponents()