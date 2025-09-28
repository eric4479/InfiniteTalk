#!/usr/bin/env python3
"""
Demonstration script for InfiniteTalk Model Path Configuration.

This script shows how the new model path configuration works
across different deployment environments without requiring
the full InfiniteTalk dependencies.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_manager import ModelPathManager
from comfyui_handler import ComfyUIModelHandler


def demo_local_setup():
    """Demonstrate local development setup"""
    print("🏠 LOCAL DEVELOPMENT SETUP")
    print("-" * 40)
    
    # Default local setup
    path_manager = ModelPathManager()
    path_manager.print_environment_info()
    
    print("Command to run:")
    print("python3 generate_infinitetalk.py --input_json examples/single_example_image.json")
    print()


def demo_runpod_setup():
    """Demonstrate Runpod setup"""
    print("☁️  RUNPOD DEPLOYMENT SETUP") 
    print("-" * 40)
    
    # Simulate Runpod environment
    original_env = os.environ.get('RUNPOD_POD_ID')
    os.environ['RUNPOD_POD_ID'] = 'demo-pod-123'
    os.environ['INFINITETALK_MODEL_DIR'] = '/workspace/models'
    
    try:
        path_manager = ModelPathManager()
        path_manager.print_environment_info()
        
        print("Setup commands for Runpod:")
        print("export INFINITETALK_MODEL_DIR='/workspace/models'")
        print("python3 scripts/download_models.py")
        print("python3 generate_infinitetalk.py --print_paths --input_json examples/single_example_image.json")
        print()
        
    finally:
        # Clean up environment
        if original_env:
            os.environ['RUNPOD_POD_ID'] = original_env
        else:
            os.environ.pop('RUNPOD_POD_ID', None)
        os.environ.pop('INFINITETALK_MODEL_DIR', None)


def demo_comfyui_setup():
    """Demonstrate ComfyUI integration"""
    print("🎨 COMFYUI INTEGRATION SETUP")
    print("-" * 40)
    
    # Simulate ComfyUI environment
    os.environ['COMFYUI_MODEL_DIR'] = '/workspace/ComfyUI/models'
    os.environ['INFINITETALK_MODEL_DIR'] = '/workspace/models'
    
    try:
        # Create ComfyUI handler
        handler = ComfyUIModelHandler()
        handler.print_comfyui_info()
        
        print("Setup commands for ComfyUI:")
        print("export INFINITETALK_MODEL_DIR='/workspace/models'")
        print("export COMFYUI_MODEL_DIR='/workspace/ComfyUI/models'")
        print("python3 scripts/download_models.py --create-symlinks")
        print()
        
        # Show node configuration
        config = handler.get_comfyui_node_config()
        print("Node configuration for custom nodes:")
        for key, value in config['model_paths'].items():
            print(f"  {key}: {value}")
        print()
        
    finally:
        os.environ.pop('COMFYUI_MODEL_DIR', None)
        os.environ.pop('INFINITETALK_MODEL_DIR', None)


def demo_download_script():
    """Demonstrate model download script"""
    print("📥 MODEL DOWNLOAD SCRIPT")
    print("-" * 40)
    
    # Import download script functions
    download_script_path = Path(__file__).parent.parent / 'scripts' / 'download_models.py'
    sys.path.insert(0, str(download_script_path.parent))
    
    try:
        import download_models
        
        models = download_models.get_models_to_download()
        print("Models that will be downloaded:")
        for model in models:
            required = "✓" if model['required'] else "○"
            print(f"  {required} {model['description']}")
            print(f"    Repository: {model['repo_id']}")
        print()
        
        print("Download commands:")
        print("# Check existing models")
        print("python3 scripts/download_models.py --check-only")
        print()
        print("# Download all models")
        print("python3 scripts/download_models.py")
        print()
        print("# Download with ComfyUI symlinks")
        print("python3 scripts/download_models.py --create-symlinks")
        print()
        
    except ImportError as e:
        print(f"Could not import download script: {e}")


def demo_environment_detection():
    """Demonstrate environment detection"""
    print("🔍 ENVIRONMENT DETECTION")
    print("-" * 40)
    
    # Test different environment variables
    environments = [
        ("Local Development", {}),
        ("Runpod", {"RUNPOD_POD_ID": "test-pod"}),
        ("Google Colab", {"COLAB_GPU": "0"}),
        ("GCP", {"GOOGLE_CLOUD_PROJECT": "my-project"}),
    ]
    
    original_env = {k: os.environ.get(k) for k in ['RUNPOD_POD_ID', 'COLAB_GPU', 'GOOGLE_CLOUD_PROJECT']}
    
    for env_name, env_vars in environments:
        # Clean environment
        for key in original_env.keys():
            os.environ.pop(key, None)
        
        # Set test environment
        for key, value in env_vars.items():
            os.environ[key] = value
        
        try:
            path_manager = ModelPathManager()
            print(f"{env_name}:")
            for env_type, detected in path_manager.env_info.items():
                if detected:
                    print(f"  ✓ {env_type}")
            print()
        finally:
            # Clean up
            for key in env_vars.keys():
                os.environ.pop(key, None)
    
    # Restore original environment
    for key, value in original_env.items():
        if value is not None:
            os.environ[key] = value


def main():
    """Run all demonstrations"""
    print("🚀 InfiniteTalk Model Path Configuration Demo")
    print("=" * 50)
    print()
    
    demo_environment_detection()
    demo_local_setup()
    demo_runpod_setup() 
    demo_comfyui_setup()
    demo_download_script()
    
    print("=" * 50)
    print("✅ This implementation solves Issue #123 by providing:")
    print("   • Automatic environment detection")
    print("   • Platform-specific model paths")
    print("   • Unified model download system")
    print("   • ComfyUI integration support")
    print("   • Backward compatibility")
    print()
    print("📖 See MODEL_PATH_FIX.md for complete documentation")


if __name__ == '__main__':
    main()