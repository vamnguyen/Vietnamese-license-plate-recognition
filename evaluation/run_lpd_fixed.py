import numpy as np
# Monkeypatch np.int to int to fix deprecation error in yolov5
if not hasattr(np, 'int'):
    np.int = int

import sys
import os
import pathlib
import warnings

warnings.filterwarnings("ignore")

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
yolov5_dir = os.path.join(root_dir, 'yolov5')

# Add yolov5 to sys.path so we can import val
if yolov5_dir not in sys.path:
    sys.path.insert(0, yolov5_dir)
sys.path.append(root_dir)

# Import val after patching
try:
    import val
except ImportError as e:
    # If import fails, it might be due to relative imports in val.py depending on CWD
    # We might need to change CWD to yolov5_dir
    print(f"Import failed: {e}. Switching CWD to {yolov5_dir}")
    os.chdir(yolov5_dir)
    import val

def run_lpd():
    data_path = os.path.join(root_dir, 'evaluation/lpd.yaml')
    weights_path = os.path.join(root_dir, 'model/LP_detector.pt')
    
    print("Starting LPD Evaluation...")
    print(f"Data: {data_path}")
    print(f"Weights: {weights_path}")
    
    # Run validation
    # Capturing output might be hard if val.py prints to logger. 
    # It prints to console.
    results = val.run(
        data=data_path,
        weights=weights_path,
        task='val',
        imgsz=640,
        batch_size=32, # CPU might struggle, but let's try
        conf_thres=0.001,
        iou_thres=0.6,
        plots=False,
        device='cpu'
    )
    
    # results is (mp, mr, map50, map, ...)
    print("-" * 30)
    print("LPD Results (Raw):")
    print(results)
    
    mp, mr, map50, map_ver = results[0][:4]
    
    # F1 score is not returned directly in the tuple (it's in the stats list inside val.py but not returned)
    # But F1 = 2 * (P * R) / (P + R)
    f1 = 0
    if (mp + mr) > 0:
        f1 = 2 * (mp * mr) / (mp + mr)
    
    print("-" * 30)
    print(f"Precision: {mp:.4f}")
    print(f"Recall: {mr:.4f}")
    print(f"mAP@0.5: {map50:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print("-" * 30)

if __name__ == "__main__":
    run_lpd()
