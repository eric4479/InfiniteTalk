#!/bin/bash
# Universal setup script for testing Issue #123 fix on Runpod

echo "🚀 InfiniteTalk Issue #123 Fix - Universal Setup"
echo "==============================================="

# Check if we're in the right directory
if [[ ! -f "generate_infinitetalk.py" ]]; then
    echo "❌ Error: Please run this from the InfiniteTalk root directory"
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📋 Current branch: $CURRENT_BRANCH"

# Method detection
if [[ "$CURRENT_BRANCH" == "fix-model-download-paths" ]]; then
    echo "✅ Already on fix-model-download-paths branch"
elif git show-ref --verify --quiet refs/heads/fix-model-download-paths; then
    echo "🔄 Switching to fix-model-download-paths branch"
    git checkout fix-model-download-paths
elif git show-ref --verify --quiet refs/remotes/origin/fix-model-download-paths; then
    echo "🔄 Checking out fix-model-download-paths from origin"
    git checkout -b fix-model-download-paths origin/fix-model-download-paths
else
    echo "⚠️  fix-model-download-paths branch not found"
    echo "📝 Available options:"
    echo "   1. Use existing fixes if files are present"
    echo "   2. Apply patch file if available"
    echo "   3. Set up fork (see FORK_SETUP_GUIDE.md)"
    
    # Check if key files exist
    if [[ -f "src/config_manager.py" && -f "scripts/download_models.py" ]]; then
        echo "✅ Key fix files found - proceeding with current state"
    elif [[ -f "issue-123-model-path-fix.patch" ]]; then
        echo "📥 Patch file found - applying fixes"
        git apply issue-123-model-path-fix.patch
        echo "✅ Patch applied successfully"
    else
        echo "❌ No fixes found. Please follow FORK_SETUP_GUIDE.md"
        exit 1
    fi
fi

# Set up Runpod environment
echo "🔧 Setting up Runpod environment..."

# Check if we're on Runpod
if [[ -n "$RUNPOD_POD_ID" ]]; then
    echo "✅ Runpod environment detected"
    export INFINITETALK_MODEL_DIR="/workspace/models"
    export COMFYUI_MODEL_DIR="/workspace/ComfyUI/models"
else
    echo "⚠️  Not on Runpod - using test environment"
    export INFINITETALK_MODEL_DIR="./test_models"
    export COMFYUI_MODEL_DIR="./test_comfyui/models"
fi

echo "📁 Model directories:"
echo "   INFINITETALK_MODEL_DIR: $INFINITETALK_MODEL_DIR"
echo "   COMFYUI_MODEL_DIR: $COMFYUI_MODEL_DIR"

# Create directories
echo "📂 Creating model directories..."
mkdir -p "$INFINITETALK_MODEL_DIR"
if [[ -n "$COMFYUI_MODEL_DIR" ]]; then
    mkdir -p "$COMFYUI_MODEL_DIR"/{checkpoints,loras,vae,audio_encoders}
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install huggingface_hub python-dotenv

# Test configuration
echo "🧪 Testing configuration..."
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

try:
    from config_manager import ModelPathManager
    pm = ModelPathManager()
    print('✅ Configuration loaded successfully')
    print(f'   Environment: {[k for k,v in pm.env_info.items() if v]}')
    print(f'   Model dir: {pm.base_model_dir}')
    print(f'   ComfyUI dir: {pm.comfyui_model_dir}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Download models: python3 scripts/download_models.py"
echo "   2. Test paths: python3 scripts/download_models.py --check-only"
echo "   3. Run inference: python3 generate_infinitetalk.py --print_paths --input_json examples/..."
echo ""
echo "🔧 Environment variables set:"
echo "   export INFINITETALK_MODEL_DIR='$INFINITETALK_MODEL_DIR'"
echo "   export COMFYUI_MODEL_DIR='$COMFYUI_MODEL_DIR'"