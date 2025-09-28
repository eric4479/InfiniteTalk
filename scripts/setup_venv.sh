#!/bin/bash
# InfiniteTalk Virtual Environment Setup Script
# Provides multiple options for setting up the development environment

set -e

echo "🐍 InfiniteTalk Virtual Environment Setup"
echo "=========================================="
echo "This script helps you set up the optimal Python environment for InfiniteTalk"
echo

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

# Check current environment
print_status "Checking current Python environment..."
echo "   Current Python: $(python --version)"
echo "   Current Location: $(which python)"

# Check for conda
if command -v conda >/dev/null 2>&1; then
    echo "   Conda available: ✅"
    CONDA_AVAILABLE=true
else
    echo "   Conda available: ❌"
    CONDA_AVAILABLE=false
fi

# Check existing environments
if $CONDA_AVAILABLE; then
    print_status "Existing conda environments:"
    conda env list | grep -E "(multitalk|infinitetalk)" || echo "   No InfiniteTalk-related environments found"
fi

echo
echo "🎯 Environment Setup Options:"
echo
echo "1. Use existing 'multitalk' conda environment (recommended if available)"
echo "2. Create new conda environment 'infinitetalk-dev'"
echo "3. Create Python venv 'infinitetalk-venv'"
echo "4. Use current system Python (not recommended)"
echo "5. Check requirements only"
echo

read -p "Choose an option (1-5): " choice

case $choice in
    1)
        print_status "Using existing 'multitalk' conda environment..."
        
        if conda env list | grep -q "multitalk"; then
            print_success "Found existing 'multitalk' environment"
            
            # Activate and check
            source $HOME/miniconda3/etc/profile.d/conda.sh
            conda activate multitalk
            
            python_version=$(python --version)
            print_success "Activated multitalk environment: $python_version"
            
            # Check if requirements are installed
            print_status "Checking installed packages..."
            
            # Check key packages
            missing_packages=()
            
            for package in torch transformers diffusers accelerate opencv-python; do
                if ! python -c "import $package" 2>/dev/null; then
                    missing_packages+=($package)
                fi
            done
            
            if [ ${#missing_packages[@]} -eq 0 ]; then
                print_success "All key packages are installed!"
            else
                print_status "Missing packages: ${missing_packages[*]}"
                read -p "Install missing packages? (y/n): " install_missing
                if [[ $install_missing == "y" ]]; then
                    print_status "Installing missing requirements..."
                    pip install -r requirements.txt
                    print_success "Requirements installed"
                fi
            fi
            
            # Test InfiniteTalk imports
            print_status "Testing InfiniteTalk imports..."
            if python -c "from src.config_manager import ModelPathManager; print('✅ InfiniteTalk imports working')" 2>/dev/null; then
                print_success "InfiniteTalk modules can be imported"
            else
                print_status "InfiniteTalk modules need path setup"
            fi
            
        else
            print_error "multitalk environment not found"
            exit 1
        fi
        ;;
        
    2)
        print_status "Creating new conda environment 'infinitetalk-dev'..."
        
        if ! $CONDA_AVAILABLE; then
            print_error "Conda not available"
            exit 1
        fi
        
        # Create new environment
        conda create -n infinitetalk-dev python=3.10 -y
        
        # Activate new environment
        source $HOME/miniconda3/etc/profile.d/conda.sh
        conda activate infinitetalk-dev
        
        print_success "Created and activated infinitetalk-dev environment"
        
        # Install PyTorch with CUDA
        print_status "Installing PyTorch with CUDA support..."
        pip install torch==2.4.1 torchvision==0.19.1 torchaudio==2.4.1 --index-url https://download.pytorch.org/whl/cu121
        
        # Install xformers
        print_status "Installing xformers..."
        pip install -U xformers==0.0.28 --index-url https://download.pytorch.org/whl/cu121
        
        # Install other requirements
        print_status "Installing InfiniteTalk requirements..."
        pip install -r requirements.txt
        
        print_success "infinitetalk-dev environment setup complete!"
        ;;
        
    3)
        print_status "Creating Python venv 'infinitetalk-venv'..."
        
        # Create venv directory
        VENV_DIR="$HOME/.virtualenvs"
        mkdir -p "$VENV_DIR"
        
        # Create virtual environment
        python -m venv "$VENV_DIR/infinitetalk-venv"
        
        # Activate venv
        source "$VENV_DIR/infinitetalk-venv/bin/activate"
        
        print_success "Created and activated infinitetalk-venv"
        
        # Upgrade pip
        pip install --upgrade pip
        
        # Install requirements
        print_status "Installing requirements..."
        pip install -r requirements.txt
        
        print_success "infinitetalk-venv setup complete!"
        ;;
        
    4)
        print_status "Using current system Python..."
        print_status "Installing requirements to system Python..."
        
        read -p "This will install packages system-wide. Continue? (y/n): " confirm
        if [[ $confirm == "y" ]]; then
            pip install -r requirements.txt
            print_success "Requirements installed to system Python"
        else
            print_status "Installation cancelled"
            exit 0
        fi
        ;;
        
    5)
        print_status "Checking requirements only..."
        
        echo "📋 InfiniteTalk Requirements Analysis:"
        echo
        echo "Python Version: 3.10 (recommended)"
        echo "Current Python: $(python --version)"
        echo
        echo "Key Requirements from requirements.txt:"
        head -15 requirements.txt | while read line; do
            echo "  - $line"
        done
        echo "  ... and more"
        echo
        echo "Additional Requirements:"
        echo "  - PyTorch 2.4+ with CUDA support"
        echo "  - xformers for attention optimization"
        echo "  - flash-attention for performance"
        echo
        exit 0
        ;;
        
    *)
        print_error "Invalid option"
        exit 1
        ;;
esac

echo
print_success "Environment setup complete!"
echo
echo "🎯 Next steps:"
echo "1. Test the environment: python scripts/test_runpod_deployment.py"
echo "2. Download models: python scripts/download_complete_infinitetalk.py --skip-optional"
echo "3. Run InfiniteTalk: python generate_infinitetalk.py --help"
echo
echo "💡 To activate this environment in the future:"
if [[ $choice == 1 ]] || [[ $choice == 2 ]]; then
    echo "   conda activate $(conda info --envs | grep '*' | awk '{print $1}')"
elif [[ $choice == 3 ]]; then
    echo "   source $HOME/.virtualenvs/infinitetalk-venv/bin/activate"
fi
echo
echo "📚 Documentation:"
echo "   - Workflow guide: WORKFLOW_GUIDE.md"
echo "   - Runpod deployment: RUNPOD_DEPLOYMENT.md"
echo "   - Complete solution: WORKFLOW_SOLUTION.md"