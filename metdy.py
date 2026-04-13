import json

# Paths
input_path = r"D:\New folder (6)\metadata.json"
output_path = r"D:\New folder (6)\metadata_48fps.json"

print(f"🔍 Final Alignment - Canonical PascalCase Schema: {input_path}...")

try:
    with open(input_path, 'r') as f:
        original_data = json.load(f)

    raw_frames = original_data.get('Metadata', original_data.get('SceneInfo', []))
    
    if not raw_frames:
        print("❌ Error: Could not find frame data!")
        exit()

    new_frames = []
    print(f"🚀 Doubling {len(raw_frames)} frames for 48fps Master...")

    for i, entry in enumerate(raw_frames):
        bz = entry.get('bezier_curve_data', entry.get('BezierCurveData', {}))
        
        # 🧪 THE FIX: 
        # 1. 'LuminanceParameters' must be PascalCase and a LIST [].
        # 2. Internal keys like 'AverageRGB' must be PascalCase.
        # 3. 'Anchors' is the abbreviated key the tool asked for earlier.
        frame_payload = {
            "LuminanceParameters": [
                {
                    "AverageRGB": int(entry.get('average_maxrgb', entry.get('AverageRGB', 100))),
                    "LuminanceDistributions": [int(x) for x in entry.get('distribution_values', entry.get('LuminanceDistributions', [0]*10))],
                    "MaxScl": [int(x) for x in entry.get('maxscl', entry.get('MaxScl', [1000, 1000, 1000]))]
                }
            ],
            "NumberOfWindows": 1,
            "TargetedSystemDisplayMaximumLuminance": int(entry.get('targeted_system_display_maximum_luminance', 1000)),
            "BezierCurveData": {
                "Anchors": [int(x) for x in bz.get('bezier_curve_anchors', bz.get('Anchors', [0]*9))],
                "KneePointX": int(bz.get('knee_point_x', bz.get('KneePointX', 512))),
                "KneePointY": int(bz.get('knee_point_y', bz.get('KneePointY', 512)))
            }
        }

        # Double the frames for the 48fps timeline
        new_frames.append(frame_payload)
        new_frames.append(frame_payload)

    # Reconstruct the header
    final_output = {
        "JSONInfo": {
            "HDR10plusProfile": "B",
            "Version": "1.0"
        },
        "SceneInfo": new_frames
    }

    print(f"💾 Saving to: {output_path}...")
    # Minifying is safer for the tool's parser
    with open(output_path, 'w') as f:
        json.dump(final_output, f, separators=(',', ':'))

    print(f"✅ Success! Metadata is now in the Canonical Schema.")

except Exception as e:
    print(f"❌ Error: {e}")