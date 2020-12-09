import matplotlib.animation as animation
import os
import sys
from cv2 import cv2 as cv
import matplotlib.image as mpimg
from tempfile import TemporaryFile

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
from main_ui import Ui_DockWidget
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget, QLineEdit, QLabel

# Todo:
# find_intrinsic()
# find_extrinsic()
# find_find_distortion()
# find_stereo_disparity()


class window(QDockWidget, Ui_DockWidget):
    def __init__(self, parent=None):
        super(window, self).__init__(parent)
        self.setupUi(self)
        self.on_binding_ui()

    def on_binding_ui(self):
        self.pushButton.clicked.connect(self.DrawContour1)
        self.pushButton_2.clicked.connect(self.DrawContour2)
        self.pushButton_2_1.clicked.connect(self.findcorners)
        self.pushButton_2_2.clicked.connect(self.find_intrinsic)
        self.pushButton_2_3.clicked.connect(self.find_extrinsic)
        self.pushButton_2_4.clicked.connect(self.find_distortion)
        self.pushButton_3.clicked.connect(self.augmentation3d)
        self.pushButton_4.clicked.connect(self.stereo_disparity)

    def DrawContour1(self):
        plt.close('all')

        im = cv.imread('Datasets/Q1_Image/coin01.jpg')
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        gray_blur = cv.GaussianBlur(imgray, (15, 15), 0)
        ret, thresh = cv.threshold(gray_blur, 127, 255, 0)
        im2, contours1, hierarchy = cv.findContours(thresh, cv.RETR_TREE,
            cv.CHAIN_APPROX_SIMPLE)

        contours1.pop(0)
        cv.drawContours(im, contours1, -1, (0, 255, 0), 2)

        coin_count1 = len(contours1)
        text = 'There are ' + str(coin_count1) + ' coins in coin01.jpg'
        label = self.label_2
        label.setText(text)

        cv2plt = im[:,:,::-1]
        plt.imshow(cv2plt)
        plt.show()

    def DrawContour2(self):
        plt.close('all')

        im = cv.imread('Datasets/Q1_Image/coin02.jpg')
        imgray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)
        gray_blur = cv.GaussianBlur(imgray, (15, 15), 0)
        ret, thresh = cv.threshold(gray_blur, 127, 255, 0)
        im2, contours2, hierarchy = cv.findContours(thresh, cv.RETR_TREE,
            cv.CHAIN_APPROX_SIMPLE)

        contours2.pop(0)
        cv.drawContours(im, contours2, -1, (0, 255, 0), 2)

        coin_count2 = len(contours2)
        text = 'There are ' + str(coin_count2) + ' coins in coin01.jpg'
        label = self.label_3
        label.setText(text)

        cv2plt = im[:,:,::-1]
        plt.imshow(cv2plt)
        plt.show()

    def findcorners(self):
        plt.close('all')

        # termination criteria
        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((11*8, 3), np.float32)
        objp[:, :2] = np.mgrid[0:11, 0:8].T.reshape(-1, 2)
        # Arrays to store object points and image points from all the images.
        objpoints = []  # 3d point in real world space
        imgpoints = []  # 2d points in image plane.

        for i in range(1, 16):
            img_name = str(i) + '.bmp'
            fname = os.path.join('Datasets/Q2_Image', img_name)

            img = cv.imread(fname)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv.findChessboardCorners(gray, (11, 8), None)
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)
                corners2 = cv.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
                imgpoints.append(corners)
                # Draw and display the corners
                cv.drawChessboardCorners(img, (11, 8), corners2, ret)

                ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
                    objpoints, imgpoints, gray.shape[::-1], None, None)

                plt_img = img[:, :, ::-1]
                plt.figure(fname)
                plt.imshow(plt_img)
                np.savez('output.npz', mtx, dist, rvecs, tvecs)

        plt.show()

    def find_intrinsic(self):
        pass

    def find_extrinsic(self):
        num = self.spinBox.value()
        print(num)
        pass

    def find_distortion(self):
        pass

    def draw(self, img, corners, imgpts):
        imgpts = np.int32(imgpts).reshape(-1, 2)
        # draw pillars in blue color
        for i, j in zip(range(3), [1,2,0]):
            img = cv.line(img, tuple(imgpts[i]), tuple(
                imgpts[3]), (0, 0, 255), 20)
            img = cv.line(img, tuple(imgpts[i]), tuple(
                imgpts[j]), (0, 0, 255), 20)

        return img

    def augmentation3d(self):

        with np.load('output.npz') as X:
            mtx, dist, _, _ = [X[i] for i in ('arr_0', 'arr_1', 'arr_2', 'arr_3')]


        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        objp = np.zeros((11*8, 3), np.float32)
        objp[:, :2] = np.mgrid[0:11, 0:8].T.reshape(-1, 2)

        axis = np.float32([[1, 1, 0], [5, 1, 0],
                           [3, 5, 0], [3, 3, -3]])


        filepath = list()
        for i in range(5):
            path = os.path.join('Datasets/Q3_Image', str(i+1) + '.bmp')
            filepath.append(path)

        ims = list()
        fig = plt.figure('augumentation3d')

        for fname in filepath:
            img = cv.imread(fname)
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            ret, corners = cv.findChessboardCorners(gray, (11, 8), None)

            if ret == True:
                corners2 = cv.cornerSubPix(
                    gray, corners, (11, 11), (-1, -1), criteria)

                # Find the rotation and translation vectors.
                _, rvecs, tvecs, _= cv.solvePnPRansac(objp, corners2, mtx, dist)

                # project 3D points to image plane
                imgpts, _ = cv.projectPoints(axis, rvecs, tvecs, mtx, dist)
                
                img = self.draw(img, corners2, imgpts)

                plt_img = img[:, :, ::-1]
                im = plt.imshow(plt_img, animated=True)

                ims.append([im])
        print(len(ims))

        _ = animation.ArtistAnimation(fig, ims, interval=500,
                                        blit=True, repeat_delay=500)
        plt.show()

    def stereo_disparity(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = window()
    ui.show()

    sys.exit(app.exec_())
