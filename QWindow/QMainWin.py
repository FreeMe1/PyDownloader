"""
    author : FreeHe
"""


"""
    所有窗口UI类模块
"""

import os
import pickle
from PyQt5.QtCore import QPoint, Qt, QTimer
from PyQt5.QtGui import QCursor, QFont
from PyQt5.QtWidgets import (QApplication, QComboBox, QFileDialog, QHBoxLayout,
                             QInputDialog, QLabel, QLineEdit, QMainWindow,
                             QProgressBar, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget, QMessageBox)

__all__ = ['QMainWin']


# -----------------------------------------------------


class QTitleLabel(QLabel):
    """
    新建标题栏标签类
    """

    def __init__(self, *args):
        super(QTitleLabel, self).__init__(*args)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setFixedHeight(30)


class QTitleButton(QPushButton):
    """
    新建标题栏按钮类
    """

    def __init__(self, *args):
        super(QTitleButton, self).__init__(*args)
        self.setFont(QFont("Webdings"))  # 特殊字体以不借助图片实现最小化最大化和关闭按钮
        self.setFixedWidth(40)


class QUnFrameWindow(QWidget):
    """
    无边框窗口类
    """

    def __init__(self):
        super(QUnFrameWindow, self).__init__(
            None, Qt.FramelessWindowHint)  # 设置为顶级窗口，无边框
        self._padding = 5  # 设置边界宽度为5
        self.initTitleLabel()  # 安放标题栏标签
        self.setWindowTitle = self._setTitleText(
            self.setWindowTitle)  # 用装饰器将设置WindowTitle名字函数共享到标题栏标签上
        self.setWindowTitle("UnFrameWindow")
        self.initLayout()  # 设置框架布局
        self.setMinimumWidth(250)
        self.setMouseTracking(True)  # 设置widget鼠标跟踪
        self.initDrag()  # 设置鼠标跟踪判断默认值

    def initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def initTitleLabel(self):
        # 安放标题栏标签
        self._TitleLabel = QTitleLabel(self)
        # 设置标题栏标签鼠标跟踪（如不设，则标题栏内在widget上层，无法实现跟踪）
        self._TitleLabel.setMouseTracking(True)
        self._TitleLabel.setIndent(10)  # 设置标题栏文本缩进
        self._TitleLabel.move(0, 0)  # 标题栏安放到左上角

    def initLayout(self):
        # 设置框架布局
        self._MainLayout = QVBoxLayout()
        self.setLayout(self._MainLayout)

    def addLayout(self, QLayout):
        # 给widget定义一个addLayout函数，以实现往竖放框架的正确内容区内嵌套Layout框架
        self._MainLayout.addLayout(QLayout)

    def _setTitleText(self, func):
        # 设置标题栏标签的装饰器函数
        def wrapper(*args):
            self._TitleLabel.setText(*args)
            return func(*args)
        return wrapper

    def setTitleAlignment(self, alignment):
        # 给widget定义一个setTitleAlignment函数，以实现标题栏标签的对齐方式设定
        self._TitleLabel.setAlignment(alignment | Qt.AlignVCenter)

    def setCloseButton(self, bool):
        # 给widget定义一个setCloseButton函数，为True时设置一个关闭按钮
        if bool == True:
            self._CloseButton = QTitleButton(
                b'\xef\x81\xb2'.decode("utf-8"), self)
            # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._CloseButton.setProperty("name", "CloseButton")
            self._CloseButton.setToolTip("关闭窗口")
            # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._CloseButton.setMouseTracking(True)
            self._CloseButton.setFixedHeight(
                self._TitleLabel.height())  # 设置按钮高度为标题栏高度
            self._CloseButton.clicked.connect(self.close)  # 按钮信号连接到关闭窗口的槽函数

    def setMinButtons(self, bool):
        # 给widget定义一个setMinMaxButtons函数，为True时设置一组最小化最大化按钮
        if bool == True:
            self._MinimumButton = QTitleButton(
                b'\xef\x80\xb0'.decode("utf-8"), self)
            # 设置按钮的ObjectName以在qss样式表内定义不同的按钮样式
            self._MinimumButton.setProperty("name", "MinButton")
            self._MinimumButton.setToolTip("最小化")
            # 设置按钮鼠标跟踪（如不设，则按钮在widget上层，无法实现跟踪）
            self._MinimumButton.setMouseTracking(True)
            self._MinimumButton.setFixedHeight(
                self._TitleLabel.height())  # 设置按钮高度为标题栏高度
            self._MinimumButton.clicked.connect(
                self.showMinimized)  # 按钮信号连接到最小化窗口的槽函数

    def _changeNormalButton(self):
        # 切换到恢复窗口大小按钮
        try:
            self.showMaximized()  # 先实现窗口最大化
            self._MaximumButton.setText(
                b'\xef\x80\xb2'.decode("utf-8"))  # 更改按钮文本
            self._MaximumButton.setToolTip("恢复")  # 更改按钮提示
            self._MaximumButton.disconnect()  # 断开原本的信号槽连接
            self._MaximumButton.clicked.connect(
                self._changeMaxButton)  # 重新连接信号和槽
        except:
            pass

    def _changeMaxButton(self):
        # 切换到最大化按钮
        try:
            self.showNormal()
            self._MaximumButton.setText(b'\xef\x80\xb1'.decode("utf-8"))
            self._MaximumButton.setToolTip("最大化")
            self._MaximumButton.disconnect()
            self._MaximumButton.clicked.connect(self._changeNormalButton)
        except:
            pass

    def resizeEvent(self, QResizeEvent):
        # 自定义窗口调整大小事件
        self._TitleLabel.setFixedWidth(self.width())  # 将标题标签始终设为窗口宽度
        # 分别移动三个按钮到正确的位置
        try:
            self._CloseButton.move(self.width() - self._CloseButton.width(), 0)
        except:
            pass
        try:
            self._MinimumButton.move(
                self.width() - (self._CloseButton.width() + 1) * 2 + 1, 0)
        except:
            pass
        try:
            self._MaximumButton.move(
                self.width() - (self._CloseButton.width() + 1) * 2 + 1, 0)
        except:
            pass
        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                            for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                             for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                             for y in range(self.height() - self._padding, self.height() + 1)]

    def mousePressEvent(self, event):
        # 重写鼠标点击的事件
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self._TitleLabel.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势
        if QMouseEvent.pos() in self._corner_rect:
            self.setCursor(Qt.SizeFDiagCursor)
        elif QMouseEvent.pos() in self._bottom_rect:
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._right_rect:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        # 鼠标释放后，各扳机复位
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False


