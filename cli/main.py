from typing import Optional
import datetime
import typer
import os
from pathlib import Path
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.table import Table
from collections import deque
import time
from rich.align import Align
from rich.rule import Rule

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from cli.models import AnalystType
from cli.utils import *

console = Console()

app = typer.Typer(
    name="TradingAgents",
    help="TradingAgents CLI: Multi-Agents LLM Financial Trading Framework",
    add_completion=True,  # Enable shell completion
)


# Create a deque to store recent messages with a maximum length
class MessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # Store the complete final report
        self.agent_status = {
            # Analyst Team
            "Market Analyst": "pending",
            "Social Analyst": "pending",
            "News Analyst": "pending",
            "Fundamentals Analyst": "pending",
            # Research Team
            "Bull Researcher": "pending",
            "Bear Researcher": "pending",
            "Research Manager": "pending",
            # Trading Team
            "Trader": "pending",
            # Risk Management Team
            "Risky Analyst": "pending",
            "Neutral Analyst": "pending",
            "Safe Analyst": "pending",
            # Portfolio Management Team
            "Portfolio Manager": "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # For the panel display, only show the most recently updated section
        latest_section = None
        latest_content = None

        # Find the most recently updated section
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content
               
        if latest_section and latest_content:
            # Format the current section for display
            section_titles = {
                "market_report": "Market Analysis",
                "sentiment_report": "Social Sentiment",
                "news_report": "News Analysis",
                "fundamentals_report": "Fundamentals Analysis",
                "investment_plan": "Research Team Decision",
                "trader_investment_plan": "Trading Team Plan",
                "final_trade_decision": "Portfolio Management Decision",
            }
            self.current_report = (
                f"### {section_titles[latest_section]}\n{latest_content}"
            )

        # Update the final complete report
        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        # Analyst Team Reports
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "sentiment_report",
                "news_report",
                "fundamentals_report",
            ]
        ):
            report_parts.append("## Analyst Team Reports")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### Market Analysis\n{self.report_sections['market_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### Social Sentiment\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### News Analysis\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### Fundamentals Analysis\n{self.report_sections['fundamentals_report']}"
                )

        # Research Team Reports
        if self.report_sections["investment_plan"]:
            report_parts.append("## Research Team Decision")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # Trading Team Reports
        if self.report_sections["trader_investment_plan"]:
            report_parts.append("## Trading Team Plan")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # Portfolio Management Decision
        if self.report_sections["final_trade_decision"]:
            report_parts.append("## Portfolio Management Decision")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


message_buffer = MessageBuffer()


def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def _create_header_panel():
    """Create the header panel"""
    return Panel(
        "[bold green]Welcome to TradingAgents CLI[/bold green]\n"
        "[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
        title="Welcome to TradingAgents",
        border_style="green",
        padding=(1, 2),
        expand=True,
    )

def _format_agent_status(status):
    """Format agent status with appropriate styling"""
    if status == "in_progress":
        return Spinner(
            "dots", text="[blue]in_progress[/blue]", style="bold cyan"
        )
    else:
        status_color = {
            "pending": "yellow",
            "completed": "green",
            "error": "red",
        }.get(status, "white")
        return f"[{status_color}]{status}[/{status_color}]"

def _create_progress_table():
    """Create the progress table with agent statuses"""
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,
        title=None,
        padding=(0, 2),
        expand=True,
    )
    progress_table.add_column("Team", style="cyan", justify="center", width=20)
    progress_table.add_column("Agent", style="green", justify="center", width=20)
    progress_table.add_column("Status", style="yellow", justify="center", width=20)

    # Group agents by team
    teams = {
        "Analyst Team": [
            "Market Analyst",
            "Social Analyst",
            "News Analyst",
            "Fundamentals Analyst",
        ],
        "Research Team": ["Bull Researcher", "Bear Researcher", "Research Manager"],
        "Trading Team": ["Trader"],
        "Risk Management": ["Risky Analyst", "Neutral Analyst", "Safe Analyst"],
        "Portfolio Management": ["Portfolio Manager"],
    }

    for team, agents in teams.items():
        # Add first agent with team name
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        status_cell = _format_agent_status(status)
        progress_table.add_row(team, first_agent, status_cell)

        # Add remaining agents in team
        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            status_cell = _format_agent_status(status)
            progress_table.add_row("", agent, status_cell)

        # Add horizontal line after each team
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    return Panel(progress_table, title="Progress", border_style="cyan", padding=(1, 2))

