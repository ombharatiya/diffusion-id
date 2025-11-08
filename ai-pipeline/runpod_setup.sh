#!/bin/bash
# RunPod ComfyUI Setup Script for Face Swap + Cartoon Stylization
# Optimized for 10,000+ image processing

set -e

echo "=== ComfyUI Face Swap Setup for RunPod ==="

# Update system
apt-get update
apt-get install -y git wget curl

# Install ComfyUI
cd /workspace
if [ ! -d "ComfyUI" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git
fi
cd ComfyUI

# Install Python dependencies
pip install -r requirements.txt
pip install insightface onnxruntime-gpu

# Create directories
mkdir -p models/checkpoints
mkdir -p models/ipadapter
mkdir -p models/controlnet
mkdir -p models/insightface
mkdir -p custom_nodes

# Download required models
echo "Downloading models..."

# Base checkpoint (Realistic Vision for better face quality)
cd models/checkpoints
if [ ! -f "realisticVisionV60B1_v51VAE.safetensors" ]; then
    wget -O realisticVisionV60B1_v51VAE.safetensors \
        "https://huggingface.co/SG161222/Realistic_Vision_V6.0_B1_noVAE/resolve/main/realisticVisionV60B1_v51VAE.safetensors"
fi

# IP-Adapter for style transfer
cd ../ipadapter
if [ ! -f "ip-adapter-faceid-plusv2_sd15.bin" ]; then
    wget -O ip-adapter-faceid-plusv2_sd15.bin \
        "https://huggingface.co/h94/IP-Adapter-FaceID/resolve/main/ip-adapter-faceid-plusv2_sd15.bin"
fi

# ControlNet for face structure
cd ../controlnet
if [ ! -f "control_v11p_sd15_openpose.pth" ]; then
    wget -O control_v11p_sd15_openpose.pth \
        "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth"
fi

# InsightFace models for face detection
cd ../insightface
if [ ! -d "models" ]; then
    mkdir -p models/buffalo_l
    cd models/buffalo_l
    wget https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip
    unzip buffalo_l.zip
    rm buffalo_l.zip
    cd ../..
fi

# Install ComfyUI Manager (for easy custom node management)
cd /workspace/ComfyUI/custom_nodes
if [ ! -d "ComfyUI-Manager" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Manager.git
fi

# Install IPAdapter Plus custom nodes
if [ ! -d "ComfyUI_IPAdapter_plus" ]; then
    git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
    cd ComfyUI_IPAdapter_plus
    pip install -r requirements.txt
    cd ..
fi

# Install InstantID nodes
if [ ! -d "ComfyUI-InstantID" ]; then
    git clone https://github.com/cubiq/ComfyUI-InstantID.git
    cd ComfyUI-InstantID
    pip install -r requirements.txt
    cd ..
fi

# Install FaceDetailer for better face detection
if [ ! -d "ComfyUI-Impact-Pack" ]; then
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack.git
    cd ComfyUI-Impact-Pack
    pip install -r requirements.txt
    cd ..
fi

echo "=== Setup Complete ==="
echo "To start ComfyUI, run:"
echo "cd /workspace/ComfyUI && python main.py --listen 0.0.0.0 --port 8188"
echo ""
echo "For API access, use: http://<runpod-ip>:8188"
