import sys
import os
import glob
import torch
import cv2
import yaml
import warnings
from difflib import SequenceMatcher
import numpy as np

warnings.filterwarnings("ignore")

# Add root to sys.path to import function.helper
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

import function.helper as helper
import function.utils_rotate as utils_rotate

def calculate_ocr_metrics():
    # Load class list
    yaml_path = os.path.join(root_dir, 'training/Letter_detect.yaml')
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
        classes = data['names']

    # Load model
    print("Loading OCR model...")
    # Use yolov5 folder in root as source
    model_path = os.path.join(root_dir, 'model/LP_ocr.pt')
    repo_path = os.path.join(root_dir, 'yolov5')
    
    # helper.read_plate expects the model object
    # We load it using torch.hub as in main.py
    # Note: main.py uses 'yolov5' as repo which relies on it being in cwd
    try:
        yolo_license_plate = torch.hub.load(repo_path, 'custom', path=model_path, source='local', force_reload=True)
    except Exception as e:
        print(f"Error loading model: {e}")
        # Try adjusting path if running from evaluation folder? 
        # But we will run from root.
        sys.exit(1)

    yolo_license_plate.conf = 0.60
    
    # Overwrite model names because the checkpoint seems to have rotated/shifting names
    # while the weights correspond to the standard Letter_detect.yaml order.
    yolo_license_plate.names = classes
    print(f"Overwritten Model Names with {len(classes)} classes from yaml.")


    val_img_dir = os.path.join(root_dir, 'dataset-vietnam-license/OCR/images/val')
    val_lbl_dir = os.path.join(root_dir, 'dataset-vietnam-license/OCR/labels/val')

    image_files = glob.glob(os.path.join(val_img_dir, '*.jpg')) + glob.glob(os.path.join(val_img_dir, '*.png'))
    image_files.sort()

    print(f"Found {len(image_files)} validation images.")

    total_chars = 0
    correct_chars = 0
    total_plates = 0
    correct_plates = 0

    valid_samples = 0

    for img_path in image_files:
        if not os.path.exists(img_path):
            continue
            
        # Read Image
        img = cv2.imread(img_path)
        if img is None:
            continue

        # Predict
        try:
            pred_text = helper.read_plate(yolo_license_plate, img)
        except Exception as e:
            print(f"Error predicting {img_path}: {e}")
            pred_text = "unknown"

        if pred_text == "unknown":
            pred_text = ""
        
        # Read GT
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        lbl_path = os.path.join(val_lbl_dir, base_name + '.txt')
        
        gt_text = ""
        if os.path.exists(lbl_path):
            with open(lbl_path, 'r') as f:
                lines = f.readlines()
                
            gt_objs = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    cls = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    # Ensure cls is valid
                    if 0 <= cls < len(classes):
                        gt_objs.append([x, y, classes[cls]])
            
            if gt_objs:
                # Construct GT string
                # Sort by Y to separate lines
                gt_objs.sort(key=lambda k: k[1])
                
                lines_list = []
                current_line = [gt_objs[0]]
                for i in range(1, len(gt_objs)):
                    # Threshold for line separation: 0.2 (20% of image height)
                    if gt_objs[i][1] - current_line[-1][1] > 0.2:
                        lines_list.append(current_line)
                        current_line = [gt_objs[i]]
                    else:
                        current_line.append(gt_objs[i])
                lines_list.append(current_line)
                
                gt_str = ""
                for idx, line in enumerate(lines_list):
                    line.sort(key=lambda k: k[0])
                    for obj in line:
                        gt_str += obj[2]
                    if idx < len(lines_list) - 1:
                        gt_str += "-"
                gt_text = gt_str
        
        valid_samples += 1
        
        # Character Accuracy Calculation
        # Using SequenceMatcher to find matching characters
        m = SequenceMatcher(None, gt_text, pred_text)
        matches = sum(block.size for block in m.get_matching_blocks())
        
        total_chars += len(gt_text)
        correct_chars += matches
        
        # Plate Accuracy Calculation
        if gt_text == pred_text:
            correct_plates += 1
        else:
             if valid_samples <= 10:
                 print(f"Mismatch: GT='{gt_text}' Pred='{pred_text}'")

        total_plates += 1

    print("-" * 30)
    print(f"Total Plates: {total_plates}")
    print(f"Total Chars: {total_chars}")
    print(f"Correct Chars: {correct_chars}")
    print(f"Exact Match Plates: {correct_plates}")
    print("-" * 30)
    
    char_acc = (correct_chars / total_chars * 100) if total_chars > 0 else 0
    plate_acc = (correct_plates / total_plates * 100) if total_plates > 0 else 0
    
    print(f"Character Accuracy: {char_acc:.2f}%")
    print(f"Plate Accuracy: {plate_acc:.2f}%")

if __name__ == "__main__":
    calculate_ocr_metrics()
