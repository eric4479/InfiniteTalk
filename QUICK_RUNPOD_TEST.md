# Quick Runpod Testing Guide

## 🚀 One-Command Test Setup

If you have a fork with the `fix-model-download-paths` branch:

```bash
# Replace YOUR_USERNAME with your GitHub username
curl -sSL https://raw.githubusercontent.com/YOUR_USERNAME/InfiniteTalk/fix-model-download-paths/runpod_test.sh | bash
```

## 📋 Manual Setup Steps

### 1. Clone Repository with Fix
```bash
# Option A: If you have a fork with the fix branch
git clone https://github.com/YOUR_USERNAME/InfiniteTalk.git
cd InfiniteTalk
git checkout fix-model-download-paths

# Option B: Apply patch to original repo
git clone https://github.com/MeiGen-AI/InfiniteTalk.git
cd InfiniteTalk
# Download and apply the patch file
wget https://raw.githubusercontent.com/YOUR_USERNAME/InfiniteTalk/fix-model-download-paths/issue-123-model-path-fix.patch
git apply issue-123-model-path-fix.patch
```

### 2. Run Test Script
```bash
chmod +x runpod_test.sh
./runpod_test.sh
```

### 3. Test Options
```bash
# Check what files are missing
python3 scripts/check_missing_files.py

# Download optimized (saves 5.6GB)
python3 scripts/download_models_optimized.py

# Test inference
python3 generate_infinitetalk.py --print_paths --input_json examples/single_example_image.json
```

## ✅ Expected Results

- Models download to `/workspace/models` (not local `weights/`)
- Environment detected as Runpod
- Only essential files downloaded
- Issue #123 confirmed fixed

## 🔧 Environment Variables

The fix automatically sets:
```bash
INFINITETALK_MODEL_DIR="/workspace/models"
COMFYUI_MODEL_DIR="/workspace/ComfyUI/models"  # if ComfyUI present
```