import gradio as gr
import datetime
import json
import os
import threading
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from config_utils import get_default_provider, get_default_model
from gradio_utils import (
    validate_ticker,
    validate_date,
    get_llm_providers,
    get_models_for_provider,
    format_config_display,
    create_download_files,
    parse_and_validate_date
)
from streaming_handler import StreamingHandler

# Session state initialization function
def init_session_state():
    """Initialize session state for a new user."""
    return {
        "running": False,
        "current_ticker": None,
        "current_date": None,
        "results": {},
        "progress": {},
        "error": None,
        "streaming_handler": StreamingHandler()
    }

def start_analysis(
    session_state: dict,
    ticker: str,
    analysis_date: datetime.datetime,
    selected_analysts: List[str],
    llm_provider: str,
    deep_think_model: str,
    quick_think_model: str,
    max_debate_rounds: int,
    online_tools: bool,
    progress=gr.Progress()
) -> Tuple[Dict, str, str, str, str, str, str, str, str, str]:
    """Start the trading analysis process."""
    
    # Initialize session state if not provided
    if not session_state:
        session_state = init_session_state()
    
    streaming_handler = session_state["streaming_handler"]
    
    # Validate and process date using optimized function
    is_valid, analysis_date_str, error_msg = parse_and_validate_date(analysis_date)
    if not is_valid:
        return session_state, f"❌ {error_msg}", "", "", "", "", "", "", "", ""
    
    # Validate inputs
    if not validate_ticker(ticker):
        return session_state, "❌ Invalid ticker symbol", "", "", "", "", "", "", "", ""
    
    if session_state["running"]:
        return session_state, "⚠️ Analysis already in progress", "", "", "", "", "", "", "", ""
    
    # Set up analysis state
    session_state["running"] = True
    session_state["current_ticker"] = ticker.upper()
    session_state["current_date"] = analysis_date_str
    session_state["results"] = {}
    session_state["progress"] = {}
    session_state["error"] = None
    
    # Reset streaming handler
    streaming_handler.reset()
    
    try:
        # Create configuration
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = llm_provider
        config["deep_think_llm"] = deep_think_model
        config["quick_think_llm"] = quick_think_model
        config["max_debate_rounds"] = max_debate_rounds
        config["online_tools"] = online_tools
        
        # Initialize TradingAgentsGraph
        ta = TradingAgentsGraph(debug=True, config=config)
        
        # Start analysis in separate thread
        def run_analysis():
            try:
                progress(0.1, desc="Starting analysis...")
                
                # Set up streaming handler callback
                streaming_handler.set_analysis_params(ticker.upper(), analysis_date_str)
                
                progress(0.2, desc="Initializing agents...")
                
                # Run analysis
                _, decision = ta.propagate(ticker.upper(), analysis_date_str)
                
                progress(1.0, desc="Analysis complete!")
                
                # Store results
                session_state["results"] = {
                    "decision": decision,
                    "reports": streaming_handler.get_all_reports()
                }
                
            except Exception as e:
                session_state["error"] = str(e)
                progress(1.0, desc=f"Error: {str(e)}")
            finally:
                session_state["running"] = False
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.start()
        
        # Return initial status
        return (
            session_state,
            f"🚀 Starting analysis for {ticker.upper()} on {analysis_date_str}...",
            "⏳ Initializing...",
            "⏳ Pending...",
            "⏳ Pending...",
            "⏳ Pending...",
            "⏳ Pending...",
            "⏳ Pending...",
            "⏳ Pending...",
            ""
        )
        
    except Exception as e:
        session_state["running"] = False
        session_state["error"] = str(e)
        return session_state, f"❌ Error: {str(e)}", "", "", "", "", "", "", "", ""

def get_analysis_status(session_state: dict):
    """Get current analysis status and results."""
    if session_state["error"]:
        return f"❌ Error: {session_state['error']}"
    
    if not session_state["running"]:
        if session_state["results"]:
            return f"✅ Analysis complete for {session_state['current_ticker']}"
        return "⏸️ Ready to start analysis"
    
    return f"🔄 Analyzing {session_state['current_ticker']} on {session_state['current_date']}..."