def _format_message_content(content):
    """Format message content for display"""
    content_str = content
    if isinstance(content, list):
        # Handle list of content blocks (Anthropic format)
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
            else:
                text_parts.append(str(item))
        content_str = ' '.join(text_parts)
    elif not isinstance(content_str, str):
        content_str = str(content)
        
    # Truncate message content if too long
    if len(content_str) > 200:
        content_str = content_str[:197] + "..."
    return content_str

def _create_messages_panel(spinner_text=None):
    """Create the messages panel"""
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,
        box=box.MINIMAL,
        show_lines=True,
        padding=(0, 1),
    )
    messages_table.add_column("Time", style="cyan", width=8, justify="center")
    messages_table.add_column("Type", style="green", width=10, justify="center")
    messages_table.add_column(
        "Content", style="white", no_wrap=False, ratio=1
    )

    # Combine tool calls and messages
    all_messages = []

    # Add tool calls
    for timestamp, tool_name, args in message_buffer.tool_calls:
        # Truncate tool call args if too long
        if isinstance(args, str) and len(args) > 100:
            args = args[:97] + "..."
        all_messages.append((timestamp, "Tool", f"{tool_name}: {args}"))

    # Add regular messages
    for timestamp, msg_type, content in message_buffer.messages:
        content_str = _format_message_content(content)
        all_messages.append((timestamp, msg_type, content_str))

    # Sort by timestamp
    all_messages.sort(key=lambda x: x[0])

    # Get recent messages
    max_messages = 12
    recent_messages = all_messages[-max_messages:]

    # Add messages to table
    for timestamp, msg_type, content in recent_messages:
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    if spinner_text:
        messages_table.add_row("", "Spinner", spinner_text)

    # Add footer if messages were truncated
    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]Showing last {max_messages} of {len(all_messages)} messages[/dim]"
        )

    return Panel(
        messages_table,
        title="Messages & Tools",
        border_style="blue",
        padding=(1, 2),
    )

def _create_analysis_panel():
    """Create the analysis panel"""
    if message_buffer.current_report:
        return Panel(
            Markdown(message_buffer.current_report),
            title="Current Report",
            border_style="green",
            padding=(1, 2),
        )
    else:
        return Panel(
            "[italic]Waiting for analysis report...[/italic]",
            title="Current Report",
            border_style="green",
            padding=(1, 2),
        )

def _create_footer_panel():
    """Create the footer panel with statistics"""
    tool_calls_count = len(message_buffer.tool_calls)
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "Reasoning"
    )
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("Stats", justify="center")
    stats_table.add_row(
        f"Tool Calls: {tool_calls_count} | LLM Calls: {llm_calls_count} | Generated Reports: {reports_count}"
    )

    return Panel(stats_table, border_style="grey50")

def update_display(layout, spinner_text=None):
    """Update the display layout with current data"""
    # Update all panels using helper functions
    layout["header"].update(_create_header_panel())
    layout["progress"].update(_create_progress_table())
    layout["messages"].update(_create_messages_panel(spinner_text))
    layout["analysis"].update(_create_analysis_panel())
    layout["footer"].update(_create_footer_panel())


