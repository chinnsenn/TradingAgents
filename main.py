from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import os
from datetime import datetime

# Create a custom config
config = DEFAULT_CONFIG.copy()

# Use environment variables or defaults for configuration
config["llm_provider"] = os.getenv("LLM_PROVIDER", "google")
config["backend_url"] = os.getenv("BACKEND_URL", "https://generativelanguage.googleapis.com/v1")
config["deep_think_llm"] = os.getenv("DEEP_THINK_LLM", "gemini-2.0-flash")
config["quick_think_llm"] = os.getenv("QUICK_THINK_LLM", "gemini-2.0-flash")
config["max_debate_rounds"] = int(os.getenv("MAX_DEBATE_ROUNDS", "1"))
config["online_tools"] = os.getenv("ONLINE_TOOLS", "True").lower() == "true"

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# Use environment variables for demonstration ticker and date
demo_ticker = os.getenv("DEMO_TICKER", "NVDA")
demo_date = os.getenv("DEMO_DATE", "2024-05-10")

# forward propagate
_, decision = ta.propagate(demo_ticker, demo_date)
print(f"Trading decision for {demo_ticker} on {demo_date}: {decision}")

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
