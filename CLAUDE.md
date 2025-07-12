# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM framework for financial trading analysis. It simulates a real-world trading firm with specialized agents (analysts, researchers, traders, risk management) that collaborate to make trading decisions through structured workflows and debates.

## Essential Commands

### Installation & Setup
```bash
# Install dependencies using UV
uv sync

# Or install dependencies manually
uv pip install -e .
```

### Configuration Requirements
- **Required**: Create `llm_provider.json` from example file: `cp llm_provider.json.example llm_provider.json`
- **Optional**: Create `.env` file with `FINNHUB_API_KEY=your_key` for financial data
- The system uses the **first provider and model** from `llm_provider.json` as defaults

### Running the Application
```bash
# GUI Web Interface
python launch_gui.py

# CLI Interface  
python -m cli.main

# Direct Python usage
python main.py
```

### Testing
```bash
# Run Streamlit test
python test_streamlit.py

# No comprehensive test suite currently configured
```

## Architecture Overview

### Core Components

**Graph-based Architecture (`tradingagents/graph/`)**
- `TradingAgentsGraph`: Main orchestrator class using LangGraph
- `trading_graph.py`: Core workflow engine
- `conditional_logic.py`: Decision routing logic
- `propagation.py`: Information flow management
- `reflection.py`: Learning and memory updates

**Agent Types (`tradingagents/agents/`)**
- **Analysts**: `market_analyst.py`, `news_analyst.py`, `fundamentals_analyst.py`, `social_media_analyst.py`
- **Researchers**: `bull_researcher.py`, `bear_researcher.py`
- **Risk Management**: `conservative_debator.py`, `aggressive_debator.py`, `neutral_debator.py`
- **Trader**: `trader.py`
- **Managers**: `research_manager.py`, `risk_manager.py`

**Data Pipeline (`tradingagents/dataflows/`)**
- `yfin_utils.py`: Yahoo Finance integration
- `finnhub_utils.py`: Finnhub API integration
- `googlenews_utils.py`: News data collection
- `reddit_utils.py`: Social media sentiment
- `data_cache/`: Cached financial data

**Interfaces**
- **CLI**: `cli/main.py` - Command-line interface with rich terminal output
- **GUI Web Interface**: `streamlit_app.py`, `launch_gui.py` - Modern web-based interface
- **Package**: Direct import via `TradingAgentsGraph`

### Configuration System

**LLM Configuration (`llm_provider.json`)** - **REQUIRED**
- Single source of truth for all LLM settings
- Supports multiple providers: OpenAI, Anthropic, DeepSeek, Ollama, custom APIs
- System uses first provider/model as defaults
- Loaded via `config_utils.py`

**Default Configuration (`tradingagents/default_config.py`)**
- Base settings for debate rounds, tool usage, directories
- LLM settings loaded dynamically from JSON config
- `online_tools: True` uses live data, `False` uses cached data

### Key Workflows

**Analysis Process**
1. **Data Collection**: Multiple data sources (financial, news, social)
2. **Agent Analysis**: Parallel analysis by specialist agents
3. **Research Debate**: Bull vs bear researchers debate findings
4. **Risk Assessment**: Risk management team evaluates proposals
5. **Trading Decision**: Final trade recommendation with reasoning

**Memory System (`tradingagents/agents/utils/memory.py`)**
- `FinancialSituationMemory`: Stores analysis results and decisions
- Supports reflection and learning from past trading outcomes

## Development Notes

### Project Structure
- Results stored in `results/{TICKER}/{DATE}/` with detailed reports
- Logs written to `tradingagents.log`
- Data cached in `tradingagents/dataflows/data_cache/`

### Key Dependencies
- **LangGraph**: Agent workflow orchestration
- **LangChain**: LLM integrations (OpenAI, Anthropic, Google)
- **Streamlit**: Modern web interface framework
- **Rich/Typer**: CLI interface and formatting
- **yfinance/finnhub**: Financial data sources
- **pandas/numpy**: Data processing

### Important Files
- `tradingagents/graph/trading_graph.py:96`: LLM initialization
- `config_utils.py`: LLM provider configuration loader
- `cli/main.py`: CLI entry point with rich terminal interface
- `streamlit_app.py`: Streamlit web interface with real-time updates
- `launch_gui.py`: Web application launcher
- `main.py`: Simple Python usage example

### Common Issues
- Missing `llm_provider.json` will prevent startup
- API keys for financial data sources are optional but recommended
- Large number of API calls made during analysis - consider using cheaper models for testing