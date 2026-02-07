# 数据库图片下载功能指南 📥

## 概述

本项目现在支持**从本地数据库下载图片**功能。这一功能使你能够：

1. **批量下载**：从数据库中读取已记录的所有图片URL
2. **智能去重**：自动检查文件是否已存在，避免重复下载
3. **并行下载**：使用多线程加速下载过程
4. **日志跟踪**：详细的下载日志帮助你追踪进度

---

## 命令用法

### 下载 Reddit 数据库中的图片

```bash
python main.py reddit-db
```

**功能**：
- 从 `images.db` 数据库中读取所有 Reddit 图片记录
- 下载到 `~/Pictures/背景/download` 目录
- 自动跳过已存在的文件

**示例输出**：
```
🚀 初始化数据库图片下载器... (源: reddit)
📁 图片保存目录: /home/user/Pictures/背景/download
✅ 下载器初始化完成
📊 从数据库获取 303 条图片记录
📥 准备下载 303 个图片...
⬇️ 开始下载: filename.png <- https://i.redd.it/...
✅ 下载完成: filename.png
...
```

---

### 下载 Wallhaven 数据库中的图片

```bash
python main.py wallhaven-db
```

**功能**：
- 从 `wallhaven_images.db` 数据库中读取所有 Wallhaven 图片记录
- 下载到 `~/Pictures/背景/wallhaven` 目录
- 支持多格式图片（PNG、JPG、WEBP、AVIF等）

**示例输出**：
```
🎬 选择 Wallhaven 数据库下载器
📊 从数据库获取 329 条图片记录
⬇️ 开始下载: hash.png <- https://wallhaven.cc/...
✅ 下载完成: hash.png
```

---

### 下载所有数据库中的图片

```bash
python main.py db-all
```

**功能**：
- 依次下载 Reddit 和 Wallhaven 数据库中的所有图片
- 相当于运行 `reddit-db` 和 `wallhaven-db` 两个命令

**流程**：
1. 下载 Reddit 数据库图片 → `~/Pictures/背景/download`
2. 下载 Wallhaven 数据库图片 → `~/Pictures/背景/wallhaven`

---

## 原有功能

### 下载新图片

```bash
# 从 Reddit 下载新图片
python main.py reddit

# 从 Wallhaven 下载新图片
python main.py wallhaven

# 从所有源下载新图片
python main.py all
```

---

## 工作流示例

### 场景 1：首次使用

1. **从网络获取图片信息并下载**
   ```bash
   python main.py reddit      # 获取 Reddit 图片并保存
   python main.py wallhaven   # 获取 Wallhaven 图片并保存
   ```
   
2. **图片信息会自动保存到数据库**（包含URL和哈希值）

3. **后续重新下载数据库中的图片** （例如清空文件夹后）
   ```bash
   python main.py reddit-db   # 从数据库重新下载所有图片
   ```

### 场景 2：定期更新

```bash
# 通常运行（更新新图片）
python main.py all

# 定期维护（恢复已删除的图片）
python main.py db-all
```

---

## 配置说明

### 数据库路径和保存目录

配置文件位置：
- Reddit: `config/reddit_config.py`
- Wallhaven: `config/wallhaven_config.py`

关键配置项：

```python
# Reddit 配置
REDDIT_CONFIG = {
    'save_dir': os.path.expanduser("~/Pictures/背景/download"),
    'db_path': 'images.db',
    # ...
}

# Wallhaven 配置
WALLHAVEN_CONFIG = {
    'save_dir': os.path.expanduser("~/Pictures/背景/wallhaven"),
    'db_path': 'wallhaven_images.db',
    # ...
}
```

### 自定义下载参数

编辑配置文件以修改：
- `save_dir`: 图片保存目录
- `db_path`: 数据库文件路径
- `download_timeout`: 下载超时时间（秒）

---

## 监控和调试

### 查看日志

日志文件位置：`logs/database_downloader_*.log`

```bash
# 查看最新的下载日志
ls -lt logs/ | head -5
tail -f logs/database_downloader_*.log
```

### 数据库查询

```bash
# 查看 Reddit 数据库中的图片数量
sqlite3 images.db "SELECT COUNT(*) FROM images;"

# 查看 Wallhaven 数据库中的图片数量
sqlite3 wallhaven_images.db "SELECT COUNT(*) FROM images;"

# 查看数据库中的URL列表
sqlite3 images.db "SELECT name, url FROM images LIMIT 10;"
```

---

## 常见问题

### Q: 如何从头开始下载所有图片？
**A:** 
```bash
# 方法 1：直接从数据库下载
python main.py db-all

# 方法 2：清空文件夹后从网络获取新图片
rm ~/Pictures/背景/download/*.{png,jpg,webp}
python main.py reddit
```

### Q: 如果某些图片下载失败怎么办？
**A:** 再次运行下载命令，已下载的文件会被跳过，只会重新尝试失败的文件。

### Q: 图片保存在哪里？
**A:** 
- Reddit 图片: `~/Pictures/背景/download/`
- Wallhaven 图片: `~/Pictures/背景/wallhaven/`

### Q: 可以修改保存目录吗？
**A:** 可以，编辑相应的配置文件（`config/reddit_config.py` 或 `config/wallhaven_config.py`）修改 `save_dir` 参数。

---

## 性能优化

### 下载速度调整

在配置文件中修改：

```python
'sleep_time': 1,              # 请求之间的延迟（秒）
'download_timeout': 20,       # 下载超时（秒）
'request_timeout': 10,        # 请求超时（秒）
```

### 并发下载

`DatabaseImageDownloader` 默认使用 5 个线程并行下载。如需调整，编辑源文件：

```python
self.max_workers = 5  # 改为所需的线程数
```

---

## 技术实现

### 核心类

- **DatabaseImageDownloader**: 通用数据库下载器
- **RedditDatabaseDownloader**: Reddit 专用下载器
- **WallhavenDatabaseDownloader**: Wallhaven 专用下载器

### 工作流程

1. **初始化**：连接数据库，创建保存目录
2. **查询**：从数据库读取所有图片记录（URL、哈希值等）
3. **检查**：比对本地文件，确定哪些需要下载
4. **下载**：使用多线程并行下载所有图片
5. **统计**：生成下载统计报告

---

## 更新日志

### v1.0 - 数据库下载功能发布

✨ **新增功能**：
- ✅ 从 SQLite 数据库读取图片信息
- ✅ 批量并行下载
- ✅ 智能文件去重
- ✅ 详细的下载日志
- ✅ 多线程支持
- ✅ 图片格式验证

---

## 支持的图片格式

- 🖼️ PNG
- 🖼️ JPG / JPEG
- 🖼️ GIF
- 🖼️ WEBP
- 🖼️ AVIF

---
