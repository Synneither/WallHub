from src.RedditImageDownloader import RedditImageDownloader
from src.WallhavenImageDownloader import WallhavenImageDownloader
from src.DatabaseImageDownloader import (
    DatabaseImageDownloader,
    RedditDatabaseDownloader,
    WallhavenDatabaseDownloader
)
from config import REDDIT_CONFIG, WALLHAVEN_CONFIG
import os
import sys

def print_usage():
    """打印使用说明"""
    print("\n" + "=" * 60)
    print("📖 使用说明")
    print("=" * 60)
    print("\n下载新图片:")
    print("  python main.py reddit          - 从 Reddit 下载")
    print("  python main.py wallhaven       - 从 Wallhaven 下载")
    print("  python main.py all             - 从所有源下载")
    print("\n下载数据库中的图片:")
    print("  python main.py reddit-db       - 下载 Reddit 数据库中的图片")
    print("  python main.py wallhaven-db    - 下载 Wallhaven 数据库中的图片")
    print("  python main.py db-all          - 下载所有数据库中的图片")
    print("\n标记缺失图片为 unstable:")
    print("  python main.py mark-unstable           - 标记所有源数据库中缺失的本地图片为 unstable")
    print("  python main.py reddit-mark-unstable    - 仅标记 Reddit 源")
    print("  python main.py wallhaven-mark-unstable - 仅标记 Wallhaven 源")
    print("\n还原标记:")
    print("  python main.py restore-stable          - 将所有 unstable 记录还原为 stable")
    print("=" * 60 + "\n")

def main():
    try:
        # 检查命令行参数
        source = 'reddit'  # 默认源
        if len(sys.argv) > 1:
            source = sys.argv[1].lower()
        
        if source == 'reddit':
            print("🎬 选择 Reddit 下载器")
            downloader = RedditImageDownloader()
            downloader.run()
        
        elif source == 'wallhaven':
            print("🎬 选择 Wallhaven 下载器")
            downloader = WallhavenImageDownloader()
            downloader.run()
        
        elif source == 'all':
            print("🎬 选择所有下载源")
            # 运行所有下载器
            print("\n=== 开始 Reddit 下载 ===")
            reddit_downloader = RedditImageDownloader()
            reddit_downloader.run()
            
            print("\n=== 开始 Wallhaven 下载 ===")
            wallhaven_downloader = WallhavenImageDownloader()
            wallhaven_downloader.run()
        
        elif source == 'reddit-db':
            print("🎬 选择 Reddit 数据库下载器")
            db_downloader = RedditDatabaseDownloader(
                db_path=REDDIT_CONFIG['db_path'],
                save_dir=REDDIT_CONFIG['save_dir']
            )
            db_downloader.run()
        
        elif source == 'wallhaven-db':
            print("🎬 选择 Wallhaven 数据库下载器")
            db_downloader = WallhavenDatabaseDownloader(
                db_path=WALLHAVEN_CONFIG['db_path'],
                save_dir=WALLHAVEN_CONFIG['save_dir']
            )
            db_downloader.run()
        
        elif source == 'db-all':
            print("🎬 选择从所有数据库下载图片")
            
            print("\n=== 开始下载 Reddit 数据库图片 ===")
            reddit_db_downloader = RedditDatabaseDownloader(
                db_path=REDDIT_CONFIG['db_path'],
                save_dir=REDDIT_CONFIG['save_dir']
            )
            reddit_db_downloader.run()
            
            print("\n=== 开始下载 Wallhaven 数据库图片 ===")
            wallhaven_db_downloader = WallhavenDatabaseDownloader(
                db_path=WALLHAVEN_CONFIG['db_path'],
                save_dir=WALLHAVEN_CONFIG['save_dir']
            )
            wallhaven_db_downloader.run()

        elif source == 'mark-unstable':
            print("🔎 标记所有源缺失的本地图片为 unstable...")
            print("--- Reddit ---")
            reddit_downloader = RedditImageDownloader()
            r_updated = reddit_downloader.mark_missing_images_unstable()
            print(f"Reddit: 标记 {r_updated} 条记录为 unstable")

            print("--- Wallhaven ---")
            wallhaven_downloader = WallhavenImageDownloader()
            w_updated = wallhaven_downloader.mark_missing_images_unstable()
            print(f"Wallhaven: 标记 {w_updated} 条记录为 unstable")

            print("--- 同步文件夹到数据库 ---")
            import subprocess
            try:
                result = subprocess.run([sys.executable, 'sync_folder_to_db.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("同步完成")
                else:
                    print(f"同步失败: {result.stderr}")
            except Exception as e:
                print(f"同步出错: {e}")

        elif source == 'reddit-mark-unstable':
            print("🔎 标记 Reddit 源缺失的本地图片为 unstable...")
            reddit_downloader = RedditImageDownloader()
            updated = reddit_downloader.mark_missing_images_unstable()
            print(f"Reddit: 标记 {updated} 条记录为 unstable")

        elif source == 'wallhaven-mark-unstable':
            print("🔎 标记 Wallhaven 源缺失的本地图片为 unstable...")
            wallhaven_downloader = WallhavenImageDownloader()
            updated = wallhaven_downloader.mark_missing_images_unstable()
            print(f"Wallhaven: 标记 {updated} 条记录为 unstable")

            print("--- 同步 Wallhaven 文件夹到数据库 ---")
            import subprocess
            try:
                result = subprocess.run([sys.executable, 'sync_folder_to_db.py'], capture_output=True, text=True)
                if result.returncode == 0:
                    print("同步完成")
                else:
                    print(f"同步失败: {result.stderr}")
            except Exception as e:
                print(f"同步出错: {e}")

        elif source == 'restore-stable':
            print("🔄 还原所有 unstable 记录为 stable...")
            import sqlite3
            from config import REDDIT_CONFIG, WALLHAVEN_CONFIG
            
            restored_count = 0
            
            # 还原 Reddit 数据库
            try:
                conn = sqlite3.connect(REDDIT_CONFIG['db_path'])
                cursor = conn.cursor()
                cursor.execute("UPDATE images SET stable = 1 WHERE stable = 0")
                r_count = cursor.rowcount
                conn.commit()
                conn.close()
                print(f"Reddit: 还原 {r_count} 条记录")
                restored_count += r_count
            except Exception as e:
                print(f"Reddit 数据库还原失败: {e}")
            
            # 还原 Wallhaven 数据库
            try:
                conn = sqlite3.connect(WALLHAVEN_CONFIG['db_path'])
                cursor = conn.cursor()
                cursor.execute("UPDATE images SET stable = 1 WHERE stable = 0")
                w_count = cursor.rowcount
                conn.commit()
                conn.close()
                print(f"Wallhaven: 还原 {w_count} 条记录")
                restored_count += w_count
            except Exception as e:
                print(f"Wallhaven 数据库还原失败: {e}")
            
            print(f"总共还原 {restored_count} 条记录为 stable")
        
        else:
            print(f"❌ 未知的命令: {source}")
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
  main()