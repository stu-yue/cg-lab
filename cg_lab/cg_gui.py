#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import math
import os
import numpy as np
from PIL import Image
import warnings
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from gui_files.MyDialog import *
import webbrowser
warnings.filterwarnings('ignore')

# 全局设置
CWD = os.getcwd()                   # 获取当前工作目录路径
FONT = QFont("YouYuan", 12,)        # 字体
MAX_NUM_CONTROL_POINTS = 6          # 最大控制点个数
HELP_FILE = 'https://github.com/stu-yue'

class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.color = QColor(0, 0, 0)
        self.pen_width = 2
        self.temp_id = ''
        self.temp_item = None
        self.temp_rect = None
        self.temp_anchor = None
        self.temp_isNew = True
        self.x0, self.y0 = None, None
        self.flags = {'translate': 0, 'rotate': 0, 'scale': 0, 'clip': 0}
        self.copy_item = None
    
    def set_color(self, new_color):
        self.color = new_color
    
    def set_width(self, new_width):
        self.pen_width = new_width
    
    def start_copy(self):
        if self.selected_id != '' and self.selected_id in self.item_dict:
            self.copy_item = self.item_dict[self.selected_id].copy()
            self.copy_item.id = self.main_window.get_id()
            return True
        return False

    def start_paste(self):
        if self.copy_item != None:
            self.status = 'paste'

    def reset_status(self):
        self.status = ''

    def set_status(self, new_status):
        self.status = new_status

    def remove_items(self):
        all_items = self.scene().items()
        for item in all_items:
            self.scene().removeItem(item)

    def clear_canvas(self):
        self.remove_items()
        self.item_dict = {}
        self.selected_id = ''
        self.status = ''
        self.temp_algorithm = ''
        self.color = QColor(0, 0, 0)
        self.temp_id = ''
        self.temp_item = None
        self.temp_isNew = True

    def start_draw_line(self, algorithm, item_id):
        self.temp_isNew = True
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.temp_isNew = True
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    def start_draw_ellipse(self, algorithm, item_id):
        self.temp_isNew = True
        self.status = 'ellipse'
        self.temp_algorithm = algorithm
        self.temp_id = item_id
    
    def start_draw_curve(self, algorithm, item_id):
        self.temp_isNew = True
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def finish_draw(self):
        self.temp_isNew = True                      # TODO: TBD
        if self.temp_item:
            self.temp_item.finish_draw()
        self.temp_item = None
        self.temp_id = self.main_window.get_id()

    def start_edit_item(self, edit_type, algorithm=None):
        self.finish_draw()
        self.status = edit_type
        self.temp_algorithm = algorithm
        self.updateScene([self.sceneRect()])

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])
        boundingRect = self.item_dict[selected].boundingRect()
        self.main_window.statusBar().showMessage(f'图元选择: {selected} [{int(boundingRect.left())}, {int(boundingRect.bottom())}, {int(boundingRect.right())}, {int(boundingRect.top())}]')
    
    def add_item_to_scene_dict(self):
        self.scene().addItem(self.temp_item)
        self.item_dict[self.temp_id] = self.temp_item

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        print("start:", [x, y])
        if event.button() == Qt.LeftButton: 
            if self.status == 'line':
                self.temp_item = MyItem(self, self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color, self.pen_width)
                self.add_item_to_scene_dict()
            elif self.status == 'polygon':
                if self.temp_isNew:
                    self.temp_isNew = False
                    self.temp_item = MyItem(self, self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color, self.pen_width)
                    self.add_item_to_scene_dict()
            elif self.status == 'ellipse':
                self.temp_item = MyItem(self, self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color, self.pen_width)
                self.add_item_to_scene_dict()
            elif self.status == 'curve':
                if self.temp_isNew:
                    self.temp_isNew = False
                    self.temp_item = MyItem(self, self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color, self.pen_width)
                    self.add_item_to_scene_dict()
                else:                                           # 插入控制点
                    insert_pos = len(self.temp_item.p_list) - 1
                    self.temp_item.p_list.insert(insert_pos, [x, y])
            elif self.status == 'translate' and self.selected_id != '' and self.selected_id in self.item_dict:
                if not (self.status == 'rotate' and self.item_dict[self.selected_id].item_type == 'ellipse'):
                    self.temp_id = self.selected_id
                    self.temp_item = self.item_dict[self.temp_id]
                    self.flags[self.status] = True
                    self.x0, self.y0 = x, y            
            elif self.status in ['rotate', 'scale'] and self.selected_id != '' and self.selected_id in self.item_dict:
                if not (self.status == 'rotate' and self.item_dict[self.selected_id].item_type == 'ellipse'):
                    if self.flags[self.status] == 0:            # 抛锚
                        self.temp_id = self.selected_id
                        self.temp_item = self.item_dict[self.temp_id]
                        self.flags[self.status] = 1
                        self.temp_anchor = MyItem(self, self.temp_id, 'rect', [[x, y], [x, y]], '', QColor(255,0,255), 10)
                        self.scene().addItem(self.temp_anchor)
                    elif self.flags[self.status] == 1:
                        self.flags[self.status] = 2
                        self.x0, self.y0 = x, y
            elif self.status == 'clip' and self.selected_id != '' and self.selected_id in self.item_dict:
                if self.item_dict[self.selected_id].item_type == 'line':
                    self.temp_id = self.selected_id
                    self.temp_item = self.item_dict[self.temp_id]
                    self.flags['clip'] = 1
                    self.x0, self.y0 = x, y
                    self.temp_rect = MyItem(self, self.temp_id, 'rect', [[x, y], [x, y]], '', Qt.blue, 1)
                    self.scene().addItem(self.temp_rect)
            elif self.status == 'paste':
                last_pos = self.copy_item.p_list[0]
                self.copy_item.edit('translate', '', [x - last_pos[0], y - last_pos[1]])
                self.scene().addItem(self.copy_item)
                self.item_dict[self.copy_item.id] = self.copy_item
                self.selection_changed(self.copy_item.id)
                self.status = ''
                self.copy_item = None
            elif self.status == '':
                self.clear_selection()
                for item in self.item_dict.values():            # 遍历图元字典，确定选择对象
                    if item.contains([x, y]) and self.selected_id == '':
                        self.selection_changed(item.id)
        elif event.button() == Qt.RightButton:
            if self.status in ['polygon', 'curve']:
                self.finish_draw()

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line'and self.temp_item != None:
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon'and self.temp_item != None:
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse'and self.temp_item != None:
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve' and self.temp_item != None:
            modify_pos = -1 if len(self.temp_item.p_list) == 2 else -2
            self.temp_item.p_list[modify_pos] = [x, y]
        elif self.status == 'translate' and self.flags[self.status]:
            self.temp_item.edit('translate', '', [x - self.x0, y - self.y0])
            self.x0, self.y0 = x, y
        elif self.status == 'rotate' and self.flags[self.status] == 2:
            rx, ry = self.temp_anchor.center()
            theta = (math.atan2(y - ry, x - rx) - math.atan2(self.y0 - ry, self.x0 - rx)) * 180 / math.pi
            self.temp_item.edit('rotate', '', [rx, ry, theta])
        elif self.status == 'scale' and self.flags[self.status] == 2:
            sx, sy = self.temp_anchor.center()
            last_len = math.sqrt((self.x0 - sx) ** 2 + (self.y0 - sy) ** 2)
            now_len = math.sqrt((x - sx) ** 2 + (y - sy) ** 2)
            s = float(now_len / last_len)
            self.temp_item.edit('scale', '', [sx, sy, s])
        elif self.status == 'clip' and self.flags[self.status]:
            self.temp_rect.p_list[1] = [x, y]
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y()) 
        print("end:", [x, y])                           # TODO: delete
        if event.button() == Qt.LeftButton:             # 左键释放
            if self.status in ['line', 'ellipse']:
                self.finish_draw()
            elif self.status == 'polygon':
                self.temp_item.p_list.append([x, y])
            elif self.status == 'curve':
                if len(self.temp_item.p_list) == MAX_NUM_CONTROL_POINTS:
                    self.finish_draw()
            elif self.status == 'translate' and self.flags[self.status] == 1:
                self.flags[self.status] = 0
            elif self.status in ['rotate', 'scale'] and self.flags[self.status] == 2:
                self.flags[self.status] = 0
                self.scene().removeItem(self.temp_anchor)
                self.temp_anchor = None
                self.finish_draw()
            elif self.status == 'clip' and self.flags[self.status] == 1:
                self.flags[self.status] = 0
                self.temp_item.edit('clip', self.temp_algorithm, [[self.x0, self.y0], [x, y]])
                self.scene().removeItem(self.temp_rect)
                p_list = self.temp_item.p_list
                if not p_list or p_list[0][0] == p_list[1][0] and p_list[0][1] == p_list[1][1]:
                    self.scene().removeItem(self.temp_item)
                self.status = ''
                self.selected_id = ''
                self.finish_draw()
        self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)



