import subprocess
import os

# Use a raw string for the path to handle backslashes correctly
file_path = r"D:\TorrentDownloads\James Bond The Living Daylights (1987) [1080p].mkv"

def full_integrity_scan(input_file):
    if not os.path.exists(input_file):
        print(f"CRITICAL ERROR: File not found at {input_file}")
        return

    print(f"--- STARTING FULL SURGICAL SCAN ---")
    
    # We use a list to avoid shell quoting issues entirely
    # -vf showinfo: provides technical data for every single frame
    # -f null -: decodes everything but saves no file (stress test)
    cmd = [
        'ffmpeg', 
        '-v', 'error',              # Only show actual errors
        '-i', input_file, 
        '-f', 'null', 
        '-'
    ]
    
    try:
        # capture_output=True collects the errors into a variable
        process = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        report_path = "surgical_scan_results.txt"
        
        with open(report_path, "w") as f:
            if process.stderr:
                f.write("--- CORRUPTION DETECTED ---\n")
                f.write(process.stderr)
                print("\nSCALPEL FINDINGS:")
                # Print the first 10 errors so you can see them immediately
                print("\n".join(process.stderr.splitlines()[:10]))
            else:
                f.write("No bitstream errors found. The file structure is healthy.")
                print("No errors found in the bitstream.")

        print(f"\nFull surgical report saved to: {os.path.abspath(report_path)}")
        
    except Exception as e:
        print(f"An error occurred during surgery: {e}")

full_integrity_scan(file_path)