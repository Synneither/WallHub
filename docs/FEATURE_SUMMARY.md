# 新增功能总结 ✨

## 功能名称
**数据库图片下载器** - 从本地SQL数据库批量下载图片

---

## 功能描述

新增了一个完整的数据库图片下载模块，允许用户从SQLite数据库中读取已记录的图片信息，并批量下载到本地目录。

### 核心特性

✅ **数据库查询**
- 从SQLite数据库中读取所有图片URL和元数据
- 支持 Reddit 数据库 (`images.db`)
- 支持 Wallhaven 数据库 (`wallhaven_images.db`)

✅ **智能下载**
- 自动检测本地文件，跳过已下载的图片
- 基于文件哈希值进行去重
- 图片格式验证，确保文件完整性

✅ **并行处理**
- 多线程并发下载（默认5个线程）
- 可配置的并发数量
- 队列管理和错误恢复

✅ **日志跟踪**
- 详细的操作日志
- 按时间戳命名的日志文件
- 下载统计和边界统计

---

## 新增文件

### 1. [src/DatabaseImageDownloader.py](src/DatabaseImageDownloader.py)
**功能模块**
- `DatabaseImageDownloader`: 基础下载器类
- `RedditDatabaseDownloader`: Reddit专用下载器
- `WallhavenDatabaseDownloader`: Wallhaven专用下载器

**类方法**
```python
# 初始化下载器
downloader = RedditDatabaseDownloader(db_path, save_dir)

# 运行下载
downloader.run()

# 从数据库获取图片
images = downloader.get_images_from_db()

# 下载单个图片
downloader.download_image(image_data)
```

---

## 使用方式

### 命令行接口

```bash
# 下载 Reddit 数据库中的图片
python main.py reddit-db

# 下载 Wallhaven 数据库中的图片
python main.py wallhaven-db

# 下载所有数据库中的图片
python main.py db-all
```

### Python API

```python
from src.DatabaseImageDownloader import RedditDatabaseDownloader
from config import REDDIT_CONFIG

# 创建下载器
downloader = RedditDatabaseDownloader(
    db_path=REDDIT_CONFIG['db_path'],
    save_dir=REDDIT_CONFIG['save_dir']
)

# 运行下载
downloader.run()
```

---

## 配置参数

### 默认配置

**Reddit:**
- 数据库路径: `images.db`
- 保存目录: `~/Pictures/背景/download`
- 最大线程: 5
- 下载超时: 20秒

**Wallhaven:**
- 数据库路径: `wallhaven_images.db`
- 保存目录: `~/Pictures/背景/wallhaven`
- 最大线程: 5
- 下载超时: 20秒

### 可配置项

编辑 `src/DatabaseImageDownloader.py` 中的：

```python
self.max_workers = 5              # 最大并发线程数
self.download_timeout = 20        # 下载超时（秒）
self.request_timeout = 10         # 请求超时（秒）
self.sleep_time = 1               # 请求间隔（秒）
```

---

## 数据库结构

### Reddit 数据库 (images.db)

```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    hash TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL UNIQUE,
    stable INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Wallhaven 数据库 (wallhaven_images.db)

```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallhaven_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    hash TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL UNIQUE,
    source_url TEXT,
    resolution TEXT,
    stable INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## 工作流程

```
┌─────────────────────────┐
│   启动下载器            │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   初始化日志系统        │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   连接SQLite数据库      │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   查询所有图片记录      │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   检查本地文件          │
│   (去重和验证)          │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   多线程并行下载        │
│   (默认5个线程)         │
└────────────┬────────────┘
             │
┌────────────▼────────────┐
│   生成统计报告          │
└─────────────────────────┘
```

---

## 性能指标

### 当前测试数据

- **Reddit数据库**
  - 总图片数: 303
  - 已下载: 274+
  - 下载并发: 5线程
  - 预估下载时间: 5-10分钟（取决于网络速度）

- **Wallhaven数据库**
  - 总图片数: 329
  - 下载并发: 5线程
  - 预估下载时间: 10-15分钟（取决于网络速度）

### 优化建议

- 增加 `max_workers` 以加快下载速度（需考虑网络限制）
- 减少 `sleep_time` 以加快请求速度（需尊重API速率限制）
- 增加 `download_timeout` 以处理网络不稳定

