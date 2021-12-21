#!/usr/bin/env python
# -*- coding:utf-8 -*-
# refer to Procedural Elements for Computer Graphics
# 本文件只允许依赖math库
import math

# for debugging
import os
import time

def sign(x):
    if x > 0:
        return 1
    elif x == 0:
        return 0
    else:
        return -1


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if len(p_list) == 0:
        return []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if (x0, y0) == (x1, y1):                                # 避免length为0
            result.append((x0, y0))
        else:
            length = max(abs(x1 - x0), abs(y1 - y0))            # 取直线的最大增长长度
            dx, dy = (x1 - x0) / length, (y1 - y0) / length     # 选择dx，dy中最大者为光栅增大的一个单元，(其中一个增大为1个单元，另一个为k或1/k个单元)
            x, y = x0, y0
            for i in range(0, length + 1):                      # [0, length] contains end points
                result.append((int(x + 0.5), int(y + 0.5)))     # 对坐标四舍五入
                x = x + dx
                y = y + dy
    elif algorithm == 'Bresenham':                              # refer to 2.3.2 general Bresenham (integer version)
        if (x0, y0) == (x1, y1):
            result.append((x0, y0))
        else:                                                   # (x0, y0) and (x1, y1) are not equal
            x, y = x0, y0
            dx, dy = abs(x1 - x0), abs(y1 - y0)
            sx, sy = sign(x1 - x0), sign(y1 - y0)
            if dy > dx:                                         # 根据直线斜率，选择是否互换dy，dx
                dx, dy = dy, dx
                Interchange = 1
            else:
                Interchange = 0
            e = 2 * dy  - dx                                    # 初始化决策参数
            for i in range(0, dx + 1):                          # [0, dx]
                result.append((int(x), int(y)))
                while e > 0:
                    if Interchange ==  1:
                        x = x + sx
                    else:
                        y = y + sy
                    e = e - 2 * dx
                if Interchange == 1:
                    y = y + sy
                else:
                    x = x + sx
                e = e + 2 * dy
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_circle(p_list, algorithm=None):
    """绘制圆(Bresenham算法)

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]])  圆的正方形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """

    def mh(x, y, dis):
        x = x + 1
        y = y
        dis = dis + 2 * x + 1
        return x, y, dis

    def md(x, y, dis):
        x = x + 1
        y = y - 1
        dis = dis + 2 * x - 2 * y + 2
        return x, y, dis

    def mv(x, y, dis):
        x = x
        y = y - 1
        dis = dis - 2 * y + 1
        return x, y, dis

    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if x0 != y0 or x1 != y1:
        raise ValueError('To plot a circle, need a square enclosure!')
    # compute center and radius
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2
    R = abs(x1 - x0) // 2
    #print(cx, cy, R)        # TODO: delete
    # initialize the variables
    x = 0
    y = R
    dis = (x + 1)**2 + (y - 1)**2 - R**2
    Limit = 0
    while y >= Limit:
        result.append((int(cx + x), int(cy + y)))   # in first quadrant
        result.append((int(cx - x), int(cy + y)))   # in second quadrant
        result.append((int(cx - x), int(cy - y)))   # in third quadrant
        result.append((int(cx + x), int(cy - y)))   # in fourth quadrant
        # if case 1 or 2
        if dis < 0:
            delta = 2 * dis + 2 * y - 1
            # determin whetheer case 1 or case 2
            if delta <= 0:
                x, y, dis = mh(x, y, dis)                 # call mh(x, y, dis)
            else:
                x, y, dis = md(x, y, dis)                 # call md(x, y, dis)
        elif dis > 0:
            delta = 2 * dis - 2 * x - 1
            if delta <= 0:
                x, y, dis = md(x, y, dis)                 # call md(x, y, dis)
            else:
                x, y, dis = mv(x, y, dis)                 # call mv(x, y, dis)
        elif dis == 0:
            x, y, dis = md(x, y, dis)                     # call md(x, y, dis)
    # finish
    return result


