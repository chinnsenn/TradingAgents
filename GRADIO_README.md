# TradingAgents Gradio GUI

A modern web-based interface for the TradingAgents multi-agent financial trading framework that simulates real-world trading firms with specialized AI agents.


## Launch Script: launch_gui.py

This script provides an interactive command-line interface to start the TradingAgents GUI with customizable options.

### Features of launch_gui.py

- Checks system requirements including Python version (3.8+) and necessary Python packages (gradio, langchain, pandas, numpy).
- Warns if essential API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, FINNHUB_API_KEY) are missing.
- Allows interactive or command line selection of LLM provider with default endpoints.
- Supports arguments: --host, --port, --share, --debug, --skip-check, --provider, --backend-url.
- Starts a gradio server for the GUI app on specified host and port.
- Handles keyboard interrupts and errors gracefully with user messages.

### Usage

Run with default options:
```
python launch_gui.py
```

With options, e.g.:
```
python launch_gui.py --host 127.0.0.1 --port 8080 --debug
```

### Environment Variables

Ensure the needed API keys are set, or the GUI will warn about missing keys but still start.

### LLM Providers Supported

- OpenAI
- Anthropic
- Google
- OpenRouter
- Ollama (local)

### Example Workflow

1. Start the script.
2. If no provider argument, select a provider interactively.
3. GUI initializes and runs on given host/port.

### Error and Interrupt Handling

- KeyboardInterrupt displays thanks message on exit.
- Other exceptions print error and exit with status 1.
