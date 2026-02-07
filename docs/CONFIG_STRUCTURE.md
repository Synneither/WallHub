# 📁 项目结构 - 配置文件分离

## 新的项目结构

```
backgrounds/
├── main.py                          # 程序入口
├── reddit_config.py                 # 🆕 Reddit 专用配置
├── wallhaven_config.py              # 🆕 Wallhaven 专用配置
├── config.py                        # ⚠️  已弃用（保留用于兼容性）
├── src/
│   ├── downloader.py                # Reddit 下载器
│   ├── WallhavenImageDownloader.py   # Wallhaven 下载器
│   ├── utils.py                     # 通用工具函数
│   └── __pycache__/
├── Test/
│   └── test_wallhaven.py            # Wallhaven 测试脚本
├── logs/                            # 日志文件
├── requirements.txt                 # 依赖列表
└── ... (其他文档文件)
```

---

## 📝 配置文件说明

### `reddit_config.py` - Reddit 专用配置
用于 Reddit 图片下载器的配置：
- 保存目录
- Reddit API URL
- 数据库路径
- Headers 配置
- 超时设置

**使用方式：**
```python
from reddit_config import REDDIT_CONFIG
```

### `wallhaven_config.py` - Wallhaven 专用配置
用于 Wallhaven 图片下载器的配置：
- 保存目录
- API URL
- 搜索参数（关键词、分类、内容等级等）
- 分辨率和宽高比过滤
- 数据库路径
- 超时和延迟设置

**使用方式：**
```python
from wallhaven_config import WALLHAVEN_CONFIG
```

### `config.py` - 已弃用
⚠️ **不再使用，仅保留用于兼容性**

旧的统一配置文件已拆分为 `reddit_config.py` 和 `wallhaven_config.py`。

---

## 🔄 迁移说明

### 对于开发者

**导入配置的新方式：**

```python
# Reddit 下载器
from reddit_config import REDDIT_CONFIG
config = REDDIT_CONFIG['save_dir']

# Wallhaven 下载器
from wallhaven_config import WALLHAVEN_CONFIG
api_url = WALLHAVEN_CONFIG['api_url']
```

**工具函数更新：**

`get_existing_hashes` 函数现在支持可选的 `db_path` 参数：

```python
from src.utils import get_existing_hashes

# 使用默认数据库（images.db）
hashes = get_existing_hashes(save_dir)

# 使用自定义数据库
hashes = get_existing_hashes(save_dir, 'wallhaven_images.db')
```

### 对于用户

**无需额外配置！** 直接使用即可：

```bash
# 仅从 Wallhaven 下载
python main.py wallhaven

# 仅从 Reddit 下载
python main.py reddit

# 从两个源都下载
python main.py all
```

### 修改配置

**修改 Wallhaven 配置：**

编辑 `wallhaven_config.py`，例如：

```python
WALLHAVEN_CONFIG = {
    'search_query': 'landscape',  # 改为风景
    'categories': '001',           # 仅 General
    'max_images': 30,              # 增加下载数量
    # ... 其他配置
}
```

**修改 Reddit 配置：**

编辑 `reddit_config.py`，例如：

```python
REDDIT_CONFIG = {
    'reddit_url': 'https://www.reddit.com/r/wallpaper/',  # 改为其他 subreddit
    'max_images': 50,
    # ... 其他配置
}
```

---

## 📊 文件变动总结

| 文件 | 状态 | 说明 |
|-----|------|------|
| `reddit_config.py` | 🆕 新建 | Reddit 专用配置 |
| `wallhaven_config.py` | 🆕 新建 | Wallhaven 专用配置 |
| `src/downloader.py` | ✏️ 修改 | 使用 REDDIT_CONFIG |
| `src/WallhavenImageDownloader.py` | ✏️ 修改 | 使用 WALLHAVEN_CONFIG |
| `src/utils.py` | ✏️ 修改 | 支持可选 db_path 参数 |
| `test_wallhaven_improved.py` | ✏️ 修改 | 导入新的配置文件 |
| `test_wallhaven_api.py` | ✏️ 修改 | 导入新的配置文件 |
| `Test/test_wallhaven.py` | ✏️ 修改 | 导入新的配置文件 |
| `config.py` | ⚠️ 弃用 | 保留用于兼容性 |

---

## ✅ 验证成功

```
✅ 配置导入成功
  Reddit 数据库: images.db
  Wallhaven 数据库: wallhaven_images.db

✅ Wallhaven 下载器初始化成功
✅ 所有测试通过
```

---

## 🎯 优点

1. **明确分离** - Reddit 和 Wallhaven 配置完全独立
2. **易于维护** - 修改某个源的配置不会影响其他源
3. **灵活配置** - 可以为不同源设置完全不同的参数
4. **模块化** - 添加新的下载源更容易
5. **向后兼容** - 旧的 `config.py` 仍然存在（虽然不使用）

---

## 📝 后续改进建议

未来可以考虑：

- [ ] 创建配置管理工具（GUI 配置界面）
- [ ] 支持多个 Wallhaven 配置文件（不同的下载任务）
- [ ] 支持 `.env` 环境变量配置
- [ ] 配置文件校验和验证
- [ ] 配置文件版本管理

---

祝你使用愉快！🎉
