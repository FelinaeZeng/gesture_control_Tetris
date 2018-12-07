import cv2
import numpy as np
import os
import time

import threading
cap = cv2.VideoCapture(0)
i = 0
while True:
    ret, frame = cap.read()
    #cv2.imshow("11",frame)
    max_area = 0
    x0 = 400
    y0 = 200
    height = 200
    width = 200
    skinkernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame,(640,480))

    low_range = np.array([0, 50, 80])
    upper_range = np.array([30, 200, 255])

    cv2.rectangle(frame, (x0, y0), (x0 + width, y0 + height), (0, 255, 0), 1)
    # roi = cv2.UMat(frame[y0:y0+height, x0:x0+width])
    roi = frame[y0:y0 + height, x0:x0 + width]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Apply skin color range
    mask = cv2.inRange(hsv, low_range, upper_range)

    mask = cv2.erode(mask, skinkernel, iterations=1)
    mask = cv2.dilate(mask, skinkernel, iterations=1)

    # blur
    mask = cv2.GaussianBlur(mask, (15, 15), 1)

    # bitwise and mask original frame
    res = cv2.bitwise_and(roi, roi, mask=mask)
    # color to grayscale
    # res = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    cv2.imshow("result", res)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite("G:\\"+str(i)+".png", res)  # 保存路径
        i = i +1
        print(i)
    #k = cv2.waitKey(1)

