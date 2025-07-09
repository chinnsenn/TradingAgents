import gradio as gr
import datetime
import json
import os
import threading
import time
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
    create_download_files
)
from streaming_handler import StreamingHandler

# Global variables for analysis state
analysis_state = {
    "running": False,
    "current_ticker": None,
    "current_date": None,
    "results": {},
    "progress": {},
    "error": None
}

streaming_handler = StreamingHandler()

def start_analysis(
    ticker: str,
    analysis_date: datetime.datetime,
    selected_analysts: List[str],
    llm_provider: str,
    deep_think_model: str,
    quick_think_model: str,
    max_debate_rounds: int,
    online_tools: bool,
    progress=gr.Progress()
) -> Tuple[str, str, str, str, str, str, str, str, str]:
    """Start the trading analysis process."""
    
    global analysis_state
    
    # Debug information
    print(f"DEBUG: Received date: {analysis_date} (type: {type(analysis_date)})")
    
    # Convert date to string format
    if analysis_date is None:
        return "❌ Please select a date", "", "", "", "", "", "", "", ""
    
    try:
        if isinstance(analysis_date, datetime.datetime):
            analysis_date_str = analysis_date.strftime("%Y-%m-%d")
        elif isinstance(analysis_date, datetime.date):
            analysis_date_str = analysis_date.strftime("%Y-%m-%d")
        elif isinstance(analysis_date, (int, float)):
            # Handle timestamp
            dt = datetime.datetime.fromtimestamp(analysis_date)
            analysis_date_str = dt.strftime("%Y-%m-%d")
        elif isinstance(analysis_date, str):
            # Try to parse the string to validate it
            if analysis_date.strip():
                # Check if it's already in correct format
                try:
                    parsed_date = datetime.datetime.strptime(analysis_date.strip(), "%Y-%m-%d")
                    analysis_date_str = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    # Try ISO format (YYYY-MM-DDTHH:MM:SS)
                    try:
                        # Handle various ISO formats
                        date_str = analysis_date.strip()
                        if 'T' in date_str:
                            date_str = date_str.split('T')[0]
                        parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                        analysis_date_str = parsed_date.strftime("%Y-%m-%d")
                    except ValueError:
                        # Try other common formats
                        try:
                            parsed_date = datetime.datetime.strptime(analysis_date.strip(), "%m/%d/%Y")
                            analysis_date_str = parsed_date.strftime("%Y-%m-%d")
                        except ValueError:
                            print(f"DEBUG: Failed to parse date string: '{analysis_date}'")
                            return "❌ Invalid date format. Please use YYYY-MM-DD", "", "", "", "", "", "", "", ""
            else:
                return "❌ Please select a valid date", "", "", "", "", "", "", "", ""
        else:
            # Try to convert to string and parse
            date_str = str(analysis_date)
            print(f"DEBUG: Trying to parse unknown type as string: '{date_str}'")
            if date_str and date_str != "None":
                try:
                    parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    analysis_date_str = parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    return "❌ Invalid date format. Please use YYYY-MM-DD", "", "", "", "", "", "", "", ""
            else:
                return "❌ Please select a valid date", "", "", "", "", "", "", "", ""
    except Exception as e:
        print(f"DEBUG: Date conversion error: {str(e)}")
        return f"❌ Date processing error: {str(e)}", "", "", "", "", "", "", "", ""
    
    print(f"DEBUG: Converted date string: {analysis_date_str}")
    
    # Validate inputs
    if not validate_ticker(ticker):
        return "❌ Invalid ticker symbol", "", "", "", "", "", "", "", ""
    
    # Check if date is in the future
    try:
        parsed_date = datetime.datetime.strptime(analysis_date_str, "%Y-%m-%d").date()
        if parsed_date > datetime.date.today():
            return "❌ Date cannot be in the future", "", "", "", "", "", "", "", ""
    except ValueError:
        return "❌ Invalid date format", "", "", "", "", "", "", "", ""
    
    if analysis_state["running"]:
        return "⚠️ Analysis already in progress", "", "", "", "", "", "", "", ""
    
    # Set up analysis state
    analysis_state["running"] = True
    analysis_state["current_ticker"] = ticker.upper()
    analysis_state["current_date"] = analysis_date_str
    analysis_state["results"] = {}
    analysis_state["progress"] = {}
    analysis_state["error"] = None
    
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
                analysis_state["results"] = {
                    "decision": decision,
                    "reports": streaming_handler.get_all_reports()
                }
                
            except Exception as e:
                analysis_state["error"] = str(e)
                progress(1.0, desc=f"Error: {str(e)}")
            finally:
                analysis_state["running"] = False
        
        # Start analysis thread
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.start()
        
        # Return initial status
        return (
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
        analysis_state["running"] = False
        analysis_state["error"] = str(e)
        return f"❌ Error: {str(e)}", "", "", "", "", "", "", "", ""

def get_analysis_status():
    """Get current analysis status and results."""
    if analysis_state["error"]:
        return f"❌ Error: {analysis_state['error']}"
    
    if not analysis_state["running"]:
        if analysis_state["results"]:
            return f"✅ Analysis complete for {analysis_state['current_ticker']}"
        return "⏸️ Ready to start analysis"
    
    return f"🔄 Analyzing {analysis_state['current_ticker']} on {analysis_state['current_date']}..."

def get_live_updates():
    """Get live updates from streaming handler."""
    updates = streaming_handler.get_latest_updates()
    
    if not updates:
        return "⏳ Waiting for updates..."
    
    return "\n".join([f"[{update['timestamp']}] {update['message']}" for update in updates[-10:]])

def get_agent_status():
    """Get current agent status."""
    status = streaming_handler.get_agent_status()
    
    status_text = "**Agent Status:**\n\n"
    
    # Group agents by team
    teams = {
        "Analyst Team": ["Market Analyst", "Social Analyst", "News Analyst", "Fundamentals Analyst"],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "Portfolio Management": ["Portfolio Manager"]
    }
    
    for team, agents in teams.items():
        status_text += f"**{team}:**\n"
        for agent in agents:
            agent_status = status.get(agent, "pending")
            emoji = {"pending": "⏳", "running": "🔄", "completed": "✅", "error": "❌"}.get(agent_status, "⏳")
            status_text += f"  {emoji} {agent}: {agent_status.title()}\n"
        status_text += "\n"
    
    return status_text

def get_report_content(report_type: str):
    """Get content for a specific report type."""
    if not analysis_state["results"]:
        return "⏳ Analysis not completed yet..."
    
    reports = analysis_state["results"].get("reports", {})
    content = reports.get(report_type, "No content available")
    
    if content:
        return content
    
    return "⏳ Report not generated yet..."

def refresh_status():
    """Refresh all status components."""
    return (
        get_analysis_status(),
        get_live_updates(),
        get_agent_status(),
        get_report_content("market_report"),
        get_report_content("sentiment_report"),
        get_report_content("news_report"),
        get_report_content("fundamentals_report"),
        get_report_content("investment_plan"),
        get_report_content("trader_investment_plan"),
        get_report_content("final_trade_decision")
    )

def create_download_content():
    """Create downloadable content."""
    if not analysis_state["results"]:
        return None, None
    
    # Create JSON download
    json_content = json.dumps(analysis_state["results"], indent=2)
    
    # Create markdown download
    reports = analysis_state["results"].get("reports", {})
    md_content = f"# Trading Analysis Report\n\n"
    md_content += f"**Ticker:** {analysis_state['current_ticker']}\n"
    md_content += f"**Date:** {analysis_state['current_date']}\n\n"
    
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
    
    with gr.Blocks(
        title="TradingAgents GUI", 
        theme=gr.themes.Soft(),
        css=custom_css
    ) as demo:
        gr.Markdown("# 📈 TradingAgents GUI")
        gr.Markdown("Multi-Agent LLM Financial Trading Framework")
        
        with gr.Row():
            # Left column - Configuration
            with gr.Column(scale=1):
                gr.Markdown("## 🔧 Configuration")
                
                # Basic inputs
                ticker_input = gr.Textbox(
                    label="Ticker Symbol",
                    placeholder="e.g., NVDA, AAPL, TSLA",
                    value="NVDA"
                )
                
                date_input = gr.DateTime(
                    label="Analysis Date",
                    value=datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                    include_time=False,
                    timezone=None,
                    info="Select a date for analysis (cannot be in the future)"
                )
                
                # Analyst selection
                analyst_choices = [
                    "Market Analyst",
                    "Social Media Analyst", 
                    "News Analyst",
                    "Fundamentals Analyst"
                ]
                
                selected_analysts = gr.CheckboxGroup(
                    label="Select Analysts",
                    choices=analyst_choices,
                    value=analyst_choices
                )
                
                # LLM Configuration
                gr.Markdown("### 🤖 LLM Configuration")
                
                # Get default provider and model from JSON config
                try:
                    default_provider = get_default_provider()
                    default_model = get_default_model(default_provider)
                except Exception as e:
                    # If JSON config fails, show error
                    gr.Markdown(f"⚠️ **Error loading LLM configuration:** {str(e)}")
                    gr.Markdown("Please ensure `llm_provider.json` exists and is properly configured.")
                    default_provider = ""
                    default_model = ""
                
                llm_provider = gr.Dropdown(
                    label="LLM Provider",
                    choices=get_llm_providers(),
                    value=default_provider
                )
                
                deep_think_model = gr.Dropdown(
                    label="Deep Think Model",
                    choices=get_models_for_provider(default_provider) if default_provider else [],
                    value=default_model
                )
                
                quick_think_model = gr.Dropdown(
                    label="Quick Think Model", 
                    choices=get_models_for_provider(default_provider) if default_provider else [],
                    value=default_model
                )
                
                max_debate_rounds = gr.Slider(
                    label="Max Debate Rounds",
                    minimum=1,
                    maximum=5,
                    value=1,
                    step=1
                )
                
                online_tools = gr.Checkbox(
                    label="Use Online Tools",
                    value=True
                )
                
                # Start button
                start_btn = gr.Button("🚀 Start Analysis", variant="primary", size="lg")
                
                # Status display
                status_display = gr.Textbox(
                    label="Status",
                    value="⏸️ Ready to start analysis",
                    interactive=False
                )
            
            # Right column - Results
            with gr.Column(scale=2):
                gr.Markdown("## 📊 Analysis Results")
                
                with gr.Tabs():
                    # Live tab
                    with gr.Tab("🔴 Live"):
                        live_updates = gr.Textbox(
                            label="Live Updates",
                            value="⏳ Waiting for updates...",
                            lines=10,
                            interactive=False
                        )
                        
                        agent_status = gr.Markdown(
                            value=get_agent_status()
                        )
                        
                        refresh_btn = gr.Button("🔄 Refresh", size="sm")
                        
                        gr.Markdown(
                            "💡 **Tip:** Click refresh to see live updates during analysis",
                            elem_classes="refresh-tip"
                        )
                    
                    # Market Analysis tab
                    with gr.Tab("📈 Market Analysis"):
                        market_report = gr.Markdown(
                            value="⏳ Analysis not started...",
                            height=400
                        )
                    
                    # Social Analysis tab
                    with gr.Tab("💬 Social Analysis"):
                        social_report = gr.Markdown(
                            value="⏳ Analysis not started...",
                            height=400
                        )
                    
                    # News Analysis tab
                    with gr.Tab("📰 News Analysis"):
                        news_report = gr.Markdown(
                            value="⏳ Analysis not started...",
                            height=400
                        )
                    
                    # Fundamentals tab
                    with gr.Tab("📊 Fundamentals"):
                        fundamentals_report = gr.Markdown(
                            value="⏳ Analysis not started...",
                            height=400
                        )
                    
                    # Research tab
                    with gr.Tab("🔍 Research"):
                        research_report = gr.Markdown(
                            value="⏳ Analysis not started...",
                            height=400
                        )
                    
                    # Trading Plan tab
                    with gr.Tab("💼 Trading Plan"):
                        trading_report = gr.Markdown(
                            value="⏳ Analysis not started...",
                            height=400
                        )
                    
                    # Final Decision tab
                    with gr.Tab("🎯 Final Decision"):
                        final_report = gr.Markdown(
                            value="⏳ Analysis not started...",
                            height=400
                        )
                    
                    # Downloads tab
                    with gr.Tab("💾 Downloads"):
                        gr.Markdown("### Download Analysis Results")
                        
                        download_json = gr.DownloadButton(
                            label="📄 Download JSON",
                            value=None,
                            visible=False
                        )
                        
                        download_md = gr.DownloadButton(
                            label="📝 Download Markdown",
                            value=None,
                            visible=False
                        )
        
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
            outputs=[
                status_display,
                live_updates,
                agent_status,
                market_report,
                social_report,
                news_report,
                fundamentals_report,
                research_report,
                trading_report,
                final_report
            ]
        )
        
        # Initial load
        demo.load(
            refresh_status,
            outputs=[
                status_display,
                live_updates,
                agent_status,
                market_report,
                social_report,
                news_report,
                fundamentals_report,
                research_report,
                trading_report,
                final_report
            ]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )