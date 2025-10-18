"""
Core module for MCP Server
© 2025-2030 Ashutosh Sinha
"""

from .core_utils import validate_name
from .properties_configurator import PropertiesConfigurator

__all__ = [
    'validate_name',
    'PropertiesConfigurator'
]

__version__ = '1.0.0'
__author__ = 'Ashutosh Sinha'
__copyright__ = '© 2025-2030 Ashutosh Sinha'