"""
    author : FreeHe
"""

# 启动文件

import os.path
import sys
import pickle
from PyQt5.QtWidgets import QApplication, QPushButton
from QWindow.QMainWin import QMainWin
from threadGet.threadGet import ThreadGet

app = QApplication(sys.argv)
if os.path.exists('config.pkl'):
    with open('config.pkl', 'rb') as f:
        config = pickle.load(f)
        work_dir = config['work_dir']
        work_num = int(config['work_num'])
else:
    work_dir = os.path.dirname(os.path.abspath(__file__))
    work_num = 20
win = QMainWin(ThreadGet(work_dir, work_num = work_num))
win.show()
sys.exit(app.exec_())

#  TODO // start button event logic
