"""
Shared configuration utilities for reading LLM provider configurations.
Used by CLI and Streamlit interfaces.
"""

import json
import os
from typing import Dict, List, Optional, Any


def load_llm_providers() -> Dict[str, Any]:
    """Load LLM provider configuration from llm_provider.json file."""
    config_path = os.path.join(os.path.dirname(__file__), "llm_provider.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"LLM provider configuration file not found: {config_path}\n"
            "Please create a llm_provider.json file with your LLM provider configurations."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except Exception as e:
        raise RuntimeError(f"Error loading LLM provider configuration: {e}")


def get_provider_by_name(provider_name: str) -> Optional[Dict[str, Any]]:
    """Get provider configuration by name."""
    config = load_llm_providers()
    for provider in config.get("Providers", []):
        if provider["name"].lower() == provider_name.lower():
            return provider
    return None


def get_all_providers() -> List[Dict[str, Any]]:
    """Get all provider configurations."""
    config = load_llm_providers()
    return config.get("Providers", [])


def get_provider_names() -> List[str]:
    """Get list of all provider names."""
    providers = get_all_providers()
    return [provider["name"] for provider in providers]


def get_provider_models(provider_name: str) -> List[str]:
    """Get list of models for a specific provider."""
    provider = get_provider_by_name(provider_name)
    if provider:
        return provider.get("models", [])
    return []


def get_provider_info(provider_name: str) -> Optional[Dict[str, Any]]:
    """Get provider information including name, URL, API key, and models."""
    provider = get_provider_by_name(provider_name)
    if provider:
        return {
            "name": provider["name"],
            "api_base_url": provider["api_base_url"],
            "api_key": provider.get("api_key", ""),
            "models": provider.get("models", []),
            "transformer": provider.get("transformer", {})
        }
    return None


def validate_provider_model(provider_name: str, model_name: str) -> bool:
    """Validate if a model exists for a given provider."""
    models = get_provider_models(provider_name)
    return model_name in models


def get_default_provider() -> str:
    """Get the first available provider as default."""
    providers = get_provider_names()
    if not providers:
        raise RuntimeError("No LLM providers configured in llm_provider.json")
    return providers[0]


def get_default_model(provider_name: str) -> str:
    """Get the first available model for a provider as default."""
    models = get_provider_models(provider_name)
    if not models:
        raise RuntimeError(f"No models configured for provider '{provider_name}' in llm_provider.json")
    return models[0]