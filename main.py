from ultralytics import YOLO
import cv2, csv


# load yolov8 model
model = YOLO('yolov8n.pt')

print("Classes:", model.names)        # dict like {0:'person', 1:'bicycle', ...}
# If you want an id by name:
name_to_id = {v:k for k,v in model.names.items()}
print("sports ball id =", name_to_id.get("sports ball"))

# 2) (Optional) track only a specific class, e.g., "bottle"
name_to_id = {v: k for k, v in model.names.items()}
TARGET = name_to_id.get("sports ball")  # or set to None to track all
print("Classes:", model.names)
print("Target Class:", TARGET)

# load video
video_path = './assets/ball-in.mp4'
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

tracker_cfg = "bytetrack.yaml"

CONF = 0.15     # lower for better recall under blur
IOU  = 0.5
IMGZ = 960       # larger input helps with motion blur (736–960 good)

data = []                              # rows to save
frame_idx = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame_idx += 1
    t_sec = frame_idx / fps

    # 5) Run tracking (ByteTrack) on this frame
    results = model.track(
        frame,
        persist=True,              # keep track IDs across frames
        tracker=tracker_cfg,       # <-- ByteTrack
        conf=CONF,
        iou=IOU,
        imgsz=IMGZ,
        classes=[TARGET] if TARGET is not None else None,
        verbose=False
    )

    r = results[0]

    # collect rows: one row per detection/track this frame
    if r.boxes is not None and len(r.boxes):
        boxes = r.boxes
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i])
            if TARGET is not None and cls_id != TARGET:
                continue
            track_id = int(boxes.id[i]) if boxes.id is not None else -1
            conf = float(boxes.conf[i])
            x1, y1, x2, y2 = map(float, boxes.xyxy[i].tolist())
            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

            data.append([
                frame_idx, t_sec, track_id, cls_id, model.names[cls_id],
                conf, x1, y1, x2, y2, cx, cy
            ])
        
    # 6) Visualize
    frame_vis = results[0].plot()
    cv2.imshow("ByteTrack + YOLOv8", frame_vis)
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

with open('data.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow([
        'frame','time_s','track_id','class_id','class_name','conf',
        'x1','y1','x2','y2','cx','cy'
    ])
    w.writerows(data)

print(f"Saved {len(data)} rows to data.csv")