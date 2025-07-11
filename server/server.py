from flask import Flask, request, Response
import cv2 as cv
import numpy as np
import threading
import time
import collections, time, threading
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



LAT_WIN  = 50 
FPS_WIN  = 50         
ALT_WIN  = 30 
_stats   = {}


def get_stats(ip):
    d = _stats.setdefault(ip, {})
    if "lat" not in d:
        d["lat"] = collections.deque(maxlen=LAT_WIN)
    if "ts"  not in d:
        d["ts"]  = collections.deque(maxlen=FPS_WIN)
    if "alt" not in d:
        d["alt"] = collections.deque(maxlen=ALT_WIN)     # ← добавляем, если нет
    return d

def send_alert_with_latency(message, caption, raw, annotated, camip, t_capture):
    t0 = time.time()
    send_alert(message, caption, raw, annotated)   # ← ваш исходный синхронный вызов
    alt_ms = (time.time() - t_capture) * 1000

    with lock:
        get_stats(camip)["alt"].append(alt_ms)


def draw_stat(img, label, value, y, color):
    text = f"{label:<4}{value:>6}"
    (w, h), _ = cv.getTextSize(text, cv.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv.rectangle(img, (5, y - h - 6), (5 + w + 8, y + 4),
                 (0, 0, 0), -1)                       # подложка
    cv.putText(img, text, (10, y),
               cv.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv.LINE_AA)



@app.route("/snap", methods = ['POST'])
def receiveFrames():
    t_capture = time.time()                                   # фиксация прихода
    payload = request.data
    camip   = request.remote_addr
    rawFrame = cv.imdecode(np.frombuffer(payload, np.uint8), cv.IMREAD_COLOR)
    if rawFrame is None:
        return "Invalid image", 400

    # --- inf -------------------------------------------------------------
    status, annotatedFrame = detect.guns(rawFrame.copy())
    people_cnt, annotatedFrame = detect.people(annotatedFrame)

    with lock:
        cam = get_cam_by_ip(camip) or cm.Camera(camip)
        if cam not in cams: cams.append(cam)
        cam.updateRaw(rawFrame); cam.updateAnnotated(annotatedFrame)

    # --- latency / fps ---------------------------------------------------
    with lock:
        st = get_stats(camip)
        now = time.time()
        st["lat"].append((now - t_capture) * 1000)
        st["ts"].append(now)
        med_lat = np.median(st["lat"])
        fps     = 1/np.mean(np.diff(st["ts"])) if len(st["ts"])>1 else 0
        med_alt = np.median(st["alt"]) if st["alt"] else 0

    cv.putText(annotatedFrame, f"LAT {med_lat:.0f}ms", (10,25),
               cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    cv.putText(annotatedFrame, f"FPS {fps:.1f}",   (10,50),
               cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    if med_alt:
        cv.putText(annotatedFrame, f"ALRT {med_alt:.0f}ms", (10,75),
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

    # --- alert -----------------------------------------------------------
    if status["pistol"] > 0 and (now - cam.lastNotified > 10):
        threading.Thread(
            target=send_alert_with_latency,
            args=("⚠️GUN DETECTED!⚠️",
                  f"<b>Pistol</b> detected at {datetime.now():%Y-%m-%d %H:%M:%S} on {camip}",
                  rawFrame, annotatedFrame, camip, t_capture),
            daemon=True
        ).start()
        cam.lastNotified = now

    return "OK", len(payload)








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