def get_live_updates(session_state: dict):
    """Get live updates from streaming handler."""
    streaming_handler = session_state["streaming_handler"]
    updates = streaming_handler.get_latest_updates()
    
    if not updates:
        return "⏳ Waiting for updates..."
    
    return "\n".join([f"[{update['timestamp']}] {update['message']}" for update in updates[-10:]])

def get_agent_status(session_state: dict):
    """Get current agent status using optimized caching."""
    streaming_handler = session_state["streaming_handler"]
    
    if not session_state["running"] and not session_state["results"]:
        return "**代理状态：**\n\n⏸️ 等待开始分析..."
    
    # Use optimized status summary
    status_summary = streaming_handler.get_agent_status_summary()
    
    if status_summary["all_completed"] and session_state["results"]:
        return "**代理状态：**\n\n✅ 所有代理已完成分析\n\n📊 点击下方查看完整报告"
    
    # Show current running agent
    if status_summary["current_agent"]:
        return f"**代理状态：**\n\n🔄 **正在执行:** {status_summary['current_agent']}\n\n⏳ 其他代理等待中..."
    
    # Show progress summary
    completed_count = len(status_summary["completed_agents"])
    total_count = streaming_handler._total_agents
    
    return f"**代理状态：**\n\n📈 进度: {completed_count}/{total_count} 完成\n\n⏳ 分析进行中..."

def get_report_content(session_state: dict, report_type: str):
    """Get content for a specific report type."""
    if not session_state["results"]:
        return "⏳ Analysis not completed yet..."
    
    reports = session_state["results"].get("reports", {})
    content = reports.get(report_type, "No content available")
    
    if content:
        return content
    
    return "⏳ Report not generated yet..."

def refresh_status(session_state: dict):
    """Refresh all status components using optimized caching."""
    # Use optimized status summary to reduce redundant calculations
    streaming_handler = session_state["streaming_handler"]
    status_summary = streaming_handler.get_agent_status_summary()
    
    # If analysis is complete, return with auto-switch indicator
    if status_summary["all_completed"] and session_state["results"]:
        return (
            session_state,
            get_analysis_status(session_state),
            get_live_updates(session_state),
            get_agent_status(session_state),
            get_report_content(session_state, "market_report"),
            get_report_content(session_state, "sentiment_report"),
            get_report_content(session_state, "news_report"),
            get_report_content(session_state, "fundamentals_report"),
            get_report_content(session_state, "investment_plan"),
            get_report_content(session_state, "trader_investment_plan"),
            get_report_content(session_state, "final_trade_decision"),
            gr.Tabs(selected=1)  # Auto-switch to Complete Reports tab
        )
    
    return (
        session_state,
        get_analysis_status(session_state),
        get_live_updates(session_state),
        get_agent_status(session_state),
        get_report_content(session_state, "market_report"),
        get_report_content(session_state, "sentiment_report"),
        get_report_content(session_state, "news_report"),
        get_report_content(session_state, "fundamentals_report"),
        get_report_content(session_state, "investment_plan"),
        get_report_content(session_state, "trader_investment_plan"),
        get_report_content(session_state, "final_trade_decision"),
        gr.Tabs(selected=0)  # Stay on Live Progress tab
    )

def create_download_content(session_state: dict):
    """Create downloadable content."""
    if not session_state["results"]:
        return None, None
    
    # Create JSON download
    json_content = json.dumps(session_state["results"], indent=2)
    
    # Create markdown download
    reports = session_state["results"].get("reports", {})
    md_content = f"# Trading Analysis Report\n\n"
    md_content += f"**Ticker:** {session_state['current_ticker']}\n"
    md_content += f"**Date:** {session_state['current_date']}\n\n"
    
    for report_type, content in reports.items():
        if content:
            md_content += f"## {report_type.replace('_', ' ').title()}\n\n{content}\n\n"
    
    return json_content, md_content

