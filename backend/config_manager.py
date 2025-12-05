import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Configuration file path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
CONFIG_FILE = os.path.join(PROJECT_ROOT, "ai_config.json")

# Default configuration
DEFAULT_CONFIG = {
    "host": "http://localhost:11434",
    "logic_model": "ministral-3:14b",
    "vision_model": "qwen3-vl:latest"
}

class ConfigManager:
    """Manages persistent AI configuration."""
    
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file, or create with defaults if it doesn't exist."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
                return config
            except Exception as e:
                logger.error(f"Error loading config file: {e}. Using defaults.")
                return DEFAULT_CONFIG.copy()
        else:
            logger.info("No config file found. Creating with defaults.")
            self._save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
            return False
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self._config.copy()
    
    def update(self, updates: Dict[str, Any]) -> bool:
        """Update configuration values and save to file."""
        self._config.update(updates)
        return self._save_config(self._config)
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        self._config = DEFAULT_CONFIG.copy()
        return self._save_config(self._config)

# Global instance
config_manager = ConfigManager()
