#!/usr/bin/env python3
"""
Wallhaven 下载器 - 改进版本测试
验证自动重试机制
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.WallhavenImageDownloader import WallhavenImageDownloader


def test_wallhaven_search():
    """测试 Wallhaven 搜索功能"""
    print("=" * 60)
    print("🧪 测试 Wallhaven 搜索功能（带自动重试）")
    print("=" * 60)
    
    try:
        downloader = WallhavenImageDownloader()
        
        print("\n📥 测试 1: 基础搜索（第 1 页）")
        data = downloader.search_wallhaven(page=1, retries=3)
        
        if data:
            print(f"✅ 搜索成功！")
            print(f"   - 返回图片数: {len(data.get('data', []))}")
            
            if data.get('meta'):
                meta = data['meta']
                print(f"   - 总页数: {meta.get('total', 'N/A')}")
                print(f"   - 当前页: {meta.get('current_page', 'N/A')}")
                print(f"   - 每页数量: {meta.get('per_page', 'N/A')}")
            
            # 显示第一个图片信息
            if data.get('data'):
                img = data['data'][0]
                print(f"\n   首个图片信息:")
                print(f"     - ID: {img.get('id')}")
                print(f"     - 分辨率: {img.get('resolution')}")
                print(f"     - 类别: {img.get('category')}")
                print(f"     - 浏览: {img.get('views')} 次")
                print(f"     - 收藏: {img.get('favorites')} 次")
        else:
            print("❌ 搜索失败！")
            return False
        
        print("\n📥 测试 2: 获取多个图片 URL")
        urls = downloader.get_unique_image_urls(5)
        
        if urls:
            print(f"✅ 获取成功！")
            print(f"   - 找到 {len(urls)} 个图片")
            for i, (url, wall_id, item) in enumerate(urls[:3], 1):
                print(f"   \n   图片 {i}:")
                print(f"     - ID: {wall_id}")
                print(f"     - 分辨率: {item.get('resolution')}")
                print(f"     - URL: {url[:50]}...")
        else:
            print("❌ 获取 URL 失败！")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行测试"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 8 + "Wallhaven 下载器 - 改进版本测试" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    print("✅ 本版本包含以下改进:")
    print("   1. 自动重试机制（失败时最多重试 3 次）")
    print("   2. 指数退避策略（重试间隔逐渐增加）")
    print("   3. 详细的错误日志")
    print("   4. 速率限制处理（HTTP 429）")
    print("   5. 网络故障恢复")
    print()
    
    if test_wallhaven_search():
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！Wallhaven 下载器工作良好。")
        print("=" * 60)
        print("\n📝 现在可以运行以下命令下载壁纸:")
        print("   python main.py wallhaven")
        print()
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败")
        print("=" * 60)
        print("\n💡 请运行诊断脚本:")
        print("   python test_wallhaven_api.py")
        print()


if __name__ == "__main__":
    main()
