import sqlite3
import requests
import os
import logging
import hashlib
import time
import concurrent.futures
from datetime import datetime
from contextlib import contextmanager
from src.utils import is_valid_image


class DatabaseImageDownloader:
    """从数据库中下载图片的下载器"""
    
    def __init__(self, db_path, save_dir, source='all'):
        """
        初始化数据库图片下载器
        
        Args:
            db_path: SQLite数据库路径
            save_dir: 图片保存目录
            source: 图片源 ('reddit', 'wallhaven', 'all')
        """
        self._setup_logging()
        self.logger = logging.getLogger('DatabaseImageDownloader')
        self.logger.info(f"🚀 初始化数据库图片下载器... (源: {source})")
        
        self.db_path = db_path
        self.save_dir = save_dir
        self.source = source
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        self.request_timeout = 10
        self.download_timeout = 20
        self.sleep_time = 1
        self.max_workers = 5
        
        # 创建保存目录
        os.makedirs(self.save_dir, exist_ok=True)
        self.logger.info(f"📁 图片保存目录: {self.save_dir}")
        
        self.logger.info("✅ 下载器初始化完成")

    def _setup_logging(self):
        """设置日志系统"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"{log_dir}/database_downloader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

    @contextmanager
    def get_db_connection(self):
        """数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"❌ 数据库事务回滚: {e}")
            raise
        finally:
            conn.close()

    def get_images_from_db(self):
        """从数据库获取所有未下载的图片记录"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查表是否存在
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
                if not cursor.fetchone():
                    self.logger.warning("⚠️ 数据库中没有images表，返回空列表")
                    return []
                
                # 获取所有图片
                cursor.execute("SELECT id, name, url, hash, wallhaven_id FROM images where stable=1")
                images = cursor.fetchall()
                
                self.logger.info(f"📊 从数据库获取 {len(images)} 条图片记录")
                return [dict(row) for row in images]
        
        except sqlite3.Error as e:
            self.logger.error(f"❌ 数据库查询错误: {e}")
            return []

    def generate_filename(self, image_hash, url, wallhaven_id=None):
        """生成安全的文件名"""
        import re
        # 提取扩展名
        extension = self._get_extension_from_url(url)
        
        # 如果是 Wallhaven 图片，使用 wallhaven_id 生成文件名
        if wallhaven_id:
            safe_id = re.sub(r'[^a-zA-Z0-9]', '', wallhaven_id)
            return f"wallhaven_{safe_id}.{extension}"
        else:
            return f"{image_hash}.{extension}"

    def _get_extension_from_url(self, url):
        """从URL获取文件扩展名"""
        # 移除查询参数
        path = url.split('?')[0].lower()
        
        if path.endswith('.jpg') or path.endswith('.jpeg'):
            return 'jpg'
        elif path.endswith('.png'):
            return 'png'
        elif path.endswith('.gif'):
            return 'gif'
        elif path.endswith('.webp'):
            return 'webp'
        elif path.endswith('.avif'):
            return 'avif'
        else:
            return 'jpg'  # 默认使用jpg

    def download_image(self, image_data):
        """下载单个图片"""
        url = image_data['url']
        image_hash = image_data['hash']
        wallhaven_id = image_data.get('wallhaven_id')
        filename = self.generate_filename(image_hash, url, wallhaven_id)
        filepath = os.path.join(self.save_dir, filename)
        
        # 检查文件是否已存在
        if os.path.exists(filepath):
            self.logger.debug(f"⏭️ 图片已存在，跳过: {filename}")
            return True
        
        try:
            self.logger.info(f"⬇️ 开始下载: {filename} <- {url}")
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.download_timeout,
                stream=True
            )
            response.raise_for_status()
            
            # 验证是否为有效图片
            content_type = response.headers.get('content-type', '')
            if not is_valid_image(response.content, content_type):
                self.logger.warning(f"⚠️ 无效的图片格式，跳过: {url}")
                return False
            
            # 保存文件
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.logger.info(f"✅ 下载完成: {filename}")
            time.sleep(self.sleep_time)  # 速率限制
            return True
        
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"⚠️ 下载失败: {url} - {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ 保存文件错误: {filepath} - {e}")
            return False

    def run(self):
        """运行下载器"""
        self.logger.info("=" * 60)
        self.logger.info("🎬 开始下载数据库中的图片")
        self.logger.info("=" * 60)
        
        # 获取数据库中的图片
        images = self.get_images_from_db()
        
        if not images:
            self.logger.warning("⚠️ 数据库中没有图片记录，无法下载")
            return
        
        self.logger.info(f"📥 准备下载 {len(images)} 个图片...")
        
        # 并行下载
        downloaded_count = 0
        failed_count = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.download_image, img): img for img in images}
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        downloaded_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    self.logger.error(f"❌ 下载线程异常: {e}")
                    failed_count += 1
        
        # 输出统计信息
        self.logger.info("=" * 60)
        self.logger.info("📊 下载统计")
        self.logger.info(f"✅ 成功: {downloaded_count}")
        self.logger.info(f"⏭️  已存在: {len(images) - downloaded_count - failed_count}")
        self.logger.info(f"❌ 失败: {failed_count}")
        self.logger.info(f"📁 保存目录: {self.save_dir}")
        self.logger.info("=" * 60)


class RedditDatabaseDownloader(DatabaseImageDownloader):
    """Reddit数据库图片下载器"""
    
    def __init__(self, db_path, save_dir):
        super().__init__(db_path, save_dir, source='reddit')


class WallhavenDatabaseDownloader(DatabaseImageDownloader):
    """Wallhaven数据库图片下载器"""
    
    def __init__(self, db_path, save_dir):
        super().__init__(db_path, save_dir, source='wallhaven')
