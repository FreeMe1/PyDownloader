"""
    author : FreeHe
"""

from threading import Thread as Td
from threadGet.task import Task
import time


class ThreadGet(object):
    def __init__(self, work_dir, cache=1024*400, work_num=1):
        self.work_dir = work_dir
        self.cache = cache
        self.work_num = work_num
        self.thread = None
        self.thread_dict = dict({})  # url: Task
        self.__status = 'pause'  # 'pause', 'start', 'stop'

    def add_url(self, url):
        task = Task(url, work_dir=self.work_dir, cache=self.cache)
        if not self.thread_dict.get(url):
            self.thread_dict[url] = task

    @property
    def thread_status(self):
        status = list([])
        pause_num = 0
        start_num = 0
        for thread in self.thread_dict.keys():
            status.append((thread, self.thread_dict[thread].get_status()))
        for s in status:
            if s[1] == 'pause':
                pause_num += 1
            elif s[1] == 'start':
                start_num += 1
        return status, pause_num, start_num

    def pause_thread(self, url):
        if self.thread_dict[url]:
            self.thread_dict[url].set_status('pause')

    def cancel_thread(self, url):
        if self.thread_dict[url]:
            self.thread_dict[url].cancel_download()

    def start_thread(self, url):
        """ 用于启动单个下载线程 """
        if self.get_status() == 'pause':
            return
        if self.thread_status[2] < self.work_num:
            if self.thread_dict.get(url):
                if not self.thread_dict[url].thread:
                    self.thread_dict[url].thread_download()
                else:
                    self.thread_dict[url].set_status('start')

    def pause_all(self):
        self.__status = 'pause'

    def start(self):
        self.__status = 'start'

    def get_status(self):
        return self.__status

    def finished_all(self):
        status = self.thread_status
        if status[2] == 0 and status[1] == 0 and not len(status):
            return True

    def scan_thread(self):
        """ 用于总开关->启动暂停所有下载线程 """
        if self.get_status() == 'pause':
            for t in self.thread_dict.values():
                if t.get_status() == 'start':
                    t.set_status('pause')
            print('then i m in scan - pause')
        else:
            if self.get_status() == 'start' and not self.finished_all():
                print('then i m in scan - start')
                for num in range(self.work_num):
                    for url in self.thread_status[0]:
                        if url[1] == 'pause':
                            self.start_thread(url[0])
                            break
            if self.get_status() == 'start' and self.finished_all():
                self.pause_all()


