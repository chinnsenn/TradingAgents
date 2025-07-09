# TradingAgents/graph/trading_graph.py

import os
import logging
from pathlib import Path
import json
from datetime import date, datetime
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.dataflows.interface import set_config
from config_utils import get_provider_info

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tradingagents.log')
    ]
)
logger = logging.getLogger(__name__)


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG.copy()
        
        # 从 llm_provider.json 加载LLM配置
        try:
            from config_utils import get_default_provider, get_default_model
            
            # 如果配置中没有指定LLM设置，从JSON文件加载
            if "llm_provider" not in self.config:
                default_provider = get_default_provider()
                self.config["llm_provider"] = default_provider
                
            if "deep_think_llm" not in self.config:
                self.config["deep_think_llm"] = get_default_model(self.config["llm_provider"])
                
            if "quick_think_llm" not in self.config:
                self.config["quick_think_llm"] = get_default_model(self.config["llm_provider"])
                
        except Exception as e:
            logger.error(f"❌ Failed to load LLM configuration from llm_provider.json: {e}")
            raise RuntimeError("LLM configuration required. Please ensure llm_provider.json exists and is properly configured.")

        logger.info(f"🚀 Initializing TradingAgentsGraph with config: provider={self.config.get('llm_provider')}, "
                   f"deep_model={self.config.get('deep_think_llm')}, quick_model={self.config.get('quick_think_llm')}")

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # Initialize LLMs with dynamic configuration
        self._initialize_llms()
        
        self.toolkit = Toolkit(config=self.config)

        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(selected_analysts)
        
        logger.info("✅ TradingAgentsGraph initialization completed successfully")

    def _initialize_llms(self):
        """Initialize LLM instances with dynamic configuration and logging."""
        provider = self.config["llm_provider"]
        deep_model = self.config["deep_think_llm"]
        quick_model = self.config["quick_think_llm"]
        
        logger.info(f"🤖 Initializing LLMs for provider: {provider}")
        
        try:
            # 获取提供商信息
            provider_info = get_provider_info(provider)
            if not provider_info:
                raise ValueError(f"Provider '{provider}' not found in llm_provider.json configuration")
            
            api_base_url = provider_info["api_base_url"]
            api_key = provider_info["api_key"]
            logger.info(f"📡 Using API base URL: {api_base_url}")
            
            # 更新配置
            self.config["backend_url"] = api_base_url
            self.config["api_key"] = api_key

            # 初始化LLM实例
            if provider.lower() in ["openai", "ollama", "openrouter", "onehub", "lmstudio"]:
                logger.info(f"🔧 Creating OpenAI-compatible LLMs - Deep: {deep_model}, Quick: {quick_model}")
                
                # 创建带日志记录的LLM实例
                self.deep_thinking_llm = self._create_logged_openai_llm(
                    model=deep_model, 
                    base_url=api_base_url,
                    api_key=api_key,
                    llm_type="deep_thinking"
                )
                self.quick_thinking_llm = self._create_logged_openai_llm(
                    model=quick_model, 
                    base_url=api_base_url,
                    api_key=api_key,
                    llm_type="quick_thinking"
                )
                
            elif provider.lower() == "anthropic":
                logger.info(f"🔧 Creating Anthropic LLMs - Deep: {deep_model}, Quick: {quick_model}")
                self.deep_thinking_llm = ChatAnthropic(
                    model=deep_model, 
                    base_url=api_base_url,
                    api_key=api_key
                )
                self.quick_thinking_llm = ChatAnthropic(
                    model=quick_model, 
                    base_url=api_base_url,
                    api_key=api_key
                )
                
            elif provider.lower() == "google":
                logger.info(f"🔧 Creating Google LLMs - Deep: {deep_model}, Quick: {quick_model}")
                self.deep_thinking_llm = ChatGoogleGenerativeAI(
                    model=deep_model,
                    google_api_key=api_key
                )
                self.quick_thinking_llm = ChatGoogleGenerativeAI(
                    model=quick_model,
                    google_api_key=api_key
                )
            else:
                error_msg = f"Unsupported LLM provider: {provider}"
                logger.error(f"❌ {error_msg}")
                raise ValueError(error_msg)
                
            logger.info("✅ LLM initialization completed successfully")
            
        except Exception as e:
            error_msg = f"Failed to initialize LLMs: {str(e)}"
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e

    def _create_logged_openai_llm(self, model: str, base_url: str, api_key: str, llm_type: str):
        """Create OpenAI LLM with logging wrapper."""
        
        class LoggedChatOpenAI:
            def __init__(self, model: str, base_url: str, api_key: str, llm_type: str):
                self.llm_type = llm_type
                self.model = model
                self.base_url = base_url
                self.api_key = api_key
                self._llm = ChatOpenAI(
                    model=model,
                    base_url=base_url,
                    api_key=api_key
                )
                
            def invoke(self, input, config=None, **kwargs):
                """Invoke with logging."""
                start_time = datetime.now()
                logger.info(f"🔄 [{self.llm_type}] LLM调用开始 - 模型: {self.model} | 输入长度: {len(str(input))}")
                
                try:
                    result = self._llm.invoke(input, config, **kwargs)
                    duration = (datetime.now() - start_time).total_seconds()
                    
                    logger.info(f"✅ [{self.llm_type}] LLM调用成功 - "
                              f"耗时: {duration:.2f}s | 输出长度: {len(str(result.content))}")
                    
                    return result
                    
                except Exception as e:
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.error(f"❌ [{self.llm_type}] LLM调用失败 - "
                               f"耗时: {duration:.2f}s | 错误: {str(e)}")
                    raise
                    
            def __getattr__(self, name):
                """Delegate other attributes to the underlying LLM."""
                return getattr(self._llm, name)
        
        return LoggedChatOpenAI(
            model=model,
            base_url=base_url,
            api_key=api_key,
            llm_type=llm_type
        )

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources."""
        return {
            "market": ToolNode(
                [
                    # online tools
                    self.toolkit.get_YFin_data_online,
                    self.toolkit.get_stockstats_indicators_report_online,
                    # offline tools
                    self.toolkit.get_YFin_data,
                    self.toolkit.get_stockstats_indicators_report,
                ]
            ),
            "social": ToolNode(
                [
                    # online tools
                    self.toolkit.get_stock_news_openai,
                    # offline tools
                    self.toolkit.get_reddit_stock_info,
                ]
            ),
            "news": ToolNode(
                [
                    # online tools
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    # offline tools
                    self.toolkit.get_finnhub_news,
                    self.toolkit.get_reddit_news,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # online tools
                    self.toolkit.get_fundamentals_openai,
                    # offline tools
                    self.toolkit.get_finnhub_company_insider_sentiment,
                    self.toolkit.get_finnhub_company_insider_transactions,
                    self.toolkit.get_simfin_balance_sheet,
                    self.toolkit.get_simfin_cashflow,
                    self.toolkit.get_simfin_income_stmt,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """Run the trading agents graph for a company on a specific date."""

        self.ticker = company_name

        # Initialize state
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # Standard mode without tracing
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal)