# Create Gradio interface
def create_interface():
    """Create the main Gradio interface."""
    
    # Custom CSS for better styling
    custom_css = """
    .refresh-button {
        margin-right: 10px;
    }
    .status-indicator {
        padding: 5px 10px;
        border-radius: 5px;
        margin: 2px;
        display: inline-block;
    }
    .status-pending { background-color: #fef3c7; color: #92400e; }
    .status-running { background-color: #dbeafe; color: #1e40af; }
    .status-completed { background-color: #d1fae5; color: #065f46; }
    .status-error { background-color: #fee2e2; color: #dc2626; }
    .refresh-tip {
        font-size: 0.9em;
        color: #6b7280;
        margin-top: 10px;
        padding: 8px;
        background-color: #f3f4f6;
        border-radius: 6px;
    }
    """
    
    def create_config_section():
        """Create configuration section with optimized layout."""
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 🔧 配置参数")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        # Basic inputs
                        ticker_input = gr.Textbox(
                            label="股票代码",
                            placeholder="例如: NVDA, AAPL, TSLA",
                            value=os.getenv("DEFAULT_TICKER", "NVDA")
                        )
                        
                        date_input = gr.DateTime(
                            label="分析日期",
                            value=datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                            include_time=False,
                            timezone=None,
                            info="选择分析日期 (不能是未来日期)"
                        )
                        
                        # Analyst selection
                        analyst_choices = [
                            "Market Analyst",
                            "Social Media Analyst", 
                            "News Analyst",
                            "Fundamentals Analyst"
                        ]
                        
                        selected_analysts = gr.CheckboxGroup(
                            label="选择分析师",
                            choices=analyst_choices,
                            value=analyst_choices
                        )
                    
                    with gr.Column(scale=1):
                        # LLM Configuration
                        gr.Markdown("### 🤖 LLM 配置")
                        
                        # Get default provider and model from JSON config
                        try:
                            default_provider = get_default_provider()
                            default_model = get_default_model(default_provider)
                        except Exception as e:
                            # If JSON config fails, show error
                            gr.Markdown(f"⚠️ **LLM配置加载错误:** {str(e)}")
                            gr.Markdown("请确保 `llm_provider.json` 文件存在且配置正确。")
                            default_provider = ""
                            default_model = ""
                        
                        llm_provider = gr.Dropdown(
                            label="LLM 提供商",
                            choices=get_llm_providers(),
                            value=default_provider
                        )
                        
                        deep_think_model = gr.Dropdown(
                            label="深度思考模型",
                            choices=get_models_for_provider(default_provider) if default_provider else [],
                            value=default_model
                        )
                        
                        quick_think_model = gr.Dropdown(
                            label="快速思考模型", 
                            choices=get_models_for_provider(default_provider) if default_provider else [],
                            value=default_model
                        )
                        
                        max_debate_rounds = gr.Slider(
                            label="最大辩论轮数",
                            minimum=1,
                            maximum=5,
                            value=int(os.getenv("DEFAULT_MAX_DEBATE_ROUNDS", "1")),
                            step=1
                        )
                        
                        online_tools = gr.Checkbox(
                            label="使用在线工具",
                            value=os.getenv("DEFAULT_ONLINE_TOOLS", "True").lower() == "true"
                        )
                
                with gr.Row():
                    # Start button
                    start_btn = gr.Button("🚀 开始分析", variant="primary", size="lg")
                    
                    # Status display
                    status_display = gr.Textbox(
                        label="状态",
                        value="⏸️ 准备开始分析",
                        interactive=False,
                        scale=2
                    )
                    
        return (ticker_input, date_input, selected_analysts, llm_provider, 
                deep_think_model, quick_think_model, max_debate_rounds, 
                online_tools, start_btn, status_display)
    
    def create_report_tab(tab_name, report_key):
        """Create a report tab with consistent styling."""
        with gr.Tab(tab_name):
            return gr.Markdown(
                value="⏳ 分析未开始...",
                height=400
            )
    
    def create_progress_section():
        """Create progress monitoring section."""
        with gr.Row():
            with gr.Column():
                gr.Markdown("## 📊 分析进度与结果")
                
                with gr.Tabs() as main_tabs:
                    # Live Progress tab
                    with gr.Tab("🔴 实时进度") as live_tab:
                        with gr.Row():
                            with gr.Column(scale=1):
                                agent_status = gr.Markdown(
                                    value="**代理状态：**\n\n⏸️ 等待开始分析..."
                                )
                                
                                refresh_btn = gr.Button("🔄 刷新状态", size="sm")
                                
                                gr.Markdown(
                                    "💡 **提示:** 点击刷新查看实时分析进度",
                                    elem_classes="refresh-tip"
                                )
                            
                            with gr.Column(scale=2):
                                live_updates = gr.Textbox(
                                    label="实时更新",
                                    value="⏳ 等待更新...",
                                    lines=15,
                                    interactive=False
                                )
                    
                    # Complete Reports tab
                    with gr.Tab("📋 完整报告") as reports_tab:
                        with gr.Tabs():
                            # Create report tabs using the helper function
                            report_tabs_data = [
                                ("📈 市场分析", "market_report"),
                                ("💬 社交分析", "sentiment_report"),
                                ("📰 新闻分析", "news_report"),
                                ("📊 基本面分析", "fundamentals_report"),
                                ("🔍 研究报告", "investment_plan"),
                                ("💼 交易计划", "trader_investment_plan"),
                                ("🎯 最终决策", "final_trade_decision")
                            ]
                            
                            report_components = []
                            for tab_name, report_key in report_tabs_data:
                                report_components.append(create_report_tab(tab_name, report_key))
                            
                            # Downloads tab
                            with gr.Tab("💾 下载"):
                                gr.Markdown("### 下载分析结果")
                                
                                download_json = gr.DownloadButton(
                                    label="📄 下载 JSON",
                                    value=None,
                                    visible=False
                                )
                                
                                download_md = gr.DownloadButton(
                                    label="📝 下载 Markdown",
                                    value=None,
                                    visible=False
                                )
                                
        return (main_tabs, agent_status, refresh_btn, live_updates, 
                *report_components, download_json, download_md)
    
    with gr.Blocks(
        title="TradingAgents GUI", 
        theme=gr.themes.Soft(),
        css=custom_css
    ) as demo:
        # Session state for user isolation
        session_state = gr.State(init_session_state)
        
        gr.Markdown("# 📈 TradingAgents GUI")
        gr.Markdown("Multi-Agent LLM Financial Trading Framework")
        
        # Create sections using helper functions
        config_components = create_config_section()
        progress_components = create_progress_section()
        
        # Unpack components
        (ticker_input, date_input, selected_analysts, llm_provider, 
         deep_think_model, quick_think_model, max_debate_rounds, 
         online_tools, start_btn, status_display) = config_components
        
        (main_tabs, agent_status, refresh_btn, live_updates, 
         market_report, social_report, news_report, fundamentals_report,
         research_report, trading_report, final_report, 
         download_json, download_md) = progress_components
        
        # Event handlers
        def update_models(provider):
            models = get_models_for_provider(provider)
            return gr.Dropdown(choices=models, value=models[0] if models else "")
        
        llm_provider.change(
            update_models,
            inputs=[llm_provider],
            outputs=[deep_think_model, quick_think_model]
        )
        
        start_btn.click(
            start_analysis,
            inputs=[
                session_state,
                ticker_input,
                date_input,
                selected_analysts,
                llm_provider,
                deep_think_model,
                quick_think_model,
                max_debate_rounds,
                online_tools
            ],
            outputs=[
                session_state,
                status_display,
                live_updates,
                market_report,
                social_report,
                news_report,
                fundamentals_report,
                research_report,
                trading_report,
                final_report
            ]
        )
        
        refresh_btn.click(
            refresh_status,
            inputs=[session_state],
            outputs=[
                session_state,
                status_display,
                live_updates,
                agent_status,
                market_report,
                social_report,
                news_report,
                fundamentals_report,
                research_report,
                trading_report,
                final_report,
                main_tabs
            ]
        )
        
        # Initial load
        demo.load(
            refresh_status,
            inputs=[session_state],
            outputs=[
                session_state,
                status_display,
                live_updates,
                agent_status,
                market_report,
                social_report,
                news_report,
                fundamentals_report,
                research_report,
                trading_report,
                final_report,
                main_tabs
            ]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name=os.getenv("SERVER_HOST", "0.0.0.0"),
        server_port=int(os.getenv("SERVER_PORT", "7860")),
        share=os.getenv("SHARE", "False").lower() == "true",
        show_error=True
    )