# -----------------------------------------------------


class AboutWidget(QWidget):
    """ Tab[关于]窗口类 """
    tip = '-项目地址-'
    github = 'https://github.com/FreeHe/PyDownloader'

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        tip = QLabel(AboutWidget.tip)
        tip.setFixedSize(400, 50)
        address = QLabel(AboutWidget.github)
        address.setFixedSize(400, 50)
        self.setFixedSize(445, 200)
        layout.addWidget(tip)
        layout.addWidget(address)
        self.setLayout(layout)


class SettingWidget(QWidget):
    """ Tab[设置]窗口类 """
    def __init__(self):
        super().__init__()
        self.work_num = 2
        self.connect_num = 20
        self.work_dir = os.getcwd()
        self.layout = QVBoxLayout()
        self._init_config()
        self._init_layout()
        self._init_event()
        self.setLayout(self.layout)

    def _init_config(self):
        if os.path.exists('config.pkl'):
            with open('config.pkl', 'rb') as f:
                config = pickle.load(f)
                self.work_dir = config['work_dir']
                self.work_num = config['work_num']
                self.connect_num = config['connect_num']

    def _init_layout(self):
        self.label1 = QLabel('同时下载数 ')
        self.label1.setProperty('name', 'label')
        self.qc1 = QComboBox()
        self.qc1.addItems(['1', '2', '3', '4'])
        self.qc1.setCurrentText(self.work_num)
        box1 = QHBoxLayout()
        box1.addWidget(self.label1)
        box1.addStretch(9)
        box1.addWidget(self.qc1)
        w1 = QWidget()
        w1.setLayout(box1)
        self.label2 = QLabel('最大连接数 ')
        self.label2.setProperty('name', 'label')
        self.qc2 = QComboBox()
        self.qc2.addItems(['20', '50', '80', '100'])
        self.qc2.setCurrentText(self.connect_num)
        box2 = QHBoxLayout()
        box2.addWidget(self.label2)
        box2.addStretch(9)
        box2.addWidget(self.qc2)
        w2 = QWidget()
        w2.setLayout(box2)
        self.label3 = QLabel('下载目录 ')
        self.label3.setProperty('name', 'label')
        self.le = QLineEdit()
        self.le.setText(self.work_dir)
        self.clearLe = QPushButton('清空')
        self.viewDir = QPushButton('浏览')
        box3 = QHBoxLayout()
        box3.addWidget(self.label3)
        box3.addWidget(self.le)
        box3.addWidget(self.clearLe)
        box3.addWidget(self.viewDir)
        w3 = QWidget()
        w3.setLayout(box3)
        self.confirm = QPushButton('确认')
        self.confirm.setFixedWidth(100)
        self.label4 = QLabel('下次打开生效')
        self.label4.setFixedWidth(150)
        box4 = QHBoxLayout()
        box4.addWidget(self.confirm)
        box4.addWidget(self.label4)
        w4 = QWidget()
        w4.setLayout(box4)
        self.layout.addWidget(w1)
        self.layout.addWidget(w2)
        self.layout.addWidget(w3)
        self.layout.addWidget(w4)

    def _init_event(self):
        self.qc1.currentIndexChanged.connect(self._qc1Changed)
        self.qc2.currentIndexChanged.connect(self._qc2Changed)
        self.viewDir.clicked.connect(self._viewDirClicked)
        self.clearLe.clicked.connect(self._clearLeClicked)
        self.confirm.clicked.connect(self._confirmClicked)

    def _qc1Changed(self):
        print(self.qc1.currentText())

    def _qc2Changed(self):
        print(self.qc2.currentText())

    def _clearLeClicked(self):
        self.le.setText('')

    def _viewDirClicked(self):
        tmpDir = QFileDialog.getExistingDirectory()
        if tmpDir:
            self.le.setText(tmpDir)

    def _confirmClicked(self):
        config = dict({})
        config['work_dir'] = self.le.text()
        config['work_num'] = self.qc1.currentText()
        config['connect_num'] = self.qc2.currentText() 
        with open('config.pkl', 'wb') as f:
            pickle.dump(config, f)


