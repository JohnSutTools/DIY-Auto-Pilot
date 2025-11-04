#!/usr/bin/env python3
import cv2

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
print('Testing camera formats...')

formats = ['MJPG', 'YUYV', 'H264', 'RGB3']
for fmt in formats:
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fmt))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    ret, frame = cap.read()
    result = "OK" if ret else "FAIL"
    print(f'{fmt}: {result}')

cap.release()
print('\nTesting with CAP_ANY (default)...')
cap2 = cv2.VideoCapture(0)
cap2.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
ret2, frame2 = cap2.read()
print(f'CAP_ANY + MJPG: {"OK" if ret2 else "FAIL"}')
cap2.release()
