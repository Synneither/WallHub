"""
Wallhaven 下载器测试脚本
用于测试 Wallhaven 下载器的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.WallhavenImageDownloader import WallhavenImageDownloader
from config import WALLHAVEN_CONFIG


def test_api_connection():
    """测试 API 连接"""
    print("=" * 50)
    print("📋 测试 1: API 连接")
    print("=" * 50)
    
    downloader = WallhavenImageDownloader()
    data = downloader.search_wallhaven(page=1)
    
    if data and 'data' in data:
        print(f"✅ API 连接成功！")
        print(f"获取到 {len(data['data'])} 个壁纸")
        if data['data']:
            sample = data['data'][0]
            print(f"\n示例壁纸信息:")
            print(f"  ID: {sample.get('id')}")
            print(f"  分辨率: {sample.get('resolution')}")
            print(f"  URL: {sample.get('path', 'N/A')[:50]}...")
        return True
    else:
        print("❌ API 连接失败！")
        return False


def test_url_extraction():
    """测试 URL 提取"""
    print("\n" + "=" * 50)
    print("📋 测试 2: URL 提取")
    print("=" * 50)
    
    downloader = WallhavenImageDownloader()
    urls = downloader.get_unique_image_urls(5)
    
    print(f"✅ 成功提取 {len(urls)} 个图片 URL")
    for i, (url, wall_id, item) in enumerate(urls[:3], 1):
        print(f"\n  图片 {i}:")
        print(f"    ID: {wall_id}")
        print(f"    分辨率: {item.get('resolution')}")
        print(f"    URL: {url[:60]}...")
    
    return len(urls) > 0


def test_database():
    """测试数据库操作"""
    print("\n" + "=" * 50)
    print("📋 测试 3: 数据库操作")
    print("=" * 50)
    
    downloader = WallhavenImageDownloader()
    
    # 测试 insert_image
    test_succeeded = downloader.insert_image(
        wallhaven_id='test_id_123',
        name='test_image.jpg',
        hash_value='abc123def456',
        url='https://example.com/test.jpg',
        source_url='https://wallhaven.cc/w/test_id_123',
        resolution='1920x1080'
    )
    
    if test_succeeded:
        print("✅ 数据库写入成功！")
        
        # 检查是否可以查询到
        existing_ids = downloader.get_existing_wallhaven_ids()
        if 'test_id_123' in existing_ids:
            print("✅ 数据库查询成功！")
            return True
    
    print("❌ 数据库操作失败！")
    return False


def test_configuration():
    """测试配置"""
    print("\n" + "=" * 50)
    print("📋 测试 4: 配置检查")
    print("=" * 50)
    
    print("✅ Wallhaven 配置项：")
    for key, value in WALLHAVEN_CONFIG.items():
        if key == 'api_key' and value:
            print(f"  {key}: *** (已设置)")
        else:
            print(f"  {key}: {value}")
    
    return True


def main():
    """运行所有测试"""
    print("🧪 开始 Wallhaven 下载器测试...\n")
    
    tests = [
        ("API 连接", test_api_connection),
        ("URL 提取", test_url_extraction),
        ("数据库", test_database),
        ("配置检查", test_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Wallhaven 下载器配置正确。")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查配置。")


if __name__ == "__main__":
    main()
