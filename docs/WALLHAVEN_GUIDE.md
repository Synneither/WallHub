# Wallhaven 壁纸爬虫使用指南

## 📖 概述

本项目现已支持从 **Wallhaven** 网站爬取高质量壁纸。Wallhaven 是一个流行的壁纸分享平台，提供大量高分辨率、高质量的壁纸。

---

## 🚀 快速开始

### 基础用法

最简单的方式是运行以下命令：

```bash
python main.py wallhaven
```

这将使用默认配置从 Wallhaven 下载 20 个壁纸（默认搜索关键词：`anime`）。

---

## ⚙️ 配置 Wallhaven

编辑 `config.py` 文件中的 `WALLHAVEN_CONFIG` 部分来自定义下载行为。

### 常用配置项

#### 1. 搜索关键词

```python
'search_query': 'anime',  # 改为你想要的关键词
```

常用关键词：
- `anime` - 动画
- `landscape` - 风景
- `abstract` - 抽象
- `dark` - 黑暗系
- `nature` - 自然
- 任何其他你感兴趣的关键词

#### 2. 分类选择

```python
'categories': '111',  # 组合代码
```

分类代码：
- `1` - General (通用)
- `2` - Anime (动画)
- `4` - People (人物)

示例：
- `001` - 仅 General
- `010` - 仅 Anime
- `100` - 仅 People  
- `111` - General + Anime + People (全选)

#### 3. 内容等级

```python
'purity': '110',  # 组合代码
```

内容等级：
- `1` - SFW (安全工作场所)
- `2` - Sketchy (可疑/边界)
- `4` - NSFW (不安全工作场所)

示例：
- `100` - 仅 SFW
- `110` - SFW + Sketchy
- `111` - 全部

#### 4. 排序方式

```python
'sorting': 'date_added',  # 排序方式
'order': 'desc',  # 排序顺序
```

排序方式：
- `date_added` - 按添加日期
- `relevance` - 按关键词相关性
- `random` - 随机
- `views` - 按浏览次数
- `favorites` - 按收藏次数

排序顺序：
- `desc` - 降序（最新/最多的在前）
- `asc` - 升序（最旧/最少的在前）

#### 5. 分辨率选择

```python
'atleast': ['1920x1080', '2560x1440'],
```

常用分辨率：
- `1920x1080` - Full HD
- `2560x1440` - 2K
- `3840x2160` - 4K
- `1440x900` - 更小屏幕
- 设为 `None` 跳过分辨率过滤

#### 6. 宽高比选择

```python
'ratios': ['16x9', '21x9'],
```

常用宽高比：
- `16x9` - 标准宽屏
- `4x3` - 传统长宽比
- `21x9` - 超宽屏
- `32x9` - 极宽屏
- 设为 `None` 跳过宽高比过滤

#### 7. 下载数量

```python
'max_images': 20,  # 改为你需要的数量
```

#### 8. 保存目录

```python
'save_dir': os.path.expanduser("~/Pictures/背景/wallhaven"),
```

---

## 📋 配置示例

### 示例 1: 下载高分辨率动画壁纸

```python
WALLHAVEN_CONFIG = {
    'save_dir': os.path.expanduser("~/Pictures/背景/wallhaven"),
    'api_url': 'https://wallhaven.cc/api/v1/search',
    'api_key': '',
    'max_images': 30,
    'search_query': 'anime',
    'categories': '010',  # 仅 Anime
    'purity': '110',  # SFW + Sketchy
    'sorting': 'date_added',
    'order': 'desc',
    'atleast': ['2560x1440', '3840x2160'],  # 2K 或 4K
    'ratios': ['16x9'],
    'db_path': 'wallhaven_images.db',
}
```

运行：`python main.py wallhaven`

### 示例 2: 下载风景壁纸

