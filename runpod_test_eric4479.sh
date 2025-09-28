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
echo "📋 Ready to test! Run these commands:"
echo ""
echo "1. Download models (they'll go to /workspace/models):"
echo "   python3 scripts/download_models.py"
echo ""
echo "2. Check model paths:"
echo "   python3 scripts/download_models.py --check-only"
echo ""
echo "3. Test inference with path verification:"
echo "   python3 generate_infinitetalk.py --print_paths --input_json examples/single_example_image.json"
echo ""
echo "🎯 Expected: Models should download to /workspace/models instead of local weights/"
echo "   This confirms Issue #123 is fixed!"