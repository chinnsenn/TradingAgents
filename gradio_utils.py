import re
import datetime
from typing import List, Dict, Any, Optional

from config_utils import get_provider_names, get_provider_models, get_default_provider, get_default_model

def validate_ticker(ticker: str) -> bool:
    """Validate ticker symbol format."""
    if not ticker or not isinstance(ticker, str):
        return False
    
    # Remove whitespace and convert to uppercase
    ticker = ticker.strip().upper()
    
    # Check basic format (1-5 letters, optionally followed by numbers)
    if not re.match(r'^[A-Z]{1,5}(?:\d{0,2})?$', ticker):
        return False
    
    # Check for common invalid tickers
    invalid_tickers = {'', 'TEST', 'XXXX', 'NULL'}
    if ticker in invalid_tickers:
        return False
    
    return True

def validate_date(date_input) -> bool:
    """Validate date format (YYYY-MM-DD) or date object."""
    if not date_input:
        return False
    
    try:
        # Handle datetime.datetime objects
        if isinstance(date_input, datetime.datetime):
            # Check if date is not in the future
            today = datetime.date.today()
            return date_input.date() <= today
        
        # Handle datetime.date objects
        if isinstance(date_input, datetime.date):
            # Check if date is not in the future
            today = datetime.date.today()
            return date_input <= today
        
        # Handle string input
        if isinstance(date_input, str):
            # Check format
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_input.strip()):
                return False
            
            # Parse date
            parsed_date = datetime.datetime.strptime(date_input.strip(), '%Y-%m-%d').date()
            
            # Check if date is not in the future
            today = datetime.date.today()
            return parsed_date <= today
        
        return False
        
    except (ValueError, TypeError):
        return False

def get_llm_providers() -> List[str]:
    """Get available LLM providers from configuration."""
    return get_provider_names()


def get_models_for_provider(provider: str) -> List[str]:
    """Get available models for a specific provider from configuration."""
    return get_provider_models(provider)

def format_config_display(config: Dict[str, Any]) -> str:
    """Format configuration for display."""
    display_items = []
    
    # Key configuration items
    key_items = [
        ("LLM Provider", config.get("llm_provider", "N/A")),
        ("Deep Think Model", config.get("deep_think_llm", "N/A")),
        ("Quick Think Model", config.get("quick_think_llm", "N/A")),
        ("Max Debate Rounds", config.get("max_debate_rounds", "N/A")),
        ("Online Tools", "Yes" if config.get("online_tools", False) else "No"),
    ]
    
    for key, value in key_items:
        display_items.append(f"**{key}:** {value}")
    
    return "\n".join(display_items)

def create_download_files(results: Dict[str, Any], ticker: str, date: str) -> tuple[str, str]:
    """Create downloadable files from analysis results."""
    
    # Create JSON content
    json_content = {
        "ticker": ticker,
        "analysis_date": date,
        "timestamp": datetime.datetime.now().isoformat(),
        "results": results
    }
    
    # Create Markdown content
    md_content = f"""# Trading Analysis Report

**Ticker:** {ticker}
**Analysis Date:** {date}
**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
    
    # Add reports if available
    reports = results.get("reports", {})
    
    report_sections = [
        ("market_report", "Market Analysis"),
        ("sentiment_report", "Social Sentiment Analysis"),
        ("news_report", "News Analysis"),
        ("fundamentals_report", "Fundamentals Analysis"),
        ("investment_plan", "Investment Plan"),
        ("trader_investment_plan", "Trader Investment Plan"),
        ("final_trade_decision", "Final Trade Decision")
    ]
    
    for report_key, report_title in report_sections:
        content = reports.get(report_key)
        if content:
            md_content += f"## {report_title}\n\n{content}\n\n---\n\n"
    
    # Add final decision if available
    decision = results.get("decision")
    if decision:
        md_content += f"## Final Trading Decision\n\n{decision}\n\n"
    
    return json_content, md_content

def get_analyst_choices() -> List[str]:
    """Get available analyst types."""
    return [
        "Market Analyst",
        "Social Media Analyst",
        "News Analyst", 
        "Fundamentals Analyst"
    ]

def get_default_analysts() -> List[str]:
    """Get default analyst selection."""
    return get_analyst_choices()

def validate_analyst_selection(selected: List[str]) -> bool:
    """Validate analyst selection."""
    if not selected or not isinstance(selected, list):
        return False
    
    valid_analysts = get_analyst_choices()
    return all(analyst in valid_analysts for analyst in selected)

def get_risk_levels() -> List[str]:
    """Get available risk levels."""
    return ["Conservative", "Moderate", "Aggressive"]

def get_time_horizons() -> List[str]:
    """Get available time horizons."""
    return ["Short-term (1-7 days)", "Medium-term (1-4 weeks)", "Long-term (1-6 months)"]

def format_error_message(error: str) -> str:
    """Format error message for display."""
    return f"❌ **Error:** {error}"

def format_success_message(message: str) -> str:
    """Format success message for display."""
    return f"✅ **Success:** {message}"

def format_info_message(message: str) -> str:
    """Format info message for display."""
    return f"ℹ️ **Info:** {message}"

def format_warning_message(message: str) -> str:
    """Format warning message for display."""
    return f"⚠️ **Warning:** {message}"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for download."""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return sanitized.strip()