```python
WALLHAVEN_CONFIG = {
    'save_dir': os.path.expanduser("~/Pictures/背景/landscape"),
    'max_images': 50,
    'search_query': 'landscape',
    'categories': '001',  # 仅 General
    'purity': '100',  # 仅 SFW
    'sorting': 'views',  # 按热度排序
    'order': 'desc',
    'atleast': ['1920x1080', '2560x1440'],
    'ratios': None,  # 不限制宽高比
    'db_path': 'wallhaven_landscape.db',
}
```

运行：`python main.py wallhaven`

### 示例 3: 随机高质量壁纸

```python
WALLHAVEN_CONFIG = {
    'save_dir': os.path.expanduser("~/Pictures/背景/random"),
    'max_images': 25,
    'search_query': '',  # 空搜索，获取所有
    'categories': '111',  # 全部分类
    'purity': '100',  # 仅 SFW
    'sorting': 'random',  # 随机排序
    'order': 'desc',
    'atleast': None,  # 不限分辨率
    'ratios': ['16x9'],
    'db_path': 'wallhaven_random.db',
}
```

运行：`python main.py wallhaven`

---

## 🔐 API Key 使用（可选）

Wallhaven 提供可选的 API Key，可以绕过某些限制。

1. 访问 https://wallhaven.cc/settings/account
2. 复制你的 API Key
3. 在 `config.py` 中设置：

```python
WALLHAVEN_CONFIG = {
    'api_key': 'your_api_key_here',
    # ... 其他配置
}
```

---

## 💻 命令行使用

```bash
# 仅从 Wallhaven 下载
python main.py wallhaven

# 仅从 Reddit 下载
python main.py reddit

# 从所有源下载（Reddit + Wallhaven）
python main.py all

# 默认从 Reddit 下载
python main.py
```

---

## 🧪 测试 Wallhaven 功能

运行测试脚本验证配置：

```bash
python Test/test_wallhaven.py
```

测试将检查：
- ✅ API 连接
- ✅ 图片 URL 提取
- ✅ 数据库操作
- ✅ 配置完整性

---

## 📊 数据库管理

Wallhaven 下载器使用独立的数据库文件记录已下载的图片（默认：`wallhaven_images.db`），避免重复下载。

### 查看已下载的图片

```python
import sqlite3

conn = sqlite3.connect('wallhaven_images.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM images")
count = cursor.fetchone()[0]
print(f"已下载 {count} 个壁纸")

cursor.execute("SELECT wallhaven_id, resolution FROM images LIMIT 10")
for wall_id, resolution in cursor.fetchall():
    print(f"  {wall_id} ({resolution})")

conn.close()
```

### 清除数据库记录

```bash
rm wallhaven_images.db
```

重新运行下载器时会创建新的数据库。

---

## ⚠️ 注意事项

1. **尊重服务条款**: 遵守 Wallhaven 的使用条款，不要过度爬虫
2. **频率限制**: 脚本已内置延迟，请勿修改为过快的速率
3. **图片使用**: 大多数壁纸受版权保护，仅供个人使用
4. **分辨率可用性**: 并非所有关键词的所有分辨率都可用，脚本会自动跳过不可用的
5. **搜索结果**: 某些关键词可能返回很少结果，可能无法达到目标数量

---

## 🐛 故障排查

### 问题: "API 连接失败"

**解决方案:**
- 检查网络连接
- 确认 Wallhaven 是否可访问
- 检查是否被临时限制，稍后重试

### 问题: "找不到足够的壁纸"

**解决方案:**
- 尝试移除或修改分辨率/宽高比限制
- 更改搜索关键词
- 降低 `max_images` 目标数量
- 尝试不同的排序方式

### 问题: "下载速度很慢"

**解决方案:**
- 正常行为，脚本故意限制速率以尊重服务器
- 如需加快，可修改 `config.py` 中的 `sleep_time`（不推荐）
- 增加并发下载线程数（仅在有权限时）

---

## 📚 更多信息

- **Wallhaven 网站**: https://wallhaven.cc/
- **API 文档**: https://wallhaven.cc/help/api
- **项目 GitHub**: （链接）

---

祝你下载愉快！如有需要，欢迎提出建议或报告问题。🎉
