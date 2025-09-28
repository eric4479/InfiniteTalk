# InfiniteTalk Model Path Configuration - Fix for Issue #123

This branch implements a comprehensive solution for model download and path configuration issues when running InfiniteTalk on different platforms (Runpod, GCP, local, ComfyUI).

## Problem Statement

**Issue #123**: When running ComfyUI, InfiniteTalk, or other custom nodes that require certain models, nodes, or files, example media files to download to the correct folder under models, or others, even if running on Runpod, GCP, or locally. When clicking "download model" it tries to save locally instead of the correct platform-specific location.

## Solution Overview

This implementation provides:

1. **Dynamic Model Path Configuration** - Automatically detects deployment environment and sets appropriate model paths
2. **Environment-Aware Setup** - Different configurations for local, Runpod, GCP, and ComfyUI environments  
3. **Unified Model Download System** - Single script to download all required models to correct locations
4. **ComfyUI Integration** - Seamless integration with ComfyUI custom nodes
5. **Backward Compatibility** - Works with existing configurations while adding new features

## Key Components

### 1. ModelPathManager (`src/config_manager.py`)
- Handles dynamic model path resolution across environments
- Auto-detects Runpod, GCP, Colab, and local environments
- Supports environment variables for configuration
- Manages model directory creation and validation

### 2. Model Download Script (`scripts/download_models.py`)
- Downloads all required models (Wan, Wav2Vec, InfiniteTalk, Kokoro)
- Environment-aware download locations
- Resume support for interrupted downloads
- Validation of existing models

### 3. ComfyUI Integration (`src/comfyui_handler.py`)
- ComfyUI-specific model path handling
- Symlink creation for ComfyUI compatibility
- Node configuration generation
- Model validation for ComfyUI nodes

### 4. Enhanced Application (`generate_infinitetalk.py`)
- Updated to use flexible model paths
- New command-line arguments for model directories
- Environment detection and path printing
- Backward compatible with existing usage

## Usage Examples

### Local Development
```bash
# Use default paths
python3 generate_infinitetalk.py --input_json examples/single_example_image.json

# Custom model directory
python3 generate_infinitetalk.py \
    --model_base_dir ./my_models \
    --input_json examples/single_example_image.json
```

### Runpod Deployment
```bash
# Set environment variables
export INFINITETALK_MODEL_DIR="/workspace/models"
export COMFYUI_MODEL_DIR="/workspace/ComfyUI/models"

# Download models to correct locations
python3 scripts/download_models.py

# Run inference
python3 generate_infinitetalk.py \
    --print_paths \
    --input_json examples/single_example_image.json
```

### ComfyUI Integration
```bash
# Download models and create ComfyUI symlinks
python3 scripts/download_models.py --create-symlinks

# Check model paths for ComfyUI
python3 -c "from src.comfyui_handler import ComfyUIModelHandler; ComfyUIModelHandler().print_comfyui_info()"
```

## Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Basic configuration
INFINITETALK_MODEL_DIR=/workspace/models
COMFYUI_MODEL_DIR=/workspace/ComfyUI/models

# For Runpod
INFINITETALK_MODEL_DIR=/workspace/models
COMFYUI_MODEL_DIR=/workspace/ComfyUI/models

# For local development  
INFINITETALK_MODEL_DIR=./weights
```

## Command Line Options

### Model Download Script
```bash
python3 scripts/download_models.py [OPTIONS]

Options:
  --model-base-dir PATH     Base directory for models
  --comfyui-model-dir PATH  ComfyUI models directory
  --force                   Force download even if models exist
  --skip-optional           Skip optional models (like TTS)
  --check-only              Only check which models exist
  --create-symlinks         Create ComfyUI-compatible symlinks
```

### Main Application
```bash
python3 generate_infinitetalk.py [OPTIONS]

New options:
  --model_base_dir PATH      Base directory for all models
  --comfyui_model_dir PATH   ComfyUI models directory  
  --print_paths              Print detected paths before generation
```

## Testing

Run the comprehensive test suite:

```bash
python3 scripts/test_model_paths.py
```

Tests cover:
- Local environment configuration
- Runpod environment simulation
- ComfyUI integration
- Environment variable handling
- Model download simulation

## Benefits

1. **Platform Agnostic**: Works seamlessly across local, Runpod, GCP, and ComfyUI
2. **Automatic Detection**: No manual configuration needed in most cases
3. **Flexible Configuration**: Override any path via environment variables or CLI
4. **Backward Compatible**: Existing workflows continue to work
5. **Easy Deployment**: Single script downloads all required models
6. **ComfyUI Ready**: Full integration with ComfyUI custom nodes

## Migration Guide

### Existing Users
No changes required - existing code continues to work with default `./weights` directory.

### Runpod Users
```bash
# Set environment variable
export INFINITETALK_MODEL_DIR="/workspace/models"

# Download models
python3 scripts/download_models.py

# Use as normal
python3 generate_infinitetalk.py --input_json examples/single_example_image.json
```

### ComfyUI Node Developers
```python
from src.comfyui_handler import ComfyUIModelHandler

handler = ComfyUIModelHandler()
model_paths = handler.create_node_paths()

# Use model_paths['wan_checkpoint'], etc. in your nodes
```

## Dependencies

Added to `requirements.txt`:
- `huggingface_hub>=0.19.0` - For model downloads
- `python-dotenv>=1.0.0` - For .env file support

## File Structure

```
InfiniteTalk/
├── src/
│   ├── config_manager.py      # Model path management
│   └── comfyui_handler.py     # ComfyUI integration
├── scripts/
│   ├── download_models.py     # Unified model downloader
│   └── test_model_paths.py    # Test suite
├── .env.example               # Environment configuration template
├── requirements.txt           # Updated dependencies
└── generate_infinitetalk.py   # Enhanced main application
```

This solution completely addresses Issue #123 by providing flexible, environment-aware model path management that works across all deployment scenarios.