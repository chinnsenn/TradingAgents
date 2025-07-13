"""
系统状态页面模块
"""
import streamlit as st
from gui.state_manager import state_manager
from gui.ui_components import ui_components


class SystemStatusPage:
    """系统状态页面"""
    
    def render_main_content(self):
        """渲染主内容区域"""
        st.header("🤖 系统状态")
        
        # 系统状态概览
        ui_components.render_system_status_overview()
        
        # 详细代理状态
        st.subheader("🤖 详细代理状态")
        from gui.report_formatter import report_formatter
        st.markdown(report_formatter.format_agent_status_display())
        
        # 报告状态概览
        ui_components.render_report_status_table()
        
        # 系统操作
        ui_components.render_system_operations()


# 全局系统状态页面实例
system_status_page = SystemStatusPage()