def get_user_selections():
    """Get all user selections before starting the analysis display."""
    # Display ASCII art welcome message
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # Create welcome box content
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += "[bold green]TradingAgents: Multi-Agents LLM Financial Trading Framework - CLI[/bold green]\n\n"
    welcome_content += "[bold]Workflow Steps:[/bold]\n"
    welcome_content += "I. Analyst Team → II. Research Team → III. Trader → IV. Risk Management → V. Portfolio Management\n\n"
    welcome_content += (
        "[dim]Built by [Tauric Research](https://github.com/TauricResearch)[/dim]"
    )

    # Create and center the welcome box
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title="Welcome to TradingAgents",
        subtitle="Multi-Agents LLM Financial Trading Framework",
    )
    console.print(Align.center(welcome_box))
    console.print()  # Add a blank line after the welcome box

    # Create a boxed questionnaire for each step
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]Default: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # Step 1: Ticker symbol
    console.print(
        create_question_box(
            "Step 1: Ticker Symbol", "Enter the ticker symbol to analyze", os.getenv("DEFAULT_TICKER", "SPY")
        )
    )
    selected_ticker = get_ticker()

    # Step 2: Analysis date
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            "Step 2: Analysis Date",
            "Enter the analysis date (YYYY-MM-DD)",
            default_date,
        )
    )
    analysis_date = get_analysis_date()

    # Step 3: Select analysts
    console.print(
        create_question_box(
            "Step 3: Analysts Team", "Select your LLM analyst agents for the analysis"
        )
    )
    selected_analysts = select_analysts()
    console.print(
        f"[green]Selected analysts:[/green] {', '.join(analyst.value for analyst in selected_analysts)}"
    )

    # Step 4: Research depth
    console.print(
        create_question_box(
            "Step 4: Research Depth", "Select your research depth level"
        )
    )
    selected_research_depth = select_research_depth()

    # Step 5: OpenAI backend
    console.print(
        create_question_box(
            "Step 5: OpenAI backend", "Select which service to talk to"
        )
    )
    selected_llm_provider, backend_url, api_key = select_llm_provider()
    
    # Step 6: Thinking agents
    console.print(
        create_question_box(
            "Step 6: Thinking Agents", "Select your thinking agents for analysis"
        )
    )
    selected_shallow_thinker = select_shallow_thinking_agent(selected_llm_provider)
    selected_deep_thinker = select_deep_thinking_agent(selected_llm_provider)

    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "api_key": api_key,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
    }


def get_ticker():
    """Get ticker symbol from user input with configurable default."""
    return typer.prompt("", default=os.getenv("DEFAULT_TICKER", "SPY"))


