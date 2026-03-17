#!/usr/bin/env python3
"""
同步文件夹中的 Wallhaven 图片到数据库
"""

import os
import sqlite3
import hashlib
import logging
from datetime import datetime
from config import WALLHAVEN_CONFIG

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def sync_folder_to_db():
    """同步文件夹中的 Wallhaven 图片到数据库"""
    setup_logging()
    logger = logging.getLogger(__name__)

    save_dir = WALLHAVEN_CONFIG.get('save_dir')
    db_path = WALLHAVEN_CONFIG.get('db_path')

    if not os.path.exists(save_dir):
        logger.error(f"保存目录不存在: {save_dir}")
        return

    if not os.path.exists(db_path):
        logger.error(f"数据库文件不存在: {db_path}")
        return

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    synced_count = 0

    # 扫描文件夹
    for filename in os.listdir(save_dir):
        if not filename.startswith('wallhaven_'):
            continue

        filepath = os.path.join(save_dir, filename)
        if not os.path.isfile(filepath):
            continue

        # 计算哈希
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            image_hash = hashlib.md5(data).hexdigest()
        except Exception as e:
            logger.error(f"计算哈希失败 {filename}: {e}")
            continue

        # 检查数据库中是否已有此哈希
        cursor.execute("SELECT id FROM images WHERE hash = ?", (image_hash,))
        if cursor.fetchone():
            logger.debug(f"图片已存在于数据库: {filename}")
            continue

        # 提取 wallhaven_id
        try:
            id_part = filename.split('_')[1].split('.')[0]
        except IndexError:
            logger.warning(f"无法提取 ID: {filename}")
            continue

        # 构造 URL
        wallhaven_url = f'https://wallhaven.cc/w/{id_part}'
        source_url = wallhaven_url

        # 插入数据库
        try:
            cursor.execute(
                "INSERT INTO images (wallhaven_id, name, hash, url, source_url, resolution, stable) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (id_part, filename, image_hash, wallhaven_url, source_url, 'unknown', 1)
            )
            synced_count += 1
            logger.info(f"添加图片到数据库: {filename}")
        except sqlite3.IntegrityError as e:
            logger.warning(f"插入失败 (可能重复): {filename} - {e}")
        except Exception as e:
            logger.error(f"插入数据库失败: {filename} - {e}")

    # 提交更改
    conn.commit()
    conn.close()

    logger.info(f"同步完成，共添加 {synced_count} 个图片到数据库")

if __name__ == "__main__":
    sync_folder_to_db()