class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, canvas: QGraphicsView, item_id: str, item_type: str, p_list: list, algorithm: str = '', color: QColor = QColor(0, 0, 0), width: int = 2, parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.color = color
        self.width = width
        self.parent = parent
        self.pen = QPen()
        self.pen.setColor(color)
        self.pen.setWidth(width)
        self.canvas = canvas
        self.isDrawFinished = False
        self.selected = False
        self.centerPoint = None

        self.computeCenter()        # 计算图元中心
    
    def finish_draw(self):
        self.isDrawFinished = True
        self.computeCenter()
        self.last_p_list = self.p_list

    def computeCenter(self):
        if len(self.p_list) > 0:
            x_list = [p[0] for p in self.p_list]
            y_list = [p[1] for p in self.p_list]
            self.centerPoint = [(max(x_list) + min(x_list)) / 2, (max(y_list) + min(y_list)) / 2]      

    def center(self):
        return self.centerPoint

    def contains(self, point):
        boundingRect = self.boundingRect()
        if boundingRect.left() <= point[0] and point[0] <= boundingRect.right():
            if boundingRect.bottom() >= point[1] and point[1] >= boundingRect.top():
                return True
        return False

    def edit(self, edit_type, algorithm, params):
        if edit_type == 'translate':
            tx, ty = params
            self.p_list = alg.translate(self.p_list, tx, ty)
        elif edit_type == 'rotate':
            rx, ry, r = params
            self.p_list = alg.rotate(self.last_p_list, rx, ry, r)
        elif edit_type == 'scale':
            sx, sy, s = params
            self.p_list = alg.scale(self.last_p_list, sx, sy, s)
        elif edit_type == 'clip':
            x_min = min(params[0][0], params[1][0])
            y_min = min(params[0][1], params[1][1])
            x_max = max(params[0][0], params[1][0])
            y_max = max(params[0][1], params[1][1])
            self.p_list = alg.clip(self.p_list, x_min, y_min, x_max, y_max, algorithm)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        painter.setPen(self.pen)
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())    
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect()) 
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            for p in item_pixels:
                painter.drawPoint(*p)
            if not self.isDrawFinished:
                painter.setPen(QColor(0, 0, 255))
                item_pixels = alg.draw_polygon(self.p_list, 'Bresenham')
                for p in item_pixels:
                    painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())   
        elif self.item_type == 'rect':
            painter.drawRect(self.boundingRect())     

    def boundingRect(self) -> QRectF:
        if len(self.p_list) == 0:
            return QRectF(0, 0, 0, 0)
        x = min(self.p_list, key=lambda x: x[0])[0]
        y = min(self.p_list, key=lambda y: y[1])[1]
        w = max(self.p_list, key=lambda x: x[0])[0] - x
        h = max(self.p_list, key=lambda y: y[1])[1] - y
        return QRectF(x - 1, y - 1, w + 2, h + 2)
    
    def copy(self):
        return MyItem(self.canvas, self.id, self.item_type, self.p_list, self.algorithm, self.color, self.width, self.parent)