def get_analysis_date():
    """Get the analysis date from user input."""
    while True:
        date_str = typer.prompt(
            "", default=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        try:
            # Validate date format and ensure it's not in the future
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                console.print("[red]Error: Analysis date cannot be in the future[/red]")
                continue
            return date_str
        except ValueError:
            console.print(
                "[red]Error: Invalid date format. Please use YYYY-MM-DD[/red]"
            )


class ReportDisplayStrategy:
    """Base strategy for displaying reports"""
    
    def create_panel(self, content, title, border_style="blue"):
        """Create a standardized panel"""
        return Panel(
            Markdown(content),
            title=title,
            border_style=border_style,
            padding=(1, 2),
        )
    
    def create_team_panel(self, reports, team_title, border_style):
        """Create a team panel containing multiple reports"""
        if reports:
            return Panel(
                Columns(reports, equal=True, expand=True),
                title=team_title,
                border_style=border_style,
                padding=(1, 2),
            )
        return None

class AnalystTeamStrategy(ReportDisplayStrategy):
    """Strategy for displaying analyst team reports"""
    
    def display(self, final_state):
        """Display analyst team reports"""
        reports = []
        
        # Define report mappings
        report_mappings = [
            ("market_report", "Market Analyst"),
            ("sentiment_report", "Social Analyst"),
            ("news_report", "News Analyst"),
            ("fundamentals_report", "Fundamentals Analyst"),
        ]
        
        for report_key, title in report_mappings:
            if final_state.get(report_key):
                reports.append(self.create_panel(final_state[report_key], title))
        
        return self.create_team_panel(reports, "I. Analyst Team Reports", "cyan")

class ResearchTeamStrategy(ReportDisplayStrategy):
    """Strategy for displaying research team reports"""
    
    def display(self, final_state):
        """Display research team reports"""
        if not final_state.get("investment_debate_state"):
            return None
            
        reports = []
        debate_state = final_state["investment_debate_state"]
        
        # Define report mappings for research team
        report_mappings = [
            ("bull_history", "Bull Researcher"),
            ("bear_history", "Bear Researcher"),
            ("judge_decision", "Research Manager"),
        ]
        
        for report_key, title in report_mappings:
            if debate_state.get(report_key):
                reports.append(self.create_panel(debate_state[report_key], title))
        
        return self.create_team_panel(reports, "II. Research Team Decision", "magenta")

class TradingTeamStrategy(ReportDisplayStrategy):
    """Strategy for displaying trading team reports"""
    
    def display(self, final_state):
        """Display trading team reports"""
        if final_state.get("trader_investment_plan"):
            inner_panel = self.create_panel(final_state["trader_investment_plan"], "Trader")
            return Panel(
                inner_panel,
                title="III. Trading Team Plan",
                border_style="yellow",
                padding=(1, 2),
            )
        return None

class RiskTeamStrategy(ReportDisplayStrategy):
    """Strategy for displaying risk management team reports"""
    
    def display(self, final_state):
        """Display risk management team reports"""
        if not final_state.get("risk_debate_state"):
            return None
            
        reports = []
        risk_state = final_state["risk_debate_state"]
        
        # Define report mappings for risk team
        report_mappings = [
            ("risky_history", "Aggressive Analyst"),
            ("safe_history", "Conservative Analyst"),
            ("neutral_history", "Neutral Analyst"),
        ]
        
        for report_key, title in report_mappings:
            if risk_state.get(report_key):
                reports.append(self.create_panel(risk_state[report_key], title))
        
        return self.create_team_panel(reports, "IV. Risk Management Team Decision", "red")

class PortfolioManagerStrategy(ReportDisplayStrategy):
    """Strategy for displaying portfolio manager decision"""
    
    def display(self, final_state):
        """Display portfolio manager decision"""
        risk_state = final_state.get("risk_debate_state")
        if risk_state and risk_state.get("judge_decision"):
            inner_panel = self.create_panel(risk_state["judge_decision"], "Portfolio Manager")
            return Panel(
                inner_panel,
                title="V. Portfolio Manager Decision",
                border_style="green",
                padding=(1, 2),
            )
        return None

class ReportDisplayManager:
    """Manager that coordinates different display strategies"""
    
    def __init__(self):
        self.strategies = [
            AnalystTeamStrategy(),
            ResearchTeamStrategy(),
            TradingTeamStrategy(),
            RiskTeamStrategy(),
            PortfolioManagerStrategy(),
        ]
    
    def display_all(self, final_state):
        """Display all reports using appropriate strategies"""
        console.print("\n[bold green]Complete Analysis Report[/bold green]\n")
        
        for strategy in self.strategies:
            panel = strategy.display(final_state)
            if panel:
                console.print(panel)

def display_complete_report(final_state):
    """Display the complete analysis report with team-based panels."""
    display_manager = ReportDisplayManager()
    display_manager.display_all(final_state)


def update_research_team_status(status):
    """Update status for all research team members and trader."""
    research_team = ["Bull Researcher", "Bear Researcher", "Research Manager", "Trader"]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)

