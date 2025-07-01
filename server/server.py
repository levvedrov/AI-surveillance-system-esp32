from flask import Flask, request
import cv2 as cv
import numpy as np
import threading
import time
        

print(f"[DEBUG] Current thread: {threading.current_thread().name}")

app = Flask(__name__)


frames = {}
lock = threading.Lock()

def displayLoop():
    while True:
        now = time.time()
        with lock:
            deadCams = []
            for camip, (frame, lastSeen) in frames.items():
                if now-lastSeen > 10:
                    deadCams.append(camip)
                else:
                    cv.imshow(camip, frame)

        # dead del
            for camip in deadCams:
                print(f"[INFO] {camip} is offline. Removing...")
                del frames[camip]
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
            frames[camip] = (frame, time.time())
        



    return "OK", len(catch)



if __name__ == '__main__':
    threading.Thread(target=displayLoop, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)