import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO



model=YOLO('yolov8s.pt')


def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        colorsBGR = [x, y]
        print(colorsBGR)
        

cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap=cv2.VideoCapture(0)

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")
print(class_list)
count=0
while True:
    
    ret,frame = cap.read()
    if not ret:
        break
    count += 1
    if count % 3 != 0:
        continue
    frame=cv2.resize(frame,(1020,500))

    results=model.predict(frame)
    a = results[0].boxes.boxes
    px = pd.DataFrame(a).astype("float")
    #closest=[row_1[0],row_1[1],row_1[2],row_1[3]]
    area = []
    box = []
    for index,row in px.iterrows():
        
        if int(row[5]) == 0:
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])
            w1 = (x2-x1)
            h1 = (y2-y1)
            a  = w1*h1
            area.append(a)
            box.append([x1,y1,w1,h1])
        if len(area) != 0:

            j = area.index(max(area))
            x,y,w,h = box[j][0],box[j][1],box[j][2],box[j][3]
            cx = x + w/2
            cy = y + h/2
        cv2.rectangle(frame, (x, y), (x+w,y+h), (255, 0 , 255), 2)
        print(cx,cy,area[j])
                    
            # cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,255),3)
           
    cv2.imshow("capture", frame)
    if cv2.waitKey(1)&0xFF==27:
        break

cap.release()
cv2.destroyAllWindows()
