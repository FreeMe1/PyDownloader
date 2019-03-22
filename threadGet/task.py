"""
    author : FreeHe
"""

import os
import time
from threading import Thread
import requests

__all__ = ['Task']


class Task(object):
    """
        示例:
            task = Task('http://example.com') # 创建下载任务
            task.download() # 开始下载
            task.set_status('pause') # 设置状态 , 状态有 -> 'pause' 'start'
            task.get_status() # 获取当前状态
            task.speed # 获取平均下载速度
            task.process # 获取下载进度
            task.thread_download() # 启用线程开始下载
    """

    def __init__(self, url, work_dir, cache=1024*400):
        self.work_dir = work_dir
        self.url = url
        self.cache = cache
        self.thread = None
        self.local_file = self.work_dir+os.sep+os.path.split(self.url)[1]
        self.__status = 'pause'    # 'cancel', 'start' 'failed', 'pause', 'finished'
        self.start_time = 0
        self.server_size = 0

    def download(self):
        if self.is_failed():
            return
        try:
            self._init_response()
            with open(self.local_file, self.mode) as local_file:
                self.set_time()
                self.set_status('start')
                print(self.url, ' start')
                for chunk in self.response.iter_content(self.cache):
                    while self.is_pause() and not self.is_cancel():
                        print(self.url, ' pause')
                        time.sleep(1)
                    if self.is_cancel():
                        print(self.url, ' cancel')
                        break
                    if chunk and not self.is_cancel():
                        local_file.write(chunk)
                self.set_status('finished')
                print(self.url, ' finished')
        except Exception as e:
            self.set_status('failed')
            print(self.url, ' failed')

    def cancel_download(self):
        self.set_status('cancel')
        try:
            del self.thread
            if os.path.exists(self.local_file):
                time.sleep(0.1)
                os.remove(self.local_file)
        except Exception as e:
            print(e)

    def _init_response(self):
        """
            断点续传和新下载处理
        :return:
        """
        if os.path.exists(self.local_file):
            self.local_size = os.path.getsize(self.local_file)
            headers = {'Range': 'bytes={size}-'.format(size=self.local_size)}
            try:
                self.response = requests.get(
                    self.url, stream=True, headers=headers, timeout=10)
                self.mode = 'ab'
                self.server_size = int(self.response.headers['Content-Length'])
            except Exception as e:
                self.set_status('failed')
        else:
            try:
                self.response = requests.get(self.url, stream=True, timeout=10)
                self.mode = 'wb'
                self.local_size = 0
                self.server_size = int(self.response.headers['Content-Length'])
            except Exception as e:
                self.set_status('failed')

    def set_time(self):
        self.start_time = time.time()

    def set_status(self, status):
        self.__status = status

    def get_status(self):
        return self.__status

    def is_pause(self):
        if self.__status == 'pause':
            return True
        else:
            return False

    def is_cancel(self):
        if self.__status == 'cancel':
            return True
        else:
            return False

    def is_failed(self):
        if self.__status == 'failed':
            return True
        else:
            return False

    @property
    def speed(self):
        used_time = time.time() - self.start_time
        try:
            get_size = os.path.getsize(self.local_file) - self.local_size
        except:
            get_size = 0
        return str(round(get_size/1024/1024/used_time, 2)) + 'M/s'

    @property
    def process(self):
        if self.server_size:
            server_size = float(self.server_size/1024/1024)
        else:
            server_size = 1
        try:
            local_size = int(os.path.getsize(self.local_file)/1024/1024)
        except:
            local_size = 0
        return (str(local_size)+'MB/'+str(server_size)+'MB ', 
            str(round(local_size/server_size, 2)*100)+'%',
                local_size, server_size)

    def thread_download(self):
        if not self.thread:
            self.set_status('start')
            self.thread = Thread(target=self.download, args=[], daemon=True)
            self.thread.start()

    def __del__(self):
        del self.thread