class DownloadPanel(QWidget):
    """ Tab[下载]窗口中单个下载项的窗口类 """
    def __init__(self, work, pause_event, del_event):
        super().__init__()
        self.work = work
        self.pause_event = pause_event
        self.del_event = del_event
        self._init_panel()
        self._init_property()
        self._init_connect()

    def _init_panel(self):
        vbox = QVBoxLayout()
        # ---------------------------
        self.work_name = os.path.split(self.work)[1]
        self.name_label = QLabel(self.work_name)
        # ---------------------------
        hbox2 = QHBoxLayout()
        self.work_progressBar = QProgressBar()
        self.work_pause = QPushButton('开始')
        self.work_del = QPushButton('删除')
        option_panel = QWidget()
        hbox2.addWidget(self.work_progressBar)
        hbox2.addWidget(self.work_pause)
        hbox2.addWidget(self.work_del)
        option_panel.setLayout(hbox2)
        # ---------------------------
        hbox1 = QHBoxLayout()
        self.work_speed = QLabel('0M/s')
        self.work_progress = QLabel('0M/0M')
        self.work_percent = QLabel('0%')
        progress_panel = QWidget()
        hbox1.addWidget(self.work_speed)
        hbox1.addWidget(self.work_progress)
        hbox1.addWidget(self.work_percent)
        progress_panel.setLayout(hbox1)
        # ----------------------------
        self.gap = QLabel()
        # ----------------------------
        vbox.addWidget(self.name_label)
        vbox.addWidget(option_panel)
        vbox.addWidget(progress_panel)
        vbox.addWidget(self.gap)
        self.setLayout(vbox)

    def _init_property(self):
        self.name_label.setProperty('name', 'work_name')
        self.work_progressBar.setProperty('name', 'work_progressBar')
        self.work_pause.setProperty('name', 'work_pause')
        self.work_del.setProperty('name', 'work_del')
        self.work_speed.setProperty('name', 'work_process_label')
        self.work_progress.setProperty('name', 'work_process_label')
        self.work_percent.setProperty('name', 'work_process_label')
        self.gap.setProperty('name', 'gap')

    def _init_connect(self):
        self.work_pause.clicked.connect(lambda: self.pause_event(self.work))
        self.work_del.clicked.connect(lambda: self.del_event(self.work))


