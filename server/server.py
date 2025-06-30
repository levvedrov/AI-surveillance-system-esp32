from flask import Flask, request
import cv2 as cv
import numpy as np
import threading

print(f"[DEBUG] Current thread: {threading.current_thread().name}")

app = Flask(__name__)

@app.route("/snap", methods = ['POST'])
def receiveFrames():
    catch = request.data
    camip = request.remote_addr
    print(f"Received {len(catch)} bytes")
    print(f"From {camip}")
    with open("./catch.jpg", "wb") as file:
        file.write(catch)
    nparr = np.frombuffer(catch, np.uint8)
    frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if frame is None:
        print("cv: Error in decoding the frame")
        return "Invalid image", 400
    else:
        print("Successfully decoded")
        cv.imshow(f"{camip}", frame)
        cv.waitKey(1000)
        



    return "OK", len(catch)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)