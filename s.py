import os
tools = [r"C:\Users\HP\Documents\video converter\rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe", 
         r"C:\Users\HP\Documents\video converter\hdr10plus_tool.exe"]

for t in tools:
    print(f"{os.path.basename(t)}: {'FOUND' if os.path.exists(t) else 'MISSING'}")