---

## 错误处理

### 网络错误

自动捕获并重试：
- `RequestException`: 网络连接失败
- 超时错误: 下载超时自动跳过
- HTTP错误: 返回非200状态码时跳过

### 文件错误

安全的文件操作：
- 检查文件完整性
- 验证图片格式
- 跳过无效文件

### 数据库错误

数据库连接管理：
- SQLite连接上下文管理
- 自动回滚失败事务
- 连接池管理

---

## 日志示例

```
2026-02-07 18:22:24,768 - DatabaseImageDownloader - INFO - 🚀 初始化数据库图片下载器... (源: reddit)
2026-02-07 18:22:24,768 - DatabaseImageDownloader - INFO - 📁 图片保存目录: /home/user/Pictures/背景/download
2026-02-07 18:22:24,768 - DatabaseImageDownloader - INFO - ✅ 下载器初始化完成
2026-02-07 18:22:24,769 - DatabaseImageDownloader - INFO - 📊 从数据库获取 303 条图片记录
2026-02-07 18:22:24,770 - DatabaseImageDownloader - INFO - 📥 准备下载 303 个图片...
2026-02-07 18:22:24,771 - DatabaseImageDownloader - INFO - ⬇️ 开始下载: hash.png <- https://i.redd.it/xxx
2026-02-07 18:22:25,472 - DatabaseImageDownloader - INFO - ✅ 下载完成: hash.png
...
2026-02-07 18:22:XX,XXX - DatabaseImageDownloader - INFO - 📊 下载统计
2026-02-07 18:22:XX,XXX - DatabaseImageDownloader - INFO - ✅ 成功: 150
2026-02-07 18:22:XX,XXX - DatabaseImageDownloader - INFO - ⏭️  已存在: 150
2026-02-07 18:22:XX,XXX - DatabaseImageDownloader - INFO - ❌ 失败: 3
```

---

## 支持的图片格式

- 📸 PNG
- 📸 JPG/JPEG  
- 📸 GIF
- 📸 WEBP
- 📸 AVIF

---

## 主要改动

### 文件修改

1. **[main.py](main.py)**
   - 添加了 `DatabaseImageDownloader` 的导入
   - 添加了 `print_usage()` 函数显示帮助信息
   - 扩展了命令参数处理逻辑
   - 支持新的命令: `reddit-db`, `wallhaven-db`, `db-all`

2. **新建文件**
   - [src/DatabaseImageDownloader.py](src/DatabaseImageDownloader.py) - 核心实现
   - [docs/DATABASE_DOWNLOAD_GUIDE.md](docs/DATABASE_DOWNLOAD_GUIDE.md) - 使用指南

---

## 测试验证

✅ **功能测试**
- [x] 数据库连接成功
- [x] 图片信息查询成功
- [x] 并行下载工作正常
- [x] 文件去重功能运行
- [x] 日志记录完整

✅ **数据验证**
- [x] Reddit数据库: 303条记录 ✓
- [x] Wallhaven数据库: 329条记录 ✓
- [x] 已下载文件: 274+ ✓

---

## 后续优化方向

- [ ] 增加命令行进度条显示
- [ ] 实现增量下载标记
- [ ] 支持从特定日期之后的图片下载
- [ ] 添加下载速度限制选项
- [ ] 实现图片质量过滤
- [ ] 支持自定义文件命名规则
- [ ] 添加图片元数据保存

---

## 文档

- 📖 [详细使用指南](docs/DATABASE_DOWNLOAD_GUIDE.md)
- 📖 [项目README](docs/README.md)
- 📖 [快速参考](docs/QUICK_REFERENCE.md)

---

## 总结

✨ **新增功能概览**

| 功能 | 说明 |
|------|------|
| 数据库查询 | 从SQLite读取所有图片记录 |
| 批量下载 | 多线程并行下载303+图片 |
| 智能去重 | 自动检测已存在文件 |
| 格式验证 | 确保图片完整性 |
| 日志记录 | 详细的操作日志 |
| 错误处理 | 自动跳过失败项目 |

这个功能使得用户可以轻松地从已建立的数据库中恢复或备份所有下载过的图片。
