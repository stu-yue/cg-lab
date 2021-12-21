#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os
import cg_algorithms as alg
import numpy as np
from PIL import Image


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    os.makedirs(output_dir, exist_ok=True)

    item_dict = {}
    transform_dict = {}
    pen_color = np.zeros(3, np.uint8)   # paintbrush, [R, G, B], 0-255
    width = 0
    height = 0

    with open(input_file, 'r') as fp:
        line = fp.readline()
        while line:
            line = line.strip().split(' ')
            if line[0] == 'resetCanvas':
                width = int(line[1])
                height = int(line[2])
                item_dict = {}
                transform_dict = {}
            elif line[0] == 'saveCanvas':
                save_name = line[1]
                canvas = np.zeros([height, width, 3], np.uint8)
                canvas.fill(255)        # fill canvas with white
                    
                for item_id, (transform_type, transform_params) in transform_dict.items():
                    p_list = item_dict[item_id][1]                  # transform_params ---> [x, y, ..., algorithm]
                    if transform_type == 'translate':
                        dx, dy = transform_params
                        p_list_t = alg.translate(p_list, dx, dy)
                    elif transform_type == 'rotate':
                        x, y, r = transform_params
                        p_list_t = alg.rotate(p_list, x, y, r)
                    elif transform_type == 'scale':
                        x, y, s = transform_params
                        p_list_t = alg.scale(p_list, x, y, s)
                    elif transform_type == 'clip':
                        x0, y0, x1, y1, algorithm = transform_params
                        p_list_t = alg.clip(p_list, x0, y0, x1, y1, algorithm)
                    item_dict[item_id][1] = p_list_t       # transform item

                for item_type, p_list, algorithm, color in item_dict.values():
                    if item_type == 'line':
                        pixels = alg.draw_line(p_list, algorithm)
                    elif item_type == 'polygon':
                        pixels = alg.draw_polygon(p_list, algorithm)
                    elif item_type == 'circle':
                        pixels = alg.draw_circle(p_list)
                    elif item_type == 'ellipse':
                        pixels = alg.draw_ellipse(p_list)
                    elif item_type == 'curve':
                        pixels = alg.draw_curve(p_list, algorithm)
                    # modified
                    for x, y in pixels:
                        if x < 0 or x >= width or y < 0 or y >= height:     # for debug
                            print(x, y)
                            print('Beyond the canvas!') 
                        else:
                            canvas[y, x] = color

                Image.fromarray(canvas).save(os.path.join(output_dir, save_name + '.bmp'), 'bmp')

            elif line[0] == 'setColor':
                pen_color[0] = int(line[1])
                pen_color[1] = int(line[2])
                pen_color[2] = int(line[3])
            elif line[0] == 'drawLine':
                assert len(line) == 7, 'drawLine: Seven arguments are expected!'
                item_id = line[1]
                x0, y0, x1, y1 = map(int, line[2: 6])
                algorithm = line[6]
                item_dict[item_id] = ['line', [[x0, y0], [x1, y1]], algorithm, np.array(pen_color)]
            elif line[0] == 'drawPolygon':
                item_id = line[1]
                p_list = [[int(x), int(y)] for x, y in zip(line[2: -2: 2], line[3: -1: 2])]
                algorithm = line[-1]
                item_dict[item_id] = ['polygon', p_list, algorithm, np.array(pen_color)]
            elif line[0] == 'drawCircle':
                assert len(line) == 6, 'drawCircle: Six arguments are expected!'
                item_id = line[1]
                x0, y0, x1, y1 = map(int, line[2: 6])
                algorithm = 'Bresenham'
                item_dict[item_id] = ['circle', [[x0, y0], [x1, y1]], algorithm, np.array(pen_color)]
            elif line[0] == 'drawEllipse':
                assert len(line) == 6, 'drawEllipse: Six arguments are expected!'
                item_id = line[1]
                x0, y0, x1, y1 = map(int, line[2: 6])
                algorithm = 'midpoint'
                item_dict[item_id] = ['ellipse', [[x0, y0], [x1, y1]], algorithm, np.array(pen_color)]
            elif line[0] == 'drawCurve':
                item_id = line[1]
                p_list = [[int(x), int(y)] for x, y in zip(line[2: -2: 2], line[3: -1: 2])]
                algorithm = line[-1]
                item_dict[item_id] = ['curve', p_list, algorithm, np.array(pen_color)]
            elif line[0] == 'translate':
                assert len(line) == 4, 'translate: Four arguments are expected!'
                item_id = line[1]
                dx, dy = map(int, line[2: ])
                transform_dict[item_id] = ['translate', [dx, dy]]
            elif line[0] == 'rotate':
                assert len(line) == 5, 'rotate: Five arguments are expected!'
                item_id = line[1]
                x, y, r = map(int, line[2: ])
                transform_dict[item_id] = ['rotate', [x, y, r]]
            elif line[0] == 'scale':
                assert len(line) == 5, 'scale: Five arguments are expected!'
                item_id = line[1]
                x, y, s = int(line[2]), int(line[3]), float(line[4])
                transform_dict[item_id] = ['scale', [x, y, s]]
            elif line[0] == 'clip':
                assert len(line) == 7, 'clip: Seven arguments are expected!'
                item_id = line[1]
                x0, y0, x1, y1 = map(int, line[2: 6])
                x_min, y_min, x_max, y_max = min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)
                algorithm = line[6]
                transform_dict[item_id] = ['clip', [x_min, y_min, x_max, y_max, algorithm]]

            ...

            line = fp.readline()

