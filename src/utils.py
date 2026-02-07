import requests
import hashlib
import os
from bs4 import BeautifulSoup
import re
import sqlite3

def get_existing_hashes(save_dir, db_path=None):
    """从数据库获取现有图片的哈希"""
    if db_path is None:
        db_path = 'images.db'  # 默认数据库
    existing_hashes = set()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM images")
        rows = cursor.fetchall()
        for row in rows:
            existing_hashes.add(row[0])
        conn.close()
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    return existing_hashes

def existed_picture(db_path=None):
    """从数据库获取现有图片的哈希"""
    if db_path is None:
        db_path = 'images.db'  # 默认数据库
    existing_hashes = set()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM images where stable=1")
        rows = cursor.fetchall()
        for row in rows:
            existing_hashes.add(row[0])
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")        
    return existing_hashes
def extract_image_url(post_data):
    """从Reddit API数据中提取图片URL"""
    try:
        # 尝试获取图集数据
        if 'gallery_data' in post_data[0]['data']['children'][0]['data']:
            gallery = post_data[0]['data']['children'][0]['data']['gallery_data']
            media_id = gallery['items'][0]['media_id']
            return f"https://i.redd.it/{media_id}.jpg"

        # 尝试直接图片链接
        if 'url' in post_data[0]['data']['children'][0]['data']:
            url = post_data[0]['data']['children'][0]['data']['url']

            # 过滤有效图片链接
            if re.match(r'https?://(i\.redd\.it|i\.imgur\.com)/.+\.(jpg|jpeg|png|webp)', url):
                return url

            # 处理Imgur相册链接
            if 'imgur.com/a/' in url:
                return get_imgur_album(url)

    except (KeyError, IndexError):
        pass

    return None

def get_imgur_album(album_url):
    """获取Imgur相册中的第一张图片"""
    try:
        response = requests.get(album_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        image = soup.select_one('meta[property="og:image"]')
        return image['content'] if image else None
    except:
        return None

def is_valid_image(data, content_type=''):
    """增强版图片验证函数"""
    if not data:
        return False

    # 基于Content-Type的验证
    if 'image/jpeg' in content_type:
        return data.startswith(b'\xff\xd8\xff')
    elif 'image/png' in content_type:
        return data.startswith(b'\x89PNG\r\n\x1a\n')
    elif 'image/gif' in content_type:
        return data.startswith(b'GIF87a') or data.startswith(b'GIF89a')
    elif 'image/webp' in content_type:
        return data.startswith(b'RIFF') and len(data) > 12 and data[8:12] == b'WEBP'

    # 通用文件头验证
    if data.startswith(b'\xff\xd8\xff'):  # JPEG
        return True
    if data.startswith(b'\x89PNG\r\n\x1a\n'):  # PNG
        return True
    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):  # GIF
        return True
    if len(data) > 12 and data.startswith(b'RIFF') and data[8:12] == b'WEBP':  # WebP
        return True

    return False