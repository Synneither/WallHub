"""
Wallhaven 壁纸下载器配置
"""

import os
from secrets.api_keys import WALLHAVEN_API_KEY

# Wallhaven 配置
WALLHAVEN_CONFIG = {
    # 基本配置
    'save_dir': os.path.expanduser("~/Pictures/背景/wallhaven"),  # Wallhaven图片保存目录
    'api_url': 'https://wallhaven.cc/api/v1/search',
    'api_key': WALLHAVEN_API_KEY,  # 从 secrets/api_keys.py 导入
    'max_images': 100,
    'default_pages': 1,  # 默认开始页数
    'max_pages': 100,  # 最大页数，用于控制下载数量
    
    # 搜索参数
    'search_query': None,  # 搜索关键词，例如: 'anime', 'landscape', 'abstract'
    'categories': '010',  # 类别: 1-General, 2-Anime, 4-People (可组合，如: '101' = General+People)
    'purity': '111',  # 纯净度: 1-SFW, 2-Sketchy, 4-NSFW (可组合，如: '110' = SFW+Sketchy)
    'sorting': 'toplist',
    'topRange':'1y',  # 排序方式: date_added, relevance, random, views, favorites
    'order': 'desc',  # 排序顺序: desc (降序), asc (升序)
    
    # 可选的分辨率和宽高比过滤
    'atleast': '1920x1080',  # 例如: ['1920x1080', '2560x1440'], 或者用 None 跳过此过滤
    'ratios': 'landscape',  # 例如: ['16x9', '21x9'], 或者用 None 跳过此过滤
    
    # 数据库配置
    'db_path': 'wallhaven_images.db',  # Wallhaven专用数据库
    
    # 网络配置
    'request_timeout': 10,  # 请求超时（秒）
    'download_timeout': 20,  # 下载超时（秒）
    'sleep_time': 2,  # 请求之间的延迟（秒）
}
