import cv2
from cvzone.HandTrackingModule import HandDetector
import math


CAM_WIDTH, CAM_HEIGHT = 640, 480
PINCH_THRESHOLD_PX = 40
SMOOTHING = 0.3

RECT_SIZE = (120, 80)
RECT_COLOR = (255, 255, 255)
FILL_ALPHA = 0.25

LABELS = ["Box1", "Box2", "Box3"]
INITIAL_CENTERS = [
    (int(CAM_WIDTH * 0.25), int(CAM_HEIGHT * 0.4)),
    (int(CAM_WIDTH * 0.50), int(CAM_HEIGHT * 0.6)),
    (int(CAM_WIDTH * 0.75), int(CAM_HEIGHT * 0.4)),
]

class DragRect:
    def __init__(self, center, size, label=""):
        self.cx, self.cy = center
        self.w, self.h = size
        self.label = label

    def contains(self, x, y):
        return (self.cx - self.w // 2 <= x <= self.cx + self.w // 2) and (self.cy - self.h // 2 <= y <= self.cy + self.h // 2)

    def move_towards(self, x, y, smoothing=0.0):
        self.cx = int(self.cx + (x - self.cx) * smoothing)
        self.cy = int(self.cy + (y - self.cy) * smoothing)

    def draw(self, img):
        x1, y1 = self.cx - self.w // 2, self.cy - self.h // 2
        x2, y2 = x1 + self.w, y1 + self.h
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), RECT_COLOR, -1)
        cv2.addWeighted(overlay, FILL_ALPHA, img, 1 - FILL_ALPHA, 0, img)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), 2)
        label_text = self.label if self.label else "Drag me"
        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        pad = 8
        bar_y2 = y1 + th + 2 * pad
        cv2.rectangle(img, (x1, y1), (x1 + tw + 2 * pad, bar_y2), (0, 0, 0), -1)
        cv2.putText(img, label_text, (x1 + pad, y1 + th + pad - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    rects = [DragRect(c, RECT_SIZE, LABELS[i]) for i, c in enumerate(INITIAL_CENTERS)]
    grabbed_index = None

    while True:
        success, img = cap.read()
        if not success:
            break
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)
        cursor_x, cursor_y, is_pinching = None, None, False

        if hands:
            lmList = hands[0]['lmList']
            ix, iy = lmList[8][0:2]
            tx, ty = lmList[4][0:2]
            cursor_x, cursor_y = ix, iy
            if math.hypot(ix - tx, iy - ty) < PINCH_THRESHOLD_PX:
                is_pinching = True
            cv2.circle(img, (ix, iy), 10, (0, 0, 0), cv2.FILLED)
            cv2.circle(img, (ix, iy), 16, (255, 255, 255), 2)

        if is_pinching and cursor_x is not None:
            if grabbed_index is None:
                for i in range(len(rects) - 1, -1, -1):
                    if rects[i].contains(cursor_x, cursor_y):
                        grabbed_index = i
                        break
            if grabbed_index is not None:
                rects[grabbed_index].move_towards(cursor_x, cursor_y, smoothing=SMOOTHING)
        else:
            grabbed_index = None

        for r in rects:
            r.draw(img)

        cv2.putText(img, "Pinch to grab & drag | Press 'q' to quit", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(img, "Pinch to grab & drag | Press 'q' to quit", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        cv2.imshow("Virtual Drag & Drop - CVZone", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
