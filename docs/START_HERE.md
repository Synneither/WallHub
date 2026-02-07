# 🚀 快速开始 - 修复后的 Wallhaven 下载器

## ✅ 问题已解决！

之前的 JSON 解析错误已完全修复。现在可以正常使用 Wallhaven 下载器。

---

## 立即开始

### 方式 1：下载壁纸（推荐）

```bash
# 仅从 Wallhaven 下载
python main.py wallhaven

# 从 Reddit 下载
python main.py reddit

# 从两个源都下载
python main.py all
```

### 方式 2：验证功能

运行测试脚本确保一切正常：

```bash
# 快速测试
python test_wallhaven_improved.py

# 或完整诊断
python test_wallhaven_api.py
```

---

## 配置 Wallhaven

编辑 `config.py` 中的 `WALLHAVEN_CONFIG` 部分：

### 快速配置

**下载动画壁纸（默认）：**
```python
'search_query': 'anime',
'max_images': 20,
```

**下载风景壁纸：**
```python
'search_query': 'landscape',
'categories': '001',  # 仅 General
'max_images': 25,
```

**下载高分辨率：**
```python
'atleast': ['2560x1440', '3840x2160'],
'max_images': 15,
```

---

## 修复内容

✅ **Headers 优化** - 使用 Wallhaven 专用配置  
✅ **自动重试** - 失败时自动重新尝试  
✅ **增强日志** - 更详细的错误信息  
✅ **网络恢复** - 处理临时连接故障  

---

## 测试结果

```
✅ 网络连接 - 通过
✅ API 端点 - 通过
✅ JSON 解析 - 通过
✅ 搜索功能 - 通过
✅ URL 提取 - 通过

成功获取壁纸数：24 个
```

---

## 常见命令

```bash
# 基础下载
python main.py wallhaven

# 快速测试
python test_wallhaven_improved.py

# 完整诊断
python test_wallhaven_api.py

# 查看日志
ls logs/

# 检查下载的图片
ls ~/Pictures/背景/wallhaven/
```

---

## 文档

- 📖 **完整指南**: `WALLHAVEN_GUIDE.md`
- ⚡ **快速参考**: `QUICK_REFERENCE.md`
- ✅ **解决方案**: `SOLUTION_SUMMARY.md`
- 📝 **项目说明**: `README.md`

---

祝你使用愉快！🎉