class MyGraphicsScene(QGraphicsScene):
    """
    自定义画板类，背景选择绘制网格线
    """

    def __init__(self, *args, isShowGrid=False):
        super().__init__(*args)
        self.isShowGrid = isShowGrid
    
    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        if not self.isShowGrid:
            return super().drawBackground(painter, rect)

        # 边界值调整
        density = 25
        left = rect.left()
        right = rect.right()
        top = rect.top()
        bottom = rect.bottom()
        left = (left / density) * density
        right = (right / density) * density
        top = (top / density) * density
        bottom = (bottom / density) * density
        # 设置画笔
        pen = QPen()
        pen.setColor(QColor(60,60,60))
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        # 绘制横线
        for i in range(0, int(top-1), -density):       # 绘制Y轴正半轴
            painter.drawLine(left, i, right, i)
        for i in range(0, int(bottom+1), density):       # 绘制Y轴负半轴
            painter.drawLine(left, i, right, i)
        # 绘制竖线
        for i in range(0, int(right+1), density):       # 绘制X轴正半轴
            painter.drawLine(i, top, i, bottom)
        for i in range(0, int(left-1), -density):       # 绘制X轴负半轴
            painter.drawLine(i, top, i, bottom)


# 主窗体的宽与高
MAINWINDOW_W = 1800
MAINWINDOW_H = 1600