def extract_content_string(content):
    """Extract string content from various message formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Handle Anthropic's list format
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    text_parts.append(f"[Tool: {item.get('name', 'unknown')}]")
            else:
                text_parts.append(str(item))
        return ' '.join(text_parts)
    else:
        return str(content)

def _prepare_analysis_config(selections):
    """Prepare configuration for analysis with user selections"""
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]
    config["backend_url"] = selections["backend_url"]
    config["api_key"] = selections["api_key"]
    config["llm_provider"] = selections["llm_provider"].lower()
    return config

def _setup_analysis_directories(config, selections):
    """Create necessary directories for analysis results"""
    results_dir = Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)
    return results_dir, report_dir, log_file

def _create_decorators(log_file, report_dir):
    """Create decorator functions for message logging and report saving"""
    def save_message_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")  # Replace newlines with spaces
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")
        return wrapper
    
    def save_tool_call_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, args = obj.tool_calls[-1]
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [Tool Call] {tool_name}({args_str})\n")
        return wrapper

    def save_report_section_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if section_name in obj.report_sections and obj.report_sections[section_name] is not None:
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w") as f:
                        f.write(content)
        return wrapper
    
    return save_message_decorator, save_tool_call_decorator, save_report_section_decorator

def _setup_message_decorators(message_buffer, log_file, report_dir):
    """Setup decorators for message logging and report saving"""
    save_message_decorator, save_tool_call_decorator, save_report_section_decorator = _create_decorators(log_file, report_dir)
    
    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(message_buffer, "add_tool_call")
    message_buffer.update_report_section = save_report_section_decorator(message_buffer, "update_report_section")

def _initialize_analysis_display(layout, selections):
    """Initialize the display layout and add initial messages"""
    update_display(layout)
    
    # Add initial messages
    message_buffer.add_message("System", f"Selected ticker: {selections['ticker']}")
    message_buffer.add_message(
        "System", f"Analysis date: {selections['analysis_date']}"
    )
    message_buffer.add_message(
        "System",
        f"Selected analysts: {', '.join(analyst.value for analyst in selections['analysts'])}",
    )
    update_display(layout)

    # Reset agent statuses
    for agent in message_buffer.agent_status:
        message_buffer.update_agent_status(agent, "pending")

    # Reset report sections
    for section in message_buffer.report_sections:
        message_buffer.report_sections[section] = None
    message_buffer.current_report = None
    message_buffer.final_report = None

    # Update agent status to in_progress for the first analyst
    first_analyst = f"{selections['analysts'][0].value.capitalize()} Analyst"
    message_buffer.update_agent_status(first_analyst, "in_progress")
    update_display(layout)

    # Create spinner text
    spinner_text = (
        f"Analyzing {selections['ticker']} on {selections['analysis_date']}..."
    )
    update_display(layout, spinner_text)

def _process_analysis_chunk(chunk, layout, selections):
    """Process individual analysis chunk and update displays"""
    if len(chunk["messages"]) > 0:
        # Get the last message from the chunk
        last_message = chunk["messages"][-1]

        # Extract message content and type
        if hasattr(last_message, "content"):
            content = extract_content_string(last_message.content)  # Use the helper function
            msg_type = "Reasoning"
        else:
            content = str(last_message)
            msg_type = "System"

        # Add message to buffer
        message_buffer.add_message(msg_type, content)                

        # If it's a tool call, add it to tool calls
        if hasattr(last_message, "tool_calls"):
            for tool_call in last_message.tool_calls:
                # Handle both dictionary and object tool calls
                if isinstance(tool_call, dict):
                    message_buffer.add_tool_call(
                        tool_call["name"], tool_call["args"]
                    )
                else:
                    message_buffer.add_tool_call(tool_call.name, tool_call.args)

        # Update reports and agent status based on chunk content
        _update_analysis_reports(chunk, selections)

        # Update the display
        update_display(layout)

def _update_analysis_reports(chunk, selections):
    """Update report sections and agent status based on chunk content"""
    # Analyst Team Reports
    if "market_report" in chunk and chunk["market_report"]:
        message_buffer.update_report_section(
            "market_report", chunk["market_report"]
        )
        message_buffer.update_agent_status("Market Analyst", "completed")
        # Set next analyst to in_progress
        if "social" in selections["analysts"]:
            message_buffer.update_agent_status(
                "Social Analyst", "in_progress"
            )

    if "sentiment_report" in chunk and chunk["sentiment_report"]:
        message_buffer.update_report_section(
            "sentiment_report", chunk["sentiment_report"]
        )
        message_buffer.update_agent_status("Social Analyst", "completed")
        # Set next analyst to in_progress
        if "news" in selections["analysts"]:
            message_buffer.update_agent_status(
                "News Analyst", "in_progress"
            )

    if "news_report" in chunk and chunk["news_report"]:
        message_buffer.update_report_section(
            "news_report", chunk["news_report"]
        )
        message_buffer.update_agent_status("News Analyst", "completed")
        # Set next analyst to in_progress
        if "fundamentals" in selections["analysts"]:
            message_buffer.update_agent_status(
                "Fundamentals Analyst", "in_progress"
            )

    if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
        message_buffer.update_report_section(
            "fundamentals_report", chunk["fundamentals_report"]
        )
        message_buffer.update_agent_status(
            "Fundamentals Analyst", "completed"
        )
        # Set all research team members to in_progress
        update_research_team_status("in_progress")

    # Handle research and risk team debates
    _handle_debate_states(chunk)

def _handle_debate_states(chunk):
    """Handle investment and risk debate states"""
    # Research Team - Handle Investment Debate State
    if (
        "investment_debate_state" in chunk
        and chunk["investment_debate_state"]
    ):
        debate_state = chunk["investment_debate_state"]
        _handle_investment_debate(debate_state)

    # Trading Team
    if (
        "trader_investment_plan" in chunk
        and chunk["trader_investment_plan"]
    ):
        message_buffer.update_report_section(
            "trader_investment_plan", chunk["trader_investment_plan"]
        )
        # Set first risk analyst to in_progress
        message_buffer.update_agent_status("Risky Analyst", "in_progress")

    # Risk Management Team - Handle Risk Debate State
    if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
        risk_state = chunk["risk_debate_state"]
        _handle_risk_debate(risk_state)

def _handle_investment_debate(debate_state):
    """Handle investment debate state updates"""
    # Update Bull Researcher status and report
    if "bull_history" in debate_state and debate_state["bull_history"]:
        # Keep all research team members in progress
        update_research_team_status("in_progress")
        # Extract latest bull response
        bull_responses = debate_state["bull_history"].split("\n")
        latest_bull = bull_responses[-1] if bull_responses else ""
        if latest_bull:
            message_buffer.add_message("Reasoning", latest_bull)
            # Update research report with bull's latest analysis
            message_buffer.update_report_section(
                "investment_plan",
                f"### Bull Researcher Analysis\n{latest_bull}",
            )

    # Update Bear Researcher status and report
    if "bear_history" in debate_state and debate_state["bear_history"]:
        # Keep all research team members in progress
        update_research_team_status("in_progress")
        # Extract latest bear response
        bear_responses = debate_state["bear_history"].split("\n")
        latest_bear = bear_responses[-1] if bear_responses else ""
        if latest_bear:
            message_buffer.add_message("Reasoning", latest_bear)
            # Update research report with bear's latest analysis
            message_buffer.update_report_section(
                "investment_plan",
                f"{message_buffer.report_sections['investment_plan']}\n\n### Bear Researcher Analysis\n{latest_bear}",
            )

    # Update Research Manager status and final decision
    if (
        "judge_decision" in debate_state
        and debate_state["judge_decision"]
    ):
        # Keep all research team members in progress until final decision
        update_research_team_status("in_progress")
        message_buffer.add_message(
            "Reasoning",
            f"Research Manager: {debate_state['judge_decision']}",
        )
        # Update research report with final decision
        message_buffer.update_report_section(
            "investment_plan",
            f"{message_buffer.report_sections['investment_plan']}\n\n### Research Manager Decision\n{debate_state['judge_decision']}",
        )
        # Mark all research team members as completed
        update_research_team_status("completed")
        # Set first risk analyst to in_progress
        message_buffer.update_agent_status(
            "Risky Analyst", "in_progress"
        )

def _handle_risk_debate(risk_state):
    """Handle risk debate state updates"""
    # Update Risky Analyst status and report
    if (
        "current_risky_response" in risk_state
        and risk_state["current_risky_response"]
    ):
        message_buffer.update_agent_status(
            "Risky Analyst", "in_progress"
        )
        message_buffer.add_message(
            "Reasoning",
            f"Risky Analyst: {risk_state['current_risky_response']}",
        )
        # Update risk report with risky analyst's latest analysis only
        message_buffer.update_report_section(
            "final_trade_decision",
            f"### Risky Analyst Analysis\n{risk_state['current_risky_response']}",
        )

    # Update Safe Analyst status and report
    if (
        "current_safe_response" in risk_state
        and risk_state["current_safe_response"]
    ):
        message_buffer.update_agent_status(
            "Safe Analyst", "in_progress"
        )
        message_buffer.add_message(
            "Reasoning",
            f"Safe Analyst: {risk_state['current_safe_response']}",
        )
        # Update risk report with safe analyst's latest analysis only
        message_buffer.update_report_section(
            "final_trade_decision",
            f"### Safe Analyst Analysis\n{risk_state['current_safe_response']}",
        )

    # Update Neutral Analyst status and report
    if (
        "current_neutral_response" in risk_state
        and risk_state["current_neutral_response"]
    ):
        message_buffer.update_agent_status(
            "Neutral Analyst", "in_progress"
        )
        message_buffer.add_message(
            "Reasoning",
            f"Neutral Analyst: {risk_state['current_neutral_response']}",
        )
        # Update risk report with neutral analyst's latest analysis only
        message_buffer.update_report_section(
            "final_trade_decision",
            f"### Neutral Analyst Analysis\n{risk_state['current_neutral_response']}",
        )

    # Check if this is the final decision from portfolio manager
    if "judge_decision" in risk_state and risk_state["judge_decision"]:
        message_buffer.update_agent_status(
            "Portfolio Manager", "in_progress"
        )
        message_buffer.add_message(
            "Reasoning",
            f"Portfolio Manager: {risk_state['judge_decision']}",
        )
        # Update risk report with final decision only
        message_buffer.update_report_section(
            "final_trade_decision",
            f"### Portfolio Manager Decision\n{risk_state['judge_decision']}",
        )
        # Mark risk analysts as completed
        message_buffer.update_agent_status("Risky Analyst", "completed")
        message_buffer.update_agent_status("Safe Analyst", "completed")
        message_buffer.update_agent_status(
            "Neutral Analyst", "completed"
        )
        message_buffer.update_agent_status(
            "Portfolio Manager", "completed"
        )

def _finalize_analysis(graph, trace, selections, layout):
    """Finalize analysis and display final results"""
    # Get final state and decision
    final_state = trace[-1]
    decision = graph.process_signal(final_state["final_trade_decision"])

    # Update all agent statuses to completed
    for agent in message_buffer.agent_status:
        message_buffer.update_agent_status(agent, "completed")

    message_buffer.add_message(
        "Analysis", f"Completed analysis for {selections['analysis_date']}"
    )

    # Update final report sections
    for section in message_buffer.report_sections.keys():
        if section in final_state:
            message_buffer.update_report_section(section, final_state[section])

    # Display the complete final report
    display_complete_report(final_state)

    update_display(layout)

def run_analysis():
    """Run the complete trading analysis workflow"""
    # First get all user selections
    selections = get_user_selections()

    # Create config with selected research depth
    config = _prepare_analysis_config(selections)

    # Initialize the graph
    graph = TradingAgentsGraph(
        [analyst.value for analyst in selections["analysts"]], config=config, debug=True
    )

    # Create result directory
    results_dir, report_dir, log_file = _setup_analysis_directories(config, selections)

    # Setup message decorators
    _setup_message_decorators(message_buffer, log_file, report_dir)

    # Now start the display layout
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        # Initialize display
        _initialize_analysis_display(layout, selections)

        # Initialize state and get graph args
        init_agent_state = graph.propagator.create_initial_state(
            selections["ticker"], selections["analysis_date"]
        )
        args = graph.propagator.get_graph_args()

        # Stream the analysis
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            _process_analysis_chunk(chunk, layout, selections)
            trace.append(chunk)

        # Finalize analysis
        _finalize_analysis(graph, trace, selections, layout)


@app.command()
def analyze():
    run_analysis()


if __name__ == "__main__":
    app()
