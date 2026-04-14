# video_converter
# 🎬 Advanced Video Interpolation & HDR10+ Reconstructor

A specialized toolkit for high-fidelity 4K video interpolation and dynamic metadata reconstruction. Originally engineered to process the massive frame-load of *Avatar* (2009) at 48fps on consumer-grade hardware.

## 🚀 Key Features

- **RIFE "Safe-Mode" Orchestration**: Optimized thread management (`1:1:1`) to prevent VRAM overflow on 4GB/6GB GPUs (e.g., RTX 3050 Laptop).
- **HDR10+ Metadata Reconstruction**: A Python-based engine that aligns frame-accurate metadata with interpolated streams, satisfying strict Rust-based parser requirements.
- **Fail-Safe Resume Logic**: Automatically detects progress and staging, allowing for multi-day renders to be stopped and resumed without data loss.
- **UHD Tiling Support**: Native integration with RIFE's `-u` flag for seamless 4K image synthesis.

## 🛠️ Technical Challenges Overcome

### 1. The VRAM Bottleneck
Processing 4K frames typically crashes mobile GPUs. This project implements a **Vulkan-bridge handshake** that isolates memory loads, ensuring the RTX 3050 never exceeds its 4GB limit while maintaining UHD output.

### 2. Strict Metadata Parity
HDR10+ parsers (like `hdr10plus_tool`) are written in strict-type Rust. This toolkit includes a JSON reconstructor that solves the common "missing field" and "PascalCase" errors by programmatically aligning 500k+ metadata entries.

## 📦 Prerequisites

- **Python 3.13+**
- **RIFE-ncnn-vulkan**: The core interpolation engine.
- **FFmpeg**: For 10-bit HEVC stream assembly.
- **HDR10+ Tool**: For metadata injection.

## ⚙️ Installation

```bash
git clone [https://github.com/16-THARUN/video_converter.git](https://github.com/16-THARUN/video_converter.git)
cd video_converter
pip install -r requirements.txt
