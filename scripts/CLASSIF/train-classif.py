from ultralytics import YOLO
import os

ROOT = "/home/STual/DAN-cadastre"

# Paths
model_path = ROOT + "/scripts/CLASSIF/models/yolo11m-cls.pt"
save_dir = ROOT + "/scripts/CLASSIF/"

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Parameters
args = {
    "data":ROOT+'/data/CLASSIF/yolo_gt/data.yaml',
    "epochs":200, #SOCFACE : 200
    "imgsz":800, #SOCFACE : 1024
    "batch":6, #SOCFACE : 4
    "device":[0],
    'pretrained': True,
    "verbose":True,
    "seed":42,
    "val":True,
    "project":save_dir,
    "name":"train",
}

# Run
if __name__ == "__main__":

    model = YOLO(model_path)

    results = model.train(**args)

    results.save()