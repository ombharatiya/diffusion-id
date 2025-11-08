# DiffusionID: AI-Powered Identity-Preserving Portrait Generation

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Workflow-orange.svg)](https://github.com/comfyanonymous/ComfyUI)
[![Stable Diffusion](https://img.shields.io/badge/Stable%20Diffusion-XL-purple.svg)](https://stability.ai/)

> **Production-grade diffusion pipeline for identity-preserving portrait stylization at scale. Combines InstantID face embeddings with cartoon style transfer and automated print-ready card generation.**

---

## 🎯 Project Overview

A two-stage production pipeline that transforms user photographs into stylized cartoon portraits and generates customized 3"×7" print-ready cards. Designed for high-volume processing (10,000+ cards) with cost efficiency as a primary goal.

**Key Achievements:**
- 💰 **95% cost reduction** vs commercial APIs ($0.002 vs $0.03 per image)
- ⚡ **8-second processing** per image on GPU
- 🎨 **Identity preservation** with cartoon stylization
- 📄 **Automated PDF generation** with intelligent layouts
- 🚀 **Production-ready** for 10,000+ card batches

---

## 📁 Project Structure

```
diffusion-id/
├── ai-pipeline/                    # Stage 1: AI Image Processing
│   ├── comfyui_api.py             # ComfyUI REST API client
│   ├── batch_processor.py         # Parallel batch processing
│   ├── runpod_setup.sh            # Automated deployment
│   ├── workflows/                 # 24 workflow iterations
│   │   └── workflow_faceid_swap_v2.json  # Final production workflow
│   ├── examples/                  # Sample input/output images
│   ├── README.md                  # Detailed AI pipeline docs
│   └── WORKFLOW_EVOLUTION.md      # Complete tuning history
│
├── pdf-generator/                 # Stage 2: PDF Card Generation
│   ├── generate_cards.py          # Main PDF generation script
│   ├── config.json                # Layout configuration
│   ├── card_template.html         # HTML template reference
│   ├── input-sample/              # Sample CSV and images
│   ├── output/                    # Generated PDFs
│   ├── README.md                  # Detailed PDF generator docs
│   └── requirements.txt           # Python dependencies
│
└── PROJECT_TECHNICAL_DOCUMENTATION.md  # Complete technical specs
```

---

## 🚀 Quick Start

### Stage 1: AI Image Processing

Generate stylized portraits from source photos:

```bash
cd ai-pipeline

# Deploy to RunPod GPU
bash runpod_setup.sh

# Start ComfyUI server
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188

# Process images
python batch_processor.py
```

**📖 [Full AI Pipeline Documentation →](ai-pipeline/)**

---

### Stage 2: PDF Card Generation

Convert portraits into print-ready cards:

```bash
cd pdf-generator

# Install dependencies
pip install -r requirements.txt

# Generate cards from CSV
python generate_cards.py

# Use custom config
python generate_cards.py my_config.json
```

**📖 [Full PDF Generator Documentation →](pdf-generator/)**

---

## 💡 Key Features

### Stage 1: AI Image Processing
- **Face Identity Preservation:** InstantID + IP-Adapter FaceID Plus v2
- **Cartoon Stylization:** Automatic style transfer to match template
- **Batch Processing:** 4 parallel workers with retry logic
- **Cost Optimization:** Self-hosted on RunPod ($0.002/image)
- **Quality Tuning:** 24 workflow iterations documented

### Stage 2: PDF Generation
- **Intelligent Layouts:** Conditional sizing based on content length
- **Optimal Line Breaking:** Word-boundary detection algorithm
- **Flexible Borders:** Per-section configuration
- **Print Quality:** 300 DPI equivalent output
- **CSV Batch Processing:** Hundreds of cards from simple input

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Processing Speed** | 8 seconds/image (RTX 4090) |
| **Cost per Image** | $0.002 (self-hosted) |
| **Batch Throughput** | 450 images/hour |
| **Quality** | 9/10 identity, 8/10 style |
| **PDF Generation** | <1 second/card |

### Cost Comparison (10,000 images)

| Solution | Cost | Time |
|----------|------|------|
| **This System (RunPod)** | **$15-20** | 22 hours |
| Replicate API | $300 | 1 hour |
| Local MacBook | $0 | 3-7 days |

---

## 🛠️ Technology Stack

### AI Pipeline
- **Framework:** ComfyUI, PyTorch 2.8.0
- **Models:** Stable Diffusion XL, InstantID, IP-Adapter FaceID Plus v2, InsightFace
- **Infrastructure:** RunPod GPU Cloud (RTX 3090/4090)
- **Languages:** Python 3.9+, Shell scripting

### PDF Generation
- **Libraries:** ReportLab, Pillow
- **Format:** PostScript points (72 DPI base)
- **Output:** Print-ready PDFs (3"×7")

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [ai-pipeline/](ai-pipeline/) | AI processing setup and usage |
| [pdf-generator/](pdf-generator/) | PDF generation configuration |
| [WORKFLOW_EVOLUTION.md](ai-pipeline/WORKFLOW_EVOLUTION.md) | 24 workflow iterations history |
| [PROJECT_TECHNICAL_DOCUMENTATION.md](PROJECT_TECHNICAL_DOCUMENTATION.md) | Complete technical specifications |

---

## 🎨 Example Workflow

```mermaid
graph LR
    A[Source Photo] --> B[Face Detection]
    B --> C[Identity Extraction]
    C --> D[Style Transfer]
    D --> E[Cartoon Portrait]
    E --> F[CSV + Config]
    F --> G[PDF Generator]
    G --> H[Print-Ready Card]
```

**Input:** User photograph + body template  
**Output:** 3"×7" print-ready PDF card with stylized portrait

---

## 🔧 Configuration

### AI Pipeline Configuration
- **Workflow:** `ai-pipeline/workflows/workflow_faceid_swap_v2.json`
- **Parameters:** Sampling steps, CFG scale, IP-Adapter strength
- **GPU:** RTX 3090 or RTX 4090 recommended

### PDF Configuration
- **File:** `config.json` (30+ parameters)
- **Dimensions:** All in PostScript points
- **Layouts:** Conditional based on content length
- **Borders:** Per-section customization

---

## 📦 Installation

### Prerequisites
- Python 3.9+
- RunPod account (for AI processing)
- 60GB storage (for models)

### Setup

```bash
# Clone repository
git clone https://github.com/ombharatiya/diffusion-id.git
cd diffusion-id

# AI Pipeline setup
cd ai-pipeline
bash runpod_setup.sh

# PDF Generator setup
cd ../pdf-generator
pip install -r requirements.txt
```

---

## 🎯 Use Cases

- **Event Photography:** Generate hundreds of personalized cards
- **Corporate IDs:** Professional portrait cards with branding
- **Conference Badges:** Stylized attendee cards
- **Marketing Materials:** Custom promotional cards
- **Educational:** Student/staff ID cards

---

## 🔬 Technical Highlights

### AI Pipeline Innovations
1. **Cost Optimization:** 95% reduction through self-hosting
2. **Identity Preservation:** FaceID Plus v2 for strong facial features
3. **Style Consistency:** Tuned IP-Adapter weights (0.85)
4. **Parallel Processing:** 4 concurrent workers with retry logic
5. **Workflow Evolution:** 24 iterations documented

### PDF Generation Innovations
1. **Conditional Layouts:** Dynamic sizing based on content
2. **Optimal Line Breaking:** Word-boundary algorithm
3. **Point-Based Precision:** PostScript point system
4. **Flexible Borders:** Independent per-section control
5. **JSON Configuration:** 30+ parameters, no code changes

---

## 📈 Scalability

| Scale | Setup Time | Processing Time | Cost |
|-------|-----------|-----------------|------|
| 10 cards | 5 min | 2 min | $0.02 |
| 100 cards | 5 min | 15 min | $0.20 |
| 1,000 cards | 30 min | 2.5 hours | $2.00 |
| 10,000 cards | 30 min | 22 hours | $15-20 |

---

## 🤝 Contributing

This is a portfolio project showcasing AI/ML engineering and document automation. Feel free to fork and adapt for your use cases.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👤 Author

**Om Bharatiya**

- Portfolio: [Your Portfolio URL]
- LinkedIn: [Your LinkedIn]
- GitHub: [@ombharatiya](https://github.com/ombharatiya)

---

## 🙏 Acknowledgments

- **ComfyUI:** Workflow orchestration framework
- **InstantID:** Face identity preservation
- **IP-Adapter:** Style transfer technology
- **RunPod:** GPU cloud infrastructure
- **ReportLab:** PDF generation library

---

## 📚 Additional Resources

- [ComfyUI Documentation](https://github.com/comfyanonymous/ComfyUI)
- [InstantID Paper](https://instantid.github.io/)
- [RunPod Platform](https://runpod.io)
- [ReportLab User Guide](https://www.reportlab.com/docs/reportlab-userguide.pdf)

---

**⭐ If you find this project useful, please consider giving it a star!**

---

*Last Updated: November 8, 2025*
