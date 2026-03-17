#!/usr/bin/env python3
"""
更新数据库中 Wallhaven 图片的 name 字段为新格式
"""

import os
import sqlite3
import re
from config import WALLHAVEN_CONFIG

def update_db_names():
    """更新数据库中 Wallhaven 图片的 name 字段"""
    print("开始更新")

    db_path = WALLHAVEN_CONFIG.get('db_path')
    print(f"db_path: {db_path}")

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查询所有 wallhaven_id 不为空的记录
    cursor.execute("SELECT id, wallhaven_id, name FROM images WHERE wallhaven_id IS NOT NULL AND wallhaven_id != ''")
    rows = cursor.fetchall()
    print(f"找到 {len(rows)} 条记录")

    updated_count = 0

    for row in rows:
        print(f"处理记录: {row}")
        db_id, wallhaven_id, current_name = row

        # 生成新文件名
        safe_id = re.sub(r'[^a-zA-Z0-9]', '', wallhaven_id)

        # 获取扩展名
        if '.' in current_name:
            ext = current_name.split('.')[-1].lower()
        else:
            ext = 'jpg'  # 默认

        new_name = f"wallhaven_{safe_id}.{ext}"

        # 如果已经是正确的，跳过
        if current_name == new_name:
            print(f"跳过: {current_name}")
            continue

        # 更新数据库
        cursor.execute("UPDATE images SET name = ? WHERE id = ?", (new_name, db_id))
        updated_count += 1
        print(f"更新 name: {current_name} -> {new_name}")

    # 提交更改
    conn.commit()
    conn.close()

    print(f"更新完成，共更新 {updated_count} 条记录")

if __name__ == "__main__":
    update_db_names()