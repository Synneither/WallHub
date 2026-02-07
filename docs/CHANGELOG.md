# 功能更新总结

## 🎉 添加 Wallhaven 壁纸爬虫功能

已成功为项目添加 **Wallhaven** 壁纸网站的爬虫功能，现在支持从多个源下载壁纸。

---

## ✨ 新增功能

### 1. **Wallhaven 下载器** (`src/WallhavenImageDownloader.py`)
   - 完整的 Wallhaven API 集成
   - 支持搜索关键词、分类、内容等级过滤
   - 支持分辨率和宽高比过滤
   - 多线程并发下载
   - SQLite 数据库追踪已下载的图片
   - 自动去重（基于图片哈希和 Wallhaven ID）

### 2. **配置系统扩展** (`config.py`)
   - 新增 `WALLHAVEN_CONFIG` 配置字典
   - 支持自定义搜索参数：
     - 搜索关键词 (`search_query`)
     - 图片分类 (`categories`)
     - 内容等级 (`purity`)
     - 排序方式 (`sorting`, `order`)
     - 分辨率过滤 (`atleast`)
     - 宽高比过滤 (`ratios`)
   - 支持可选 API Key（用于绕过某些限制）

### 3. **多源下载支持** (`main.py`)
   - 添加命令行参数支持：
     - `python main.py reddit` - 仅从 Reddit 下载
     - `python main.py wallhaven` - 仅从 Wallhaven 下载
     - `python main.py all` - 从所有源下载
   - 保持向后兼容（默认为 Reddit）

### 4. **测试套件** (`Test/test_wallhaven.py`)
   - API 连接测试
   - 图片 URL 提取测试
   - 数据库操作测试
   - 配置完整性检查

### 5. **文档更新**
   - 更新 `README.md` - 全面的项目文档
   - 新增 `WALLHAVEN_GUIDE.md` - Wallhaven 专用使用指南
   - 包含配置示例、故障排查、最佳实践

---

## 📁 新增/修改文件

### 新增文件
- `src/WallhavenImageDownloader.py` - Wallhaven 下载器核心类
- `Test/test_wallhaven.py` - Wallhaven 功能测试
- `WALLHAVEN_GUIDE.md` - Wallhaven 使用指南

### 修改文件
- `config.py` - 添加 `WALLHAVEN_CONFIG`
- `main.py` - 添加命令行参数支持
- `README.md` - 更新项目文档

---

## 🚀 使用方法

### 快速开始

```bash
# 仅从 Wallhaven 下载
python main.py wallhaven

# 仅从 Reddit 下载
python main.py reddit

# 从所有源下载
python main.py all
```

### 配置示例

编辑 `config.py` 中的 `WALLHAVEN_CONFIG`：

```python
WALLHAVEN_CONFIG = {
    'search_query': 'anime',  # 搜索关键词
    'categories': '010',  # 仅 Anime（可选：001=General, 100=People, 111=全部）
    'purity': '110',  # SFW + Sketchy（可选：100=仅SFW, 111=全部）
    'sorting': 'date_added',  # 按日期排序
    'order': 'desc',  # 降序
    'max_images': 20,  # 下载数量
    'atleast': ['1920x1080', '2560x1440'],  # 分辨率过滤
    'ratios': ['16x9'],  # 宽高比过滤
    'save_dir': os.path.expanduser("~/Pictures/背景/wallhaven"),
    'db_path': 'wallhaven_images.db',
}
```

---

## 🔑 主要特性

### 智能去重
- **哈希去重**: 基于图片内容 MD5 哈希
- **ID 去重**: 基于 Wallhaven 图片 ID
- **URL 去重**: 基于图片 URL

### 灵活过滤
- 按关键词搜索
- 按分类过滤（通用/动画/人物）
- 按内容等级（SFW/Sketchy/NSFW）
- 按分辨率和宽高比

### 高效下载
- 多线程并发（默认 5 线程）
- 自动速率限制
- 完整的错误处理和重试

### 数据管理
- SQLite 数据库存储元信息
- 分离的数据库文件（Reddit 和 Wallhaven）
- 支持图片信息查询和追踪

---

## 📋 配置参数说明

| 参数 | 说明 | 示例 |
|-----|------|------|
| `search_query` | 搜索关键词 | `anime`, `landscape` |
| `categories` | 分类代码 (1/2/4) | `010`, `111` |
| `purity` | 内容等级 (1/2/4) | `100`, `110` |
| `sorting` | 排序方式 | `date_added`, `relevance` |
| `max_images` | 下载数量 | `20`, `50` |
| `atleast` | 分辨率列表 | `['1920x1080']` |
| `ratios` | 宽高比列表 | `['16x9']` |

---

## 🧪 测试

运行测试套件验证功能：

```bash
python Test/test_wallhaven.py
```

测试包括：
- ✅ API 连接检查
- ✅ 图片 URL 提取验证
- ✅ 数据库操作验证
- ✅ 配置完整性检查

---

## ⚠️ 注意事项

1. **服务条款**: 遵守 Wallhaven 的使用条款
2. **速率限制**: 脚本自动控制请求频率，勿强行修改
3. **图片版权**: 大多数壁纸受版权保护，仅供个人使用
4. **数据库**: Reddit 和 Wallhaven 使用独立数据库，避免冲突

---

## 📚 详细文档

- **完整指南**: 见 `WALLHAVEN_GUIDE.md`
- **项目说明**: 见 `README.md`
- **配置参考**: 见 `config.py` 中的注释

---

## 🔄 后续改进方向

- [ ] 添加更多壁纸源（Bing Daily Wallpaper、Unsplash 等）
- [ ] Web UI 前端
- [ ] 定时自动下载功能
- [ ] 图片分类和标签管理
- [ ] 批量配置导出/导入

---

祝你使用愉快！🎉
