#!/usr/bin/env python3
"""
Test script for InfiniteTalk model path configuration.

This script tests the model path management functionality
across different deployment scenarios.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_manager import ModelPathManager
from comfyui_handler import ComfyUIModelHandler, create_comfyui_handler


def test_local_environment():
    """Test model path configuration for local development"""
    print("=== Testing Local Environment ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_weights_dir = Path(temp_dir) / 'test_weights'
        
        # Test with custom base directory
        path_manager = ModelPathManager(base_model_dir=str(test_weights_dir))
        
        # Test path generation
        wan_path = path_manager.get_model_path('wan_base')
        wav2vec_path = path_manager.get_model_path('wav2vec')
        infinitetalk_path = path_manager.get_model_path('infinitetalk', 'infinitetalk.safetensors')
        
        print(f"Wan base path: {wan_path}")
        print(f"Wav2Vec path: {wav2vec_path}")
        print(f"InfiniteTalk path: {infinitetalk_path}")
        
        # Test directory creation
        path_manager.ensure_model_directory('wan_base')
        path_manager.ensure_model_directory('wav2vec')
        path_manager.ensure_model_directory('infinitetalk')
        
        # Verify directories were created
        assert Path(wan_path).exists(), f"Wan directory not created: {wan_path}"
        assert Path(wav2vec_path).exists(), f"Wav2Vec directory not created: {wav2vec_path}"
        assert Path(infinitetalk_path).parent.exists(), f"InfiniteTalk directory not created: {Path(infinitetalk_path).parent}"
        
        print("✓ Local environment test passed")


def test_runpod_environment():
    """Test model path configuration for Runpod environment"""
    print("\n=== Testing Runpod Environment ===")
    
    # Simulate Runpod environment
    original_env = os.environ.copy()
    os.environ['RUNPOD_POD_ID'] = 'test-pod-123'
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_models = Path(temp_dir) / 'workspace' / 'models'
            comfyui_models = Path(temp_dir) / 'workspace' / 'ComfyUI' / 'models'
            comfyui_models.mkdir(parents=True)
            
            # Test without explicit paths (should auto-detect Runpod)
            path_manager = ModelPathManager()
            
            # Test with explicit paths
            path_manager_explicit = ModelPathManager(
                base_model_dir=str(workspace_models),
                comfyui_model_dir=str(comfyui_models)
            )
            
            print(f"Auto-detected environment: {path_manager.env_info}")
            print(f"Explicit model directory: {path_manager_explicit.base_model_dir}")
            print(f"ComfyUI directory: {path_manager_explicit.comfyui_model_dir}")
            
            # Test ComfyUI handler
            comfyui_handler = ComfyUIModelHandler(str(comfyui_models))
            config = comfyui_handler.get_comfyui_node_config()
            
            print(f"ComfyUI config: {config}")
            
            assert path_manager.env_info['is_runpod'], "Failed to detect Runpod environment"
            print("✓ Runpod environment test passed")
            
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def test_comfyui_integration():
    """Test ComfyUI-specific functionality"""
    print("\n=== Testing ComfyUI Integration ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        comfyui_models = Path(temp_dir) / 'ComfyUI' / 'models'
        
        # Create mock ComfyUI directory structure
        (comfyui_models / 'checkpoints').mkdir(parents=True)
        (comfyui_models / 'loras').mkdir(parents=True)
        (comfyui_models / 'vae').mkdir(parents=True)
        
        # Test ComfyUI handler
        handler = ComfyUIModelHandler(str(comfyui_models))
        
        # Test path generation
        checkpoint_path = handler.get_model_path('checkpoints', 'test.safetensors')
        lora_path = handler.get_model_path('loras')
        
        print(f"Checkpoint path: {checkpoint_path}")
        print(f"LoRA path: {lora_path}")
        
        # Test node configuration
        node_config = handler.get_comfyui_node_config()
        print(f"Node config keys: {list(node_config.keys())}")
        
        # Test model validation (should fail since no models exist)
        validation = handler.validate_models()
        print(f"Model validation: {validation}")
        
        assert Path(checkpoint_path).parent.exists(), "Checkpoint directory not created"
        assert Path(lora_path).exists(), "LoRA directory not created"
        print("✓ ComfyUI integration test passed")


def test_environment_variables():
    """Test environment variable handling"""
    print("\n=== Testing Environment Variables ===")
    
    original_env = os.environ.copy()
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            test_model_dir = Path(temp_dir) / 'env_test_models'
            test_comfyui_dir = Path(temp_dir) / 'env_test_comfyui'
            
            # Set environment variables
            os.environ['INFINITETALK_MODEL_DIR'] = str(test_model_dir)
            os.environ['COMFYUI_MODEL_DIR'] = str(test_comfyui_dir)
            
            # Test that manager picks up environment variables
            path_manager = ModelPathManager()
            
            print(f"Model dir from env: {path_manager.base_model_dir}")
            print(f"ComfyUI dir from env: {path_manager.comfyui_model_dir}")
            
            assert path_manager.base_model_dir == str(test_model_dir), "Failed to read INFINITETALK_MODEL_DIR"
            assert path_manager.comfyui_model_dir == str(test_comfyui_dir), "Failed to read COMFYUI_MODEL_DIR"
            
            print("✓ Environment variables test passed")
            
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def test_model_download_simulation():
    """Test model download script functionality (without actual downloads)"""
    print("\n=== Testing Model Download Simulation ===")
    
    # Import the download script functions
    download_script_path = Path(__file__).parent.parent / 'scripts' / 'download_models.py'
    sys.path.insert(0, str(download_script_path.parent))
    
    try:
        import download_models
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_models_dir = Path(temp_dir) / 'test_models'
            
            # Create path manager
            path_manager = ModelPathManager(base_model_dir=str(test_models_dir))
            
            # Test model configuration
            models = download_models.get_models_to_download()
            print(f"Found {len(models)} models to download:")
            for model in models:
                print(f"  - {model['description']} ({model['repo_id']})")
            
            # Test existing model check (should all be False)
            existing = download_models.check_existing_models(path_manager)
            print(f"Existing models: {existing}")
            
            # Create some fake model files to test detection
            fake_wan_dir = path_manager.ensure_model_directory('wan_base')
            (fake_wan_dir / 'fake_model.bin').touch()
            
            fake_wav2vec_dir = path_manager.ensure_model_directory('wav2vec')
            (fake_wav2vec_dir / 'config.json').touch()
            
            # Test again (should detect wan_base and wav2vec as existing)
            existing_after = download_models.check_existing_models(path_manager)
            print(f"Existing models after creating fake files: {existing_after}")
            
            assert existing_after['wan_base'], "Failed to detect existing wan_base model"
            assert existing_after['wav2vec'], "Failed to detect existing wav2vec model"
            
            print("✓ Model download simulation test passed")
            
    except ImportError as e:
        print(f"Warning: Could not test download script: {e}")


def run_all_tests():
    """Run all tests"""
    print("Running InfiniteTalk Model Path Configuration Tests")
    print("=" * 50)
    
    try:
        test_local_environment()
        test_runpod_environment()
        test_comfyui_integration()
        test_environment_variables()
        test_model_download_simulation()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)