import subprocess
import os

def repair_movie(input_path):
    if not os.path.exists(input_path):
        print(f"Error: File not found at {input_path}")
        return

    
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_REPAIRED{ext}"

   
    cmd = [
        'ffmpeg', 
        '-i', input_path, 
        '-c', 'copy', 
        '-map', '0', 
        '-y', 
        output_path
    ]

    try:
        print(f"Processing: {os.path.basename(input_path)}")
        print("Rebuilding MKV container... please wait.")
     
        subprocess.run(cmd, check=True, capture_output=True)
        
        print("-" * 30)
        print(f"SUCCESS!")
        print(f"Fixed file saved to: {output_path}")
        print("-" * 30)
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr.decode()}")
    except FileNotFoundError:
        print("Error: FFmpeg not found. Please install FFmpeg and add it to your PATH.")

repair_movie(r"D:\TorrentDownloads\James Bond The Living Daylights (1987) [1080p].mkv")