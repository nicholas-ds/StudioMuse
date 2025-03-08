import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class Config:
    """
    Configuration management for StudioMuse that works across platforms.
    Loads configuration from multiple sources with priority order:
    1. Environment variables
    2. User configuration file
    3. Default configurations
    """
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        """Singleton pattern to ensure only one config instance exists"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from all sources"""
        # Start with defaults
        self._config = {
            "api": {
                "host": "127.0.0.1",
                "port": 8000
            },
            "llm": {
                "default_provider": "gemini",
                "temperature": 0.2
            }
        }
        
        # Load from config file if exists
        config_file = self._get_config_file_path()
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    file_config = json.load(f)
                    self._update_nested_dict(self._config, file_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
        
        # Override with environment variables
        self._load_from_env()
    
    def _get_config_file_path(self) -> Path:
        """Get the path to the config file based on the platform"""
        if os.name == "nt":  # Windows
            base_dir = Path(os.environ.get("APPDATA", "")) / "GIMP" / "3.0" / "studiomuse"
        else:  # macOS/Linux
            base_dir = Path.home() / "Library" / "Application Support" / "GIMP" / "3.0" / "studiomuse"
        
        # Ensure directory exists
        base_dir.mkdir(parents=True, exist_ok=True)
        
        return base_dir / "config.json"
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # API settings
        if host := os.environ.get("STUDIOMUSE_API_HOST"):
            self._config["api"]["host"] = host
        
        if port := os.environ.get("STUDIOMUSE_API_PORT"):
            self._config["api"]["port"] = int(port)
        
        # LLM settings
        if provider := os.environ.get("STUDIOMUSE_LLM_PROVIDER"):
            self._config["llm"]["default_provider"] = provider
        
        if temp := os.environ.get("STUDIOMUSE_LLM_TEMPERATURE"):
            self._config["llm"]["temperature"] = float(temp)
    
    def _update_nested_dict(self, d: Dict, u: Dict):
        """Recursively update a nested dictionary"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated key"""
        parts = key.split(".")
        result = self._config
        
        for part in parts:
            if isinstance(result, dict) and part in result:
                result = result[part]
            else:
                return default
        
        return result
    
    def save(self):
        """Save current configuration to file"""
        config_file = self._get_config_file_path()
        try:
            with open(config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

# Global config instance
config = Config() 