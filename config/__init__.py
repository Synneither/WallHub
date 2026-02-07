"""
配置模块

包含所有下载器的配置文件
"""

from .wallhaven_config import WALLHAVEN_CONFIG
from .reddit_config import REDDIT_CONFIG

__all__ = ['WALLHAVEN_CONFIG', 'REDDIT_CONFIG']
