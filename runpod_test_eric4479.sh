#!/bin/bash
# Runpod Test Script for eric4479/InfiniteTalk Issue #123 Fix

echo "🚀 InfiniteTalk Issue #123 Fix - Runpod Test"
echo "Repository: https://github.com/eric4479/InfiniteTalk"
echo "Branch: fix-model-download-paths"
echo "============================================="

# Step 1: Clone your fork
if [[ ! -d "InfiniteTalk" ]]; then
    echo "📥 Cloning eric4479/InfiniteTalk..."
    git clone https://github.com/eric4479/InfiniteTalk.git
    cd InfiniteTalk
else
    echo "📁 InfiniteTalk directory already exists"
    cd InfiniteTalk
fi

# Step 2: Checkout the fix branch
echo "🔄 Switching to fix-model-download-paths branch..."
git checkout fix-model-download-paths

# Step 3: Verify we have the fix files
echo "🔍 Verifying fix files are present..."
REQUIRED_FILES=(
    "src/config_manager.py"
    "src/comfyui_handler.py"
    "scripts/download_models.py"
    "scripts/setup_runpod.sh"
    "scripts/universal_setup.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file - MISSING!"
        exit 1
    fi
done

# Step 4: Run the setup
echo "🔧 Running Runpod setup..."
chmod +x scripts/setup_runpod.sh
./scripts/setup_runpod.sh

echo ""
echo "🎉 Setup Complete!"
echo "================="
echo ""
echo "📋 Testing Options:"
echo ""
echo "🔍 1. Check what files are missing:"
echo "   python3 scripts/check_missing_files.py"
echo ""
echo "📥 2. Download only essential files (RECOMMENDED - saves 5.6GB):"
echo "   python3 scripts/download_models_optimized.py --estimate-size  # See sizes first"
echo "   python3 scripts/download_models_optimized.py                 # Download optimized"
echo ""
echo "📥 3. Or use original downloader (downloads more):"
echo "   python3 scripts/download_models.py"
echo ""
echo "✅ 4. Test inference with path verification:"
echo "   python3 generate_infinitetalk.py --print_paths --input_json examples/single_example_image.json"
echo ""
echo "🎯 Expected Results:"
echo "   ✅ Models download to /workspace/models (not local weights/)"
echo "   ✅ Environment detected as Runpod"
echo "   ✅ Only essential files downloaded (~16GB vs ~22GB)"
echo "   ✅ Issue #123 confirmed fixed!"