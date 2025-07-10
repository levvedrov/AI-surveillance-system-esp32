from flask import Flask, request, Response
import cv2 as cv
import numpy as np
import threading
import time
import camclass as cm
import detect
from notification import notification
import asyncio
from datetime import datetime
import threading
        

print(f"[DEBUG] Current thread: {threading.current_thread().name}")

app = Flask(__name__)

cams = []

lock = threading.Lock()

def get_cam_by_ip(ip):
    for cam in cams:
        if cam.ip == ip:
            return cam
    return None

def send_alert(header, text, raw, annotated):
    asyncio.run(notification.send_telegram_notifification(header, text, raw, annotated))

def displayLoop():
    while True:
        now = time.time()
        with lock:
            deadCams = []
            for cam in cams:
                if now-cam.lastSeen >= 10:
                    deadCams.append(cam.ip)
                else:
                    if cam.rawFrame is not None:
                        cv.imshow(cam.ip+"-annotated ", cam.annotatedFrame)
                        pass

        # dead del
            for camip in deadCams:
                print(f"[INFO] {camip} is offline. Removing...")
                cams.remove(get_cam_by_ip(camip))
                cv.destroyWindow(camip)

        if cv.waitKey(1) == 27:
            break
        time.sleep(0.01)
    cv.destroyAllWindows()




@app.route("/snap", methods = ['POST'])
def receiveFrames():
    catch = request.data
    camip = request.remote_addr
    print(f"Received {len(catch)} bytes")
    print(f"From {camip}")
    nparr = np.frombuffer(catch, np.uint8)
    rawFrame = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if rawFrame is None:
        print("cv: Error in decoding the frame")
        return "Invalid image", 400
    else:
        print("Successfully decoded")
        raw = rawFrame.copy()
        status, annotatedFrame = detect.guns(rawFrame)
        

        amountOfPeople, annotatedFrame = detect.people(annotatedFrame)
        
        
        with lock:
            cam = get_cam_by_ip(camip)
            if cam == None:
                cam = cm.Camera(camip)
                cams.append(cam)
            cam.updateRaw(rawFrame)
            cam.updateAnnotated(annotatedFrame)

        if status["pistol"]>0 and (time.time()-cam.lastNotified>10):
             
            threading.Thread(
                target=send_alert,
                args=("⚠️GUN DETECTED!⚠️", f"\nA <b>pistol</b> was detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} on {camip}", raw, annotatedFrame),
                daemon=True
            ).start()

            cam.lastNotified = time.time()
    return "OK", len(catch)








@app.route("/getaliveips", methods = ['GET'])
def sendAliveIps():
    with lock:
        return {"cams": [cam.ip for cam in cams]}   


@app.route("/get", methods=['GET'])
def frameToClient():
    camip = request.args.get('ip')
    print(f"[GET] Requested IP = {camip}")

    if not camip:
        print("[GET] No IP provided")
        return "Missing IP", 400

    with lock:
        cam = get_cam_by_ip(camip)
        if not cam:
            print("[GET] Camera not found")
            return "No such camera", 404
        if cam.annotatedFrame is None:
            print("[GET] No frame available yet")
            return "No frame", 404

        success, jpeg = cv.imencode(".jpg", cam.annotatedFrame)
        if not success:
            print("[GET] JPEG encoding failed")
            return "Encoding error", 500

        print("[GET] Sending encoded frame")
        return Response(jpeg.tobytes(), mimetype='image/jpeg')





if __name__ == '__main__':
    
    threading.Thread(target=displayLoop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)