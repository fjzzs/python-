# -*- coding: utf-8 -*-
'''
-------------------
@作  者: 枫子-samual
@日  期: 2024-06-09
@文件名: B站热搜.py
-------------------
'''

from click import echo
from vthread import pool
from parsel import Selector
from yt_dlp import YoutubeDL
from jsonpath import jsonpath
from fake_useragent import UserAgent
from easygui import textbox, multchoicebox
from httpx import Client, HTTPError, RequestError

class Spider():
    def __init__(self):
        self.encoding = 'utf-8'
        self.suffix_url = 'https://v.api.aa1.cn/api/bilibili-rs/'
        self.download_path = 'G:/python-files/bilibili_mp4'
        self.headers = {'Upgrade-Insecure-Requests': '1'}
        self.ydl_opts = {
            'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
            'external-downloader': 'aria2c',
            'downloader-args': {
                'aria2c': '-c -j 3 -x 8 -k 1M'
            }
        }
        self.ydl = YoutubeDL(self.ydl_opts)
        self.client = Client(timeout=None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def get_json(self, url):
        try:
            self.headers['User-Agent'] = UserAgent().random
            response = self.client.get(url=url, headers=self.headers)
            response.raise_for_status()
            response.encoding = self.encoding
            return response.json()
        except HTTPError as e:
            echo(f'HTTP错误: {e}')
        except RequestError as e:
            echo(f'请求错误: {e}')
        except Exception as e:
            echo(f'发生异常: {e}')

    @pool(10)
    def download_video(self, result_link):
        self.ydl.download(result_link)

    def main(self):
        json_data = self.get_json(self.suffix_url)
        if json_data:
            titles = jsonpath(json_data, '$..title')
            links = jsonpath(json_data, '$..link')
            title_link_map = dict(zip(titles, links))
            result_titles = multchoicebox("请选择网易云音乐歌单：", '网易云音乐下载器', titles)
            if result_titles:
                result_links = [title_link_map[title] for title in result_titles]
                text = '\n'.join(result_titles)
            ret = textbox("您选择的结果", '结果列表', text)
            for result_link in result_links:
                self.download_video(result_link)
        pool.wait()

if __name__ == '__main__':
    with Spider() as spider:
        spider.main()
    echo('本次下载完毕！！！')