def get_example_tickers() -> List[str]:
    """Get example ticker symbols for suggestions."""
    return [
        "AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", 
        "TSLA", "META", "NFLX", "AMD", "INTC"
    ]

def get_date_suggestions() -> List[str]:
    """Get date suggestions for analysis."""
    today = datetime.date.today()
    suggestions = []
    
    # Add recent dates
    for i in range(7):
        date = today - datetime.timedelta(days=i)
        # Skip weekends for stock analysis
        if date.weekday() < 5:
            suggestions.append(date.strftime('%Y-%m-%d'))
    
    return suggestions

def parse_configuration(
    llm_provider: str,
    deep_think_model: str,
    quick_think_model: str,
    max_debate_rounds: int,
    online_tools: bool
) -> Dict[str, Any]:
    """Parse and validate configuration parameters."""
    
    config = {
        "llm_provider": llm_provider,
        "deep_think_llm": deep_think_model,
        "quick_think_llm": quick_think_model,
        "max_debate_rounds": max(1, min(5, int(max_debate_rounds))),
        "online_tools": bool(online_tools)
    }
    
    # Validate provider and models using shared configuration
    available_providers = get_llm_providers()
    if llm_provider not in available_providers:
        config["llm_provider"] = get_default_provider()
    
    provider_models = get_models_for_provider(config["llm_provider"])
    if deep_think_model not in provider_models:
        config["deep_think_llm"] = get_default_model(config["llm_provider"])
    
    if quick_think_model not in provider_models:
        config["quick_think_llm"] = get_default_model(config["llm_provider"])
    
    return config

def get_status_emoji(status: str) -> str:
    """Get emoji for status."""
    status_emojis = {
        "pending": "⏳",
        "running": "🔄", 
        "completed": "✅",
        "error": "❌",
        "cancelled": "⏹️"
    }
    return status_emojis.get(status.lower(), "❓")

def format_progress_message(step: str, progress: float) -> str:
    """Format progress message with emoji and percentage."""
    emoji = "🔄" if progress < 1.0 else "✅"
    percentage = int(progress * 100)
    return f"{emoji} {step} ({percentage}%)"

def get_theme_colors() -> Dict[str, str]:
    """Get theme colors for the interface."""
    return {
        "primary": "#2563eb",
        "secondary": "#64748b", 
        "success": "#16a34a",
        "error": "#dc2626",
        "warning": "#d97706",
        "info": "#0ea5e9"
    }

def parse_and_validate_date(date_input) -> tuple[bool, str, str]:
    """
    Parse and validate date input from various formats.
    
    Returns:
        tuple: (is_valid, date_string, error_message)
    """
    if not date_input:
        return False, "", "请选择一个日期"
    
    try:
        # Handle datetime.datetime objects
        if isinstance(date_input, datetime.datetime):
            date_obj = date_input.date()
        # Handle datetime.date objects
        elif isinstance(date_input, datetime.date):
            date_obj = date_input
        # Handle numeric timestamps
        elif isinstance(date_input, (int, float)):
            dt = datetime.datetime.fromtimestamp(date_input)
            date_obj = dt.date()
        # Handle string inputs
        elif isinstance(date_input, str):
            date_str = date_input.strip()
            if not date_str:
                return False, "", "请选择一个有效的日期"
            
            # Try different date formats
            formats = [
                "%Y-%m-%d",
                "%m/%d/%Y",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f"
            ]
            
            date_obj = None
            for fmt in formats:
                try:
                    if 'T' in date_str and fmt == "%Y-%m-%d":
                        date_str = date_str.split('T')[0]
                    parsed_date = datetime.datetime.strptime(date_str, fmt)
                    date_obj = parsed_date.date()
                    break
                except ValueError:
                    continue
            
            if date_obj is None:
                return False, "", "无效的日期格式，请使用 YYYY-MM-DD 格式"
        else:
            # Try to convert to string and parse
            try:
                date_str = str(date_input)
                if date_str == "None" or not date_str:
                    return False, "", "请选择一个有效的日期"
                parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                date_obj = parsed_date.date()
            except ValueError:
                return False, "", "无效的日期格式，请使用 YYYY-MM-DD 格式"
        
        # Check if date is in the future
        if date_obj > datetime.date.today():
            return False, "", "日期不能是未来的日期"
        
        # Return formatted date string
        return True, date_obj.strftime("%Y-%m-%d"), ""
        
    except Exception as e:
        return False, "", f"日期处理错误: {str(e)}"