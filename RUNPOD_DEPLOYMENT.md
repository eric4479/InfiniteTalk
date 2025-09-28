# InfiniteTalk Runpod Deployment Guide

Deploy InfiniteTalk with Issue #123 fixes (dynamic model paths) on Runpod using the GitHub repository.

## 🚀 Quick Deploy on Runpod

### Option 1: One-Line Setup (Recommended)

```bash
# Clone and setup InfiniteTalk with fixes
cd /workspace && \
git clone https://github.com/eric4479/InfiniteTalk.git && \
cd InfiniteTalk && \
git checkout fix-model-download-paths && \
bash scripts/universal_setup.sh
```

### Option 2: Manual Step-by-Step Setup

```bash
# 1. Clone the repository
cd /workspace
git clone https://github.com/eric4479/InfiniteTalk.git
cd InfiniteTalk

# 2. Switch to the fix branch
git checkout fix-model-download-paths

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download optimized models (saves 5.6GB+ bandwidth)
python scripts/download_models_optimized.py --skip-optional

# 5. Test the installation
python scripts/test_runpod_basic.py
```

## 📋 Runpod Template Configuration

### Recommended Container Settings

- **Container Image**: `runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04`
- **GPU**: RTX 4090 or better (24GB+ VRAM recommended)
- **Disk Space**: 50GB+ (for models and temporary files)
- **Port**: 7860 (for Gradio interface)

### Environment Variables (Optional)

```bash
# Set custom model directory (optional)
INFINITETALK_MODEL_DIR=/workspace/models

# For ComfyUI integration
COMFYUI_MODEL_DIR=/workspace/ComfyUI/models
```

## 🔧 Advanced Setup Options

### Docker Container Setup

```dockerfile
# Dockerfile for InfiniteTalk on Runpod
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

WORKDIR /workspace

# Clone InfiniteTalk with fixes
RUN git clone https://github.com/eric4479/InfiniteTalk.git && \
    cd InfiniteTalk && \
    git checkout fix-model-download-paths

# Install dependencies
RUN cd InfiniteTalk && pip install -r requirements.txt

# Set up model paths for Runpod
ENV INFINITETALK_MODEL_DIR=/workspace/models
ENV IS_RUNPOD=true

# Expose port for Gradio
EXPOSE 7860

# Default command
CMD ["python", "/workspace/InfiniteTalk/app.py", "--share", "--server-port", "7860"]
```

### Jupyter Notebook Setup

```python
# Cell 1: Clone and setup
import os
os.chdir('/workspace')

!git clone https://github.com/eric4479/InfiniteTalk.git
os.chdir('/workspace/InfiniteTalk')
!git checkout fix-model-download-paths

# Cell 2: Install dependencies
!pip install -r requirements.txt

# Cell 3: Download models
!python scripts/download_models_optimized.py --skip-optional

# Cell 4: Test installation
!python scripts/test_runpod_basic.py

# Cell 5: Start InfiniteTalk
!python app.py --share --server-port 7860
```

## 🎯 What's Fixed in This Version

### Issue #123 Resolution
- ✅ **Dynamic Model Paths**: Automatically detects Runpod environment
- ✅ **Runpod Optimization**: Models save to `/workspace/models` instead of local directories
- ✅ **Bandwidth Savings**: Optimized downloads (15.6GB vs 21.5GB)
- ✅ **Environment Detection**: Automatically configures for Runpod

### Key Features
- ✅ **Automatic Setup**: Universal setup script handles everything
- ✅ **Runpod-Specific Paths**: Uses `/workspace` for persistent storage
- ✅ **Optimized Downloads**: Only essential model files
- ✅ **Testing Scripts**: Built-in validation and testing
- ✅ **Error Handling**: Comprehensive error messages and recovery

## 📁 File Structure on Runpod

```
/workspace/
├── InfiniteTalk/                    # Main application
│   ├── scripts/
│   │   ├── universal_setup.sh       # One-command setup
│   │   ├── download_models_optimized.py  # Efficient downloads
│   │   └── test_runpod_basic.py     # Runpod validation
│   ├── src/
│   │   ├── config_manager.py        # Dynamic path management
│   │   └── utils.py                 # Environment detection
│   ├── generate_infinitetalk.py     # Main generation script
│   └── app.py                       # Gradio interface
└── models/                          # Model storage (auto-created)
    ├── Wan2.1-I2V-14B-480P/         # Base video model
    ├── chinese-wav2vec2-base/       # Audio encoder
    └── InfiniteTalk/                # InfiniteTalk weights
```

## 🧪 Testing Commands

```bash
# Test environment detection
python -c "
from src.config_manager import ModelPathManager
manager = ModelPathManager()
print('Environment Detection:')
for key, value in manager.env_info.items():
    print(f'  {key}: {value}')
print(f'Model directory: {manager.base_model_dir}')
"

# Test model download
python scripts/download_models_optimized.py --estimate-size

# Test generation (after models downloaded)
python generate_infinitetalk.py \
  --mode t2v \
  --text "A beautiful sunset over mountains" \
  --duration 60 \
  --output /workspace/test_output.mp4
```

## 🚀 Launch Commands

### Gradio Interface
```bash
cd /workspace/InfiniteTalk
python app.py --share --server-port 7860
```

### Direct Generation
```bash
cd /workspace/InfiniteTalk
python generate_infinitetalk.py \
  --mode t2v \
  --text "Your prompt here" \
  --duration 120 \
  --output /workspace/output.mp4
```

### ComfyUI Integration (if ComfyUI is installed)
```bash
# Set up as ComfyUI custom node
cd /workspace/ComfyUI/custom_nodes
git clone https://github.com/eric4479/InfiniteTalk.git
cd InfiniteTalk
git checkout fix-model-download-paths
pip install -r requirements.txt

# ComfyUI will automatically detect the node
cd /workspace/ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

## 🔍 Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```bash
   # Use CPU fallback
   python generate_infinitetalk.py --device cpu --mode t2v --text "test"
   ```

2. **Model Download Fails**
   ```bash
   # Check internet connection and retry
   python scripts/download_models_optimized.py --force
   ```

3. **Path Issues**
   ```bash
   # Verify environment detection
   python scripts/test_runpod_basic.py
   ```

### Log Analysis
```bash
# Check system info
python -c "
import torch
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda}')
print(f'GPU: {torch.cuda.get_device_name() if torch.cuda.is_available() else \"None\"}')
"
```

## 📊 Performance Expectations

### Model Download Times (on Runpod)
- **Base Wan model**: ~10-15 minutes (15GB)
- **Audio encoder**: ~2-3 minutes (500MB)
- **InfiniteTalk weights**: ~1 minute (100MB)
- **Total**: ~15-20 minutes for first setup

### Generation Times (RTX 4090)
- **Text-to-Video (60 frames)**: ~5-10 minutes
- **Image-to-Video (60 frames)**: ~3-7 minutes
- **Multi-talk**: ~10-15 minutes

## 🔗 Repository Links

- **Main Fork**: https://github.com/eric4479/InfiniteTalk
- **Fix Branch**: https://github.com/eric4479/InfiniteTalk/tree/fix-model-download-paths
- **Original Issue**: https://github.com/MeiGen-AI/InfiniteTalk/issues/123

## 📝 Notes

- This version includes all Issue #123 fixes for proper Runpod deployment
- Models are automatically saved to persistent `/workspace` storage
- Environment detection ensures optimal configuration for Runpod
- Optimized downloads save significant bandwidth and setup time
- All testing scripts are included for validation

**Ready for immediate deployment on Runpod!** 🚀