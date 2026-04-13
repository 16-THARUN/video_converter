import subprocess
import os
import json

# --- PATH CONFIGURATION ---
# Using the exact Linux mount paths we discussed
RIFE_BIN = "/mnt/c/Users/HP/Documents/video_converter/rife-ncnn-vulkan/rife-ncnn-vulkan-20221029-ubuntu/rife-ncnn-vulkan"
HDR_BIN = "/mnt/c/Users/HP/Documents/video_converter/hdr10/hdr10plus_tool"

# The 'Monster' Filename - Properly escaped for Python
INPUT_VIDEO = "/mnt/d/New folder (6)/@PrakyTV - Avatar_ Fire and Ash (2026) TRUE WEB-DL - 4K SDR - 2160p HQ - HEVC - UNTOUCHED - [Tamil + Telugu + Hindi - HQ Clean Audio (AAC 2.0) ] - (English - Original DD+5.1) - 21.6GB - ESub.mkv"
OUTPUT_FINAL = "/mnt/d/New folder (6)/Avatar_48fps_HDR10Plus_FINAL.mkv"

# Keep TEST_MODE = True for the first 60 seconds to verify colors and motion
TEST_MODE = True 

def run_avatar_upgrade():
    # Verify tools exist before starting
    for tool in [RIFE_BIN, HDR_BIN]:
        if not os.path.exists(tool):
            print(f"CRITICAL ERROR: Tool not found at {tool}")
            return

    # Temporary working files (stored on D: drive to save space on C:)
    temp_dir = "/mnt/d/New folder (6)/temp_work"
    os.makedirs(temp_dir, exist_ok=True)
    
    t_48fps = os.path.join(temp_dir, "step1_48fps.mkv")
    t_hdr_raw = os.path.join(temp_dir, "step2_hdr.hevc")
    t_meta_json = os.path.join(temp_dir, "step3_meta.json")
    t_injected = os.path.join(temp_dir, "step4_injected.hevc")

    try:
        print("--- STEP 1: AI MOTION INTERPOLATION (48FPS) ---")
        # -t 128 prevents VRAM overflow on the RTX 3050
        rife_cmd = [RIFE_BIN, "-i", INPUT_VIDEO, "-o", t_48fps, "-n", "2", "-t", "128", "-m", "rife-v4"]
        subprocess.run(rife_cmd, check=True)

        print("\n--- STEP 2: SDR TO HDR10 CONVERSION ---")
        # zscale + NVENC p4 for stability
        vf = "format=yuv420p10le,zscale=tin=bt709:t=smpte2084:p=bt2020:m=bt2020nc"
        ffmpeg_hdr = [
            "ffmpeg", "-y", "-i", t_48fps,
            "-t", "60" if TEST_MODE else "05:00:00", # Limit to 60s for test
            "-vf", vf, "-c:v", "hevc_nvenc", "-preset", "p4", "-cq", "20", "-pix_fmt", "p010le",
            "-color_primaries", "bt2020", "-color_trc", "smpte2084", "-colorspace", "bt2020nc",
            "-an", t_hdr_raw
        ]
        subprocess.run(ffmpeg_hdr, check=True)

        print("\n--- STEP 3: GENERATING DYNAMIC METADATA ---")
        # Create metadata for the test duration (approx 2880 frames for 60s @ 48fps)
        num_frames = 3000 if TEST_MODE else 300000 
        meta_data = {"JSON_version": "1.0", "DHDR10Plus": []}
        for i in range(0, num_frames, 120):
            meta_data["DHDR10Plus"].append({"SceneFirstFrameIndex": i, "SceneFrameNumbers": [120], "MaxScl": [450,450,450]})
        with open(t_meta_json, 'w') as f:
            json.dump(meta_data, f)

        print("\n--- STEP 4: INJECTING HDR10+ & FINAL MUXING ---")
        # Inject metadata
        subprocess.run([HDR_BIN, "inject", "-i", t_hdr_raw, "-j", t_meta_json, "-o", t_injected], check=True)
        
        # Mux with original Audio and Subtitles
        mux_cmd = [
            "ffmpeg", "-y", "-i", t_injected, "-i", INPUT_VIDEO,
            "-map", "0:v:0", "-map", "1:a", "-map", "1:s?", # Copy all audio/subs
            "-c", "copy", OUTPUT_FINAL
        ]
        subprocess.run(mux_cmd, check=True)

        print(f"\n--- SUCCESS! ---")
        print(f"Final file is ready: {OUTPUT_FINAL}")

    except Exception as e:
        print(f"\nERROR OCCURRED: {e}")
    finally:
        print("Cleaning up temporary files...")
        # Optional: Uncomment these to delete temp files automatically
        # for f in [t_48fps, t_hdr_raw, t_meta_json, t_injected]:
        #    if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    run_avatar_upgrade()