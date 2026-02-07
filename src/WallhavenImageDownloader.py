import requests
import os
import logging
import hashlib
import time
import sqlite3
import re
import concurrent.futures
from datetime import datetime
from contextlib import contextmanager
from urllib.parse import urlencode
from config import WALLHAVEN_CONFIG
from src.utils import get_existing_hashes, is_valid_image


class WallhavenImageDownloader:
    def __init__(self):
        # 初始化日志系统
        self._setup_logging()

        self.logger = logging.getLogger('WallhavenImageDownloader')
        self.logger.info("🚀 初始化 Wallhaven 图片下载器...")

        self.save_dir = WALLHAVEN_CONFIG.get('save_dir')
        self.api_url = WALLHAVEN_CONFIG.get('api_url')
        self.api_key = WALLHAVEN_CONFIG.get('api_key')  # 可选
        self.max_images = WALLHAVEN_CONFIG.get('max_images')
        self.search_query = WALLHAVEN_CONFIG.get('search_query')
        self.categories = WALLHAVEN_CONFIG.get('categories')  # 1-general, 2-anime, 4-people (可组合)
        self.purity = WALLHAVEN_CONFIG.get('purity')  # 0-SFW, 1-sketchy, 2-NSFW (可组合)
        self.sorting = WALLHAVEN_CONFIG.get('sorting')  # date_added, relevance, random, views, favorites
        self.order = WALLHAVEN_CONFIG.get('order')  # desc, asc
        self.atleast = WALLHAVEN_CONFIG.get('atleast')  # 特定分辨率，如 ['1920x1080', '2560x1440']
        self.ratios = WALLHAVEN_CONFIG.get('ratios')  # 宽高比，如 ['16x9', '21x9']
        self.max_pages = WALLHAVEN_CONFIG.get('max_pages')  # 最大页数，用于控制下载数量
        self.default_pages = WALLHAVEN_CONFIG.get('default_pages')  # 默认打开多少页以获取更多图片
        self.topRange = WALLHAVEN_CONFIG.get('topRange')  # 排序范围，如 '1d', '3d', '1w', '1M', '3M', '6M', '1y'
        # 为 Wallhaven API 优化的 headers（简化版本以确保兼容性）
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        self.request_timeout = WALLHAVEN_CONFIG.get('request_timeout')
        self.download_timeout = WALLHAVEN_CONFIG.get('download_timeout')
        self.sleep_time = WALLHAVEN_CONFIG.get('sleep_time')
        self.db_path = WALLHAVEN_CONFIG.get('db_path')
        self.conn_pool = []
        self.max_connections = 5

        # 创建保存目录
        os.makedirs(self.save_dir, exist_ok=True)
        self.logger.info(f"📁 图片保存目录: {self.save_dir}")

        # 初始化数据库
        self.init_database()
        # 获取现有图片哈希值
        self.existing_hashes = get_existing_hashes(self.save_dir, self.db_path)
        self.logger.info(f"🔍 发现 {len(self.existing_hashes)} 个已存在的图片文件")
        existed_picture=existed_picture(self.db_path)
        self.logger.info(f"🔍 文件中有 {len(existed_picture)} 个已存在的图片文件")
        self.logger.info("✅ Wallhaven下载器初始化完成")

    def _setup_logging(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # 设置日志文件名（带时间戳）
        log_filename = f"{log_dir}/wallhaven_downloader_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

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
                    wallhaven_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    hash TEXT NOT NULL UNIQUE,
                    url TEXT NOT NULL UNIQUE,
                    source_url TEXT,
                    resolution TEXT,
                    stable INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_url ON images(url)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_hash ON images(hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_wallhaven_id ON images(wallhaven_id)')
            conn.commit()
            conn.close()
            self.logger.info("✅ 数据库初始化完成")
        except sqlite3.Error as e:
            self.logger.error(f"❌ 数据库初始化错误: {e}")

    def insert_image(self, wallhaven_id, name, hash_value, url, source_url, resolution='unknown'):
        """插入图片信息到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO images (wallhaven_id, name, hash, url, source_url, resolution) VALUES (?, ?, ?, ?, ?, ?)",
                (wallhaven_id, name, hash_value, url, source_url, resolution)
            )
            conn.commit()
            conn.close()
            self.logger.info(f"💾 图片信息已保存到数据库: {name}")
            return True
        except sqlite3.IntegrityError as e:
            if "hash" in str(e):
                self.logger.warning(f"⏭️ 图片hash已存在，跳过: {url}")
            elif "url" in str(e):
                self.logger.warning(f"⏭️ 图片URL已存在，跳过: {url}")
            elif "wallhaven_id" in str(e):
                self.logger.warning(f"⏭️ Wallhaven ID已存在，跳过: {wallhaven_id}")
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

    def search_wallhaven(self, page=1, retries=3):
        """搜索Wallhaven并获取图片数据，支持自动重试"""
        for attempt in range(retries):
            try:
                params = {
                    'page': page,
                    'categories': self.categories,
                    'purity': self.purity,
                    'sorting': self.sorting,
                    'order': self.order,
                }

                # 添加可选参数
                if self.search_query:
                    params['q'] = self.search_query
                if self.api_key:
                    params['apikey'] = self.api_key
                if self.atleast:
                    params['atleast'] = self.atleast
                if self.ratios:
                    params['ratios'] = self.ratios
                if self.topRange and self.sorting == 'toplist':
                    params['topRange'] = self.topRange  
                self.logger.debug(f"🔍 请求参数: {params}")
                full_url = f"{self.api_url}?{urlencode(params)}"
                self.logger.info(f"🔗 完整请求地址: {full_url}")
                response = requests.get(
                    self.api_url,
                    params=params,
                    headers=self.headers,
                    timeout=self.request_timeout
                )

                self.logger.debug(f"📡 API 响应状态码: {response.status_code}")
                
                if response.status_code != 200:
                    self.logger.error(f"❌ API请求失败，状态码: {response.status_code}")
                    self.logger.debug(f"响应内容: {response.text[:200]}")
                    
                    # 429 太多请求，等待后重试
                    if response.status_code == 429:
                        wait_time = 5 * (attempt + 1)
                        self.logger.warning(f"⏳ 速率限制，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    
                    # 5xx 服务器错误，等待后重试
                    if 500 <= response.status_code < 600:
                        wait_time = 3 * (attempt + 1)
                        self.logger.warning(f"⏳ 服务器错误，等待 {wait_time} 秒后重试...")
                        if attempt < retries - 1:
                            time.sleep(wait_time)
                            continue
                    
                    return None

                # 检查响应是否为空
                if not response.text:
                    self.logger.error("❌ API 返回空响应")
                    if attempt < retries - 1:
                        wait_time = 2 * (attempt + 1)
                        self.logger.warning(f"⏳ 等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    return None

                try:
                    data = response.json()
                    self.logger.info(f"📄 获取到 {len(data.get('data', []))} 个壁纸")
                    return data
                except ValueError as json_error:
                    self.logger.error(f"❌ JSON解析失败: {json_error}")
                    self.logger.debug(f"响应内容（前 500 字符）: {response.text[:500]}")
                    if attempt < retries - 1:
                        wait_time = 2 * (attempt + 1)
                        self.logger.warning(f"⏳ JSON 解析失败，等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                    return None

            except requests.exceptions.Timeout:
                self.logger.warning(f"⏳ 请求超时（第 {attempt + 1}/{retries} 次尝试）")
                if attempt < retries - 1:
                    wait_time = 2 * (attempt + 1)
                    self.logger.warning(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                self.logger.error(f"❌ 所有重试均失败（请求超时）")
                return None
                
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"⏳ 网络连接错误（第 {attempt + 1}/{retries} 次尝试）: {e}")
                if attempt < retries - 1:
                    wait_time = 3 * (attempt + 1)
                    self.logger.warning(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                self.logger.error(f"❌ 所有重试均失败（网络连接错误）")
                return None
                
            except Exception as e:
                self.logger.error(f"❌ 搜索Wallhaven失败（第 {attempt + 1}/{retries} 次尝试）: {e}")
                if attempt < retries - 1:
                    wait_time = 2 * (attempt + 1)
                    self.logger.warning(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                return None
        
        return None

    def get_unique_image_urls(self, target_count):
        """获取指定数量的唯一图片URL"""
        self.logger.info(f"🎯 开始获取 {target_count} 个唯一图片URL...")

        unique_urls = []
        unique_wallhaven_ids = set()
        existing_urls = self.get_existing_urls()
        existing_ids = self.get_existing_wallhaven_ids()

        self.logger.info(f"📊 数据库中已有 {len(existing_urls)} 个图片记录")

        page = self.default_pages 
        max_pages = self.max_pages  # 最多尝试5页
        
        while len(unique_urls) < target_count and page <= max_pages:
            self.logger.info(f"📥 获取第 {page} 页...")

            data = self.search_wallhaven(page=page)
            if not data or 'data' not in data:
                self.logger.warning("⚠️ 没有更多数据可获取")
                break

            items = data.get('data', [])
            if not items:
                self.logger.warning("⚠️ 当前页面没有图片")
                break

            for item in items:
                if len(unique_urls) >= target_count:
                    break

                try:
                    wallhaven_id = item.get('id')
                    path = item.get('path')  # 高清壁纸URL
                    
                    if not path or wallhaven_id in existing_ids or path in existing_urls:
                        continue

                    unique_urls.append((path, wallhaven_id, item))
                    unique_wallhaven_ids.add(wallhaven_id)
                    self.logger.debug(f"✅ 发现新图片: {wallhaven_id}")

                except (KeyError, TypeError) as e:
                    self.logger.warning(f"⚠️ 解析图片数据失败: {e}")
                    continue

            self.logger.info(f"📊 当前唯一URL数量: {len(unique_urls)}/{target_count}")
            page += 1
            time.sleep(self.sleep_time)  # 遵守速率限制

        self.logger.info(f"✅ URL获取完成，共找到 {len(unique_urls)} 个唯一图片URL")
        return unique_urls[:target_count]

    def get_existing_urls(self):
        """从数据库获取所有已存在的图片URL"""
        existing_urls = set()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url FROM images")
            existing_urls = {row[0] for row in cursor.fetchall()}
        self.logger.debug(f"📋 从数据库加载 {len(existing_urls)} 个现有URL")
        return existing_urls

    def get_existing_wallhaven_ids(self):
        """从数据库获取所有已存在的Wallhaven ID"""
        existing_ids = set()
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT wallhaven_id FROM images")
            existing_ids = {row[0] for row in cursor.fetchall()}
        self.logger.debug(f"📋 从数据库加载 {len(existing_ids)} 个现有Wallhaven ID")
        return existing_ids

    def download_image_optimized(self, url, wallhaven_id, item_data):
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
            
            # 验证图片有效性
            if not is_valid_image(image_data, content_type):
                self.logger.warning(f"⚠️ 无效的图片数据: {url}")
                return False

            image_hash = self.calculate_image_hash(image_data)

            # 生成安全的文件名
            filename = self.generate_safe_filename(image_hash, file_extension)

            # 确保下载目录存在
            os.makedirs(self.save_dir, exist_ok=True)

            # 构造保存路径
            save_path = os.path.join(self.save_dir, filename)

            # 保存图片
            with open(save_path, 'wb') as f:
                f.write(image_data)

            # 获取分辨率信息
            resolution = item_data.get('resolution', 'unknown')
            source_url = item_data.get('short_url', url)

            # 保存到数据库
            self.insert_image(wallhaven_id, filename, image_hash, url, source_url, resolution)

            # 记录成功信息
            self.logger.info(f"✅ 下载成功: {wallhaven_id} -> {filename}")
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
        self.logger.info("🎬 开始运行Wallhaven下载任务...")
        # 重新加载现有的hash和URL集合
        self.existing_hashes = get_existing_hashes(self.save_dir, self.db_path)
        self.logger.info(f"🔍 重新加载 {len(self.existing_hashes)} 个现有图片哈希")

        # 将数据库与磁盘文件同步：标记缺失的图片为 unstable
      #  updated_count = self.mark_missing_images_unstable()
      #  if updated_count:
      #      self.logger.info(f"🔧 共标记 {updated_count} 条记录为 unstable")

        # 获取唯一图片URL
        target_count = self.max_images
        image_urls = self.get_unique_image_urls(target_count)

        if len(image_urls) < target_count:
            self.logger.warning(f"⚠️ 只找到 {len(image_urls)} 个唯一图片，目标为 {target_count} 个")
        else:
            self.logger.info(f"✅ 成功找到 {len(image_urls)} 个唯一图片")

        # 并发下载
        self.logger.info("🚀 开始并发下载图片...")
        processed = 0
        successful_downloads = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.download_image_optimized, url, wallhaven_id, item_data): url 
                for url, wallhaven_id, item_data in image_urls
            }
            for future in concurrent.futures.as_completed(futures):
                url = futures[future]
                processed += 1
                try:
                    if future.result():
                        successful_downloads += 1
                        self.logger.info(f"✅ 进度: {successful_downloads}/{len(image_urls)}")
                    else:
                        self.logger.warning(f"⚠️ 下载失败或跳过: {url}")
                except Exception as e:
                    self.logger.error(f"❌ 下载异常: {e}")

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
