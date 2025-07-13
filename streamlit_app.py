"""
TradingAgents Streamlit Web 应用程序 - 重构版本
专业的多代理LLM金融交易分析框架
"""

import streamlit as st
from error_handler import setup_error_handling
from gui.config import PAGE_CONFIG, PAGE_OPTIONS, CUSTOM_CSS
from gui.state_manager import state_manager
from gui.pages.new_analysis import new_analysis_page
from gui.pages.historical_analysis import historical_analysis_page
from gui.pages.system_status import system_status_page
from config_utils import get_provider_names, get_default_provider, get_provider_info


class TradingAgentsApp:
    """TradingAgents Streamlit 应用程序主类"""
    
    def __init__(self):
        """初始化应用"""
        # 初始化状态管理器
        state_manager.initialize_all_states()
        self.load_configuration()
    
    def load_configuration(self):
        """加载应用配置"""
        self.default_provider = get_default_provider()
        self.default_provider_info = get_provider_info(self.default_provider) if self.default_provider else None
        self.load_historical_data()
    
    def load_historical_data(self):
        """加载历史分析数据"""
        try:
            from gui_utils import get_all_available_tickers, get_all_analysis_results
            tickers = get_all_available_tickers()
            analysis_data = get_all_analysis_results()
            # 使用state_manager统一管理历史数据
            state_manager.update_historical_data(tickers, analysis_data)
        except Exception as e:
            st.error(f"❌ 加载历史分析数据失败: {e}")
            # 使用state_manager设置空数据
            state_manager.update_historical_data([], {})
    
    def render_header(self):
        """渲染应用头部"""
        st.title("🚀 TradingAgents - 多代理LLM金融交易框架")
        st.markdown("**专业的AI驱动金融分析系统**")
        
        # 显示配置信息
        self._render_config_info()
    
    def _render_config_info(self):
        """渲染配置信息"""
        current_providers = get_provider_names()
        config_info = ""
        
        if self.default_provider:
            config_info = f"- 默认提供商：{self.default_provider.upper()}\\n"
            if self.default_provider_info:
                config_info += f"- API 地址：{self.default_provider_info['api_base_url']}\\n"
        
        config_info += f"- 可用提供商：{', '.join(current_providers)}\\n"
        config_info += f"- 历史记录：已加载 {len(st.session_state.available_tickers)} 个股票的分析记录"
        
        with st.expander("📊 当前配置", expanded=False):
            st.markdown(config_info)
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.header("🎛️ 控制面板")
            
            # 页面选择
            page = st.selectbox("选择功能", PAGE_OPTIONS)
            
            # 根据页面渲染对应的控制面板
            if page == "🆕 新建分析":
                new_analysis_page.render_sidebar_controls()
            elif page == "📚 历史分析":
                historical_analysis_page.render_sidebar_controls()
            # 系统状态页面无需侧边栏控件
            
            return page
    
    def handle_page_transitions(self, current_page: str):
        """处理页面切换逻辑"""
        # 页面状态管理 - 检测页面切换并重置状态
        if 'current_page' not in st.session_state:
            st.session_state.current_page = current_page
        
        # 如果页面发生切换
        if st.session_state.current_page != current_page:
            if st.session_state.current_page == "📚 历史分析" and current_page == "🆕 新建分析":
                # 从历史分析切换到新建分析，重置分析状态
                state_manager.reset_to_new_analysis_mode()
                
            elif st.session_state.current_page == "🆕 新建分析" and current_page == "📚 历史分析":
                # 从新建分析切换到历史分析
                state_manager.switch_to_historical_mode()
            
            st.session_state.current_page = current_page
    
    def render_main_content(self, page: str):
        """根据选择的页面渲染主内容"""
        if page == "🆕 新建分析":
            new_analysis_page.render_main_content()
        elif page == "📚 历史分析":
            historical_analysis_page.render_main_content()
        elif page == "🤖 系统状态":
            system_status_page.render_main_content()
    
    def run(self):
        """运行应用"""
        # 设置页面配置
        st.set_page_config(**PAGE_CONFIG)
        
        # 添加自定义CSS
        st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
        
        # 渲染应用头部
        self.render_header()
        
        # 渲染侧边栏并获取当前页面
        current_page = self.render_sidebar()
        
        # 处理页面切换
        self.handle_page_transitions(current_page)
        
        # 渲染主内容
        self.render_main_content(current_page)


def main():
    """主函数 - 应用入口点"""
    # 启用全局错误处理
    setup_error_handling(enable_debug=True)
    
    # 创建并运行应用
    app = TradingAgentsApp()
    app.run()


if __name__ == "__main__":
    main()