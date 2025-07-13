"""
GUI配置模块 - 集中管理UI相关的配置常量
"""

# 页面配置
PAGE_CONFIG = {
    "page_title": "TradingAgents - 多代理LLM金融交易框架",
    "page_icon": "🚀",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 页面选项
PAGE_OPTIONS = [
    "🆕 新建分析", 
    "📚 历史分析", 
    "🤖 系统状态"
]

# CSS样式
CUSTOM_CSS = """
<style>
/* 右侧状态面板样式 */
.stColumns > div:last-child {
    padding-left: 1rem;
    border-left: 2px solid #f0f2f6;
    z-index: 1000;
    position: relative;
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

/* 防止spinner遮挡右侧面板 */
.stSpinner {
    z-index: 999;
}

/* 确保状态面板始终可见 */
.status-panel {
    z-index: 1001 !important;
    position: relative;
    background: white;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 分析进行中时的样式调整 */
.analysis-running .stColumns > div:last-child {
    pointer-events: auto !important;
    opacity: 1 !important;
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

/* 禁用整个页面的spinner遮罩 */
.stApp > div > div > div > div > div:first-child {
    pointer-events: auto !important;
}
</style>
"""

# 默认股票代码
DEFAULT_TICKER = "SPY"

# 研究深度范围
RESEARCH_DEPTH_RANGE = {
    "min_value": 1,
    "max_value": 5,
    "default": 2,
    "step": 1
}

# 日志相关配置
LOG_CONFIG = {
    "max_entries": 100,
    "display_limit": 50
}

# 进度相关配置
PROGRESS_CONFIG = {
    "total_expected_steps": 50,
    "ui_update_interval": 1.0,  # 秒
    "progress_log_interval": 10  # 每N步记录一次进度
}

# 错误处理建议
ERROR_SOLUTIONS = [
    "1. 检查网络连接",
    "2. 验证LLM API密钥配置", 
    "3. 确认`llm_provider.json`文件格式正确",
    "4. 检查股票代码是否有效",
    "5. 尝试使用较少的分析师或较低的研究深度",
    "6. 查看终端控制台获取完整错误堆栈信息"
]

# 状态文本配置
STATUS_MESSAGES = {
    "ready": "⏳ 准备开始分析...",
    "completed": "✅ 所有分析已完成",
    "waiting": "⏸️ 等待下一个分析步骤...",
    "starting": "⏳ 正在启动分析系统...",
    "running": "🔄 正在进行分析...",
    "stopped": "⏹️ 分析已被用户停止",
    "idle": "✅ 系统空闲"
}

# 按钮文本配置
BUTTON_TEXTS = {
    "start_analysis": "🚀 开始分析",
    "analysis_running": "🔄 分析进行中...",
    "analysis_starting": "⏳ 正在启动...",
    "stop_analysis": "⏹️ 停止分析",
    "force_stop": "⏹️ 强制停止分析",
    "refresh_data": "🔄 刷新历史数据",
    "clear_analysis": "🗑️ 清空当前分析",
    "export_status": "💾 导出当前状态",
    "load_historical": "📖 加载历史分析",
    "clear_logs": "🗑️ 清空日志"
}

# 指标标签配置
METRIC_LABELS = {
    "analysis_progress": "分析进度",
    "completed_agents": "已完成代理", 
    "generated_reports": "生成报告",
    "loaded_reports": "加载报告",
    "total_content": "总内容",
    "analysis_stock": "分析股票",
    "stock_code": "股票代码",
    "analysis_date": "分析日期",
    "stock_count": "股票数量",
    "total_analyses": "总分析记录",
    "avg_analyses": "平均记录数"
}

# 帮助文本配置
HELP_TEXTS = {
    "no_analysis": "👈 请在左侧控制面板中配置分析参数并开始分析",
    "starting_analysis": "🚀 系统正在准备分析环境，这可能需要几秒钟时间",
    "results_placeholder": "📊 分析结果将在分析完成后显示在此处",
    "no_historical": "👈 请在左侧控制面板中选择要查看的历史分析记录",
    "no_historical_data": "暂无历史分析数据",
    "no_logs": "暂无日志记录",
    "no_analyses": "暂无分析记录"
}

# 创建历史数据说明
HISTORICAL_DATA_GUIDE = """
**如何创建历史分析数据：**
1. 切换到「🆕 新建分析」页面
2. 配置分析参数并运行分析
3. 分析完成后会自动保存到历史记录
"""

# 导出文件名模板
EXPORT_FILENAME_TEMPLATE = "trading_agents_status_{timestamp}.json"