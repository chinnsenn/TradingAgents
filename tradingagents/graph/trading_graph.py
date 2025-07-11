# TradingAgents/graph/trading_graph.py

# 标准库导入
import os
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

# 第三方库导入
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode

# 本地模块导入
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

class LoggedChatOpenAI:
    """OpenAI LLM wrapper with comprehensive logging capabilities."""
    
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
        logger = logging.getLogger(__name__)
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
        logging.FileHandler(os.getenv('LOG_FILE', 'tradingagents.log'))
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

    def _get_provider_config(self, provider):
        """Get and validate provider configuration"""
        provider_info = get_provider_info(provider)
        if not provider_info:
            raise ValueError(f"Provider '{provider}' not found in llm_provider.json configuration")
        
        api_base_url = provider_info["api_base_url"]
        api_key = provider_info["api_key"]
        logger.info(f"📡 Using API base URL: {api_base_url}")
        
        # 更新配置
        self.config["backend_url"] = api_base_url
        self.config["api_key"] = api_key
        
        return api_base_url, api_key
    
    def _create_openai_compatible_llms(self, deep_model, quick_model, api_base_url, api_key):
        """Create OpenAI-compatible LLM instances"""
        logger.info(f"🔧 Creating OpenAI-compatible LLMs - Deep: {deep_model}, Quick: {quick_model}")
        
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
    
    def _create_anthropic_llms(self, deep_model, quick_model, api_base_url, api_key):
        """Create Anthropic LLM instances"""
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
    
    def _create_google_llms(self, deep_model, quick_model, api_key):
        """Create Google LLM instances"""
        logger.info(f"🔧 Creating Google LLMs - Deep: {deep_model}, Quick: {quick_model}")
        
        self.deep_thinking_llm = ChatGoogleGenerativeAI(
            model=deep_model,
            google_api_key=api_key
        )
        self.quick_thinking_llm = ChatGoogleGenerativeAI(
            model=quick_model,
            google_api_key=api_key
        )

    def _initialize_llms(self):
        """Initialize LLM instances with dynamic configuration and logging."""
        provider = self.config["llm_provider"]
        deep_model = self.config["deep_think_llm"]
        quick_model = self.config["quick_think_llm"]
        
        logger.info(f"🤖 Initializing LLMs for provider: {provider}")
        
        try:
            # 获取提供商信息
            api_base_url, api_key = self._get_provider_config(provider)

            # 初始化LLM实例
            if provider.lower() in ["openai", "ollama", "openrouter", "onehub", "lmstudio"]:
                self._create_openai_compatible_llms(deep_model, quick_model, api_base_url, api_key)
            elif provider.lower() == "anthropic":
                self._create_anthropic_llms(deep_model, quick_model, api_base_url, api_key)
            elif provider.lower() == "google":
                self._create_google_llms(deep_model, quick_model, api_key)
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

    def _load_state_logging_config(self):
        """Load state logging configuration from JSON file"""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "config", 
            "state_logging.json"
        )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load state logging config: {e}. Using default mapping.")
            return self._get_default_logging_config()

    def _get_default_logging_config(self):
        """Get default logging configuration if config file is unavailable"""
        return {
            "state_mapping": {
                "basic_fields": [
                    "company_of_interest", "trade_date", "market_report", 
                    "sentiment_report", "news_report", "fundamentals_report",
                    "investment_plan", "final_trade_decision"
                ],
                "simple_mappings": {
                    "trader_investment_decision": "trader_investment_plan"
                },
                "nested_mappings": {
                    "investment_debate_state": {
                        "source_key": "investment_debate_state",
                        "fields": ["bull_history", "bear_history", "history", "current_response", "judge_decision"]
                    },
                    "risk_debate_state": {
                        "source_key": "risk_debate_state", 
                        "fields": ["risky_history", "safe_history", "neutral_history", "history", "judge_decision"]
                    }
                }
            },
            "output_config": {
                "directory_template": "eval_results/{ticker}/TradingAgentsStrategy_logs/",
                "filename_template": "full_states_log_{trade_date}.json",
                "indent": 4
            }
        }

    def _build_state_dict(self, final_state, config):
        """Build state dictionary using configuration mapping"""
        result = {}
        mapping = config["state_mapping"]
        
        # Add basic fields
        for field in mapping["basic_fields"]:
            if field in final_state:
                result[field] = final_state[field]
        
        # Add simple mappings (field name changes)
        for output_key, source_key in mapping["simple_mappings"].items():
            if source_key in final_state:
                result[output_key] = final_state[source_key]
        
        # Add nested mappings
        for output_key, nested_config in mapping["nested_mappings"].items():
            source_key = nested_config["source_key"]
            if source_key in final_state and final_state[source_key]:
                nested_result = {}
                for field in nested_config["fields"]:
                    if field in final_state[source_key]:
                        nested_result[field] = final_state[source_key][field]
                result[output_key] = nested_result
        
        return result

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file using configurable mapping."""
        config = self._load_state_logging_config()
        
        # Build state dictionary using configuration
        state_dict = self._build_state_dict(final_state, config)
        self.log_states_dict[str(trade_date)] = state_dict
        
        # Save to file using configured paths
        output_config = config["output_config"]
        directory_path = output_config["directory_template"].format(ticker=self.ticker)
        filename = output_config["filename_template"].format(trade_date=trade_date)
        
        directory = Path(directory_path)
        directory.mkdir(parents=True, exist_ok=True)
        
        with open(directory / filename, "w") as f:
            json.dump(self.log_states_dict, f, indent=output_config["indent"])

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
