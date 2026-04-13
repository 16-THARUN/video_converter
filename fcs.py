import subprocess
import os
import sys

# 1. FINAL PATH CONFIGURATION
INPUT = r"D:\New folder (6)\avatar_24fps_raw.hevc"
BASE_DIR = r"C:\Users\HP\Desktop\AvatarProject"
RIFE_EXE = r"C:\Users\HP\Documents\video_converter\rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe"
MODEL = r"C:\Users\HP\Documents\video_converter\rife-ncnn-vulkan-20221029-windows\rife-v4.6"

# Outputs
OUT_HEVC = os.path.join(BASE_DIR, "avatar_48fps_final_10bit.hevc")
IN_FRAMES = os.path.join(BASE_DIR, "frames_in")
OUT_FRAMES = os.path.join(BASE_DIR, "frames_out")

# 2. SANITY CHECK
if not os.path.exists(INPUT):
    sys.exit(f"❌ Input file not found at: {INPUT}")

for d in [IN_FRAMES, OUT_FRAMES]:
    if not os.path.exists(d): 
        os.makedirs(d)

# 3. STEP 1: EXTRACT (Force 8-bit to save Terabytes of space)
# Using rgb24 ensures the files are ~12MB instead of ~50MB per frame.
print("🎞️ Step 1: Extracting 4K frames to 8-bit PNG...")
extract_cmd = [
    "ffmpeg", "-y", "-i", INPUT, 
    "-fps_mode", "passthrough", 
    "-pix_fmt", "rgb24", 
    os.path.join(IN_FRAMES, "%08d.png")
]
subprocess.run(extract_cmd)

# 4. STEP 2: INTERPOLATE (UHD Mode for HP GPU)
print("🚀 Step 2: RIFE Interpolation (4K UHD Mode)...")
rife_cmd = [
    RIFE_EXE, "-i", IN_FRAMES, "-o", OUT_FRAMES, 
    "-m", MODEL, "-n", "2", "-u", "-f", "%08d.png"
]
subprocess.run(rife_cmd)

# 5. STEP 3: RE-ENCODE (Back to 10-bit for HDR)
# This uses the CPU (libx265). Slow but highest quality.
print("🎬 Step 3: Re-encoding to 10-bit Master...")
encode_cmd = [
    "ffmpeg", "-y", "-framerate", "48", 
    "-i", os.path.join(OUT_FRAMES, "%08d.png"),
    "-c:v", "libx265", "-crf", "18", 
    "-pix_fmt", "yuv420p10le", 
    "-tag:v", "hvc1", 
    OUT_HEVC
]
subprocess.run(encode_cmd)

print(f"✅ DONE! File location: {OUT_HEVC}")