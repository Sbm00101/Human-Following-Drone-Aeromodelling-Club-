#!/usr/bin/env python3
import cv2
import numpy as np
import asyncio

from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

async def arm():
    drone = System()
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
    print("takeoff")
    await drone.action.takeoff()

    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    print("bringing above to human level")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -1.0, 0.0))
    await asyncio.sleep(10)

async def run( area,x):
    """ Does Offboard control using position NED coordinates. """
    while(1):
     while(area > 40000 ):
        print("moving backward")
        await drone.offboard.set_position_ned(PositionNedYaw(0.0, -x-1.0, -1.0, 0.0))
        await asyncio.sleep(10)

     while( area < 20000):
        print("moving forward")
        await drone.offboard.set_position_ned(PositionNedYaw(0.0, -x+1.0, -1.0, 0.0))
        await asyncio.sleep(10)
      

  
     if(cv2.waitKey(1) & 0xFF == ord('q')):
      print("-- Stopping offboard")
      try:
        await drone.offboard.stop()
      except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")


if name == "main":
 cv2.namedWindow('win',cv2.WINDOW_NORMAL)
 cv2.resizeWindow('win', 1920, 1080)
 face_cascade= cv2.CascadeClassifier('facedetection.xml')
 cap = cv2.VideoCapture(0)
 asyncio.run(arm())

 while (cap.isOpened()):
    ret, frame=cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    # Only consider the first face detected
    if len(faces) > 0:
        (x, y, w, h) = faces[0]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 10)
        area = w*h
        print("area of face=" + str(area))
        

        cv2.imshow('win', frame)

    # Run the asyncio loop
    asyncio.run(run( area,x ))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
 cv2.destroyAllWindows()