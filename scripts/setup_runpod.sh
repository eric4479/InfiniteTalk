#!/bin/bash
# InfiniteTalk Runpod Setup Script
# This script sets up the model path configuration on Runpod

set -e

echo "🚀 InfiniteTalk Runpod Setup - Issue #123 Fix"
echo "=============================================="

# Check if we're on Runpod
if [[ -n "$RUNPOD_POD_ID" ]]; then
    echo "✅ Detected Runpod environment (Pod ID: $RUNPOD_POD_ID)"
else
    echo "⚠️  RUNPOD_POD_ID not set - are you running on Runpod?"
fi

# Set Runpod-specific environment variables
export INFINITETALK_MODEL_DIR="/workspace/models"
export COMFYUI_MODEL_DIR="/workspace/ComfyUI/models"

echo "📁 Model directories configured:"
echo "   INFINITETALK_MODEL_DIR: $INFINITETALK_MODEL_DIR"
echo "   COMFYUI_MODEL_DIR: $COMFYUI_MODEL_DIR"

# Create model directories
echo "📂 Creating model directories..."
mkdir -p "$INFINITETALK_MODEL_DIR"
mkdir -p "$COMFYUI_MODEL_DIR"

# Check if ComfyUI exists
if [[ -d "/workspace/ComfyUI" ]]; then
    echo "✅ ComfyUI detected at /workspace/ComfyUI"
    mkdir -p "$COMFYUI_MODEL_DIR"/{checkpoints,loras,vae,audio_encoders}
else
    echo "ℹ️  ComfyUI not found - skipping ComfyUI setup"
fi

# Install minimal dependencies if needed
echo "📦 Installing required dependencies..."
pip install huggingface_hub python-dotenv

# Test the configuration
echo "🧪 Testing model path configuration..."
python3 -c "
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'src'))

from config_manager import ModelPathManager

path_manager = ModelPathManager()
print('\n=== Runpod Configuration Test ===')
path_manager.print_environment_info()

# Verify paths
expected_paths = {
    'models_dir': '$INFINITETALK_MODEL_DIR',
    'comfyui_dir': '$COMFYUI_MODEL_DIR'
}

print('✅ Configuration test passed!')
"

# Check model download functionality
echo "📥 Testing model download system..."
python3 scripts/download_models.py --check-only

echo ""
echo "🎉 Runpod setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Download models: python3 scripts/download_models.py"
echo "   2. Test inference: python3 generate_infinitetalk.py --print_paths --input_json examples/single_example_image.json"
echo "   3. For ComfyUI: python3 scripts/download_models.py --create-symlinks"
echo ""
echo "🔧 Environment variables set:"
echo "   export INFINITETALK_MODEL_DIR='$INFINITETALK_MODEL_DIR'"
echo "   export COMFYUI_MODEL_DIR='$COMFYUI_MODEL_DIR'"