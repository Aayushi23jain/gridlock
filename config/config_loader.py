"""Simple configuration loader for UI metadata."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_ui_metadata() -> Dict[str, Any]:
    """Load UI metadata from configuration file."""
    config_path = Path(__file__).parent / "ui_metadata.yaml"
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_violation_metadata(violation_type: str) -> Dict[str, Any]:
    """Get UI metadata for a specific violation type."""
    config = load_ui_metadata()
    return config.get('violation_ui_metadata', {}).get(violation_type, {})


def get_severity_colors() -> Dict[str, str]:
    """Get severity color mappings."""
    config = load_ui_metadata()
    return config.get('ui_theme', {}).get('severity_colors', {})


def get_severity_icons() -> Dict[str, str]:
    """Get severity icon mappings."""
    config = load_ui_metadata()
    return config.get('ui_theme', {}).get('severity_icons', {})


def get_app_settings() -> Dict[str, Any]:
    """Get application settings."""
    config = load_ui_metadata()
    return config.get('app_settings', {})


def get_default_location() -> Dict[str, Any]:
    """Get default map location."""
    config = load_ui_metadata()
    return config.get('default_location', {"lat": 12.9716, "lon": 77.5946, "zoom": 13})