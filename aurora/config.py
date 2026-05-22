"""Configuration management for AuroraAgent."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class ModelConfig:
    provider: str = "openai-compat"
    name: str = "gpt-4o"
    base_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    max_turns: int = 50


@dataclass
class SessionConfig:
    db_path: str = "~/.aurora-agent/sessions.db"
    workspace: str = "~/AuroraWorkspace"


@dataclass
class CompetitionConfig:
    cache_ttl_hours: int = 24
    update_interval_days: int = 7


@dataclass
class EvaluationConfig:
    default_dimensions: list = field(default_factory=lambda: ["innovation", "team", "business", "employment", "education"])
    confidence_threshold: float = 0.7


@dataclass
class GuardrailConfig:
    max_consecutive_calls: int = 5
    max_calls_per_minute: int = 60


@dataclass
class ContextConfig:
    max_tokens: int = 8192
    compress_threshold: float = 0.65
    keep_recent: int = 5


@dataclass
class LoopConfig:
    max_concurrent: int = 3


@dataclass
class Config:
    model: ModelConfig = field(default_factory=ModelConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    competition: CompetitionConfig = field(default_factory=CompetitionConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    guardrail: GuardrailConfig = field(default_factory=GuardrailConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    loop: LoopConfig = field(default_factory=LoopConfig)


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from file and environment variables."""
    config = Config()
    
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if 'model' in data:
            for key, value in data['model'].items():
                if key == 'api_key' and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    setattr(config.model, key, os.environ.get(env_var, ''))
                else:
                    setattr(config.model, key, value)
        
        if 'session' in data:
            for key, value in data['session'].items():
                setattr(config.session, key, value)
        
        if 'competition' in data:
            for key, value in data['competition'].items():
                setattr(config.competition, key, value)
        
        if 'evaluation' in data:
            for key, value in data['evaluation'].items():
                setattr(config.evaluation, key, value)
        
        if 'guardrail' in data:
            for key, value in data['guardrail'].items():
                setattr(config.guardrail, key, value)
        
        if 'context' in data:
            for key, value in data['context'].items():
                setattr(config.context, key, value)
        
        if 'loop' in data:
            for key, value in data['loop'].items():
                setattr(config.loop, key, value)
    
    # Environment variables override config file
    if 'AURORA_API_KEY' in os.environ:
        config.model.api_key = os.environ['AURORA_API_KEY']
    if 'AURORA_BASE_URL' in os.environ:
        config.model.base_url = os.environ['AURORA_BASE_URL']
    if 'AURORA_MODEL' in os.environ:
        config.model.name = os.environ['AURORA_MODEL']
    
    # Expand paths
    config.session.db_path = os.path.expanduser(config.session.db_path)
    config.session.workspace = os.path.expanduser(config.session.workspace)
    
    return config
