#!/bin/bash
# One-line InfiniteTalk deployment for Runpod
# Usage: curl -sSL https://raw.githubusercontent.com/eric4479/InfiniteTalk/fix-model-download-paths/runpod_quick_deploy.sh | bash

set -e

echo "🚀 InfiniteTalk Quick Deploy for Runpod"
echo "======================================"
echo

# Navigate to workspace
cd /workspace

# Clone repository if not exists
if [ ! -d "InfiniteTalk" ]; then
    echo "📥 Cloning InfiniteTalk repository..."
    git clone https://github.com/eric4479/InfiniteTalk.git
else
    echo "📁 InfiniteTalk directory already exists"
fi

# Enter directory and checkout fix branch
cd InfiniteTalk
echo "🔀 Switching to fix branch..."
git checkout fix-model-download-paths

# Run the setup script
echo "⚙️ Running setup script..."
bash scripts/setup_runpod.sh

echo "🎉 Quick deployment complete!"
echo "📚 See RUNPOD_DEPLOYMENT.md for full documentation"