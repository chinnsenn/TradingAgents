"""
TradingAgents GUI应用程序的样式配置
"""

import datetime
from config_utils import get_provider_names, get_default_provider, get_default_model

# Gradio自定义CSS样式
CUSTOM_CSS = """
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
}

.main-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}

.status-panel {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    height: 400px;
    overflow-y: auto;
}

.report-panel {
    background: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
    height: 500px;
    overflow-y: auto;
}

.config-panel {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.agent-status-completed {
    color: #28a745;
    font-weight: bold;
}

.agent-status-running {
    color: #ffc107;
    font-weight: bold;
}

.agent-status-pending {
    color: #6c757d;
}

.analysis-progress {
    background: linear-gradient(90deg, #28a745 0%, #20c997 100%);
    height: 4px;
    border-radius: 2px;
    margin: 1rem 0;
}

.error-message {
    background: #f8d7da;
    color: #721c24;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid #f5c6cb;
}

.success-message {
    background: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid #c3e6cb;
}

.warning-message {
    background: #fff3cd;
    color: #856404;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid #ffeaa7;
}

.info-message {
    background: #d1ecf1;
    color: #0c5460;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid #bee5eb;
}

/* 按钮样式 */
.primary-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.primary-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.stop-button {
    background: linear-gradient(135deg, #ff416c 0%, #ff4757 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.stop-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 65, 108, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
    .gradio-container {
        max-width: 100% !important;
        margin: 0 !important;
        padding: 1rem !important;
    }
    
    .main-header {
        padding: 1rem;
    }
    
    .status-panel, .report-panel {
        height: 300px;
    }
}
"""

# 主题配置
THEME_CONFIG = {
    "primary_hue": "blue",
    "secondary_hue": "gray",
    "neutral_hue": "gray",
    "spacing_size": "md",
    "radius_size": "md",
    "text_size": "md",
    "font": ["system-ui", "Arial", "sans-serif"],
    "font_mono": ["ui-monospace", "Consolas", "monospace"]
}

# 颜色配置
COLOR_SCHEME = {
    "primary": "#667eea",
    "secondary": "#764ba2", 
    "success": "#28a745",
    "warning": "#ffc107",
    "error": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# 图标配置
ICONS = {
    "market": "🏢",
    "social": "💬", 
    "news": "📰",
    "fundamentals": "📊",
    "bull": "🐂",
    "bear": "🐻",
    "trader": "💼",
    "risk": "⚠️",
    "portfolio": "📈",
    "analysis": "🔍",
    "report": "📋",
    "settings": "⚙️",
    "start": "🚀",
    "stop": "⏹️",
    "completed": "🟢",
    "running": "🟡",
    "pending": "⚪",
    "error": "❌",
    "success": "✅",
    "warning": "⚠️",
    "info": "ℹ️"
}

# 状态映射
STATUS_MAPPING = {
    "pending": {"text": "等待中", "color": COLOR_SCHEME["info"], "icon": ICONS["pending"]},
    "running": {"text": "进行中", "color": COLOR_SCHEME["warning"], "icon": ICONS["running"]},
    "completed": {"text": "已完成", "color": COLOR_SCHEME["success"], "icon": ICONS["completed"]},
    "error": {"text": "错误", "color": COLOR_SCHEME["error"], "icon": ICONS["error"]}
}

# 分析师配置
ANALYST_CONFIG = {
    "market": {
        "name": "市场分析师",
        "description": "分析市场趋势和技术指标",
        "icon": ICONS["market"]
    },
    "social": {
        "name": "社交分析师", 
        "description": "分析社交媒体情绪和讨论",
        "icon": ICONS["social"]
    },
    "news": {
        "name": "新闻分析师",
        "description": "分析新闻事件和市场影响",
        "icon": ICONS["news"]
    },
    "fundamentals": {
        "name": "基本面分析师",
        "description": "分析公司财务和基本面数据",
        "icon": ICONS["fundamentals"]
    }
}


def get_default_gui_config():
    """获取动态的默认GUI配置"""
    # 获取默认的提供商和模型
    default_provider = get_default_provider()
    default_deep_model = get_default_model(default_provider) if default_provider else None
    default_quick_model = get_default_model(default_provider) if default_provider else None
    
    return {
        "ticker": "SPY",
        "analysis_date": None,  # 将在运行时设置为当前日期
        "selected_analysts": ["market", "social", "news", "fundamentals"],
        "research_depth": 2,
        "llm_provider": default_provider,
        "deep_model": default_deep_model,
        "quick_model": default_quick_model
    }

def get_default_config():
    """获取默认配置，如果配置文件不可用则返回备用配置"""
    try:
        return get_default_gui_config()
    except Exception:
        # 备用配置，当配置文件不可用时使用
        return {
            "ticker": "SPY",
            "analysis_date": None,
            "selected_analysts": ["market", "social", "news", "fundamentals"],
            "research_depth": 2,
            "llm_provider": None,
            "deep_model": None,
            "quick_model": None
        }

# 默认配置 (动态生成)
# 为了向后兼容，保留 DEFAULT_GUI_CONFIG
DEFAULT_GUI_CONFIG = get_default_config()