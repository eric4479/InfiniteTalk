# Runpod Testing Guide - InfiniteTalk Model Path Fix

This guide provides step-by-step instructions for testing the Issue #123 fix on Runpod.

## 🚀 Quick Start on Runpod

### 1. Clone and Setup

```bash
# Clone the repository with the fix
git clone https://github.com/MeiGen-AI/InfiniteTalk.git
cd InfiniteTalk

# Switch to the fix branch
git checkout fix-model-download-paths

# Run the automated setup script
./scripts/setup_runpod.sh
```

### 2. Download Models

```bash
# Download all required models to /workspace/models
python3 scripts/download_models.py

# Check what was downloaded
python3 scripts/download_models.py --check-only
```

### 3. Test Inference

```bash
# Test with path printing to verify configuration
python3 generate_infinitetalk.py \
    --print_paths \
    --input_json examples/single_example_image.json
```

## 🔧 Manual Setup (Alternative)

If you prefer manual setup:

### Step 1: Environment Variables

```bash
export INFINITETALK_MODEL_DIR="/workspace/models"
export COMFYUI_MODEL_DIR="/workspace/ComfyUI/models"
```

### Step 2: Install Dependencies

```bash
pip install huggingface_hub python-dotenv
```

### Step 3: Create Directories

```bash
mkdir -p /workspace/models
mkdir -p /workspace/ComfyUI/models
```

## 🧪 Testing Scenarios

### Scenario 1: Basic Model Download Test

```bash
# Test that models download to correct location
python3 scripts/download_models.py --model-base-dir /workspace/models

# Verify they went to the right place
ls -la /workspace/models/
```

### Scenario 2: Environment Detection Test

```bash
# Should detect Runpod environment automatically
python3 -c "
from src.config_manager import ModelPathManager
pm = ModelPathManager()
pm.print_environment_info()
print('Runpod detected:', pm.env_info['is_runpod'])
"
```

### Scenario 3: ComfyUI Integration Test

```bash
# If ComfyUI is installed
python3 scripts/download_models.py --create-symlinks

# Check ComfyUI integration
python3 -c "
from src.comfyui_handler import ComfyUIModelHandler
handler = ComfyUIModelHandler()
handler.print_comfyui_info()
"
```

### Scenario 4: Full Inference Test

```bash
# Create a test input file
cat > test_input.json << 'EOF'
{
    "prompt": "A person talking",
    "cond_video": "examples/example_image.jpg",
    "cond_audio": {
        "person1": "examples/example_audio.wav"
    },
    "audio_type": "single"
}
EOF

# Test inference with new path system
python3 generate_infinitetalk.py \
    --input_json test_input.json \
    --print_paths \
    --frame_num 25
```

## 🎯 Expected Results

### ✅ What Should Work

1. **Environment Detection**:
   ```
   Environment detection:
   ✓ is_runpod: True
   ✗ is_local: False
   ```

2. **Model Paths**:
   ```
   Model paths:
   ✓ wan_base: /workspace/models/Wan2.1-I2V-14B-480P
   ✓ wav2vec: /workspace/models/chinese-wav2vec2-base
   ✓ infinitetalk: /workspace/models/InfiniteTalk/single
   ```

3. **Downloads**: Models should download to `/workspace/models/` instead of local `weights/`

4. **ComfyUI**: If ComfyUI is present, some models should map to `/workspace/ComfyUI/models/`

### ❌ What Would Fail Without the Fix

Without our fix, you would see:
- Models downloading to local `weights/` directory
- Inference failing because models aren't where expected
- Manual path specification required for every run

## 🔍 Debugging Commands

### Check Environment Variables
```bash
echo "INFINITETALK_MODEL_DIR: $INFINITETALK_MODEL_DIR"
echo "COMFYUI_MODEL_DIR: $COMFYUI_MODEL_DIR"
echo "RUNPOD_POD_ID: $RUNPOD_POD_ID"
```

### Check Directory Structure
```bash
ls -la /workspace/models/
ls -la /workspace/ComfyUI/models/ 2>/dev/null || echo "ComfyUI not found"
```

### Test Model Path Manager
```bash
python3 -c "
from src.config_manager import ModelPathManager
pm = ModelPathManager()
print('Base dir:', pm.base_model_dir)
print('ComfyUI dir:', pm.comfyui_model_dir)
print('All paths:', pm.get_all_model_paths())
"
```

### Test Download Script
```bash
# Test without actually downloading
python3 scripts/download_models.py --check-only --model-base-dir /workspace/models
```

## 🚨 Common Issues and Solutions

### Issue 1: Models Still Download Locally
**Cause**: Environment variables not set
**Solution**: 
```bash
export INFINITETALK_MODEL_DIR="/workspace/models"
# Or use the setup script
./scripts/setup_runpod.sh
```

### Issue 2: Permission Errors
**Cause**: Directory permissions on /workspace
**Solution**:
```bash
sudo mkdir -p /workspace/models
sudo chown $USER:$USER /workspace/models
```

### Issue 3: HuggingFace Hub Errors
**Cause**: Network or authentication issues
**Solution**:
```bash
pip install --upgrade huggingface_hub
# Or set HF token if needed
export HF_TOKEN="your_token_here"
```

### Issue 4: ComfyUI Not Detected
**Cause**: ComfyUI not installed or in different location
**Solution**:
```bash
# Check if ComfyUI exists
ls -la /workspace/ComfyUI/
# Or set manually
export COMFYUI_MODEL_DIR="/path/to/your/comfyui/models"
```

## 📊 Success Criteria

The fix is working correctly if:

1. ✅ Environment automatically detects Runpod (`is_runpod: True`)
2. ✅ Models download to `/workspace/models/` by default
3. ✅ No manual path specification needed
4. ✅ ComfyUI integration works if ComfyUI is present
5. ✅ Backward compatibility maintained (old arguments still work)
6. ✅ `--print_paths` shows correct Runpod-specific paths

## 🎉 After Testing

If the tests pass, this confirms that Issue #123 is resolved and the solution works correctly on Runpod. The branch is ready for merge into main.

## 📞 Support

If you encounter issues during testing:

1. Check the [MODEL_PATH_FIX.md](../MODEL_PATH_FIX.md) documentation
2. Run the debugging commands above
3. Check that you're on the `fix-model-download-paths` branch
4. Verify that the setup script completed successfully