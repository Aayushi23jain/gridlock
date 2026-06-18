"""Configuration package for Gridlock 2.0."""

from config.config_loader import (
    load_ui_metadata,
    get_violation_metadata,
    get_severity_colors,
    get_severity_icons,
    get_app_settings,
    get_default_location
)

__all__ = [
    'load_ui_metadata',
    'get_violation_metadata', 
    'get_severity_colors',
    'get_severity_icons',
    'get_app_settings',
    'get_default_location'
]
