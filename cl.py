import json
import os

# Paths
JSON_IN = r"D:\New folder (6)\metadata_48fps.json"
JSON_OUT = r"D:\AvatarProject\metadata_final_fixed.json"

def final_transformation():
    print("🧬 Transforming JSON Schema for 567,788 frames...")
    
    with open(JSON_IN, 'r') as f:
        data = json.load(f)

    # In your file, the data is inside 'SceneInfo'
    raw_frames = data.get("SceneInfo", [])
    if not raw_frames:
        print("❌ Could not find 'SceneInfo' list!")
        return

    print(f"📂 Found {len(raw_frames)} frame entries. Nesting...")

    fixed_metadata = []
    for i, frame in enumerate(raw_frames):
        # The tool expects 'SceneInfo' to be a DICT inside the frame, not a top-level list
        # We also need to ensure FrameNumber is present
        new_frame = {
            "FrameNumber": i,
            "SceneInfo": {
                "SceneNumber": int(frame.get("SceneNumber", 0)),
                "SequenceNumber": int(frame.get("SequenceNumber", 0)),
                "SceneFrameNumber": 0
            }
        }
        
        # Copy the Luminance data into the frame
        for k, v in frame.items():
            if k not in ["SceneNumber", "SequenceNumber"]:
                new_frame[k] = v
        
        fixed_metadata.append(new_frame)

    # Wrap in the mandatory quietvoid/HDR10+ LLC structure
    final_output = {
        "JSONInfo": {
            "HDR10plusProfile": "B",
            "Version": "1.0"
        },
        "JSONMetadata": fixed_metadata
    }

    print("💾 Saving 567,788 entries to D Drive...")
    with open(JSON_OUT, 'w') as f:
        json.dump(final_output, f, separators=(',', ':'))
    
    print(f"✅ SUCCESS: {JSON_OUT} is now ready.")

if __name__ == "__main__":
    final_transformation()