def draw_ellipse(p_list, algorithm=None):
    """绘制椭圆（采用中点圆生成算法）       refer to 2.5 Efficient midpoint ellipse algorithm

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    # compute center and radius
    cx = (x0 + x1) // 2         # symmetric center coordinates are rounded down
    cy = (y0 + y1) // 2
    a = abs(x1 - x0) // 2       # semi-axes are alse rounded down
    b = abs(y1 - y0) // 2
    # initialize the variables
    x = int(a + 1/2)
    y = 0
    # define temporary variables
    taa, t2aa, t4aa = a*a, 2*a*a, 4*a*a
    tbb, t2bb, t4bb = b*b, 2*b*b, 4*b*b
    t2abb = 2*a*b*b
    t2bbx = 2*b*b*x
    # initialize the decision variables in region 1
    d1 = t2bbx * (x - 1) + tbb / 2 + t2aa * (1 - tbb)
    while tbb * (x - 1/2) > taa * (y + 1):          # start in region 1
        result.append((int(cx + x), int(cy + y)))   # in first quadrant
        result.append((int(cx - x), int(cy + y)))   # in second quadrant
        result.append((int(cx - x), int(cy - y)))   # in third quadrant
        result.append((int(cx + x), int(cy - y)))   # in fourth quadrant
        if d1 < 0:
            y = y + 1
            d1 = d1 + t4aa * y + t2aa
        else:
            x = x - 1
            y = y + 1
            d1 = d1 + t4aa * y - t4bb * x + t2aa
    # initialize the decision variables in region 2
    d2 = t2bb * (x*x + 1) - t4bb * x + t2aa * (y*y + y -tbb) + taa / 2
    while x >= 0:                                   # start in region 2
        result.append((int(cx + x), int(cy + y)))   # in first quadrant
        result.append((int(cx - x), int(cy + y)))   # in second quadrant
        result.append((int(cx - x), int(cy - y)))   # in third quadrant
        result.append((int(cx + x), int(cy - y)))   # in fourth quadrant
        if d2 < 0:
            x = x - 1
            y = y + 1
            d2 = d2 + t4aa * y - t4bb * x + t2bb
        else:
            x = x - 1
            d2 = d2 - t4bb * x + t2bb
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    x_min, x_max = min(p_list, key=lambda x: x[0])[0], max(p_list, key=lambda x: x[0])[0]
    y_min, y_max = min(p_list, key=lambda x: x[1])[1], max(p_list, key=lambda x: x[1])[1]
    n_points = max(((x_max - x_min) + (y_max - y_min)) * 2, 2)
    
    if algorithm == 'Bezier':
        t, gap = 0, 1 / n_points
        while t <= 1:
            x, y = de_Casteljau(p_list, t)
            t += gap
            result.append([x, y])
    elif algorithm == 'B-spline':
        m = len(p_list)
        k = 3
        u, gap = k, (m - k) / n_points
        while (u < m):
            u += gap
            x, y = 0, 0
            for i in range(0, m):
                B_ik = deBoor_Cox(u, k + 1, i)
                x += B_ik * p_list[i][0]
                y += B_ik * p_list[i][1]
            result.append((int(x + 0.5), int(y + 0.5)))        
    return result

# Subroutine of Bezier
def de_Casteljau(p_list, u):
    """de Casteljau算法
    :param n: (int) Bezier曲线的次数
    :param p_list: (list of list of int) 控制顶点坐标, (n+1)个控制点
    :return Bezier_curve: (func) n次Bezier曲线的型值点C(u)
    """
    #        |--P_i  (r=0)
    # P^r_i--|
    #        |--(1-t)P^(r-1)_i + tP^(r-1)_(i+1)  (r=1,...,n; i=0,...,n-r)

    Q = [[x, y] for x, y in p_list]           # save input
    n = len(p_list) - 1
    for k in range(n):                      # for k:= 1 to n do
        for i in range(n - k):
            Q[i][0] = (1 - u) * Q[i][0] + u * Q[i + 1][0]
            Q[i][1] = (1 - u) * Q[i][1] + u * Q[i + 1][1]
    return int(Q[0][0] + 0.5), int(Q[0][1] + 0.5)

# Subroutine of B-splline
def deBoor_Cox(u, k, i):
    """deBoor-Cox算法
    :param u: (float) 参数u
    :param k: (int) 阶数k，次数 + 1
    :param i: (int) 下标i
    """
    if k == 1:
        if i <= u and u <= i+1:
            return 1
        else:
            return 0
    else:
        coef_1, coef_2 = 0, 0
        if u - i == 0 and i+k-1-i == 0:             # 计算系数1
            coef_1 = 0
        else:
            coef_1 = (u - i) / (i + k - i - 1)
        if i+k-u == 0 and i+k-i-1 == 0:             # 计算系数2
            coef_2 = 0
        else:
            coef_2 = (i+k-u) / (i+k-i-1)
    return coef_1 * deBoor_Cox(u, k-1, i) + coef_2 * deBoor_Cox(u, k-1, i+1)


def translate(p_list, tx, ty):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    #                       [1  0  0]
    # [x2 y2 1] = [x1 y1 1]·|0  1  0|   The homogeneous representation of the translation
    #                       [tx ty 1]
    result = []
    for x, y in p_list:
        result.append((int(x + tx), int(y + ty)))
    return result


def rotate(p_list, rx, ry, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    #                       [cosθ   sinθ   0]
    # [x2 y2 1] = [x1 y1 1]·|-sinθ  cosθ   0|   The homogeneous representation of the ratota
    #                       [ 0      0     1]
    # print(rx, ry, r)
    result = []
    rad = r / 180 * math.pi
    for x, y in p_list:
        x, y = x - rx,  y - ry
        x_t = x * math.cos(rad) - y * math.sin(rad)
        y_t = x * math.sin(rad) + y * math.cos(rad)
        result.append((int(x_t + rx), int(y_t + ry)))
    return result


def scale(p_list, sx, sy, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    #                       [sx  0   0]
    # [x2 y2 1] = [x1 y1 1]·|0   sy  0|   The homogeneous representation of the scale
    #                       [0   0   1]
    result = []
    for x, y in p_list:
        x, y = x - sx,  y - sy
        x_t = x * s
        y_t = y * s
        result.append((int(x_t + sx), int(y_t + sy)))
    return result


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    if algorithm == 'Cohen-Sutherland':
        p1, p2 = p_list[0], p_list[1]
        Window = [x_min, x_max, y_min, y_max]
        p1_code = EndPoint(p1, Window)
        p2_code = EndPoint(p2, Window)
        sum1 = Sum(p1_code)
        sum2 = Sum(p2_code)
        Vflag = Visible(p1_code, p2_code, sum1, sum2)
        if Vflag == 'yes':
            return p_list
        elif Vflag == 'no':
            return []
        Iflag = 1   # initailize Iflag
        if p1[0] == p2[0]:
            Iflag = -1      # vertical line
        elif p1[1] == p2[1]:
            Iflag = 0       # horizontal line
        else:
            Slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
        while Vflag == 'partial':
            for i in range(4):
                if p1_code[3 - i] != p2_code[3 - i]:
                    if p1_code[3 - i] == 0:     # if p1 is inside, swap end points, p_codes, sums
                        p1, p2 = p2, p1
                        p1_code, p2_code = p2_code, p1_code
                        sum1, sum2 = sum2, sum1
                    # find intersections with the window edges
                    # select the appropriate intersection routine
                    if Iflag != -1 and i <= 1:      # left and right edges
                        p1[1] = int(Slope * (Window[i] - p1[0]) + p1[1])
                        p1[0] = Window[i]
                        p1_code = EndPoint(p1, Window)
                        sum1 = Sum(p1_code)
                    if Iflag != 0 and i > 1:
                        if Iflag != -1:
                            p1[0] = int((1 / Slope) * (Window[i] - p1[1]) + p1[0])
                        p1[1] = Window[i]
                        p1_code = EndPoint(p1, Window)
                        sum1 = Sum(p1_code)
                    Vflag = Visible(p1_code, p2_code, sum1, sum2)
                    if Vflag == 'yes':
                        return [p1, p2]
                    elif Vflag == 'no':
                        return []
    elif algorithm == 'Liang-Barsky':
        (x1, y1), (x2, y2) = p_list[0], p_list[1]
        t_range = [0, 1]        # [tL, tU]
        d = [-(x2 - x1), x2 - x1, -(y2 - y1), y2 - y1]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
        for i in range(4):
            if clipt(d[i], q[i], t_range) == False:
                return []
        if t_range[1] < 1:
            x2 = int(x1 + t_range[1] * d[1])
            y2 = int(y1 + t_range[1] * d[3])
        if t_range[0] > 0:
            x1 = int(x1 + t_range[0] * d[1])
            y1 = int(y1 + t_range[0] * d[3])
        return [[x1, y1], [x2, y2]]

# Subroutines of clip(Cohen--Sutherland)
def Visible(p1_code, p2_code, sum1, sum2):
    """可见性判断
    :param p1_code, p2_code: (lsit of int) 1x4的数组，表示端点编码
    :param sum1, sum2: (int) 对端点编码的各位求和，以判断线段与裁剪框的逻辑相交
    :return (int: Vflag) 可见性(完全可见，完全不可见，部分可见)
    """
    Vflag = 'partial'   # assume the line is partially visible
    if sum1 == 0 and sum2 == 0: # check if the line is totaly visible
        Vflag = 'yes'
    else:               # check if the line is trivially invisible
        Inter = Logical(p1_code, p2_code)
        if Inter != 0:  # Inter is non-zero, which means trivially invisible
            Vflag = 'no'
    return Vflag

def EndPoint(p_list, Window):
    """端点编码:
    :param p_list: (list of int) 端点横、纵坐标
    :param Window: (list of int) 裁剪边框的左右下上范围
    :return (list of int: p_code) 1x4的数组，端点编码  
    """
    x_L, x_R, y_B, y_T = Window
    p_x, p_y = p_list
    # p_code = [p_y > y_T, p_y < y_B, p_x > x_R, p_x < x_L]
    # return p_code
    return [int(p_y > y_T), int(p_y < y_B), int(p_x > x_R), int(p_x < x_L)]

def Sum(p_code):
    """编码各位求和
    :param p_code: (list of int) 1x4的数组，表示端点编码
    :return (int: sum) 编码各位求和结果
    """
    return sum(p_code)

def Logical(p1_code, p2_code):
    """逻辑相交
    :param p1_code, p2_code: (list of int) 1x4的数组，表示端点编码
    :return (int: Inter) 对端点编码的各位求和，以判断线段与裁剪框的逻辑相交
    """
    Inter = 0
    for i in range(4):
        Inter += (p1_code[i] + p2_code[i]) >> 1
    return Inter

# Subroutine of clip(Liang-Barsky)
def clipt(d, q, t_range):
    """裁剪t值(完成可见性判断并更新tL和tU)
    :param d: (int) d = - D·n
    :param q: (int) q = w·n
    :param t_range: (list of int) t值的范围，[tL, tU]
    :return (bool: visible) 返回可见性
    """
    L, U = 0, 1
    visible = True
    if d == 0 and q < 0:
        visible = False
    elif d < 0:
        t = q / d
        if t > t_range[U]:
            visible = False
        elif t > t_range[L]:
            t_range[L] = t
    elif d > 0:
        t = q / d
        if t < t_range[L]:
            visible = False
        elif t < t_range[U]:
            t_range[U] = t
    return visible
