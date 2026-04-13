import torch
import cv2
import numpy as np

def get_gpu_peak_brightness(frame):
    # 1. Move the frame to the RTX 3050 memory
    # We use float16 to keep it fast and precise for HDR
    gpu_frame = torch.from_numpy(frame).to('cuda').half()
    
    # 2. Calculate the Peak Brightness (MaxRGB) using the GPU
    peak = torch.max(gpu_frame).item()
    
    # 3. Calculate Average brightness
    avg = torch.mean(gpu_frame).item()
    
    return peak, avg

print("Engine ready. The RTX 3050 is standing by.")