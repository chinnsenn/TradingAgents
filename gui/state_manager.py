"""
状态管理模块 - 统一管理Streamlit session state
"""
import streamlit as st
import datetime
from typing import Dict, Any, List, Optional


class SessionStateManager:
    """统一的会话状态管理器"""
    
    # 默认代理状态配置
    DEFAULT_AGENT_STATUSES = {
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
    
    # 默认报告部分配置
    DEFAULT_REPORT_SECTIONS = {
        "market_report": None,
        "sentiment_report": None,
        "news_report": None,
        "fundamentals_report": None,
        "investment_plan": None,
        "trader_investment_plan": None,
        "final_trade_decision": None,
    }
    
    def __init__(self):
        self.initialize_all_states()
    
    def initialize_all_states(self):
        """初始化所有会话状态"""
        self._init_basic_states()
        self._init_agent_states()
        self._init_report_states()
        self._init_analysis_params()
        self._init_historical_states()
        self._init_logging_states()
        self._init_ui_states()
    
    def _init_basic_states(self):
        """初始化基础状态"""
        states = {
            'analysis_running': False,
            'analysis_starting': False,
            'analysis_progress': 0.0,
            'current_status': "⏳ 准备开始分析...",
            'stop_analysis': False,
        }
        self._set_defaults(states)
    
    def _init_agent_states(self):
        """初始化代理状态"""
        if 'agent_statuses' not in st.session_state:
            st.session_state.agent_statuses = self.DEFAULT_AGENT_STATUSES.copy()
    
    def _init_report_states(self):
        """初始化报告状态"""
        if 'report_sections' not in st.session_state:
            st.session_state.report_sections = self.DEFAULT_REPORT_SECTIONS.copy()
    
    def _init_analysis_params(self):
        """初始化分析参数"""
        states = {
            'current_ticker': None,
            'current_date': None,
        }
        self._set_defaults(states)
    
    def _init_historical_states(self):
        """初始化历史数据状态"""
        states = {
            'available_tickers': [],
            'historical_analysis': {},
            'historical_ticker': None,
            'historical_date': None,
            'is_viewing_historical': False,
        }
        self._set_defaults(states)
        
        # 历史报告状态（与当前分析分离）
        if 'historical_report_sections' not in st.session_state:
            st.session_state.historical_report_sections = self.DEFAULT_REPORT_SECTIONS.copy()
    
    def _init_logging_states(self):
        """初始化日志状态"""
        states = {
            'api_logs': [],
            'show_logs': True,
            'max_log_entries': 100,
        }
        self._set_defaults(states)
    
    def _init_ui_states(self):
        """初始化UI状态"""
        states = {
            'last_step_info': "",
            'analysis_trigger': False,
            'ui_needs_refresh': False,
            'status_needs_refresh': False,
            'completion_needs_refresh': False,
        }
        self._set_defaults(states)
    
    def _set_defaults(self, states: Dict[str, Any]):
        """设置默认状态值"""
        for key, default_value in states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def reset_analysis_state(self):
        """重置分析状态"""
        self.set_analysis_progress(0.0)
        self.set_current_status("⏳ 准备开始分析...")
        self.set_analysis_running(False)
        self.set_analysis_starting(False)
        self.set_stop_analysis(False)
        st.session_state.is_viewing_historical = False
        
        # 清除执行相关标志
        self.clear_execution_flags()
        
        # 重置代理状态
        for agent in st.session_state.agent_statuses:
            st.session_state.agent_statuses[agent] = "等待中"
        
        # 清空当前分析报告
        self.clear_all_reports()
        
        # 清空分析参数和日志
        st.session_state.current_ticker = None
        st.session_state.current_date = None
        self.clear_api_logs()
        
        # 清空UI状态
        st.session_state.last_step_info = ""
        st.session_state.ui_needs_refresh = False
        st.session_state.status_needs_refresh = False
        st.session_state.completion_needs_refresh = False
        
        # 清空分析参数
        self.clear_analysis_params()
    
    def reset_to_new_analysis_mode(self):
        """切换到新建分析模式时重置状态"""
        self.reset_analysis_state()
    
    def switch_to_historical_mode(self):
        """切换到历史分析模式"""
        st.session_state.is_viewing_historical = True if st.session_state.historical_ticker else False
    
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
        
        # 在分析过程中不触发UI刷新，避免中断分析
        # UI会通过正常的渲染周期更新
    
    def add_api_log(self, log_type: str, message: str, details: dict = None):
        """添加API日志条目"""
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
    
    def set_analysis_params(self, ticker: str, analysis_date: str):
        """设置分析参数"""
        st.session_state.current_ticker = ticker.upper().strip()
        st.session_state.current_date = analysis_date
    
    def set_historical_analysis_data(self, ticker: str, date: str):
        """设置历史分析数据"""
        st.session_state.historical_ticker = ticker
        st.session_state.historical_date = date
        st.session_state.is_viewing_historical = True
        st.session_state.current_status = f"📚 已加载历史: {ticker} ({date})"
    
    def load_historical_report_sections(self, historical_results: Dict[str, Any]):
        """加载历史报告数据"""
        for key, value in historical_results.items():
            if key in st.session_state.historical_report_sections:
                st.session_state.historical_report_sections[key] = value
    
    def get_analysis_progress(self) -> float:
        """获取分析进度"""
        return st.session_state.analysis_progress
    
    def get_current_status(self) -> str:
        """获取当前状态"""
        return st.session_state.current_status
    
    def is_analysis_running(self) -> bool:
        """检查分析是否正在运行"""
        return st.session_state.analysis_running
    
    def is_analysis_starting(self) -> bool:
        """检查分析是否正在启动"""
        return st.session_state.get('analysis_starting', False)
    
    def get_active_agent(self) -> str:
        """获取当前活跃的代理"""
        return next(
            (agent for agent, status in st.session_state.agent_statuses.items() if status == "进行中"),
            "无"
        )
    
    def get_completed_agents_count(self) -> tuple:
        """获取已完成代理数量"""
        completed = sum(1 for status in st.session_state.agent_statuses.values() if status == "已完成")
        total = len(st.session_state.agent_statuses)
        return completed, total
    
    # === 分析触发器和执行状态管理 ===
    
    def set_analysis_trigger(self, value: bool = True):
        """设置分析触发器"""
        st.session_state.analysis_trigger = value
    
    def clear_analysis_trigger(self):
        """清除分析触发器"""
        st.session_state.analysis_trigger = False
    
    def is_analysis_triggered(self) -> bool:
        """检查分析是否被触发"""
        return st.session_state.get('analysis_trigger', False)
    
    def set_analysis_completed(self, value: bool = True):
        """设置分析完成状态"""
        st.session_state.analysis_completed = value
    
    def set_analysis_failed(self, value: bool = True):
        """设置分析失败状态"""
        st.session_state.analysis_failed = value
    
    def set_analysis_executed(self, value: bool = True):
        """设置分析执行标志"""
        st.session_state.analysis_executed = value
    
    def clear_execution_flags(self):
        """清除执行相关标志"""
        st.session_state.analysis_completed = False
        st.session_state.analysis_failed = False
        st.session_state.analysis_executed = False
    
    # === 进度和状态更新 ===
    
    def set_analysis_progress(self, progress: float):
        """设置分析进度"""
        st.session_state.analysis_progress = max(0.0, min(100.0, progress))
        # 立即更新进度容器
        self._update_progress_container()
    
    def increment_analysis_progress(self, increment: float):
        """增加分析进度"""
        current_progress = st.session_state.analysis_progress
        new_progress = min(100.0, current_progress + increment)
        st.session_state.analysis_progress = new_progress
        # 立即更新进度容器
        self._update_progress_container()
    
    def set_current_status(self, status: str):
        """设置当前状态文本"""
        st.session_state.current_status = status
        # 立即更新相关容器
        self._update_progress_container()
        self._update_agent_container()
    
    def _update_progress_container(self):
        """单独更新进度容器"""
        try:
            if hasattr(st.session_state, 'progress_container') and st.session_state.progress_container:
                st.session_state.progress_container.empty()
                with st.session_state.progress_container.container():
                    from gui.ui_components import ui_components
                    ui_components.render_progress_panel()
        except Exception as e:
            print(f"[DEBUG] 进度容器更新失败: {e}")
    
    def _update_agent_container(self):
        """单独更新代理容器"""
        try:
            if hasattr(st.session_state, 'agent_container') and st.session_state.agent_container:
                st.session_state.agent_container.empty()
                with st.session_state.agent_container.container():
                    from gui.ui_components import ui_components
                    ui_components.render_current_agent_panel()
        except Exception as e:
            print(f"[DEBUG] 代理容器更新失败: {e}")
    
    def set_analysis_running(self, value: bool):
        """设置分析运行状态"""
        st.session_state.analysis_running = value
    
    def set_analysis_starting(self, value: bool):
        """设置分析启动状态"""
        st.session_state.analysis_starting = value
    
    def set_stop_analysis(self, value: bool = True):
        """设置停止分析标志"""
        st.session_state.stop_analysis = value
    
    def set_last_step_info(self, info: str):
        """设置最后步骤信息"""
        st.session_state.last_step_info = info
    
    def clear_analysis_params(self):
        """清空分析参数"""
        st.session_state.analysis_params = {}
    
    # === 报告数据管理 ===
    
    def update_report_section(self, section_key: str, content: Any):
        """更新报告部分"""
        if section_key in st.session_state.report_sections:
            st.session_state.report_sections[section_key] = content
    
    def clear_all_reports(self):
        """清空所有报告"""
        for section in st.session_state.report_sections:
            st.session_state.report_sections[section] = None
    
    def update_historical_data(self, tickers: List[str], analysis_data: Dict[str, Any]):
        """更新历史数据"""
        st.session_state.available_tickers = tickers
        st.session_state.historical_analysis = analysis_data
    
    # === 原子性状态操作 ===
    
    def start_analysis_atomic(self, ticker: str, analysis_date: str):
        """原子性地启动分析（防止竞争条件）"""
        # 清除之前的状态
        self.clear_analysis_trigger()
        self.clear_execution_flags()
        
        # 设置分析参数
        self.set_analysis_params(ticker, analysis_date)
        
        # 设置启动状态
        self.set_analysis_starting(True)
        self.set_analysis_trigger(True)
        self.set_stop_analysis(False)
        self.set_analysis_progress(0.0)
        self.set_current_status("⏳ 正在启动分析系统...")
    
    def transition_to_running(self):
        """从启动状态转换到运行状态"""
        self.set_analysis_starting(False)
        self.set_analysis_running(True)
        self.set_current_status("🔄 分析正在进行中...")
    
    def finalize_analysis_success(self):
        """完成分析（成功）"""
        self.set_analysis_progress(100.0)
        self.set_current_status("✅ 所有分析已完成")
        self.set_analysis_completed(True)
        
        # 标记所有代理为已完成
        for agent in st.session_state.agent_statuses:
            st.session_state.agent_statuses[agent] = "已完成"
        
        # 设置完成刷新标志，确保右侧面板能够更新完成状态
        self.set_completion_needs_refresh(True)
    
    def finalize_analysis_failure(self, error_message: str):
        """完成分析（失败）"""
        self.set_analysis_progress(0.0)
        self.set_current_status(f"❌ 分析失败: {error_message}")
        self.set_analysis_failed(True)
        
        # 设置完成刷新标志，确保错误状态也能及时显示
        self.set_completion_needs_refresh(True)
    
    def cleanup_analysis(self):
        """清理分析资源"""
        self.set_analysis_running(False)
        self.set_analysis_starting(False)
    
    def validate_state_consistency(self) -> bool:
        """验证状态一致性"""
        # 检查基本状态逻辑
        if self.is_analysis_running() and self.is_analysis_starting():
            # 不应该同时处于启动和运行状态
            return False
        
        if self.get_analysis_progress() > 0 and not (self.is_analysis_running() or self.is_analysis_starting()):
            # 有进度但未在运行，可能是异常状态
            return False
        
        return True
    
    # === 智能UI更新机制 ===
    
    def trigger_ui_refresh_if_safe(self):
        """安全地触发UI刷新（只在非分析运行时）"""
        # 只在分析未运行时才触发UI刷新，避免中断分析流程
        if not self.is_analysis_running():
            import streamlit as st
            st.rerun()
    
    def set_analysis_starting_with_refresh(self, value: bool):
        """设置分析启动状态并触发UI刷新"""
        self.set_analysis_starting(value)
        if value:  # 分析启动时需要立即更新UI显示按钮状态
            self.trigger_ui_refresh_if_safe()
    
    def start_analysis_atomic_with_refresh(self, ticker: str, analysis_date: str):
        """原子性地启动分析并触发UI刷新"""
        # 清除之前的状态
        self.clear_analysis_trigger()
        self.clear_execution_flags()
        
        # 设置分析参数
        self.set_analysis_params(ticker, analysis_date)
        
        # 设置启动状态
        self.set_analysis_starting(True)
        self.set_analysis_trigger(True)
        self.set_stop_analysis(False)
        self.set_analysis_progress(0.0)
        self.set_current_status("⏳ 正在启动分析系统...")
        
        # 设置UI刷新标志，让右侧面板也能及时更新
        st.session_state.ui_needs_refresh = True
        
        # 触发UI刷新以立即显示状态变化
        self.trigger_ui_refresh_if_safe()
    
    def stop_analysis_with_refresh(self):
        """停止分析并触发UI刷新"""
        self.set_stop_analysis(True)
        self.set_analysis_running(False)
        self.set_analysis_starting(False)
        self.set_current_status("⏹️ 分析已被用户停止")
        
        # 清除所有刷新标志
        st.session_state.ui_needs_refresh = False
        st.session_state.status_needs_refresh = False
        st.session_state.completion_needs_refresh = False
        
        # 停止后立即刷新UI状态
        self.trigger_ui_refresh_if_safe()
    
    # === 进度更新相关的刷新机制 ===
    
    def set_status_needs_refresh(self, value: bool = True):
        """设置状态面板需要刷新的标志"""
        st.session_state.status_needs_refresh = value
    
    def set_completion_needs_refresh(self, value: bool = True):
        """设置分析完成时需要刷新的标志"""
        st.session_state.completion_needs_refresh = value
    
    def update_agent_status_with_refresh(self, agent_name: str, status: str):
        """更新代理状态并标记需要刷新状态面板"""
        self.update_agent_status(agent_name, status)
        # 设置状态面板刷新标志，用于实时更新右侧面板
        self.set_status_needs_refresh(True)
        # 立即更新动态容器（如果存在）
        self._update_dynamic_containers()
    
    def _update_dynamic_containers(self):
        """立即更新动态容器内容（避免等待st.rerun）"""
        try:
            # 使用时间戳标记避免过于频繁的更新
            import time
            current_time = time.time()
            last_update = getattr(st.session_state, '_last_container_update', 0)
            
            # 限制更新频率（最多每0.5秒更新一次）
            if current_time - last_update < 0.5:
                return
            
            st.session_state._last_container_update = current_time
            
            # 只有在动态容器存在时才更新
            if hasattr(st.session_state, 'progress_container') and st.session_state.progress_container:
                st.session_state.progress_container.empty()
                with st.session_state.progress_container.container():
                    from gui.ui_components import ui_components
                    ui_components.render_progress_panel()
            
            if hasattr(st.session_state, 'agent_container') and st.session_state.agent_container:
                st.session_state.agent_container.empty()
                with st.session_state.agent_container.container():
                    from gui.ui_components import ui_components
                    ui_components.render_current_agent_panel()
            
            if hasattr(st.session_state, 'details_container') and st.session_state.details_container:
                st.session_state.details_container.empty()
                with st.session_state.details_container.container():
                    from gui.ui_components import ui_components
                    ui_components.render_agent_status_details()
            
            if hasattr(st.session_state, 'logs_container') and st.session_state.logs_container:
                st.session_state.logs_container.empty()
                with st.session_state.logs_container.container():
                    from gui.ui_components import ui_components
                    ui_components.render_realtime_logs()
                    
        except Exception as e:
            # 静默处理容器更新错误，避免中断分析流程
            print(f"[DEBUG] 动态容器更新失败: {e}")
    
    def add_api_log_with_container_update(self, log_type: str, message: str, details: dict = None):
        """添加API日志并立即更新日志容器"""
        self.add_api_log(log_type, message, details)
        # 立即更新日志容器
        try:
            if hasattr(st.session_state, 'logs_container') and st.session_state.logs_container:
                st.session_state.logs_container.empty()
                with st.session_state.logs_container.container():
                    from gui.ui_components import ui_components
                    ui_components.render_realtime_logs()
        except Exception as e:
            print(f"[DEBUG] 日志容器更新失败: {e}")


# 全局状态管理器实例
state_manager = SessionStateManager()