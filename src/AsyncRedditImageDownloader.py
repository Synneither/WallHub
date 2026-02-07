import aiohttp
import asyncio
from aiohttp import ClientTimeout
from RedditImageDownloader import RedditImageDownloader
class AsyncRedditImageDownloader(RedditImageDownloader):
    async def download_images_async(self, urls):
        """异步下载图片"""
        timeout = ClientTimeout(total=self.download_timeout)
        connector = aiohttp.TCPConnector(limit=20, limit_per_host=5)

        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers=self.headers
        ) as session:
            tasks = [self.download_single_image(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            successful = sum(1 for r in results if r is True)
            return successful

    async def download_single_image(self, session, url):
        """下载单张图片"""
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    # ... 其余处理逻辑与原来相同
                    return await self.process_image_data(image_data, url)
        except Exception as e:
            print(f"异步下载失败: {url} - {e}")
            return False
