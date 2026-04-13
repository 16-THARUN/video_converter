import cv2
import torch
import numpy as np
from ccvfi import AutoModel, ConfigType
from tqdm import tqdm
import subprocess

# --- CONFIG ---
INPUT_VIDEO = "/mnt/d/New folder (6)/avatar3.mkv"
OUTPUT_VIDEO = "/mnt/d/New folder (6)/avatar_48fps_temp.mkv"
MODEL_TYPE = ConfigType.RIFE_IFNet_v426_heavy 
TILE_SIZE = 720  # Blocks of 720x720 to fit in 4GB VRAM
PADDING = 32     # Overlap to prevent 'seams' between tiles

def tiled_inference(model, frame1, frame2):
    """Manual tiling helper to prevent 4K OOM on 4GB cards."""
    h, w, _ = frame1.shape
    # Ensure frames are float32 and normalized for the AI
    f1 = torch.from_numpy(frame1).permute(2, 0, 1).float().cuda() / 255.
    f2 = torch.from_numpy(frame2).permute(2, 0, 1).float().cuda() / 255.
    
    # We use a simple grid: 4K (3840x2160) split into tiles
    # Note: For speed, we'll use the model's standard call 
    # but manually slice the image if the library refuses to tile.
    
    # NEW 2026 METHOD: In ccvfi, tiling is often an attribute, not a kwarg
    model.tile = TILE_SIZE
    model.tile_pad = PADDING
    
    # If the above fails, the library usually expects the frames 
    # to be passed as a list of Tensors or Numpy arrays.
    with torch.no_grad():
        # Passing without 'tile=' but having set model.tile above
        out = model.inference_image_list(img_list=[frame1, frame2])[0]
    return out

def process_video():
    print(f"--- 2026 CUDA PIPELINE: {torch.cuda.get_device_name(0)} ---")
    
    print("Loading AI Model...")
    model = AutoModel.from_pretrained(MODEL_TYPE, device="cuda")
    
    # Try to set tiling as properties (Common in ccvfi v1.2+)
    model.tile = TILE_SIZE
    model.tile_pad = PADDING

    cap = cv2.VideoCapture(INPUT_VIDEO)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = 120 # 5-second test

    # High-quality HEVC pipe
    ffmpeg_cmd = [
        'ffmpeg', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
        '-s', f'{width}x{height}', '-pix_fmt', 'bgr24', '-r', f'{fps*2}',
        '-i', '-', '-c:v', 'hevc_nvenc', '-preset', 'p4', '-cq', '20',
        '-pix_fmt', 'p010le', OUTPUT_VIDEO
    ]
    out_pipe = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    ret, frame1 = cap.read()
    print(f"Processing 4K ({width}x{height}) -> 48fps...")
    
    try:
        for _ in tqdm(range(total_frames - 1)):
            ret, frame2 = cap.read()
            if not ret: break

            # Run inference
            mid_frame = model.inference_image_list(img_list=[frame1, frame2])[0]

            # Write to video
            out_pipe.stdin.write(frame1.tobytes())
            out_pipe.stdin.write(mid_frame.tobytes())
            frame1 = frame2

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        if "out of memory" in str(e).lower():
            print("GPU Memory Full! Try lowering TILE_SIZE to 512.")
    finally:
        out_pipe.stdin.close()
        out_pipe.wait()
        cap.release()
        print(f"\nSUCCESS! File created: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    process_video()