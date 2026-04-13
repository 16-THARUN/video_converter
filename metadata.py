import json
from collections import OrderedDict

# Exact frame count for your 3h 17m file
TOTAL_FRAMES = 283894 

# We force 'HDR10plusProfile' to be the first key in the entire file
master_data = OrderedDict([
    ("HDR10plusProfile", "B"),
    ("Version", "1.0"),
    ("Metadata", [])
])

print(f"Forging {TOTAL_FRAMES} frames in 'Profile-First' format...")

for i in range(TOTAL_FRAMES):
    # We also put it first inside every frame object
    frame = OrderedDict([
        ("HDR10plusProfile", "B"),
        ("num_windows", 1),
        ("average_maxrgb", 100),
        ("distribution_values", [1, 5, 10, 25, 50, 75, 90, 95, 98, 100]),
        ("targeted_system_display_maximum_luminance", 1000),
        ("maxscl", [1000, 1000, 1000]),
        ("bezier_curve_data", {
            "knee_point_x": 512,
            "knee_point_y": 512,
            "bezier_curve_anchors": [0, 0, 0, 0, 0, 0, 0, 0, 0]
        })
    ])
    master_data["Metadata"].append(frame)

# Save using raw string for Windows path
file_path = r"D:\New folder (6)\metadata.json"
with open(file_path, "w") as f:
    json.dump(master_data, f, indent=2)

print(f"SUCCESS: {file_path} is ready.")