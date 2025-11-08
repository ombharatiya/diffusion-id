# AI Image Processing Pipeline

**Part 1 of Desk Standee Project**

Face swap and cartoon stylization system for generating professional portrait cards at scale.

---

## Quick Start

### 1. Deploy to RunPod
```bash
bash runpod_setup.sh
```

### 2. Start ComfyUI
```bash
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

### 3. Process Images
```bash
# Single image
python comfyui_api.py

# Batch processing
python batch_processor.py
```

---

## Project Structure

```
ai-pipeline/
├── comfyui_api.py              # ComfyUI REST API client
├── batch_processor.py          # Parallel batch processing
├── runpod_setup.sh            # Automated deployment script
├── requirements.txt           # Python dependencies
├── SETUP.txt                  # Detailed setup guide
├── workflows/                 # 24 workflow iterations
│   └── workflow_faceid_swap_v2.json  # RECOMMENDED
├── examples/                  # Sample input/output images
├── README.md                  # This file
└── WORKFLOW_EVOLUTION.md     # Complete tuning history
```

---

## Key Features

- **Cost:** $0.002 per image (10k images = $15-20)
- **Speed:** 8 seconds per image average
- **Quality:** Identity preservation + cartoon stylization
- **Scale:** Optimized for 10,000+ images

---

## Technical Stack

- ComfyUI + Stable Diffusion XL
- InstantID + IP-Adapter FaceID Plus v2
- InsightFace Buffalo-L
- PyTorch 2.8.0, CUDA 12.1

---

## Documentation

- **SETUP.txt:** Deployment and troubleshooting
- **WORKFLOW_EVOLUTION.md:** Complete development history (24 iterations)
- **Parent README:** Full project documentation

---

## Cost Estimate

| Images | GPU | Time | Cost |
|--------|-----|------|------|
| 10 | RTX 4090 | 80s | $0.02 |
| 100 | RTX 4090 | 13min | $0.15 |
| 1,000 | RTX 4090 | 2.2hrs | $1.50 |
| 10,000 | RTX 4090 | 22hrs | $15.00 |

---

**Status:** Production-Ready  
**Recommended Workflow:** `workflows/workflow_faceid_swap_v2.json`
