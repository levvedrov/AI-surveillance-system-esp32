from flask import Flask, request
import cv2 as cv
import numpy as np
import threading
import time
import camclass as cm
        

print(f"[DEBUG] Current thread: {threading.current_thread().name}")

app = Flask(__name__)


# frames = {}
cams = []

lock = threading.Lock()

def get_cam_by_ip(ip):
    for cam in cams:
        if cam.ip == ip:
            return cam
    return None


def displayLoop():
    while True:
        now = time.time()
        with lock:
            deadCams = []
            for cam in cams:
                if now-cam.lastSeen >= 10:
                    deadCams.append(cam.ip)
                else:
                    if cam.frame is not None:
                        cv.imshow(cam.ip, cam.frame)

        # dead del
            for camip in deadCams:
                print(f"[INFO] {camip} is offline. Removing...")
                cams.remove(get_cam_by_ip(camip))
                cv.destroyWindow(camip)
        #

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
    frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if frame is None:
        print("cv: Error in decoding the frame")
        return "Invalid image", 400
    else:
        print("Successfully decoded")
        with lock:
            cam = get_cam_by_ip(camip)
            if cam == None:
                cam = cm.Camera(camip)
                cams.append(cam)
            cam.update(frame)
    return "OK", len(catch)



if __name__ == '__main__':
    threading.Thread(target=displayLoop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)