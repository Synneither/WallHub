# 壁纸下载器 🖼️

**一个用于从 Reddit 和 Wallhaven 自动获取并下载桌面壁纸的轻量工具。**

---

## ✨ 主要功能

### Reddit 源
- 自动抓取 Reddit 帖子并提取图片 URL（支持 Imgur 图床和 Reddit 本地图片 / 相册）
- 支持特定兴趣（如 /r/Animewallpaper）

### Wallhaven 源
- 自动从 Wallhaven 搜索并下载高质量壁纸
- 支持按关键词、分类、分辨率、宽高比等条件过滤
- Wallhaven API 集成（支持可选 API Key）

### 通用功能
- 多线程/并发下载以提高效率
- 自动检测并跳过重复图片（基于哈希）
- 验证图片格式（PNG / JPG / WEBP / AVIF 等）
- 可配置的请求与下载超时、速率限制与最大抓取范围
- SQLite 数据库追踪已下载的图片

### ✨ 新增功能：数据库图片下载
- **从数据库批量下载**: 从SQLite数据库中读取所有已记录的图片URL
- **智能去重**: 自动检测本地文件，避免重复下载
- **并行处理**: 多线程并发下载（可配置）
- **完整日志**: 详细的操作记录和统计
- **支持多源**: 同时支持Reddit和Wallhaven数据库
  - `python main.py reddit-db` - 下载Reddit数据库中的图片
  - `python main.py wallhaven-db` - 下载Wallhaven数据库中的图片
  - `python main.py db-all` - 下载所有数据库中的图片

---

## 🚀 快速开始

1. 克隆仓库并安装依赖：

```bash
git clone <repo-url>
cd backgrounds
pip install -r requirements.txt
```

2. 根据需要编辑配置文件 `config.py`（下面有示例）

3. 运行脚本：

```bash
# 下载新图片
python main.py reddit          # 从 Reddit 下载新图片
python main.py wallhaven       # 从 Wallhaven 下载新图片
python main.py all             # 从所有源下载新图片

# 从数据库下载已记录的图片
python main.py reddit-db       # 下载 Reddit 数据库中的所有图片
python main.py wallhaven-db    # 下载 Wallhaven 数据库中的所有图片
python main.py db-all          # 下载所有数据库中的图片

# 默认从 Reddit 下载（如果不指定参数）
python main.py
```

脚本会将图片保存到对应配置中的 `save_dir`。

---

## ⚙️ 配置示例（`config.py`）

### Reddit 配置

```python
CONFIG = {
    'save_dir': os.path.expanduser("~/Pictures/背景/download"),
    'reddit_url': "https://www.reddit.com/r/Animewallpaper/?f=flair_name%3A%22Desktop%22",
    'max_posts': 100,
    'max_images': 20,
    'max_search_seconds': 300,
    'max_empty_batches': 2,
    'request_timeout': 10,
    'download_timeout': 20,
    'sleep_time': 2,
    'after': None,
    'db_path': 'images.db',
    'headers': { ... }
}
```

### Wallhaven 配置

```python
WALLHAVEN_CONFIG = {
    # 基本配置
    'save_dir': os.path.expanduser("~/Pictures/背景/wallhaven"),
    'api_url': 'https://wallhaven.cc/api/v1/search',
    'api_key': '',  # 可选：从 https://wallhaven.cc/settings/account 获取
    'max_images': 20,
    
    # 搜索参数
    'search_query': 'anime',  # 搜索关键词
    'categories': '111',  # 1-General, 2-Anime, 4-People
    'purity': '110',  # 1-SFW, 2-Sketchy, 4-NSFW
    'sorting': 'date_added',  # date_added, relevance, random, views, favorites
    'order': 'desc',  # desc, asc
    
    # 分辨率和宽高比过滤
    'atleast': ['1920x1080', '2560x1440'],
    'ratios': ['16x9', '21x9'],
    
    # 数据库
    'db_path': 'wallhaven_images.db',
}
```

**配置说明：**

- **save_dir**: 保存图片的目录。
- **max_images**: 需要下载的图片数量。
- **search_query** (Wallhaven): 搜索关键词，例如 'anime', 'landscape', 'abstract' 等。
- **categories** (Wallhaven): 类别代码的组合:
  - 1 = General (通用)
  - 2 = Anime (动画)
  - 4 = People (人物)
  - 例: '101' = General + People, '111' = General + Anime + People
  
- **purity** (Wallhaven): 内容等级:
  - 1 = SFW (安全工作场所)
  - 2 = Sketchy (可疑)
  - 4 = NSFW (不安全工作场所)
  - 例: '110' = SFW + Sketchy
  
- **atleast** (Wallhaven): 特定分辨率，设为 `None` 则不过滤。
- **ratios** (Wallhaven): 宽高比，设为 `None` 则不过滤。

---

## 🧭 使用示例

### Reddit 下载

修改 `config.py` 中的 `CONFIG` 部分，然后运行：

```bash
python main.py reddit
```

### Wallhaven 下载

修改 `config.py` 中的 `WALLHAVEN_CONFIG` 部分（搜索关键词、分类、分辨率等），然后运行：

```bash
# 下载动画壁纸
python main.py wallhaven

# 下载所有源
python main.py all
```

### 自定义搜索

编辑 `config.py`：

```python
WALLHAVEN_CONFIG = {
    'search_query': 'landscape',  # 改为风景
    'categories': '001',  # 仅 General
    'max_images': 30,
    # ... 其他配置
}
```

然后运行：

```bash
python main.py wallhaven
```

---

## 📁 项目结构

- `main.py` — 程序入口
- `src/` — 包含下载器与工具模块
  - `downloader.py` — Reddit 下载器
  - `WallhavenImageDownloader.py` — Wallhaven 下载器
  - `utils.py` — 共享工具函数
- `config.py` — 应用配置（Reddit 和 Wallhaven）
- `requirements.txt`, `pyproject.toml` — 依赖与包信息
- `logs/` — 日志文件

---

## 🛠️ 开发与贡献

欢迎提交 issue 或 PR：

- 修复提取器对某些图床的兼容性问题
- 添加更多的图床支持或增强去重策略
- 添加新的壁纸源（如 Bing Daily Wallpaper、Unsplash 等）

贡献前请遵循仓库的代码风格并添加对应测试（如适用）。

---

## 📚 相关文档

- [数据库图片下载详细指南](DATABASE_DOWNLOAD_GUIDE.md) - 新增功能的完整文档
- [功能总结](FEATURE_SUMMARY.md) - 功能实现的技术细节
- [变更日志](CHANGELOG.md) - 版本更新记录
- [快速参考](QUICK_REFERENCE.md) - 常用命令速查

---

## ⚠️ 注意事项

- 请遵守 Reddit 和 Wallhaven 的 API 与服务条款，尊重资源使用条款。
- 本项目仅供个人使用，下载的图片请勿用于商业用途（除非图片本身是公有域或作者许可）。
- Wallhaven 的高人气图片可能需要更多请求时间，请耐心等待。

---

## 📄 许可证

本项目遵循 **MIT License**。

---

> 有任何改进建议或需要加入的功能，欢迎在 Issue 中提出！ 💬
