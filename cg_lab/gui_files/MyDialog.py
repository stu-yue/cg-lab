import sys
import PyQt5
from PyQt5 import QtWidgets, QtGui
from  PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

root = QFileInfo(__file__).absolutePath() + '/'

class MyResetDialog(QDialog):              
    """
    自定义重置对话框类，继承QDialog类
    """  

    def __init__(self, maxWidth=600, maxHeight=600):
        super().__init__()
        self.max_width = maxWidth
        self.max_height = maxHeight
        self.setWindowIcon(QIcon(root + "ImageIcon/paintIcon4.png"))
        self.initUI()

    def initUI(self):
        self.setWindowTitle("重置画布")      # 窗口标题
        self.setFixedSize(850, 450)         # 固定
        self.lab_a = QLabel('水平(H, 像素):', self)
        self.lab_b = QLabel('垂直(V, 像素):', self)
        self.lab_c = QLabel(self)
        self.lab_c.setFixedSize(130, 140)
        self.lab_c.setPixmap(QPixmap('gui_files/ImageIcon/horizen.png'))
        self.lab_c.setScaledContents(True)
        self.lab_d = QLabel(self)
        self.lab_d.setFixedSize(130, 140)
        self.lab_d.setPixmap(QPixmap('gui_files/ImageIcon/vertical.png'))
        self.lab_d.setScaledContents(True)
 
        self.horizen_edit = QLineEdit()      # 用于接收水平大小
        self.horizen_edit.setPlaceholderText(f'请输入(0, {self.max_width})以内整数, 非法输入无效')
        self.vertical_edit = QLineEdit()      # 用于接受垂直大小
        self.vertical_edit.setPlaceholderText(f'请输入(0, {self.max_height})以内整数, 非法输入无效')
 
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  #窗口中建立确认和取消按钮
        self.buttons.buttons()[0].setText('确定')
        self.buttons.buttons()[1].setText('取消')
 
        self.grid = QGridLayout()
        self.grid.addWidget(self.lab_c,0,0,1,1)
        self.grid.addWidget(self.lab_d,1,0,1,1)
        self.grid.addWidget(self.lab_a,0,1,1,1)
        self.grid.addWidget(self.lab_b,1,1,1,1)
        self.grid.addWidget(self.horizen_edit,0,2,1,1)
        self.grid.addWidget(self.vertical_edit,1,2,1,1)
        self.grid.addWidget(self.buttons,2,2)
        self.setLayout(self.grid)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
 
    def get_data(self):                                         #   定义获取用户输入数据的方法
        """
        :return new_width: int, new_height: int, valid: bool
        """
        horizen_input = self.horizen_edit.text()
        vertical_input = self.vertical_edit.text()
        try:
            horizen_input = int(horizen_input)
            vertical_input = int(vertical_input)
        except:
            return 0, 0, False
        if 0 < horizen_input and horizen_input <= self.max_width: 
            if 0 < vertical_input and vertical_input <= self.max_height:
                return horizen_input, vertical_input, True
        return self.max_width, self.max_height, False
