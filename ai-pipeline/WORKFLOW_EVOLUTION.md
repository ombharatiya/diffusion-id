# ComfyUI Workflow Evolution & Tuning History

**Project:** DiffusionID - Identity-Preserving Portrait Generation  
**Period:** October 27-30, 2025  
**Total Iterations:** 24 workflow versions

---

## Overview

This document tracks the iterative development and tuning of ComfyUI workflows for face swapping with cartoon stylization. The project evolved through multiple approaches to solve identity preservation, style consistency, and quality issues.

---

## Chronological Development

### Phase 1: Initial Setup (Oct 27)
**File:** `simplified_workflow.json` (Oct 27 15:26)

**Approach:** Basic text-to-image generation without face swap
- Simple KSampler workflow
- No face detection or identity preservation
- Used only for testing ComfyUI setup
- **Issue:** No face swap capability, just generic generation

---

### Phase 2: Face Swap Foundation (Oct 30 Morning)
**Files:** 
- `workflow_faceswap.json` (Oct 30 11:04)
- `workflow_faceswap_ipadapter.json` (Oct 30 11:45)
- `workflow_working_faceswap.json` (Oct 30 11:50)

**Approach:** Initial face swap implementation
- Added InstantID for face detection
- IP-Adapter for style transfer
- Basic face embedding extraction
- **Issues:**
  - Face identity not preserved well
  - Style mismatch between face and body
  - Inconsistent results

---

### Phase 3: IP-Adapter Experiments (Oct 30 12:00-12:15)
**Files:**
- `workflow_simple_ipadapter.json` (Oct 30 12:08)
- `workflow_basic_ipadapter.json` (Oct 30 12:10)
- `workflow_faceid_final.json` (Oct 30 12:12)

**Approach:** Simplified IP-Adapter configurations
- Reduced node complexity
- Focused on IP-Adapter strength tuning
- Tested different face embedding methods
- **Issues:**
  - Still losing facial features
  - Body template not properly integrated

---

### Phase 4: Layout & Structure Fixes (Oct 30 13:30-13:40)
**Files:**
- `workflow_basic_working.json` (Oct 30 13:35)
- `workflow_unified_fixed.json` (Oct 30 13:37)

**Approach:** Fixed workflow structure
- Corrected node connections
- Proper VAE encoding/decoding
- Fixed latent image dimensions
- **Issues:**
  - Better structure but identity still weak
  - Need stronger face preservation

---

### Phase 5: Tuning Iterations (Oct 30 13:55-14:42)
**Files:**
- `workflow_tuned.json` (Oct 30 13:55)
- `workflow_tuned_v2_simplified.json` (Oct 30 14:06)
- `workflow_tuned_v2.json` (Oct 30 14:17)
- `workflow_tuned_v2.1.json` (Oct 30 14:42)

**Approach:** Parameter optimization
- Adjusted CFG scale (7.5 → 8.0 → 7.5)
- Modified denoise strength (0.85 → 0.75 → 0.80)
- IP-Adapter weight tuning (0.85 → 0.90 → 0.85)
- Sampling steps optimization (25 → 30 → 25)
- **Issues:**
  - Over-denoising caused loss of detail
  - High CFG made images too rigid
  - Finding balance between identity and style

---

### Phase 6: Advanced Tuning (Oct 30 14:59-15:41)
**Files:**
- `workflow_tuned_v3.json` (Oct 30 14:59)
- `workflow_tuned_v3_fixed.json` (Oct 30 15:20)
- `workflow_tuned_v3_simple.json` (Oct 30 15:41)

**Approach:** Multi-parameter refinement
- Added ControlNet for pose guidance
- Dual conditioning (positive + negative prompts)
- Better prompt engineering for cartoon style
- **Issues:**
  - ControlNet added complexity
  - Processing time increased
  - Marginal quality improvement

---

### Phase 7: Identity Focus (Oct 30 15:48-16:40)
**Files:**
- `workflow_v4_fixed_identity.json` (Oct 30 15:48)
- `workflow_v5_improved.json` (Oct 30 15:52)
- `workflow_v6_plus_face.json` (Oct 30 16:40)

**Approach:** Prioritize face identity preservation
- Increased IP-Adapter face weight
- Multiple face embedding layers
- Face-specific ControlNet
- Reduced style transfer strength
- **Issues:**
  - Better identity but less stylization
  - Face looked realistic on cartoon body (uncanny)
  - Need better balance

---

### Phase 8: Face-Only Processing (Oct 30 17:03-17:24)
**Files:**
- `workflow_v7_face_only.json` (Oct 30 17:03)
- `workflow_v7_face_only_fixed.json` (Oct 30 17:09)
- `workflow_v8_minimal_face.json` (Oct 30 17:24)

**Approach:** Process only face region
- Inpainting approach for face area
- Keep body template unchanged
- Minimal processing pipeline
- **Issues:**
  - Visible seams at face boundaries
  - Color mismatch between face and body
  - Required precise masking

---

### Phase 9: FaceID Integration (Oct 30 18:03-18:17)
**Files:**
- `workflow_faceid_swap.json` (Oct 30 18:03)
- `workflow_faceid_swap_v2.json` (Oct 30 18:17)

**Approach:** FaceID Plus v2 model
- Stronger identity embeddings
- Better face feature extraction
- Improved style harmonization
- **Result:** Best balance achieved
  - Strong identity preservation
  - Good cartoon style integration
  - Consistent results across different faces

---

## Key Technical Learnings

### 1. IP-Adapter Strength
- **Too Low (0.6-0.7):** Loses face identity
- **Optimal (0.85):** Good balance
- **Too High (0.95+):** Realistic face on cartoon body (uncanny)

