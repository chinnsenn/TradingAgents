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

# TradingAgents：多智能体 LLM 金融交易框架

> 🎉 **TradingAgents** 正式发布！我们收到了众多关于这项工作的询问，感谢社区的热情支持。
>
> 因此我们决定完全开源这个框架。期待与您一起构建具有影响力的项目！

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

🚀 [TradingAgents框架](#tradingagents-框架) | ⚡ [安装与使用](#安装与使用) | 🎬 [演示视频](https://www.youtube.com/watch?v=90gr5lwjIho) | 🖥️ [图形界面](#1-图形用户界面-gui) | 📦 [包使用方法](#tradingagents-包) | 🤝 [贡献代码](#贡献代码) | 📄 [引用](#引用)

</div>

## TradingAgents 框架

TradingAgents 是一个多智能体交易框架，模拟了真实世界交易公司的动态运作。通过部署专门的 LLM 驱动的智能体：从基本面分析师、情绪专家和技术分析师，到交易员和风险管理团队，该平台协同评估市场状况并为交易决策提供信息。此外，这些智能体还会参与动态讨论以确定最优策略。

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents 框架专为研究目的而设计。交易表现可能会因多种因素而异，包括所选择的骨干语言模型、模型温度、交易周期、数据质量以及其他非确定性因素。[这不是财务、投资或交易建议。](https://tauric.ai/disclaimer/)

我们的框架将复杂的交易任务分解为专门的角色。这确保了系统实现了对市场分析和决策制定的稳健、可扩展的方法。

### 分析师团队

- **基本面分析师**：评估公司财务状况和业绩指标，识别内在价值和潜在风险。
- **情绪分析师**：使用情绪评分算法分析社交媒体和公众情绪，以评估短期市场情绪。
- **新闻分析师**：监控全球新闻和宏观经济指标，解释事件对市场条件的影响。
- **技术分析师**：利用技术指标（如 MACD 和 RSI）检测交易模式并预测价格走势。

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### 研究团队

- 由看涨和看跌研究人员组成，他们批判性地评估分析师团队提供的见解。通过结构化辩论，他们平衡潜在收益与固有风险。

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 交易员智能体

- 综合分析师和研究人员的报告，做出明智的交易决策。它根据全面的市场洞察确定交易的时机和规模。

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### 风险管理和投资组合经理

- 通过评估市场波动性、流动性和其他风险因素，持续评估投资组合风险。风险管理团队评估和调整交易策略，向投资组合经理提供评估报告以做出最终决策。
- 投资组合经理批准/拒绝交易提案。如果获得批准，订单将被发送到模拟交易所并执行。

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## 安装与使用

### 安装

克隆 TradingAgents：
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

使用您喜欢的任何环境管理器创建虚拟环境：
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

安装依赖项：
```bash
pip install -r requirements.txt
```

### 配置

#### 环境变量

您可以使用环境变量或 `.env` 文件配置 API 密钥：

在根目录创建 `.env` 文件（使用 `.env.example` 作为模板）：
```bash
# FinnHub API 用于财务数据（支持免费套餐）
FINNHUB_API_KEY=your_finnhub_api_key
```

或直接设置为环境变量：
```bash
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY
```

#### LLM 提供商配置

TradingAgents 使用 JSON 配置文件来管理 LLM 提供商。`llm_provider.json` 文件是**必需的**，作为所有 LLM 提供商设置的单一数据源。

**从示例模板创建 `llm_provider.json` 文件：**

```bash
cp llm_provider.json.example llm_provider.json
```

然后编辑文件以添加您的 API 密钥并配置您偏好的模型：

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

**配置行为：**
- **默认选择**：系统自动使用 JSON 文件中的**第一个提供商**和**第一个模型**作为默认值
- **GUI 集成**：Gradio 界面直接从此文件加载提供商和模型选项
- **CLI 集成**：命令行界面使用相同的配置源
- **无后备方案**：如果文件缺失或无效，系统将**不会启动**并显示清晰的错误消息

**重要说明：**
- `llm_provider.json` 文件是系统运行的**必需条件**
- 所有界面（GUI、CLI、Python 包）都使用这个单一的配置源
- 不使用环境变量或硬编码的 LLM 提供商配置默认值
- 数组中的第一个提供商成为默认选择
- 每个提供商模型列表中的第一个模型成为该提供商的默认模型

**支持的 LLM 提供商包括：**
- **OpenAI**：GPT-4、GPT-4 Turbo、GPT-3.5 Turbo、O1 系列
- **Anthropic**：Claude 模型（通过 OpenRouter）
- **DeepSeek**：DeepSeek Chat、DeepSeek Reasoner
- **Google**：Gemini 模型
- **本地模型**：通过 Ollama、LM Studio 或其他 OpenAI 兼容的 API
- **自定义提供商**：任何 OpenAI 兼容的 API 端点

### 使用选项

TradingAgents 提供多种界面以适应不同的用户偏好：

#### 1. 图形用户界面 (GUI)

启动现代化的 Gradio 网页界面：
```bash
python launch_gui.py
```

GUI 提供：
- 带有实时更新的交互式股票分析
- 历史分析记录和结果管理
- 带有视觉指示器的进度跟踪
- 带有语法高亮的格式化报告
- 多语言支持（英语/中文）
- **自动 LLM 配置**：默认使用 `llm_provider.json` 中的第一个提供商和模型

#### 2. 命令行界面 (CLI)

为命令行爱好者提供：
```bash
python -m cli.main
```

您将看到一个屏幕，可以选择您想要的股票代码、日期、LLM、研究深度等。

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

将出现一个界面，显示结果加载情况，让您跟踪智能体运行时的进度。

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

#### 3. Python 包使用方法

要在您的代码中使用 TradingAgents，您可以导入 `tradingagents` 模块并初始化一个 `TradingAgentsGraph()` 对象。`.propagate()` 函数将返回一个决策。您可以运行 `main.py`，这里也有一个快速示例：

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 前向传播
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

您还可以调整默认配置来设置您自己选择的 LLM、辩论轮数等。

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 创建自定义配置
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4.1-nano"  # 使用不同的模型
config["quick_think_llm"] = "gpt-4.1-nano"  # 使用不同的模型
config["max_debate_rounds"] = 1  # 增加辩论轮数
config["online_tools"] = True # 使用在线工具或缓存数据

# 使用自定义配置初始化
ta = TradingAgentsGraph(debug=True, config=config)

# 前向传播
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

> 对于 `online_tools`，我们建议在实验时启用它们，因为它们提供对实时数据的访问。智能体的离线工具依赖于来自我们的 **Tauric TradingDB** 的缓存数据，这是我们用于回测的精选数据集。我们目前正在完善这个数据集，并计划与我们即将推出的项目一起很快发布它。敬请期待！

您可以在 `tradingagents/default_config.py` 中查看完整的配置列表。

**注意**：LLM 提供商配置专门通过 `llm_provider.json` 文件管理。

### 快速开始指南

1. **克隆仓库**：`git clone https://github.com/TauricResearch/TradingAgents.git`
2. **安装依赖**：`pip install -r requirements.txt`  
3. **设置环境**：将 `FINNHUB_API_KEY` 添加到 `.env` 文件
4. **配置 LLM 提供商**：复制并编辑示例文件：`cp llm_provider.json.example llm_provider.json`
5. **启动界面**：
   - GUI：`python launch_gui.py`
   - CLI：`python -m cli.main`
   - Python：导入并使用 `TradingAgentsGraph`

**系统将自动使用您的 JSON 配置中的第一个提供商和模型作为默认值。**

## TradingAgents 包

### 实现细节

我们使用 LangGraph 构建了 TradingAgents 以确保灵活性和模块化。我们在实验中使用 `o1-preview` 和 `gpt-4o` 作为深度思考和快速思考的 LLM。但是，出于测试目的，我们建议您使用 `o4-mini` 和 `gpt-4.1-mini` 来节省成本，因为我们的框架会进行**大量的** API 调用。

### 功能特性

- **统一配置**：所有 LLM 提供商设置的单一 JSON 文件（`llm_provider.json`）
- **智能默认值**：从配置中自动选择第一个提供商和模型作为默认值
- **多界面支持**：可选择 GUI、CLI 或 Python 包集成
- **环境配置**：通过 `.env` 文件或环境变量进行灵活的 API 密钥管理（仅用于数据源）
- **实时分析**：带有进度跟踪的实时市场数据处理
- **历史记录**：分析结果存储和检索系统
- **多语言支持**：英语和中文语言界面
- **可定制配置**：可调整的 LLM 模型、辩论轮数和分析深度
- **报告格式化**：带有结构化输出的语法高亮分析报告
- **错误预防**：当配置缺失或无效时显示清晰的错误消息

## 贡献代码

我们欢迎来自社区的贡献！无论是修复错误、改进文档还是建议新功能，您的输入都有助于让这个项目变得更好。如果您对这一研究方向感兴趣，请考虑加入我们的开源金融 AI 研究社区 [Tauric Research](https://tauric.ai/)。

## 引用

如果您发现 *TradingAgents* 对您有帮助，请引用我们的工作 :)

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