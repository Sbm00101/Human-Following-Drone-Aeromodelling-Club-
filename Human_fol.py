#!/usr/bin/env python3
import cv2
from mavsdk  import System
from mavsdk.offboard import OffboardError,PositionNedYaw,VelocityBodyYawspeed
import numpy as np
import asyncio
from ultralytics import YOLO
from PIL import Image
import cv2
import pandas as pd

drone = System()
model=YOLO('yolov8s.pt')
cap=cv2.VideoCapture(0)
my=320
mx=240

my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")



    
async def start():
    await drone.connect(system_address="udp://:14540")

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    
    await drone.action.arm()
    print("armed")
    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    print("takeoff")
    await drone.action.takeoff()
    await asyncio.sleep(5)
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0,0.0,0.0,0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return
    print("Human height")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.0, 0.0))
    await asyncio.sleep(5)
    
    
   
async def follow():
 m=0
 while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    #frame=cv2.rotate(frame,cv2.ROTATE_180)

    if success:
      try:
        # Run YOLOv8 inference on the frame
        results = model(frame, conf=0.5)
        a = results[0].boxes.boxes
        px = pd.DataFrame(a).astype("float")
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
            ar  = w1*h1
            area.append(ar)
            box.append([x1,y1,w1,h1])
         if len(area) != 0:
            m=1

            j = area.index(max(area))
            x,y,w,h = box[j][0],box[j][1],box[j][2],box[j][3]
            cx = x + w/2
            cy = y + h/2
            ary=area[j]
            tol=[mx-cx,my-cy]
            cv2.rectangle(frame, (x, y), (x+w,y+h), (255, 0 , 255), 2)
         else:
             m=0
         cv2.circle(frame,(320,240),2,(0,0,255),4) 
         cv2.imshow("capture", frame) 
      except:
          print("connect error") 
       
    if m==1:   
     if tol[0]>10 :
        try:
         await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0,0.0,0.0,-50))
         await asyncio.sleep(0.1)
         print("-30")
        except RuntimeError:
         print("Caught a RuntimeError exception. Retrying...-30")
         
        
        
     elif tol[0]<-10:
        try:
         await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0.0,0.0,0.0,50))
         await asyncio.sleep(0.1)
         print("-30")
        except RuntimeError:
         print("Caught a RuntimeError exception. Retrying...30")
         
      
        
      
    
     print(ary)    
     if ary<20000:
        try:
         await drone.offboard.set_velocity_body(VelocityBodyYawspeed(1.0,0.0,0.0,0))
         await asyncio.sleep(0.05)
         print("front 1")
        except RuntimeError:
         print("Caught a RuntimeError exception. Retrying...front 1")
        
     elif ary >200000:
        try:
         await drone.offboard.set_velocity_body(VelocityBodyYawspeed(-1.0,0.0,0.0,0))
         await asyncio.sleep(0.05)
         print("back 1")
        except RuntimeError:
         print("Caught a RuntimeError exception. Retrying...back 1")
         
     
     await asyncio.sleep(0.1)    
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        
async def stop():
   try:
             await drone.offboard.stop()
  
   except OffboardError as error:
             print("unable to stop offboard")
             print(f'{error._result.result}')
   try:

      await drone.action.land()
      print("landing...")
      await drone.action.disarm()

   except RuntimeError:
      print("Caught a RuntimeError exception. Retrying...land")
      
async def ma():
    
    await follow()


      
if __name__ == "__main__":
    asyncio.run(start())
    asyncio.run(ma())
   
    asyncio.run(stop())
    
    cap.release()
    cv2.destroyAllWindows()