### 2. Denoise Strength
- **Too Low (0.6-0.7):** Keeps too much original, poor style transfer
- **Optimal (0.85):** Good style application
- **Too High (0.95+):** Loses facial features

### 3. CFG Scale
- **Too Low (5-6):** Weak prompt adherence, inconsistent style
- **Optimal (7.5):** Good prompt following
- **Too High (9+):** Over-saturated, rigid appearance

### 4. Sampling Steps
- **Too Few (15-20):** Artifacts, incomplete generation
- **Optimal (25):** Good quality, reasonable speed
- **Too Many (40+):** Minimal improvement, 2x processing time

### 5. Model Selection
- **Realistic Vision V6:** Best for face quality
- **FaceID Plus v2:** Superior identity preservation vs standard IP-Adapter
- **InsightFace Buffalo-L:** Most accurate face detection

---

## Final Configuration (workflow_faceid_swap_v2.json)

```json
{
  "model": "Realistic Vision V6.0 B1",
  "face_model": "IP-Adapter FaceID Plus v2",
  "face_detector": "InsightFace Buffalo-L",
  "sampling": {
    "steps": 25,
    "cfg": 7.5,
    "sampler": "euler_ancestral",
    "scheduler": "normal",
    "denoise": 0.85
  },
  "ip_adapter": {
    "strength": 0.85,
    "face_weight": 0.90
  },
  "resolution": "512x768",
  "prompt": "professional cartoon illustration, doctor portrait with stethoscope, white coat, clean background, high quality",
  "negative_prompt": "realistic photo, photograph, low quality, blurry, distorted"
}
```

---

## Common Issues & Solutions

### Issue 1: Face Identity Lost
**Symptoms:** Generated face doesn't match source
**Solutions:**
- Increase IP-Adapter strength (0.85+)
- Use FaceID Plus v2 instead of standard IP-Adapter
- Ensure high-quality source image (clear, frontal face)

### Issue 2: Realistic Face on Cartoon Body
**Symptoms:** Uncanny valley effect, style mismatch
**Solutions:**
- Reduce IP-Adapter strength (0.80-0.85)
- Stronger cartoon-specific prompts
- Increase denoise for more style transfer

### Issue 3: Blurry or Low Quality
**Symptoms:** Soft details, artifacts
**Solutions:**
- Increase sampling steps (25-30)
- Use higher resolution checkpoint
- Reduce denoise slightly (0.80-0.85)

### Issue 4: Inconsistent Results
**Symptoms:** Different outputs with same inputs
**Solutions:**
- Fix random seed for reproducibility
- Use consistent sampler (euler_ancestral)
- Ensure proper face detection (frontal, well-lit)

### Issue 5: Slow Processing
**Symptoms:** >15 seconds per image
**Solutions:**
- Reduce sampling steps (20-25)
- Use smaller resolution (512x768 vs 768x1024)
- Remove unnecessary nodes (ControlNet if not needed)

---

## Performance Metrics

| Version | Processing Time | Identity Score* | Style Score* | Overall Quality |
|---------|----------------|-----------------|--------------|-----------------|
| v1-v3 | 12-15s | 6/10 | 7/10 | Poor |
| v4-v6 | 10-12s | 8/10 | 5/10 | Fair |
| v7-v8 | 8-10s | 7/10 | 8/10 | Good |
| FaceID v2 | 8s | 9/10 | 8/10 | Excellent |

*Subjective visual assessment

---

## Deployment Recommendations

### For Production (10k+ images):
- Use `workflow_faceid_swap_v2.json`
- RTX 4090 GPU (8s/image)
- Batch size: 1 (for consistency)
- Parallel workers: 4

### For Testing:
- Use `workflow_v5_improved.json` (simpler, faster)
- RTX 3090 GPU acceptable
- Single worker for debugging

### For High Quality:
- Use `workflow_faceid_swap_v2.json`
- Increase steps to 30
- Resolution 768x1024
- Accept 12s processing time

---

## Files Structure

```
ai-pipeline/
├── workflows/
│   ├── workflow_faceid_swap_v2.json    # RECOMMENDED - Final production version
│   ├── workflow_faceid_swap.json       # Good alternative
│   ├── workflow_v8_minimal_face.json   # Fastest (face-only)
│   ├── workflow_v5_improved.json       # Balanced quality/speed
│   └── [20 other experimental versions]
├── comfyui_api.py                      # API client
├── batch_processor.py                  # Batch processing
├── runpod_setup.sh                     # Deployment script
├── requirements.txt                    # Python dependencies
├── SETUP.txt                           # Setup guide
├── examples/                           # Sample images
└── WORKFLOW_EVOLUTION.md              # This file
```

---

## Quick Start

1. **Deploy to RunPod:**
   ```bash
   bash runpod_setup.sh
   ```

2. **Start ComfyUI:**
   ```bash
   cd /workspace/ComfyUI
   python main.py --listen 0.0.0.0 --port 8188
   ```

3. **Run batch processing:**
   ```bash
   python batch_processor.py
   ```

4. **Use recommended workflow:**
   - Load `workflows/workflow_faceid_swap_v2.json` in ComfyUI
   - Or API will use it automatically

---

## Future Improvements

1. **Multi-template support:** Different body poses/professions
2. **Automatic quality scoring:** Reject poor generations
3. **Dynamic parameter adjustment:** Based on source image quality
4. **Real-time preview:** WebSocket-based live updates
5. **A/B testing framework:** Compare workflow versions systematically

---

**Document Version:** 1.0  
**Last Updated:** November 8, 2025  
**Status:** Production-Ready
