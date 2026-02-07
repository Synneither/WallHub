"""
Reddit 壁纸下载器配置
"""

import os

# Reddit 配置
REDDIT_CONFIG = {
    'save_dir': os.path.expanduser("~/Pictures/背景/reddit"),
    'reddit_url': "https://www.reddit.com/r/Animewallpaper/?f=flair_name%3A%22Desktop%22",
    'max_posts': 100,
    'max_images': 20,
    # 超时与无进展限制：如果长时间没有找到新图片则停止搜索
    'max_search_seconds': 300,  # 最多搜索多少秒后放弃（默认 300 秒）
    'max_empty_batches': 1,     # 连续多少个批次没有新图片后停止（默认 5 批）
    'request_timeout': 10,
    'download_timeout': 20,
    'sleep_time': 2,
    'after': None,
    'db_path': 'reddit_images.db',
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'image',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'Cache-Control': 'max-age=0',
        'Referer': 'https://www.reddit.com/',
        'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"'
    }
}