class DownloadWidget(QWidget):
    """ Tab[下载]窗口类 """
    def __init__(self, work_list, pause_event, del_event):
        super().__init__()
        self.work_list = work_list
        self.pause_event = pause_event
        self.del_event = del_event
        self.DownloadPanelList = list([])
        self._init_download_list()

    def _init_download_list(self):
        vbox = QVBoxLayout()
        for work in self.work_list:
            tmp_panel = DownloadPanel(work, self.pause_event, self.del_event)
            vbox.addWidget(tmp_panel)
            self.DownloadPanelList.append(tmp_panel)
        self.setLayout(vbox)


class FinishedPanel(QWidget):
    """ Tab[完成]窗口中单个完成项的窗口类 """
    def __init__(self, finished, finished_del):
        super().__init__()
        self.finished = finished
        self._init_panel()
        self._init_property()
        self._init_connect(finished_del)

    def _init_panel(self):
        hbox = QHBoxLayout()
        # ----------------------------
        self.label = QLabel(self.finished)
        self.delete = QPushButton('删除')
        self.gap = QLabel()
        # ----------------------------
        hbox.addWidget(self.label)
        hbox.addStretch(9)
        hbox.addWidget(self.delete)
        panel = QWidget()
        panel.setLayout(hbox)
        # ----------------------------
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.gap)
        gap_line = QWidget()
        gap_line.setLayout(hbox1)
        # ----------------------------
        vbox = QVBoxLayout()
        vbox.addWidget(panel)
        vbox.addWidget(gap_line)
        # ----------------------------
        self.setLayout(vbox)

    def _init_property(self):
        self.label.setProperty('name', 'finished_label')
        self.delete.setProperty('name', 'finished_delete')
        self.gap.setProperty('name', 'gap')

    def _init_connect(self, finished_del):
        self.delete.clicked.connect(lambda: finished_del(self.finished))


class FinishedWidget(QWidget):
    """ Tab[完成]窗口类 """
    def __init__(self, finished_list, finished_del):
        super().__init__()
        self.finished_list = finished_list
        self.finished_del = finished_del
        self.FinishedPanel_list = list([])
        self._init_finished_list()

    def _init_finished_list(self):
        vbox = QVBoxLayout()
        for finished in self.finished_list:
            tmp_finished = FinishedPanel(finished, self.finished_del)
            vbox.addWidget(tmp_finished)
            self.FinishedPanel_list.append(tmp_finished)
        self.setLayout(vbox)


# -----------------------------------------------------