class MainWindow(QMainWindow):
    """
    主窗口类
    """
    # 默认画布的宽与高
    DEFAULT_W = 1700
    DEFAULT_H = 1500
    
    def __init__(self):
        super().__init__()
        self.item_cnt = 0
        # 使用QGraphicsView作为画布
        self.scene = MyGraphicsScene(self, isShowGrid=True)
        self.scene.setSceneRect(1, 1, self.DEFAULT_W, self.DEFAULT_H)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.DEFAULT_W + 4, self.DEFAULT_H + 4)
        self.canvas_widget.setStyleSheet("padding: 0px; border: 0px; background-color: rgb(250, 250, 250); border-color: rgb(0, 0, 0); border-width: 2px; border-style: solid;")
        self.canvas_widget.main_window = self
        # 设置菜单栏
        menubar = self.menuBar()
        menubar.setFont(FONT)
        # 文件栏
        file_menu = menubar.addMenu('文件')
        file_menu.setFont(FONT)
        save_act = file_menu.addAction('保存图片')
        save_act.setIcon(QIcon("gui_files/ImageIcon/save.png"))
        set_pen_menu = file_menu.addMenu('设置画笔')
        set_pen_menu.setFont(FONT)
        set_pen_menu.setIcon(QIcon("gui_files/ImageIcon/pen.png"))
        set_pen_color_act = set_pen_menu.addAction('画笔颜色')
        set_pen_color_act.setIcon(QIcon("gui_files/ImageIcon/set_color.png"))
        set_pen_width_act = set_pen_menu.addAction('画笔粗细')
        set_pen_width_act.setIcon(QIcon("gui_files/ImageIcon/set_width.png"))
        reset_canvas_act = file_menu.addAction('重置画布')
        reset_canvas_act.setIcon(QIcon("gui_files/ImageIcon/clear.png"))
        exit_act = file_menu.addAction('退出')
        exit_act.setIcon(QIcon("gui_files/ImageIcon/exit.png"))
        # 编辑栏
        edit_menu = menubar.addMenu('编辑')
        edit_menu.setFont(FONT)
        select_act = edit_menu.addAction('选择')
        select_act.setIcon(QIcon("gui_files/ImageIcon/select.png"))
        copy_act = edit_menu.addAction('复制')
        copy_act.setIcon(QIcon("gui_files/ImageIcon/copy.png"))
        paste_act = edit_menu.addAction('粘贴')
        paste_act.setIcon(QIcon("gui_files/ImageIcon/paste.png"))        
        translate_act = edit_menu.addAction('平移')
        translate_act.setIcon(QIcon("gui_files/ImageIcon/translate.png"))
        rotate_act = edit_menu.addAction('旋转')
        rotate_act.setIcon(QIcon("gui_files/ImageIcon/rotate.png"))
        scale_act = edit_menu.addAction('缩放')
        scale_act.setIcon(QIcon("gui_files/ImageIcon/scale.png"))
        clip_menu = edit_menu.addMenu('裁剪')
        clip_menu.setFont(FONT)
        clip_menu.setIcon(QIcon("gui_files/ImageIcon/clip.png"))
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        # 绘制栏
        draw_menu = menubar.addMenu('绘制')
        draw_menu.setFont(FONT)
        line_menu = draw_menu.addMenu('线段')
        line_menu.setIcon(QIcon("gui_files/ImageIcon/lines.png"))
        line_menu.setFont(FONT)
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_menu.setIcon(QIcon("gui_files/ImageIcon/polygon.png"))
        polygon_menu.setFont(FONT)
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        ellipse_act.setIcon(QIcon("gui_files/ImageIcon/ellipse.png"))
        curve_menu = draw_menu.addMenu('曲线')
        curve_menu.setIcon(QIcon("gui_files/ImageIcon/curve.png"))
        curve_menu.setFont(FONT)
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        # 视图栏
        view_menu = menubar.addMenu('视图')
        view_menu.setFont(FONT)
        self.show_grid_act = view_menu.addAction('显示网格')
        self.show_grid_act.setCheckable(True)
        self.show_grid_act.setChecked(True)
        # 帮助栏
        help_menu = menubar.addMenu('帮助')
        help_menu.setFont(FONT)
        help_act = help_menu.addAction('系统文档')
        help_act.setIcon(QIcon("gui_files/ImageIcon/help.png"))
        # 连接信号和槽函数
        save_act.triggered.connect(self.save_action)                            # 保存
        set_pen_color_act.triggered.connect(self.set_pen_color_action)          # 设置画笔颜色
        set_pen_width_act.triggered.connect(self.set_pen_width_action)          # 设置画笔粗细
        reset_canvas_act.triggered.connect(self.reset_canvas_action)            # 重置画布
        exit_act.triggered.connect(qApp.quit)                                   # 退出
        select_act.triggered.connect(self.select_action)                        # 选择
        copy_act.triggered.connect(self.copy_action)                            # 复制
        paste_act.triggered.connect(self.paste_action)                          # 粘贴
        translate_act.triggered.connect(self.translate_action)                  # 平移
        rotate_act.triggered.connect(self.rotate_action)                        # 旋转
        scale_act.triggered.connect(self.scale_action)                          # 缩放
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)  # Cohen-Suther裁剪
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)  # liang-Barsky裁剪
        line_naive_act.triggered.connect(self.line_naive_action)                # naive生成直线
        line_dda_act.triggered.connect(self.line_dda_action)                    # dda生成直线
        line_bresenham_act.triggered.connect(self.line_bresenham_action)        # bresenham生成直线
        polygon_dda_act.triggered.connect(self.polygon_dda_action)              # dda生成多边形
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)  # bresenham生成多边形
        ellipse_act.triggered.connect(self.ellipse_action)                      # 生成椭圆
        curve_bezier_act.triggered.connect(self.curve_bezier_action)            # bezier生成曲线
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)        # b_spline生成曲线
        self.show_grid_act.triggered.connect(self.show_grid_action)             # 开启/关闭网格
        help_act.triggered.connect(self.help_action)                            # 帮助
        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(MAINWINDOW_W, MAINWINDOW_H)
        self.setWindowTitle('图形学作业')
        self.setWindowIcon(QIcon("gui_files/ImageIcon/paintIcon4.png"))


    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id
    
    def save_action(self):
        save_name, _ = QFileDialog.getSaveFileName(self, '保存图片', CWD, '位图(*.bmp)')
        if save_name == '':
            return
        rect = self.canvas_widget.viewport().rect()
        # Create a pixmap the same size as your graphicsview
        # You can make this larger or smaller if you want.
        pixmap = QPixmap(rect.size())
        pixmap.fill(Qt.white)
        painter = QPainter(pixmap)
        # Render the graphicsview onto the pixmap and save it out.
        self.canvas_widget.render(painter, QRectF(pixmap.rect()), rect)
        painter.end()
        pixmap.save(os.path.join(save_name))
    
    def set_pen_color_action(self):
        new_color = QColorDialog.getColor(parent=self, title='设置画笔颜色')
        self.canvas_widget.set_color(QColor(new_color.rgba()))
    
    def set_pen_width_action(self):
        new_width, _ = QInputDialog.getInt(self, '设置画笔粗细', '输入画笔粗细', min=1, max=10)
        self.canvas_widget.set_width(int(new_width))

    def reset_canvas_action(self):
        dialog = MyResetDialog(maxWidth=self.DEFAULT_W, maxHeight=self.DEFAULT_H)
        if dialog.exec_():
            new_width, new_height, valid = dialog.get_data()
            if valid:
                self.scene.setSceneRect(1, 1, new_width, new_height)
                self.canvas_widget.setFixedSize(new_width + 4, new_height + 4)
                self.canvas_widget.clear_canvas()
                self.item_cnt = 0                                   # TODO: TBD

    def select_action(self):
        self.statusBar().showMessage('选择图元：鼠标左键点击选择图元，点击空白处取消选择，多个图元叠加，优先选择图元编号小者')
        self.canvas_widget.reset_status()
        self.canvas_widget.clear_selection()
    
    def copy_action(self):
        success = self.canvas_widget.start_copy()
        if success:
            self.statusBar().showMessage('复制图元：复制成功！')
        else:
            self.statusBar().showMessage('复制图元：无选中图元，先选择图元，再点击复制')

    def paste_action(self):
        self.statusBar().showMessage('粘贴图元：鼠标左键点击即可粘贴图元，图元尽可粘贴一次')
        self.canvas_widget.start_paste()

    def translate_action(self):
        self.statusBar().showMessage('平移图元：按住鼠标左键平移图元，松开结束')
        self.canvas_widget.start_edit_item('translate')
        
    def rotate_action(self):
        self.statusBar().showMessage('旋转图元：先在画布上单击一处抛掷锚点，再按住鼠标左键围绕锚点旋转图元，松开结束')
        self.canvas_widget.start_edit_item('rotate')
        
    def scale_action(self):
        self.statusBar().showMessage('缩放图元：先在画布上单击一处抛掷锚点，再按住鼠标左键围绕锚点缩放图元，松开结束')
        self.canvas_widget.start_edit_item('scale')
        
    def clip_cohen_sutherland_action(self):
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪线段：按住鼠标左键并移动，产生裁剪框，松开左键完成裁剪，注意非线段不裁剪')
        self.canvas_widget.start_edit_item('clip', 'Cohen-Sutherland')
        
    def clip_liang_barsky_action(self):
        self.statusBar().showMessage('Liang-Barsky算法裁剪线段：按住鼠标左键并移动，产生裁剪框，松开左键完成裁剪，注意非线段不裁剪')
        self.canvas_widget.start_edit_item('clip', 'Liang-Barsky')
        
    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段：按住鼠标左键并移动，产生线段，松开左键完成绘制')
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段：按住鼠标左键并移动，产生线段，松开左键完成绘制')
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段：按住鼠标左键并移动，产生线段，松开左键完成绘制')
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形：按住左键移动，然后松开完成多边形一条边的绘制，点击右键完成绘制，多边形首末点会自动连接一条线')
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.canvas_widget.clear_selection()
        self.statusBar().showMessage('Bresenham算法绘制多边形：按住左键移动，然后松开完成多边形一条边的绘制，点击右键完成绘制，多边形首末点会自动连接一条线')
    
    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse('', self.get_id())
        self.statusBar().showMessage('绘制椭圆：按住左键移动，然后松开完成椭圆绘制')
        self.canvas_widget.clear_selection() 
    
    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线：首先按住左键绘制一条线段，然后松开，之后按照多边形绘制方法绘制控制多边形，同时生成曲线，最多绘制6个控制点或按右键提前结束绘制')
        self.canvas_widget.clear_selection()
    
    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('B-spline算法绘制曲线：首先按住左键绘制一条线段，然后松开，之后按照多边形绘制方法绘制控制多边形，同时生成曲线，最多绘制6个控制点或按右键提前结束绘制')
        self.canvas_widget.clear_selection()
    
    def show_grid_action(self):
        self.scene.isShowGrid = not self.scene.isShowGrid
        self.show_grid_act.setChecked(self.scene.isShowGrid)
        self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])

    def help_action(self):
        try:
            webbrowser.open(HELP_FILE)
        except Exception as e:
            print("Can't open %s" % HELP_FILE)
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
