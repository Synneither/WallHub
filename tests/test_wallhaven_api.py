#!/usr/bin/env python3
"""
Wallhaven API 诊断脚本
用于测试和诊断 Wallhaven API 连接问题
"""

import requests
import json
import time

def test_basic_connection():
    """测试基本网络连接"""
    print("=" * 60)
    print("🧪 测试 1: 基本网络连接")
    print("=" * 60)
    
    try:
        response = requests.get('https://wallhaven.cc/', timeout=10)
        print(f"✅ 能够访问 Wallhaven 网站 (状态码: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ 无法访问 Wallhaven: {e}")
        return False


def test_api_endpoint():
    """测试 API 端点"""
    print("\n" + "=" * 60)
    print("🧪 测试 2: API 端点连接")
    print("=" * 60)
    
    api_url = 'https://wallhaven.cc/api/v1/search'
    
    try:
        # 不使用任何过滤条件的最小请求
        params = {
            'page': 1,
            'categories': '111',
            'purity': '110'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"📍 API 地址: {api_url}")
        print(f"📋 请求参数: {params}")
        
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            timeout=10
        )
        
        print(f"📡 HTTP 状态码: {response.status_code}")
        print(f"📝 响应内容长度: {len(response.text)} 字符")
        print(f"📌 响应类型: {response.headers.get('content-type', 'N/A')}")
        
        if response.text:
            print(f"📄 响应内容（前 200 字符）:\n{response.text[:200]}")
        else:
            print("⚠️  响应为空！")
            return False
        
        # 尝试解析 JSON
        try:
            data = response.json()
            print(f"\n✅ JSON 解析成功！")
            print(f"   - data 数组长度: {len(data.get('data', []))}")
            print(f"   - 其他字段: {list(data.keys())}")
            return True
        except ValueError as e:
            print(f"\n❌ JSON 解析失败: {e}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时（10 秒）")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 网络连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


def test_with_search():
    """测试带搜索关键词的请求"""
    print("\n" + "=" * 60)
    print("🧪 测试 3: 带搜索关键词的 API")
    print("=" * 60)
    
    api_url = 'https://wallhaven.cc/api/v1/search'
    
    try:
        params = {
            'q': 'anime',  # 搜索关键词
            'page': 1,
            'categories': '111',
            'purity': '110'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"🔍 搜索关键词: anime")
        
        response = requests.get(
            api_url,
            params=params,
            headers=headers,
            timeout=10
        )
        
        print(f"📡 HTTP 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取成功！")
            print(f"   - 返回壁纸数量: {len(data.get('data', []))}")
            if data.get('data'):
                first = data['data'][0]
                print(f"   - 首个壁纸 ID: {first.get('id')}")
                print(f"   - 首个壁纸分辨率: {first.get('resolution')}")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_config_loading():
    """测试配置加载"""
    print("\n" + "=" * 60)
    print("🧪 测试 4: 配置加载")
    print("=" * 60)
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from config import WALLHAVEN_CONFIG
        
        print("✅ 配置加载成功！")
        print(f"   - API URL: {WALLHAVEN_CONFIG.get('api_url')}")
        print(f"   - 搜索关键词: {WALLHAVEN_CONFIG.get('search_query')}")
        print(f"   - 分类: {WALLHAVEN_CONFIG.get('categories')}")
        print(f"   - 内容等级: {WALLHAVEN_CONFIG.get('purity')}")
        print(f"   - 最大图片数: {WALLHAVEN_CONFIG.get('max_images')}")
        return True
        
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def test_import_downloader():
    """测试导入下载器"""
    print("\n" + "=" * 60)
    print("🧪 测试 5: 导入 WallhavenImageDownloader")
    print("=" * 60)
    
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from src.WallhavenImageDownloader import WallhavenImageDownloader
        
        print("✅ 导入成功！")
        print("   正在初始化下载器...")
        
        downloader = WallhavenImageDownloader()
        print("✅ 初始化成功！")
        print(f"   - 保存目录: {downloader.save_dir}")
        print(f"   - 数据库: {downloader.db_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入/初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有诊断"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "Wallhaven API 诊断工具" + " " * 23 + "║")
    print("╚" + "=" * 58 + "╝")
    
    results = []
    
    # 运行所有测试
    results.append(("网络连接", test_basic_connection()))
    time.sleep(1)
    
    results.append(("API 端点", test_api_endpoint()))
    time.sleep(1)
    
    results.append(("搜索功能", test_with_search()))
    time.sleep(1)
    
    results.append(("配置加载", test_config_loading()))
    time.sleep(1)
    
    results.append(("导入下载器", test_import_downloader()))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 诊断总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n✅ 所有诊断通过！可以安全地使用 Wallhaven 下载器。")
    else:
        print("\n⚠️  存在问题需要修复。请查看上面的详细信息。")
        print("\n常见解决方案：")
        print("  1. 检查网络连接")
        print("  2. 检查 Wallhaven 是否可访问（www.wallhaven.cc）")
        print("  3. 尝试更换网络或使用代理")
        print("  4. 检查防火墙/路由器设置")
        print("  5. 稍后重试（可能是临时限制）")


if __name__ == "__main__":
    main()
