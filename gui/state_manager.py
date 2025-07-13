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
        }
        self._set_defaults(states)
    
    def _set_defaults(self, states: Dict[str, Any]):
        """设置默认状态值"""
        for key, default_value in states.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    def reset_analysis_state(self):
        """重置分析状态"""
        st.session_state.analysis_progress = 0.0
        st.session_state.current_status = "⏳ 准备开始分析..."
        st.session_state.analysis_running = False
        st.session_state.analysis_starting = False
        st.session_state.stop_analysis = False
        st.session_state.is_viewing_historical = False
        
        # 重置代理状态
        for agent in st.session_state.agent_statuses:
            st.session_state.agent_statuses[agent] = "等待中"
        
        # 清空当前分析报告
        for section in st.session_state.report_sections:
            st.session_state.report_sections[section] = None
        
        # 清空分析参数和日志
        st.session_state.current_ticker = None
        st.session_state.current_date = None
        st.session_state.api_logs = []
    
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


# 全局状态管理器实例
state_manager = SessionStateManager()