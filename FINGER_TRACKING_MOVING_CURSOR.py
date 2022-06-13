import math
import cv2
import numpy as np
import Palm_Tracking_Module as ptm
import time
import autopy
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import vlc
import pyautogui

##########################
wCam, hCam = 1080, 1020                 #width and height of the live feed
frameR = 220  # Frame Reduction         #adjust the value to increase mouse speed, by calculating the value in the below equation in line 77,78
smoothening = 6
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = ptm.handDetector(maxHands=1)
wScr, hScr = autopy.screen.size()
# print(wScr, hScr)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volume_Range = volume.GetVolumeRange()
min_volume = volume_Range[0]
max_volume = volume_Range[1]


while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img)
    # bbox = detector.findPosition(img)
    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        fingers = detector.fingersUp()
        # print("Fingers : " + str(fingers))
        if fingers[1] == 1:
            index_x1, index_y1 = lmList[8][1], lmList[8][2]
            print("---------------------------------------------------------------------------------------------------")
            print("Index Finger", "X : " + str({}).format(index_x1), "Y : " + str({}).format(index_y1,))
            print("---------------------------------------------------------------------------------------------------")
        if fingers[2] == 1:
            middle_x1, middle_y1 = lmList[12][1], lmList[12][2]
            print("Middle Finger", "X : {}".format(middle_x1), "Y : {}".format(middle_y1))
            print("---------------------------------------------------------------------------------------------------")
        if fingers[3] == 1:
            ring_x1, ring_y1 = lmList[16][1], lmList[16][2]
            print("Ring Finger", "X : ", ring_x1, "Y :", ring_y1)
            print("---------------------------------------------------------------------------------------------------")
        if fingers[4] == 1:
            little_x1, little_y1 = lmList[20][1], lmList[20][2]
            print("Little Finger", "X : ", little_x1, "Y :", little_y1)
            print("---------------------------------------------------------------------------------------------------")
        if fingers[0] == 0:
            thumb_x1, thumb_y1 = lmList[4][1], lmList[4][2]
            print("Thumb", "X : ", thumb_x1, "Y :", thumb_y1)
            print("---------------------------------------------------------------------------------------------------")
            # print("Middle Finger")
            # print("X : ", x2, "Y :", y2)
            # 3. Check which fingers are up
            # fingers = detector.fingersUp()
            # print(fingers)
            # cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0:                             #checking if which fingers are up
            x1, y1 = lmList[8][1:]
            x2, y2 = lmList[12][1:]
            # 5. Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
            # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening

            # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 5, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY

        # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[1] == 1 and fingers[2] == 1:
            # 9. Find distance between fingers
            length, img, lineInfo = detector.findDistance(8, 12, img)
            print("Distance Difference : ", length)
            print("---------------------------------------------------------------------------------------------------")
            # 10. Click mouse if distance short
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                #autopy.mouse.click()
                pyautogui.click()

            if length > 50:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (255, 0, 0), cv2.FILLED)
                scroll1 = int(y3)
                # scroll = int(clocY)
                # print(scroll)
                print("Distance Between index and Middle above 50 : " + str(scroll1))
                pyautogui.scroll(scroll1)

        if fingers[0] == 0 and fingers[1] == 1:
            thumb_x1, thumb_y1 = lmList[4][1], lmList[4][2]
            index_x1, index_y1 = lmList[8][1], lmList[8][2]
            midpoint_of_line_x, midpoint_of_line_y = (thumb_x1+index_x1) // 2, (thumb_y1 + index_y1) // 2
            print("Index Finger : " + str(index_x1), str(index_y1))
            print("Thumb : "+ str(thumb_x1), str(thumb_y1))
            cv2.circle(img, (thumb_x1, thumb_y1), 5, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (index_x1, index_y1), 5, (255, 0, 0), cv2.FILLED)
            cv2.line(img, (index_x1, index_y1), (thumb_x1, thumb_y1), (255, 0, 0), 5)
            cv2.circle(img, (midpoint_of_line_x, midpoint_of_line_y), 5, (255, 0, 0), cv2.FILLED)

            length_thumb_and_index = math.hypot(index_x1 - thumb_x1, index_y1 - thumb_y1)
            # print(length_thumb_and_index)

            if length_thumb_and_index < 50:
                cv2.circle(img, (midpoint_of_line_x, midpoint_of_line_y), 10, (255, 0, 255), cv2.FILLED)
            if length_thumb_and_index > 120:
                cv2.circle(img, (midpoint_of_line_x, midpoint_of_line_y), 10, (255, 255, 0), cv2.FILLED)

            vol = np.interp(length_thumb_and_index, [40, 220], [min_volume, max_volume])
            # vol_percentage = np.interp(length_thumb_and_index, [30, 180], [0, 100])
            # print(vol)
            # volume.SetMasterVolumeLevel(vol, None)


    # 11. Frame Rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, "FPS : " + str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)

    if len(lmList) != 0:
        fingers = detector.fingersUp()
        if fingers[1] == 1:
            index_x1, index_y1 = lmList[8][1], lmList[8][2]
            cv2.putText(img, "Index FInger - " + "X : " + str(index_x1) + "Y : " + str(index_y1), (20, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
        if fingers[2] == 1:
            middle_x1, middle_y1 = lmList[12][1], lmList[12][2]
            cv2.putText(img, "Middle Finger - " + "X : " + str(middle_x1) + "Y : " + str(middle_y1), (20, 120), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)
        if fingers[3] == 1:
            ring_x1, ring_y1 = lmList[16][1], lmList[16][2]
            cv2.putText(img, "Ring Finger - " + "X : " + str(ring_x1) + "Y : " + str(ring_y1), (20, 160), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
        if fingers[4] == 1:
            little_x1, little_y1 = lmList[20][1], lmList[20][2]
            cv2.putText(img, "Little Finger - " + "X : " + str(little_x1) + "Y : " + str(little_y1), (20, 200), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)
        if fingers[0] == 0:
            thumb_x1, thumb_y1 = lmList[4][1], lmList[4][2]
            cv2.putText(img, "Thumb - " + "X : " + str(thumb_x1) + "Y : " + str(thumb_y1), (20, 240), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)
        if fingers[0 == 0] and fingers[1] == 1:
            index_x1, index_y1 = lmList[8][1], lmList[8][2]
            thumb_x1, thumb_y1 = lmList[4][1], lmList[4][2]
            length_thumb_and_index = math.hypot(index_x1 - thumb_x1, index_y1 - thumb_y1)
            vol_percentage = np.interp(length_thumb_and_index, [80, 220], [0, 100])
            volume_percentage = int(vol_percentage)
            cv2.putText(img, "Volume :" + str(volume_percentage) + "%", (20, 280), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 3)


    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)