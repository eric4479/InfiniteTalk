#!/bin/bash
# Runpod Deployment Script for InfiniteTalk with Issue #123 fixes
# This script provides automated setup for Runpod environments

set -e  # Exit on any error

echo "🚀 InfiniteTalk Runpod Deployment Script"
echo "========================================"
echo "Setting up InfiniteTalk with Issue #123 fixes..."
echo

# Check if we're in the right environment
if [[ "$PWD" != *"/workspace"* ]] && [[ "$PWD" != *"/InfiniteTalk"* ]]; then
    echo "⚠️  Warning: Not in expected Runpod environment"
    echo "   Expected: /workspace or InfiniteTalk directory"
    echo "   Current: $PWD"
    echo "   Continuing anyway..."
fi

# Function to print status
print_status() {
    echo "📋 $1"
}

# Function to print success
print_success() {
    echo "✅ $1"
}

# Function to print error
print_error() {
    echo "❌ $1"
}

# Check Python version
print_status "Checking Python environment..."
python_version=$(python --version 2>&1 | cut -d' ' -f2)
echo "   Python version: $python_version"

# Check CUDA availability
if python -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>/dev/null; then
    gpu_name=$(python -c "import torch; print(torch.cuda.get_device_name() if torch.cuda.is_available() else 'None')" 2>/dev/null)
    echo "   GPU: $gpu_name"
else
    echo "   GPU: PyTorch not installed yet"
fi

# Install dependencies
print_status "Installing Python dependencies..."
if pip install -r requirements.txt --quiet; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Verify PyTorch installation
print_status "Verifying PyTorch installation..."
if python -c "import torch; print(f'PyTorch {torch.__version__} with CUDA {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')" 2>/dev/null; then
    print_success "PyTorch verification passed"
else
    print_error "PyTorch verification failed"
    exit 1
fi

# Test environment configuration
print_status "Testing environment configuration..."
if python -c "
from src.config_manager import ModelPathManager
manager = ModelPathManager()
print('Environment detected:')
for key, value in manager.env_info.items():
    if value:
        print(f'  ✓ {key}')
print(f'Model directory: {manager.base_model_dir}')
" 2>/dev/null; then
    print_success "Environment configuration verified"
else
    print_error "Environment configuration failed"
    exit 1
fi

# Check disk space
print_status "Checking available disk space..."
available_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
echo "   Available space: ${available_space}GB"

if (( $(echo "$available_space < 20" | bc -l) )); then
    print_error "Insufficient disk space (need 20GB+, have ${available_space}GB)"
    echo "   Consider using --skip-optional flag for model downloads"
else
    print_success "Sufficient disk space available"
fi

# Offer to download models and setup templates
echo
echo "🎯 Setup complete! Choose your next step:"
echo
echo "1. Download essential models + templates (~15.7GB)"
echo "   python scripts/download_complete_infinitetalk.py --skip-optional"
echo
echo "2. Download all models + LoRA + TTS (~16.1GB)" 
echo "   python scripts/download_complete_infinitetalk.py --include-lora"
echo
echo "3. Setup workflow templates only"
echo "   python scripts/download_complete_infinitetalk.py --setup-templates"
echo
echo "4. Check what files are missing"
echo "   python scripts/download_complete_infinitetalk.py --check-only"
echo
echo "5. Start Gradio interface (after models downloaded)"
echo "   python app.py --share --server-port 7860"
echo

# Ask user preference
read -p "Enter your choice (1-5) or press Enter to skip: " choice

case $choice in
    1)
        print_status "Downloading essential models and templates..."
        if python scripts/download_complete_infinitetalk.py --skip-optional; then
            print_success "Essential models and templates downloaded"
        else
            print_error "Model download failed"
            exit 1
        fi
        ;;
    2)
        print_status "Downloading all models including LoRA and TTS..."
        if python scripts/download_complete_infinitetalk.py --include-lora; then
            print_success "All models downloaded"
        else
            print_error "Model download failed"
            exit 1
        fi
        ;;
    3)
        print_status "Setting up workflow templates..."
        python scripts/download_complete_infinitetalk.py --setup-templates
        print_success "Templates setup complete"
        ;;
    4)
        print_status "Checking model and file status..."
        python scripts/download_complete_infinitetalk.py --check-only
        ;;
    5)
        print_status "Starting Gradio interface..."
        echo "   Interface will be available on port 7860"
        echo "   Press Ctrl+C to stop"
        python app.py --share --server-port 7860
        ;;
    *)
        echo "Setup complete! Run the commands above when ready."
        ;;
esac

echo
print_success "InfiniteTalk deployment complete!"
echo
echo "🔗 Quick commands:"
echo "   Test generation: python generate_infinitetalk.py --mode t2v --text 'test' --duration 30"
echo "   Start interface: python app.py --share --server-port 7860"
echo "   Check status: python scripts/test_runpod_basic.py"
echo
echo "📚 Full documentation: see RUNPOD_DEPLOYMENT.md"
echo "🐛 Issues or questions: https://github.com/eric4479/InfiniteTalk/issues"