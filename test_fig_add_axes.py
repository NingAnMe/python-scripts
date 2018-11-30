#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/11/28
@Author  : AnNing
"""
import matplotlib.pyplot as plt
import matplotlib.image as img

width = 0.1
l1 = 0
l2 = width
b = 0
w = width
h = width

label1 = 'label1'
label2 = 'label2'

image1 = img.imread('logoL.jpg')
image2 = img.imread('logoR.jpg')

rect1 = l1, b, w, h
rect2 = l2, b, w, h
fig = plt.figure(figsize=(4, 4), dpi=100)
ax_l = fig.add_axes(rect1, label=label1, anchor='C')
ax_r = fig.add_axes(rect2, label=label2, anchor='C')
ax_l.axis('off')
ax_r.axis('off')
ax_l.imshow(image1)
ax_r.imshow(image2)
fig.show()


def add_image(fig, imgsize, image_path, position='LB'):
    """
    :param fig: matplotlib.figure
    :param figsize: (width, high)
    :param imgsize: (width, high)
    :param image_path:
    :param position: 'LB' or 'RB'
    :return:
    """
    img_width, img_high = imgsize
    if position == 'LB':
        rect = [0, 0, img_width, img_high]
    elif position == 'RB':
        rect = [1.-img_width, 0, img_width, img_high]
    else:
        raise KeyError
    image = img.imread(image_path)
    ax = fig.add_axes(rect, anchor='C')
    ax.imshow(image)
    return fig, ax

# fig.add_axes(rect,label=label2)
# fig.add_axes(rect, frameon=False, facecolor='g')
# fig.add_axes(rect, polar=True)
# ax=fig.add_axes(rect, projection='polar')
# fig.delaxes(ax)
# fig.add_axes(ax)
# fig.show()
