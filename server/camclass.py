import time
class Camera:
    def __init__(self, ip):
        self.ip = ip
        self.frame = None
        self.lastSeen = time.time()
        self.framesSeen = 0

    def update(self, frame):
        self.frame = frame
        self.lastSeen = time.time()
        self.framesSeen+=1

    def isAlive(self, timeout=10):
        return time.time-self.lastSeen <= timeout



