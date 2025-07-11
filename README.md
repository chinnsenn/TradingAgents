# 🔔 本项目为 Fork 项目 | This is a Fork Project

<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>
---

# TradingAgents: Multi-Agents LLM Financial Trading Framework 

> 🎉 **TradingAgents** officially released! We have received numerous inquiries about the work, and we would like to express our thanks for the enthusiasm in our community.
>
> So we decided to fully open-source the framework. Looking forward to building impactful projects with you!

📖 **[中文文档](README_cn.md) | [English Documentation](README.md)**

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

<div align="center">

🚀 [TradingAgents](#tradingagents-framework) | ⚡ [Installation & Usage](#installation-and-usage) | 🎬 [Demo](https://www.youtube.com/watch?v=90gr5lwjIho) | 🖥️ [GUI Interface](#1-graphical-user-interface-gui) | 📦 [Package Usage](#tradingagents-package) | 🤝 [Contributing](#contributing) | 📄 [Citation](#citation)

</div>

## TradingAgents Framework

TradingAgents is a multi-agent trading framework that mirrors the dynamics of real-world trading firms. By deploying specialized LLM-powered agents: from fundamental analysts, sentiment experts, and technical analysts, to trader, risk management team, the platform collaboratively evaluates market conditions and informs trading decisions. Moreover, these agents engage in dynamic discussions to pinpoint the optimal strategy.

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents framework is designed for research purposes. Trading performance may vary based on many factors, including the chosen backbone language models, model temperature, trading periods, the quality of data, and other non-deterministic factors. [It is not intended as financial, investment, or trading advice.](https://tauric.ai/disclaimer/)

Our framework decomposes complex trading tasks into specialized roles. This ensures the system achieves a robust, scalable approach to market analysis and decision-making.

### Analyst Team
- Fundamentals Analyst: Evaluates company financials and performance metrics, identifying intrinsic values and potential red flags.
- Sentiment Analyst: Analyzes social media and public sentiment using sentiment scoring algorithms to gauge short-term market mood.
- News Analyst: Monitors global news and macroeconomic indicators, interpreting the impact of events on market conditions.
- Technical Analyst: Utilizes technical indicators (like MACD and RSI) to detect trading patterns and forecast price movements.

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Researcher Team
- Comprises both bullish and bearish researchers who critically assess the insights provided by the Analyst Team. Through structured debates, they balance potential gains against inherent risks.

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Trader Agent
- Composes reports from the analysts and researchers to make informed trading decisions. It determines the timing and magnitude of trades based on comprehensive market insights.

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Risk Management and Portfolio Manager
- Continuously evaluates portfolio risk by assessing market volatility, liquidity, and other risk factors. The risk management team evaluates and adjusts trading strategies, providing assessment reports to the Portfolio Manager for final decision.
- The Portfolio Manager approves/rejects the transaction proposal. If approved, the order will be sent to the simulated exchange and executed.

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## Installation and Usage

### Installation

Clone TradingAgents:
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

Create a virtual environment in any of your favorite environment managers:
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

#### Environment Variables

You can configure your API keys using environment variables or a `.env` file:

Create a `.env` file in the root directory (use `.env.example` as a template):
```bash
# FinnHub API for financial data (free tier supported)
FINNHUB_API_KEY=your_finnhub_api_key
```

Or set it directly as environment variable:
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
```

#### LLM Provider Configuration

TradingAgents uses a JSON configuration file to manage LLM providers. The `llm_provider.json` file is **required** and serves as the single source of truth for all LLM provider settings.

**Create the `llm_provider.json` file from the example template:**

```bash
cp llm_provider.json.example llm_provider.json
```

Then edit the file to add your API keys and configure your preferred models:

```json
{
  "Providers": [
    {
      "name": "openrouter",
      "api_base_url": "https://openrouter.ai/api/v1/chat/completions",
      "api_key": "sk-xxx",
      "models": [
        "google/gemini-2.5-pro-preview",
        "anthropic/claude-sonnet-4",
        "anthropic/claude-3.5-sonnet"
      ]
    },
    {
      "name": "deepseek",
      "api_base_url": "https://api.deepseek.com/chat/completions",
      "api_key": "sk-xxx",
      "models": ["deepseek-chat", "deepseek-reasoner"]
    },
    {
      "name": "ollama",
      "api_base_url": "http://localhost:11434/v1/chat/completions",
      "api_key": "ollama",
      "models": ["qwen2.5-coder:latest"]
    }
  ]
}
```

**Configuration Behavior:**
- **Default Selection**: The system automatically uses the **first provider** and **first model** from the JSON file as defaults
- **GUI Integration**: The Gradio interface loads provider and model options directly from this file
- **CLI Integration**: The command-line interface uses the same configuration source
- **No Fallbacks**: If the file is missing or invalid, the system will **not start** and will display a clear error message

**Important Notes:**
- The `llm_provider.json` file is **required** for the system to function
- All interfaces (GUI, CLI, Python package) use this single configuration source
- No environment variables or hardcoded defaults are used for LLM provider configuration
- The first provider in the array becomes the default selection
- The first model in each provider's model list becomes the default for that provider

**Supported LLM providers include:**
- **OpenAI**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, O1 series
- **Anthropic**: Claude models (via OpenRouter)
- **DeepSeek**: DeepSeek Chat, DeepSeek Reasoner
- **Google**: Gemini models
- **Local Models**: Via Ollama, LM Studio, or other OpenAI-compatible APIs
- **Custom Providers**: Any OpenAI-compatible API endpoint

### Usage Options

TradingAgents offers multiple interfaces to suit different user preferences:

#### 1. Graphical User Interface (GUI)

Launch the modern Gradio-based web interface:
```bash
python launch_gradio.py
```

The GUI provides:
- Interactive stock analysis with real-time updates
- Historical analysis records and result management
- Progress tracking with visual indicators
- Formatted reports with syntax highlighting
- Multi-language support (English/Chinese)
- **Automatic LLM configuration**: Defaults to the first provider and model from `llm_provider.json`

#### 2. Command Line Interface (CLI)

For command-line enthusiasts:
```bash
python -m cli.main
```

You will see a screen where you can select your desired tickers, date, LLMs, research depth, etc.

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

An interface will appear showing results as they load, letting you track the agent's progress as it runs.

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

#### 3. Python Package Usage

To use TradingAgents inside your code, you can import the `tradingagents` module and initialize a `TradingAgentsGraph()` object. The `.propagate()` function will return a decision. You can run `main.py`, here's also a quick example:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

You can also adjust the default configuration to set your own choice of LLMs, debate rounds, etc.

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["quick_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True # Use online tools or cached data

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

> For `online_tools`, we recommend enabling them for experimentation, as they provide access to real-time data. The agents' offline tools rely on cached data from our **Tauric TradingDB**, a curated dataset we use for backtesting. We're currently in the process of refining this dataset, and we plan to release it soon alongside our upcoming projects. Stay tuned!

You can view the full list of configurations in `tradingagents/default_config.py`.

**Note**: LLM provider configuration is managed exclusively through the `llm_provider.json` file.

### Quick Start Guide

1. **Clone the repository**: `git clone https://github.com/TauricResearch/TradingAgents.git`
2. **Install dependencies**: `pip install -r requirements.txt`  
3. **Set up environment**: Add `FINNHUB_API_KEY` to `.env` file
4. **Configure LLM providers**: Copy and edit the example file: `cp llm_provider.json.example llm_provider.json`
5. **Launch interface**: 
   - GUI: `python launch_gradio.py`
   - CLI: `python -m cli.main`
   - Python: Import and use `TradingAgentsGraph`

**The system will automatically use the first provider and model from your JSON configuration as defaults.**

## TradingAgents Package

### Implementation Details

We built TradingAgents with LangGraph to ensure flexibility and modularity. We utilize `o1-preview` and `gpt-4o` as our deep thinking and fast thinking LLMs for our experiments. However, for testing purposes, we recommend you use `o4-mini` and `gpt-4.1-mini` to save on costs as our framework makes **lots of** API calls.

### Features

- **Unified Configuration**: Single JSON file (`llm_provider.json`) for all LLM provider settings
- **Smart Defaults**: Automatically selects first provider and model from configuration as defaults
- **Multi-Interface Support**: Choose between GUI, CLI, or Python package integration
- **Environment Configuration**: Flexible API key management via `.env` files or environment variables (for data sources only)
- **Real-time Analysis**: Live market data processing with progress tracking
- **Historical Records**: Analysis result storage and retrieval system
- **Multi-language Support**: English and Chinese language interfaces
- **Customizable Configuration**: Adjustable LLM models, debate rounds, and analysis depth
- **Report Formatting**: Syntax-highlighted analysis reports with structured output
- **Error Prevention**: Clear error messages when configuration is missing or invalid

## Contributing

We welcome contributions from the community! Whether it's fixing a bug, improving documentation, or suggesting a new feature, your input helps make this project better. If you are interested in this line of research, please consider joining our open-source financial AI research community [Tauric Research](https://tauric.ai/).

## Citation

Please reference our work if you find *TradingAgents* provides you with some help :)

```
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```
