# 🚀 快速参考

## 基础命令

```bash
# 仅从 Wallhaven 下载
python main.py wallhaven

# 仅从 Reddit 下载
python main.py reddit

# 从所有源下载
python main.py all

# 运行测试
python Test/test_wallhaven.py
```

---

## Wallhaven 配置模板

### 🎨 动画壁纸（高分辨率）
```python
'search_query': 'anime',
'categories': '010',
'purity': '110', 
'atleast': ['2560x1440', '3840x2160'],
'max_images': 30
```

### 🌄 风景壁纸
```python
'search_query': 'landscape',
'categories': '001',
'purity': '100',
'sorting': 'views',
'max_images': 25
```

### 🎭 抽象艺术
```python
'search_query': 'abstract',
'categories': '111',
'purity': '100',
'sorting': 'date_added',
'max_images': 20
```

### 🌙 黑暗系
```python
'search_query': 'dark',
'categories': '001',
'purity': '110',
'ratios': ['16x9'],
'max_images': 15
```

---

## 常用配置速查

| 关键词 | 分类 | 等级 | 排序 |
|------|-----|------|------|
| `anime` | `010` | `110` | `date_added` |
| `landscape` | `001` | `100` | `views` |
| `abstract` | `111` | `100` | `date_added` |
| `nature` | `001` | `100` | `favorites` |
| `dark` | `111` | `110` | `random` |
| `minimal` | `001` | `100` | `date_added` |

---

## 配置代码速查

### 分类组合
- `001` = 仅 General
- `010` = 仅 Anime  
- `100` = 仅 People
- `111` = 全部分类

### 内容等级
- `100` = 仅 SFW
- `110` = SFW + Sketchy
- `111` = 全部

### 排序方式
- `date_added` - 最新发布
- `relevance` - 关键词相关度
- `random` - 随机
- `views` - 最受欢迎
- `favorites` - 最爱收藏

---

## 常见问题速解

**Q: 找不到足够的图片？**  
A: 移除分辨率/宽高比限制，或更改搜索关键词

**Q: 下载速度慢？**  
A: 正常行为，脚本自动限速（可在必要时调整 `sleep_time`）

**Q: 如何查看已下载的图片？**  
A: 检查 `~/Pictures/背景/wallhaven` 目录

**Q: 如何清除下载记录重新开始？**  
A: 删除 `wallhaven_images.db` 文件

---

## 完整参考

- 📖 完整指南: [WALLHAVEN_GUIDE.md](WALLHAVEN_GUIDE.md)
- 📋 项目文档: [README.md](README.md)
- 📝 更新日志: [CHANGELOG.md](CHANGELOG.md)
- ⚙️ 配置文件: [config.py](config.py)

---

## 快速技巧

💡 **窍门 1**: 使用 `search_query` 的组合关键词
```python
'search_query': 'anime dark'  # 搜索"动画 黑暗"相关的
```

💡 **窍门 2**: 随机获取高人气壁纸
```python
'sorting': 'favorites',
'order': 'desc'
```

💡 **窍门 3**: 获取最新发布的壁纸
```python
'sorting': 'date_added',
'order': 'desc'
```

💡 **窍门 4**: 多次运行不会重复下载
数据库自动去重，安全重复运行！

---

😊 祝你使用愉快！有问题？查看完整指南或提交 Issue。
