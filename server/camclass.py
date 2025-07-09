import time
class Camera:
    def __init__(self, ip):
        self.ip = ip
        self.rawFrame = None
        self.annotatedFrame = None
        self.lastSeen = time.time()
        self.framesSeen = 0

    def updateRaw(self, frame):
        self.rawFrame = frame
        self.lastSeen = time.time()
        self.framesSeen+=1

    def updateAnnotated(self, frame):
        self.annotatedFrame = frame
        

    def isAlive(self, timeout=10):
        return time.time-self.lastSeen <= timeout



