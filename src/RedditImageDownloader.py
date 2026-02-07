import re
import requests
import os
import logging
from datetime import datetime
from config import REDDIT_CONFIG
from src.utils import get_existing_hashes, extract_image_url, is_valid_image
import hashlib
import time
import concurrent.futures
import sqlite3
from contextlib import contextmanager
from src.utils import existed_picture
class RedditImageDownloader:
    def __init__(self):
        # 初始化日志系统
        self._setup_logging()

        self.logger = logging.getLogger('RedditImageDownloader')
        self.logger.info("🚀 初始化 Reddit 图片下载器...")

        self.save_dir = REDDIT_CONFIG['save_dir']
        self.reddit_url = REDDIT_CONFIG['reddit_url']
        self.max_posts = REDDIT_CONFIG['max_posts']
        self.headers = REDDIT_CONFIG['headers']
        self.request_timeout = REDDIT_CONFIG['request_timeout']
        self.download_timeout = REDDIT_CONFIG['download_timeout']
        self.sleep_time = REDDIT_CONFIG['sleep_time']
        self.db_path = REDDIT_CONFIG['db_path']
        self.conn_pool = []
        self.after = REDDIT_CONFIG['after']  # 用于分页的after参数
        self.max_connections = 5
        self.max_images = REDDIT_CONFIG['max_images']
        # 搜索超时与无进展限制
        self.max_search_seconds = REDDIT_CONFIG.get('max_search_seconds', 300)
        self.max_empty_batches = REDDIT_CONFIG.get('max_empty_batches', 5)

        # 创建保存目录
        os.makedirs(self.save_dir, exist_ok=True)
        self.logger.info(f"📁 图片保存目录: {self.save_dir}")
        # 初始化数据库
        self.init_database()

        # 获取现有图片哈希值
        self.existing_hashes = get_existing_hashes(self.save_dir, self.db_path)
        self.logger.info(f"🔍 发现 {len(self.existing_hashes)} 个已存在的图片文件")
        self.existed_picture=existed_picture(self.db_path)
        self.logger.info(f"🔍 文件中有 {len(self.existed_picture)} 个图片")

        self.logger.info("✅ 下载器初始化完成")

    def _setup_logging(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # 设置日志文件名（带时间戳）
        log_filename = f"{log_dir}/reddit_downloader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler()  # 同时输出到控制台
            ]
        )

        # 设置第三方库的日志级别为WARNING，避免过多调试信息
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)

    @contextmanager
    def get_db_connection(self):
        """数据库连接上下文管理器"""
        if self.conn_pool:
            conn = self.conn_pool.pop()
            self.logger.debug("♻️ 从连接池获取数据库连接")
        else:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            self.logger.debug("🆕 创建新的数据库连接")

        try:
            yield conn
            conn.commit()
            self.logger.debug("✅ 数据库事务提交成功")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"❌ 数据库事务回滚: {e}")
            raise
        finally:
            self.conn_pool.append(conn)
            self.logger.debug("🔙 数据库连接归还到连接池")

    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    hash TEXT NOT NULL UNIQUE,
                    url TEXT NOT NULL UNIQUE,
                    stable INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON images(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON images(hash)')
            conn.commit()
            conn.close()
            self.logger.info("✅ 数据库初始化完成")
        except sqlite3.Error as e:
            self.logger.error(f"❌ 数据库初始化错误: {e}")

    def insert_image(self, name, hash_value, url):
        """插入图片信息到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO images (name, hash, url) VALUES (?, ?, ?)", (name, hash_value, url))
            conn.commit()
            conn.close()
            self.logger.info(f"💾 图片信息已保存到数据库: {name}")
            return True
        except sqlite3.IntegrityError as e:
            if "hash" in str(e):
                self.logger.warning(f"⏭️ 图片hash已存在，跳过: {url}")
            elif "url" in str(e):
                self.logger.warning(f"⏭️ 图片URL已存在，跳过: {url}")
            return False
        except sqlite3.Error as e:
            self.logger.error(f"❌ 插入数据库错误: {e}")
            return False

    def get_file_extension(self, content_type, url):
        """从内容类型或URL中获取文件扩展名"""
        # 从内容类型获取扩展名
        if 'image/jpeg' in content_type:
            return 'jpg'
        elif 'image/png' in content_type:
            return 'png'
        elif 'image/gif' in content_type:
            return 'gif'
        elif 'image/webp' in content_type:
            return 'webp'

        # 从URL获取扩展名
        if url.lower().endswith('.jpg') or url.lower().endswith('.jpeg'):
            return 'jpg'
        elif url.lower().endswith('.png'):
            return 'png'
        elif url.lower().endswith('.gif'):
            return 'gif'
        elif url.lower().endswith('.webp'):
            return 'webp'

        # 默认使用 jpg
        return 'jpg'

    def calculate_image_hash(self, image_data):
        """计算图片的哈希值"""
        return hashlib.md5(image_data).hexdigest()

    def generate_safe_filename(self, image_hash, file_extension):
        """生成安全的文件名，移除非法字符"""
        # 移除哈希值中的非法字符
        safe_hash = re.sub(r'[^a-zA-Z0-9]', '', image_hash)

        # 确保扩展名有效
        safe_extension = file_extension.lower()
        if safe_extension not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            safe_extension = 'jpg'  # 默认使用jpg格式

        return f"{safe_hash}.{safe_extension}"

    def generate_filename(self, image_hash, file_extension):
        """生成图片文件名，格式为: 哈希值.扩展名"""
        return f"{image_hash}.{file_extension}"

    def get_unique_image_urls(self, target_count):
        """获取指定数量的唯一图片URL"""
        self.logger.info(f"🎯 开始获取 {target_count} 个唯一图片URL...")

        unique_urls = []
        processed_posts = 0
        after = self.after
       # self.logger.info(f"🔍 after 为 {after if after else 0}")

        existing_urls = self.get_existing_urls()
        self.logger.info(f"📊 数据库中已有 {len(existing_urls)} 个图片记录")
       # existed_picture=src.utils.existed_picture(self.db_path)
       # self.logger.info(f"📊 文件中已有 {len(existed_picture)} 个图片文件")

        # 超时/无进展控制
        start_time = time.time()
        empty_batch_counter = 0
        max_search_seconds = getattr(self, 'max_search_seconds', 300)
        max_empty_batches = getattr(self, 'max_empty_batches', 5)

        def process_post_batch(posts_batch):
            """并行处理一批帖子"""
            batch_urls = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = {}
                for child in posts_batch:
                    if len(batch_urls) >= target_count - len(unique_urls):
                        break

                    flair = child['data'].get('link_flair_text', '')
                    if flair and ('Desktop' in flair or '桌面' in flair):
                        permalink = child['data']['permalink']
                        full_url = f"https://www.reddit.com{permalink}"
                        future = executor.submit(self.fetch_post_image_url, full_url)
                        futures[future] = full_url
                        self.logger.debug(f"🔍 提交帖子处理任务: {full_url}")

                for future in concurrent.futures.as_completed(futures):
                    url = futures[future]
                    try:
                        image_url = future.result(timeout=10)
                        if image_url and image_url not in existing_urls:
                            batch_urls.append(image_url)
                            existing_urls.add(image_url)
                            self.logger.debug(f"✅ 发现新图片URL: {image_url}")
                        else:
                            self.logger.debug(f"⏭️ 跳过重复或无效URL: {url}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ 处理帖子失败: {url} - {e}")

            return batch_urls

        batch_count = 0
        while len(unique_urls) < self.max_images:
            batch_count += 1
            self.logger.info(f"📥 获取第 {batch_count} 批帖子...")

            api_url = f"https://www.reddit.com/r/Animewallpaper/.json?limit={target_count}"
            if after:
                api_url += f"&after={after}"

            try:
                response = requests.get(api_url, headers=self.headers)
                if response.status_code != 200:
                    self.logger.error(f"❌ API请求失败，状态码: {response.status_code}")
                    break

                data = response.json()
                posts = data['data']['children']
                self.logger.info(f"📄 获取到 {len(posts)} 个帖子")

                if not posts:
                    self.logger.warning("⚠️ 没有更多帖子可获取")
                    break

                batch_size = 10
                prev_count = len(unique_urls)
                for i in range(0, len(posts), batch_size):
                    batch = posts[i:i+batch_size]
                    batch_urls = process_post_batch(batch)
                    unique_urls.extend(batch_urls)
                    self.logger.info(f"📊 当前唯一URL数量: {len(unique_urls)}/{self.max_images}")

                    if len(unique_urls) >= self.max_images:
                        self.logger.info("✅ 已达到目标URL数量")
                        break

                # 检查是否有进展
                if len(unique_urls) == prev_count:
                    empty_batch_counter += 1
                    self.logger.info(f"⚠️ 未在当前批次找到新图片（连续 {empty_batch_counter}/{max_empty_batches} 次）")
                else:
                    empty_batch_counter = 0

                # 如果连续多个批次无进展，则退出
                if empty_batch_counter >= max_empty_batches:
                    self.logger.warning(f"⚠️ 连续 {max_empty_batches} 个批次没有新图片，停止搜索")
                    break

                # 检查时间超时
                elapsed = time.time() - start_time
                if elapsed >= max_search_seconds:
                    self.logger.warning(f"⏱️ 搜索超时（{elapsed:.1f}s），停止搜索")
                    break

                after = data['data'].get('after')
                self.logger.info(f"🔍 after 为 {after if after else 0}")
                if not after:
                    self.logger.warning("⚠️ 已到达帖子列表末尾")
                    break

            except Exception as e:
                self.logger.error(f"❌ 获取帖子列表失败: {e}")
                break

        self.logger.info(f"✅ URL获取完成，共找到 {len(unique_urls)} 个唯一图片URL")
        return unique_urls[:target_count]

    def fetch_post_image_url(self, post_url):
        """获取单个帖子的图片URL"""
        try:
            self.logger.debug(f"🌐 获取帖子内容: {post_url}")
            response = requests.get(post_url + ".json", headers=self.headers, timeout=8)
            if response.status_code == 200:
                image_url = extract_image_url(response.json())
                if image_url:
                    self.logger.debug(f"✅ 成功提取图片URL: {image_url}")
                return image_url
            else:
                self.logger.warning(f"⚠️ 帖子请求失败，状态码: {response.status_code}")
        except Exception as e:
            self.logger.warning(f"⚠️ 获取帖子图片URL失败: {post_url} - {e}")
        return None

    def get_existing_urls(self):
        """从数据库获取所有已存在的图片URL"""
        existing_urls = set()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM images")
            existing_urls = {row[0] for row in cursor.fetchall()}
        self.logger.debug(f"📋 从数据库加载 {len(existing_urls)} 个现有URL")
        return existing_urls

    def is_likely_duplicate(self, image_url):
        """基于URL特征判断图片是否可能重复"""
        # 方法1: 检查文件名是否已存在（快速但不完全准确）
        filename = image_url.split('/')[-1].split('?')[0]
        potential_path = os.path.join(self.save_dir, filename)
        if os.path.exists(potential_path):
            return True
        return False

    def rate_limit_delay(self):
        """控制请求频率"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed + random.uniform(0.1, 0.5)
            print(f"⏳ 请求间隔控制: 等待 {sleep_time:.1f} 秒")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def is_valid_image_url(self, url):
        """检查URL是否指向有效图片"""
        # 检查URL扩展名
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if not any(url.lower().endswith(ext) for ext in valid_extensions):
            return False

        # 检查URL格式（i.redd.it是Reddit的图片CDN）
        if 'i.redd.it' not in url:
            return False

        return True

    def download_image_optimized(self, url):
        """优化后的下载方法"""
        try:
            # 发送请求
            response = requests.get(
                url,
                headers=self.headers,
                stream=True,
                timeout=self.download_timeout
            )
            response.raise_for_status()

            # 验证内容类型
            content_type = response.headers.get('content-type', '').lower()
            if 'image' not in content_type:
                self.logger.warning(f"⚠️ 非图片内容类型: {content_type} - {url}")
                return False

            # 获取文件扩展名
            file_extension = self.get_file_extension(content_type, url)

            # 读取内容并计算哈希
            image_data = response.content
            image_hash = self.calculate_image_hash(image_data)

            # 生成安全的文件名
            filename = self.generate_safe_filename(image_hash, file_extension)

            # 确保下载目录存在
            os.makedirs(self.save_dir, exist_ok=True)

            # 构造保存路径
            save_path = os.path.join(self.save_dir, filename)

            # 记录路径信息
            self.logger.debug(f"💾 保存路径: {save_path}")

            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(image_data)
            self.insert_image(filename, image_hash, url)
            # 记录成功信息
            self.logger.info(f"✅ 下载成功: {url} -> {filename}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ 网络错误: {url} - {e}")
        except OSError as e:
            self.logger.error(f"❌ 文件系统错误: {url} - {e}")
        except Exception as e:
            self.logger.error(f"❌ 未知错误: {url} - {e}")

        return False

    def mark_missing_images_unstable(self):
        """扫描保存目录文件，若数据库记录的图片文件不存在则将其 stable 设为 0"""
        self.logger.info("🔁 检查数据库记录与本地文件一致性...")
        try:
            files = {f for f in os.listdir(self.save_dir) if os.path.isfile(os.path.join(self.save_dir, f))}
        except Exception as e:
            self.logger.error(f"❌ 无法访问保存目录: {e}")
            return 0

        updated = 0
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, stable FROM images")
                rows = cursor.fetchall()
                for row in rows:
                    row_id = row['id']
                    name = row['name']
                    stable = row['stable']
                    if name not in files and stable != 0:
                        cursor.execute("UPDATE images SET stable = 0 WHERE id = ?", (row_id,))
                        updated += 1
            if updated:
                self.logger.info(f"⚠️ 标记 {updated} 条数据库记录为 unstable (stable=0)")
            else:
                self.logger.info("✅ 数据库中的图片文件均存在，无需更新")
        except sqlite3.Error as e:
            self.logger.error(f"❌ 更新数据库时出错: {e}")
        return updated

    def run(self):
        """运行下载任务"""
        self.logger.info("🎬 开始运行下载任务...")
        # 重新加载现有的hash和URL集合
        self.existing_hashes = get_existing_hashes(self.save_dir, self.db_path)
        self.logger.info(f"🔍 重新加载 {len(self.existing_hashes)} 个现有图片哈希")

        # 将数据库与磁盘文件同步：标记缺失的图片为 unstable
      #  updated_count = self.mark_missing_images_unstable()
      #  if updated_count:
      #      self.logger.info(f"🔧 共标记 {updated_count} 条记录为 unstable")

        # 获取唯一图片URL
        target_count = self.max_posts
        max_image = self.max_images
        image_urls = self.get_unique_image_urls(target_count)

        if len(image_urls) < target_count:
            self.logger.warning(f"⚠️ 只找到 {len(image_urls)} 个唯一图片，目标为 {max_image} 个")
        else:
            self.logger.info(f"✅ 成功找到 {len(image_urls)} 个唯一图片")

        # 并发下载
        self.logger.info("🚀 开始并发下载图片...")
        processed = 0
        successful_downloads = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(self.download_image_optimized, url): url for url in image_urls}
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                processed += 1
                try:
                    if future.result():
                        successful_downloads += 1
                        self.logger.info(f"✅ 进度: {successful_downloads}/{len(image_urls)} - {url}")
                    else:
                        self.logger.warning(f"⚠️ 下载失败或跳过: {url}")
                except Exception as e:
                    self.logger.error(f"❌ 下载异常: {e} - {url}")

                # 每10个进度报告一次
                if processed % 10 == 0:
                    self.logger.info(f"📊 处理进度: {processed}/{len(image_urls)}")

        # 最终统计
        total_in_db = len(self.get_existing_urls())
        self.logger.info(f"🎉 任务完成！成功下载 {successful_downloads} 个唯一图片")
        self.logger.info(f"📊 数据库中现有 {total_in_db} 个图片记录")

        # 性能统计
        success_rate = (successful_downloads / len(image_urls)) * 100 if image_urls else 0
        self.logger.info(f"📈 成功率: {success_rate:.1f}%")