class QMainWin(QUnFrameWindow):
    qStyle = """
            QLabel {
                color: white;
                max-width:50px;
                max-height: 50px;
            }
            QLabel[name='gap'] {
                background-color: #272822;
                min-height:5px;
                min-width: 400px;
            }
            QLabel[name='label'] {
                background-color: #272822;
                color: #aaa;
                min-width: 150px;
                font-size: 25px;
            }
            QLabel[name='work_name'] {
                color: #aaa;
                min-width: 100px;
            }
            QLabel[name='work_process_label'] {
                min-width: 100px;
            }
            QLabel[name='finished_label'] {
                min-width: 100px;
            }
            QMessageBox QLabel{
                min-width: 180px;
                color: #000;
            }
            QMessageBox QPushButton {
                background-color: #eee;
                color: #000;
                min-width: 50px;
            }
            SettingWidget{
                background-color: #272822;  
            }
            DownloadWidget, FinishedWidget {
                background-color: #2e2e36;
                min-width: 450px;
                color: #aaa;
            }
            FinishedPanel {
                max-height: 100px;
            }
            DownloadPanel {
                max-height: 150px;
            }    
            QPushButton[name='finished_delete'] {
                max-width: 30px;
                background-color: #2e2e36;
            }
            QComboBox {
                background-color: #272822;
                color: #aaa;
                border-color: #aaa;
                min-width: 90px;
                font-size: 25px;
            }
            QLineEdit {
                background-color: #272822;
                color: #aaa;  
                border-width: 1px;
                border-style: dotted; 
                border-color: #aaa;
                min-width:100px;
                font-size: 20px;  
            }
            AboutWidget {
                background-color: #272822;
                color: #aaa
            }
            QTitleLabel {
                background-color: #272822;
                color: white
            }
            QTitleButton[name='CloseButton'], QTitleButton[name='MinButton'] {
                background-color: #272822;
                border-radius: 50px
            }
            QTitleButton[name='CloseButton']:hover, QTitleButton[name='MinButton']:hover {
                background-color: #cf0
            }
            QMainWin {
                background-color: #272822;
                color: white
            }
            QScrollBar {
                max-width: 5px;
                background: #cf0;
                border-width: 0px;
                border-style: none;
            }
            QScrollBar::sub-page {
                background: #272822;
                border-style: none;
            }
            QScrollBar::add-page {
                background: #272822;
                border-style: none;
            }
            QPushButton {
                background-color: #272821;
                color: white;
                min-height: 30px;
                border-radius: 0px
            }
            QPushButton:hover {
                background-color: #272521;
                color: #cf0 
            }
            QPushButton[name='addButton'] {
                font-size: 50px;
                max-width: 50px;
                max-height: 50px;
                float: left
            }
            QPushButton[name='addButton']:hover {
                color: #cf0
            }
            QPushButton[name='startButton'] {
                border-image: url(pause.png);
                max-width: 50px;
                max-height: 50px;
                float: left
            }
            QPushButton[name='work_pause'] {
                background-color: #2e2e36;
                font-size: 13px;
            }
            QPushButton[name='work_del'] {
                background-color: #2e2e36;
                font-size: 13px;
            }
            QProgressBar {
                max-height: 3px;
                max-width: 250px;
                padding-left: 5px;
            }
            QInputDialog {
                background-color: #272822;
                color: #aaa;
            }
            QInputDialog QLabel {
                max-width: 100px
            }
            QInputDialog QLineEdit {
                background-color: #272822;
                border-width: 1px;
                border-style: dotted;
                color: white;
                min-width: 300px;
                font-size: 20px
            }
            QScrollArea {
                background-color: #272822;
                color: white;
                border-style: none;
                min-width: 470px;
                min-height: 410px
            }
         """

    def __init__(self, threadGet):
        super().__init__()
        self.setFixedSize(500, 600)
        self.setStyleSheet(QMainWin.qStyle)
        self._threadGet = threadGet
        self._isClicked = False
        self._init_layout()
        self.setWindowTitle('Py-Downloader')
        self.setCloseButton(True)
        self.setMinButtons(True)
        self._init_threadGet_scan()
        self._init_threadProcess_scan()

    def _init_threadGet_scan(self):
        self.timer_1 = QTimer()
        self.timer_1.timeout.connect(self._threadGet.scan_thread)
        self.timer_1.start(1000)

    def _init_threadProcess_scan(self):
        self.timer_2 = QTimer()
        self.timer_2.timeout.connect(self._scan_threadProcess)
        self.timer_2.start(1000)

    def _scanner(self):
        thread_process_dict = dict({})
        total_process = 0
        total_local_size = 0
        total_server_size = 0
        for task_url in self._threadGet.thread_dict.keys():
            process = self._threadGet.thread_dict[task_url].process
            speed = self._threadGet.thread_dict[task_url].speed
            status = self._threadGet.thread_dict[task_url].get_status()
            thread_process_dict[task_url] = (
                process, 
                speed,
                status
                )
            total_local_size += process[2]
            total_server_size += process[3]
        if not total_server_size == 0:
            total_process = round(total_local_size/total_server_size, 2)
        else:
            total_process = 0
        return total_process, thread_process_dict

    def _scan_threadProcess(self):
        if self._threadGet.get_status() == 'start':
            self._change_ui(*self._scanner())
        elif self._threadGet.finished_all():
            self._startButtonClicked()
            self._change_ui(*self._scanner())
            QApplication.processEvents()
            
    def _change_ui(self, total_process, thread_process_dict):
        self.label.setText(str(total_process*100)+'%')
        self.processBar.setValue(int(total_process*100))
        try:
            for url in thread_process_dict.keys():
                for panel in self.DownloadWidget.DownloadPanelList:
                    if panel.work == url:
                        panel.work_speed.setText(thread_process_dict[url][1])
                        panel.work_progress.setText(thread_process_dict[url][0][0])
                        panel.work_percent.setText(thread_process_dict[url][0][1])
                        panel.work_progressBar.setValue(
                            int(thread_process_dict[url][0][2]/thread_process_dict[url][0][3]*100)
                            )
                        if thread_process_dict[url][2] == 'start':
                            panel.work_pause.setText('暂停')
                        elif thread_process_dict[url][2] == 'pause':
                            panel.work_pause.setText('开始')
                        elif thread_process_dict[url][2] == 'finished':
                            del self._threadGet.thread_dict[url]
                            if os.path.exists('config.pkl'):
                                with open('config.pkl', 'rb') as f:
                                    config = pickle.load(f)
                                if config.get('finished_list'):
                                    config['finished_list'].append(os.path.split(url)[1])
                                else:
                                    config['finished_list'] = [os.path.split(url)[1]]
                                with open('config.pkl', 'wb') as f:
                                    pickle.dump(config, f)
                            self._downloadButtonClicked()
                        elif thread_process_dict[url][2] == 'failed':
                            panel.work_pause.setText('重连')
        except:
            pass

    def _init_layout(self):
        # ------窗口布局---------------------------------------
        self.allLayout = QVBoxLayout()  # 主窗口布局
        self.topContorlLayout = QHBoxLayout()  # 窗口顶部控制卡布局
        self.topTabLayout = QHBoxLayout()  # 窗口顶部Tab选项卡布局

        # ------布局控制卡-------------------------------------
        self.addButton = QPushButton('+')
        self.addButton.setToolTip("新建任务")
        self.addButton.setProperty('name', 'addButton')  # 新建任务按钮
        self.addButton.clicked.connect(self._addButtonClicked)
        self.startButton = QPushButton()
        self.startButton.setProperty('name', 'startButton')  # 开启任务按钮
        self.startButton.clicked.connect(self._startButtonClicked)
        self.startButton.clicked.connect(self._startButtonClicked)
        self.processBar = QProgressBar()
        self.label = QLabel('0%')
        self.topContorlLayout.addWidget(self.addButton)
        self.topContorlLayout.addWidget(self.startButton)
        self.topContorlLayout.addWidget(self.processBar)
        self.topContorlLayout.addWidget(self.label)
        control = QWidget()
        control.setLayout(self.topContorlLayout)
        # ------布局Tab选项卡-----------------------------------
        self.downloadButton = QPushButton('下载')
        self.downloadButton.setProperty('name', 'downloadButton')
        self.downloadButton.clicked.connect(self._downloadButtonClicked)
        self.finishedButton = QPushButton('完成')
        self.finishedButton.setProperty('name', 'finishedButton')
        self.finishedButton.clicked.connect(self._finishedButtonClicked)
        self.settingButton = QPushButton('设置')
        self.settingButton.setProperty('name', 'settingButton')
        self.settingButton.clicked.connect(self._settingButtonClicked)
        self.massageButton = QPushButton('关于')
        self.massageButton.setProperty('name', 'massageButton')
        self.massageButton.clicked.connect(self._massageButtonClicked)
        self.topTabLayout.addWidget(self.downloadButton)
        self.topTabLayout.addWidget(self.finishedButton)
        self.topTabLayout.addWidget(self.settingButton)
        self.topTabLayout.addWidget(self.massageButton)
        tab = QWidget()  # Tab选项卡控件
        tab.setProperty('name', 'topTabLayout')
        tab.setLayout(self.topTabLayout)
        # ------Tab分页----------------------------------------
        self.tabWidget = QWidget(self)
        self.tabWidget.setFixedSize(480, 450)
        self.tabWidget.setProperty('name', 'tabWidget')
        self.QScrollArea = QScrollArea(self.tabWidget)
        self.openFileDir = QPushButton('打开文件夹')
        self.openFileDir.clicked.connect(self._openFileDirClicked)
        # ------布局主窗口--------------------------------------
        self.allLayout.addWidget(QLabel())
        self.allLayout.addWidget(control)
        self.allLayout.addWidget(tab)
        self.allLayout.addWidget(self.tabWidget)
        self.allLayout.addWidget(self.openFileDir)
        self.addLayout(self.allLayout)

    def _startButtonClicked(self):
        if not self._threadGet.thread_dict.keys():
            return
        if self._isClicked:
            """ 不知为何按一下按钮会执行两次此函数 所以有了这个判断 (->^<-) """
            self._isClicked = False
            return
        if self._threadGet.get_status() == 'pause' and not self._threadGet.finished_all():
            self.startButton.setStyleSheet(
                "QPushButton[name='startButton']{border-image:url(start.png)}")
            self._threadGet.start()
            self._isClicked = True
        else:
            self.startButton.setStyleSheet(
                "QPushButton[name='startButton']{border-image:url(pause.png)}")
            self._threadGet.pause_all()
            self._isClicked = True

    def _addButtonClicked(self):
        if os.path.exists('config.pkl'):
            with open('config.pkl', 'rb') as f:
                connect_num = int(pickle.load(f)['connect_num'])
        else:
            connect_num = 20
        url, ok = QInputDialog.getText(self, '新建任务', '链接地址')
        if ok and len(self._threadGet.thread_dict.keys()) < connect_num:
            self._threadGet.add_url(url)
            self._downloadButtonClicked()
        elif not ok:
            return
        else:
            QMessageBox.information(self, 'tip', 'number of connection is over')

    def _openFileDirClicked(self):
        import sys
        path = os.getcwd()
        with open('config.pkl', 'rb') as f:
            s = pickle.load(f)
            path = s['work_dir']
        if sys.platform == 'darwin':
            os.system('open '+path)
        else:
            os.startfile(path)
        print(path)

    def pause_event(self, url):
        self._threadGet.pause_thread(url)

    def del_event(self, url):
        self._threadGet.cancel_thread(url)
        del self._threadGet.thread_dict[url]
        self._downloadButtonClicked()

    def finished_del(self, finished):
        if os.path.exists('config.pkl'):
            with open('config.pkl', 'rb') as f:
                config = pickle.load(f)
            if config.get('finished_list'):
                if finished in config['finished_list']:
                    config['finished_list'].remove(finished)
                    with open('config.pkl', 'wb') as f:
                        pickle.dump(config, f)
        self._finishedButtonClicked()

    def _massageButtonClicked(self):
        self.QScrollArea.setWidget(AboutWidget())
        QApplication.processEvents()

    def _downloadButtonClicked(self):
        download_list = list([])
        for d in self._threadGet.thread_status[0]:
            download_list.append(d[0])
        self.DownloadWidget = DownloadWidget(
            download_list, self.pause_event, self.del_event)
        self.QScrollArea.setWidget(self.DownloadWidget)
        QApplication.processEvents()

    def _finishedButtonClicked(self):
        if os.path.exists('config.pkl'):
            with open('config.pkl', 'rb') as f:
                tmp = pickle.load(f).get('finished_list')
                finished_list = tmp if tmp else list([])
        else:
            finished_list = list([])
        self.FinishedWidget = FinishedWidget(finished_list, self.finished_del)
        self.QScrollArea.setWidget(self.FinishedWidget)
        QApplication.processEvents()

    def _settingButtonClicked(self):
        self.QScrollArea.setWidget(SettingWidget())
        QApplication.processEvents()

