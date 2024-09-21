from click import echo
from pathlib import Path
from yt_dlp import YoutubeDL
# from vthread import VThreadPool
from fake_useragent import UserAgent
from contextlib import contextmanager
from easygui import textbox, multchoicebox
from httpx import Client, Limits, HTTPError, RequestError

class Spider():
    def __init__(self):
        self.encoding = 'utf-8'
        self.download_path = Path('G:/python-files/bilibili_mp4')
        self.main_url = 'https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid=379495735'
        self.suffix_url = 'https://api.bilibili.com/x/v3/fav/resource/list?media_id=%s&pn=%d&ps=20&keyword=&order=mtime&type=0&tid=0&platform=web'
        self.cookies= {
            "_uuid": "383C102106-6710F-78A9-5955-62221023F10B10704546infoc",
            "buvid_fp": "af76a10fadaa784005042442cb5d022e",
            "buvid3": "AB22BFA6-47D8-2D77-24C3-B61E85ECB6D534216infoc",
            "b_nut": "1717907534",
            "buvid4": "A2BDF80E-4EB4-CF94-0D80-ED4B5EF1F6DF34216-024060904-h1rRKImNnVnwnvTS+Q/66Q==",
            "CURRENT_FNVAL": "4048",
            "enable_web_push": "DISABLE",
            "header_theme_version": "CLOSE",
            "SESSDATA": "b606b03c,1733666124,c98d4*62CjAiwPDppjhDsO1ZpzhSNjY33O91sJgwoHqMDn5xPAsQUIg3oC_sxHi38XFMXZ2GC0gSVjFTVWRFRFgwck1GSnRGU3pHY3JQRWQzaVZDOERTVVFNNnI1R0FNd19DMm9BaEd3VzVRYndpd1luZTJWTFJyanVrRDRuLVNUXzVnbjdDOWkycGZwa3V3IIEC",
            "bili_jct": "f19a768be875d732ec2cc7e856c3a1f7",
            "DedeUserID": "379495735",
            "DedeUserID__ckMd5": "665ef26f541889f3",
            "home_feed_column": "5",
            "browser_resolution": "1890-916",
            "bp_t_offset_379495735": "942070766850015237",
            "bili_ticket": "eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTg0NDA3ODQsImlhdCI6MTcxODE4MTUyNCwicGx0IjotMX0.VhBv8STGhytjobix0RGSauwW6EddxwxyFNyCiQg5bs0",
            "bili_ticket_expires": "1718440724",
            "b_lsid": "DF8BBA11_1900BAEC369",
            "sid": "frxx9jcj",
            "rpdid": "|(J~kkm~kRkJ0J'u~u)u)JlkR"
        }
        self.ydl_opts = {
            'outtmpl': str(self.download_path) + '/%(title)s.%(ext)s',
            'external-downloader': 'aria2c',
            'downloader-args': {
                'aria2c': '-c -j 3 -x 8 -k 1M'
            }
        }
        # self.ydl = YoutubeDL(self.ydl_opts)
        self.client = Client(cookies=self.cookies, limits=Limits(max_keepalive_connections=10), timeout=None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    @contextmanager
    def video_downloader(self):
        try:
            yield YoutubeDL(self.ydl_opts)
        finally:
            pass

    @staticmethod
    def get_valid_path_name(name):
        return re.sub(r'[\/:*?"<>|]', '', name)

    def _get_response(self, url):
        try:
            headers = {
                'Origin': 'https://space.bilibili.com',
                'Referer': 'https://space.bilibili.com/379495735',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': UserAgent().random
            }
            response = self.client.get(url=url, headers=headers)
            response.raise_for_status()
            response.encoding = self.encoding
            return response
        except HTTPError as e:
            echo(f'HTTPError: {e}')
        except RequestError as e:
            echo(f'RequestError: {e}')
        except Exception as e:
            echo(f'Exception: {e}')
        return None

    def get_json(self, url):
        response = self._get_response(url)
        return response.json() if response else {}

    # @pool(10)
    def download_video(self, bv_id):
        video_url = f'https://www.bilibili.com/video/{bv_id}'
        with self.video_downloader() as ydl:
            ydl.download([video_url])

    def get_subpage(self, id):
        page_number  = 0
        while True:
            page_number += 1
            url = self.suffix_url % (id, page_number)
            json_data = self.get_json(url)
            medias = json_data.get('data', {}).get('medias', [])
            if not medias:
                break
            infos = [(media.get('bv_id'), media.get('title')) for media in medias]
            yield infos


    def start_download(self):
        json_data = self.get_json(self.main_url)
        for item in json_data.get('data', {}).get('list', []):
            # self.list_path = self.download_path / item.get('title', '').strip()
            # self.list_path.mkdir(parents=True, exist_ok=True)
            yield from self.get_subpage(item.get('id'))

class SpiderGUI:
    def __init__(self, spider):
        self.spider = spider
        download_info = list(self.spider.start_download())[0]
        # print(download_info)
        bv_ids = [info[0] for info in download_info]
        titles = [info[-1] for info in download_info]
        print(bv_ids, titles)
        list_titles = multchoicebox("请选择视频条目：", '哔哩哔哩收藏夹下载器', titles)
        if list_titles:
            list_bv_ids = [bv_ids[titles.index(list_title)] for list_title in list_titles]
            info = '\n\n'.join([f'{list_title}\n\n{"-" * 62}\n\n' for list_title in list_titles])
            textbox("您选择的结果：", '结果列表', f'{"-" * 62}\n\n{info}')
        # with VThreadPool(10) as pool:
        #     pool.map(self.spider.download_video, list_bv_ids)
        # echo('本次下载完毕！！！')


if __name__ == '__main__':
    spider = Spider()
    SpiderGUI(spider)