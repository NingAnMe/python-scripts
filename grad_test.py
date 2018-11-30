#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2018/11/27
@Author  : AnNing
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def create_sample_data(m):
    # check if saved before
    Xfile = Path("XData.npy")
    Yfile = Path("YData.npy")
    # load data from file
    if Xfile.exists() & Yfile.exists():
        X = np.load(Xfile)
        Y = np.load(Yfile)
    else:  # generate new data
        X = np.random.random(m)
        # create some offset as noise to simulate real data
        noise = np.random.normal(0, 0.1, X.shape)
        # genarate Y data
        W = 2
        B = 3
        Y = X * W + B + noise
        np.save("XData.npy", X)
        np.save("YData.npy", Y)
    return X, Y


def forward_calculation(w, b, x):
    z = w * x + b
    return z


# w:weight, b:bias, X,Y:sample data, count: count of sample, prev_loss:last time's loss
def check_diff(w, b, X, Y, count, prev_loss):
    Z = w * X + b
    LOSS = (Z - Y) ** 2
    loss = LOSS.sum() / count / 2
    diff_loss = abs(loss - prev_loss)
    return loss, diff_loss


# z:predication value, y:sample data label, x:sample data, count:count of sample data
def dJwb_batch(X, Y, Z, count):
    p = Z - Y
    db = sum(p) / count
    q = p * X
    dw = sum(q) / count
    return dw, db


def dJwb_single(x, y, z):
    p = z - y
    db = p
    dw = p * x
    return dw, db


def update_weights(w, b, dw, db, eta):
    w = w - eta * dw
    b = b - eta * db
    return w, b


def show_result(X, Y, w, b, iteration, loss_his, w_his, b_his, n):
    # draw sample data
    plt.subplot(121)
    plt.plot(X, Y, "b.")
    # draw predication data
    Z = w * X + b
    plt.plot(X, Z, "r")
    plt.subplot(122)
    plt.plot(loss_his[0:n], "r")
    plt.plot(w_his[0:n], "b")
    plt.plot(b_his[0:n], "g")
    plt.grid(True)
    plt.show()
    print(iteration)
    print(w, b)


def print_progress(iteration, loss, diff_loss, w, b, loss_his, w_his, b_his):
    if iteration % 10 == 0:
        print(iteration, diff_loss, w, b)
    loss_his = np.append(loss_his, loss)
    w_his = np.append(w_his, w)
    b_his = np.append(b_his, b)
    return loss_his, w_his, b_his


if __name__ == '__main__':
    # count of samples
    m = 200
    # initialize_data
    eta = 0.01
    # set w,b=0, you can set to others values to have a try
    w, b = 0, 0
    eps = 1e-10
    iteration, max_iteration = 0, 10000
    # calculate loss to decide the stop condition
    prev_loss, loss, diff_loss = 0, 0, 0
    # create mock up data
    X, Y = create_sample_data(m)
    # create list history
    loss_his, w_his, b_his = list(), list(), list()

    # 随机梯度下降方式 - SGD
    while iteration < max_iteration:
        for i in range(m):
            # get x and y value for one sample
            x = X[i]
            y = Y[i]
            # get z from x,y
            z = forward_calculation(w, b, x)
            # calculate gradient of w and b
            dw, db = dJwb_single(x, y, z)
            # update w,b
            w, b = update_weights(w, b, dw, db, eta)
            # calculate loss for this batch
            loss, diff_loss = check_diff(w, b, X, Y, m, prev_loss)
            # condition 1 to stop
            if diff_loss < eps:
                break
            prev_loss = loss

        iteration += 1
        loss_his, w_his, b_his = print_progress(iteration, loss, diff_loss, w, b, loss_his, w_his,
                                                b_his)
        if diff_loss < eps:
            break

    show_result(X, Y, w, b, iteration, loss_his, w_his, b_his, 200)

    # # 批量梯度下降方式 - BGD
    # # condition 2 to stop
    # while iteration < max_iteration:
    #     # using current w,b to calculate Z
    #     Z = forward_calculation(w, b, X)
    #     # get gradient value
    #     dW, dB = dJwb_batch(X, Y, Z, m)
    #     # update w and b
    #     w, b = update_weights(w, b, dW, dB, eta)
    #     #   print(iteration,w,b)
    #     iteration += 1
    #     # condition 1 to stop
    #     loss, diff_loss = check_diff(w, b, X, Y, m, prev_loss)
    #     if diff_loss < eps:
    #         break
    #     prev_loss = loss
    #     iteration += 1
    #     loss_his, w_his, b_his = print_progress(iteration, loss, diff_loss, w, b, loss_his, w_his,
    #                                             b_his)
    #
    # show_result(X, Y, w, b, iteration, loss_his, w_his, b_his, 200)

    # # 小批量梯度下降方式 - MBGD
    # batchNumber = 20  # 设置每批的数据量为20
    # # condition 2 to stop
    # while iteration < max_iteration:
    #     # generate current batch
    #     batchX, batchY = generate_batch(X, Y, iteration, batchNumber, m)
    #     # using current w,b to calculate Z
    #     Z = forward_calculation(w, b, batchX)
    #     # get gradient value
    #     dW, dB = dJwb_batch(batchX, batchY, Z, batchNumber)
    #     # update w and b
    #     w, b = update_weights(w, b, dW, dB, eta)
    #     # calculate loss
    #     loss, diff_loss = check_diff(w, b, X, Y, m, prev_loss)
    #     # condition 1 to stop
    #     if diff_loss < eps:
    #         break
    #     prev_loss = loss
    #     iteration += 1
    #
    #     loss_his, w_his, b_his = print_progress(iteration, loss, diff_loss, w, b, loss_his, w_his,
    #                                             b_his)
    #
    # show_result(X, Y, w, b, iteration, loss_his, w_his, b_his, 300)
