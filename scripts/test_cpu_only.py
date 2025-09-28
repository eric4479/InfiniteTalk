#!/usr/bin/env python3
"""
Local CPU-only test for InfiniteTalk model path configuration.

This script tests just the path management functionality without
requiring GPU dependencies like torch, transformers, etc.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_basic_dependencies():
    """Test that basic dependencies are available"""
    try:
        from config_manager import ModelPathManager
        from comfyui_handler import ComfyUIModelHandler
        print("✓ Core modules imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import core modules: {e}")
        return False

def test_local_cpu_setup():
    """Test local CPU setup with temporary directories"""
    print("\n=== LOCAL CPU TEST ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a temporary weights directory
        weights_dir = Path(temp_dir) / 'weights'
        print(f"Using temporary weights directory: {weights_dir}")
        
        # Initialize path manager
        from config_manager import ModelPathManager
        path_manager = ModelPathManager(base_model_dir=str(weights_dir))
        
        print("\nEnvironment Detection:")
        for env_type, detected in path_manager.env_info.items():
            status = "✓" if detected else "✗"
            print(f"  {status} {env_type}")
        
        print("\nModel Paths:")
        model_paths = path_manager.get_all_model_paths()
        for model_type, path in model_paths.items():
            print(f"  {model_type}: {path}")
        
        # Test directory creation
        print("\nTesting directory creation:")
        created_dirs = []
        for model_type in ['wan_base', 'wav2vec', 'infinitetalk']:
            dir_path = path_manager.ensure_model_directory(model_type)
            created_dirs.append(str(dir_path))
            exists = "✓" if dir_path.exists() else "✗"
            print(f"  {exists} {model_type}: {dir_path}")
        
        return True

def test_environment_variables():
    """Test environment variable handling"""
    print("\n=== ENVIRONMENT VARIABLES TEST ===")
    
    original_env = {
        'INFINITETALK_MODEL_DIR': os.environ.get('INFINITETALK_MODEL_DIR'),
        'COMFYUI_MODEL_DIR': os.environ.get('COMFYUI_MODEL_DIR')
    }
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set test environment variables
            test_model_dir = Path(temp_dir) / 'test_models'
            test_comfyui_dir = Path(temp_dir) / 'test_comfyui'
            
            os.environ['INFINITETALK_MODEL_DIR'] = str(test_model_dir)
            os.environ['COMFYUI_MODEL_DIR'] = str(test_comfyui_dir)
            
            from config_manager import ModelPathManager
            path_manager = ModelPathManager()
            
            print(f"Model dir from env: {path_manager.base_model_dir}")
            print(f"ComfyUI dir from env: {path_manager.comfyui_model_dir}")
            
            # Verify paths
            assert path_manager.base_model_dir == str(test_model_dir)
            assert path_manager.comfyui_model_dir == str(test_comfyui_dir)
            
            print("✓ Environment variables working correctly")
            return True
            
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

def test_download_script_without_hf():
    """Test download script functionality without huggingface_hub"""
    print("\n=== DOWNLOAD SCRIPT TEST (NO HF) ===")
    
    # Import download script
    download_script_path = Path(__file__).parent / 'download_models.py'
    sys.path.insert(0, str(download_script_path.parent))
    
    try:
        import download_models
        
        # Test model configuration
        models = download_models.get_models_to_download()
        print(f"Found {len(models)} models configured:")
        for model in models:
            required = "Required" if model['required'] else "Optional"
            print(f"  • {model['description']} ({required})")
            print(f"    Repo: {model['repo_id']}")
        
        # Test path checking
        with tempfile.TemporaryDirectory() as temp_dir:
            from config_manager import ModelPathManager
            path_manager = ModelPathManager(base_model_dir=temp_dir)
            
            existing = download_models.check_existing_models(path_manager)
            print(f"\nExisting models check: {existing}")
            
            # Create fake model files
            fake_wan_dir = path_manager.ensure_model_directory('wan_base')
            (fake_wan_dir / 'model.bin').touch()
            
            existing_after = download_models.check_existing_models(path_manager)
            print(f"After creating fake wan model: {existing_after}")
            
        print("✓ Download script configuration working")
        return True
        
    except Exception as e:
        print(f"✗ Download script test failed: {e}")
        return False

def test_comfyui_integration():
    """Test ComfyUI integration without ComfyUI installed"""
    print("\n=== COMFYUI INTEGRATION TEST ===")
    
    try:
        from comfyui_handler import ComfyUIModelHandler
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create fake ComfyUI structure
            comfyui_models = Path(temp_dir) / 'ComfyUI' / 'models'
            comfyui_models.mkdir(parents=True)
            
            handler = ComfyUIModelHandler(str(comfyui_models))
            
            # Test path generation
            paths = handler.create_node_paths()
            print("ComfyUI node paths:")
            for key, path in paths.items():
                print(f"  {key}: {path}")
            
            # Test configuration
            config = handler.get_comfyui_node_config()
            print(f"\nConfiguration keys: {list(config.keys())}")
            
            # Test validation (should fail since no models exist)
            validation = handler.validate_models()
            print(f"Model validation: {validation}")
            
            print("✓ ComfyUI integration working")
            return True
            
    except Exception as e:
        print(f"✗ ComfyUI integration test failed: {e}")
        return False

def test_minimal_generation_args():
    """Test that the enhanced argument parsing works"""
    print("\n=== ARGUMENT PARSING TEST ===")
    
    try:
        # We can't actually import generate_infinitetalk due to dependencies,
        # but we can test the path manager components it would use
        from config_manager import ModelPathManager
        
        # Simulate what the enhanced generate_infinitetalk.py would do
        test_args = {
            'model_base_dir': './test_weights',
            'comfyui_model_dir': None,
            'print_paths': True
        }
        
        path_manager = ModelPathManager(
            base_model_dir=test_args['model_base_dir'],
            comfyui_model_dir=test_args['comfyui_model_dir']
        )
        
        # Test path resolution like the enhanced app would do
        ckpt_dir = path_manager.get_model_path('wan_base')
        wav2vec_dir = path_manager.get_model_path('wav2vec')
        infinitetalk_dir = path_manager.get_model_path('infinitetalk', 'infinitetalk.safetensors')
        
        print("Simulated argument processing:")
        print(f"  --ckpt_dir would be: {ckpt_dir}")
        print(f"  --wav2vec_dir would be: {wav2vec_dir}")
        print(f"  --infinitetalk_dir would be: {infinitetalk_dir}")
        
        if test_args['print_paths']:
            print("\nWould print environment info:")
            path_manager.print_environment_info()
        
        print("✓ Argument parsing simulation working")
        return True
        
    except Exception as e:
        print(f"✗ Argument parsing test failed: {e}")
        return False

def main():
    """Run all CPU-only tests"""
    print("🧪 InfiniteTalk Model Path Configuration - CPU Only Test")
    print("=" * 60)
    
    tests = [
        ("Basic Dependencies", test_basic_dependencies),
        ("Local CPU Setup", test_local_cpu_setup),
        ("Environment Variables", test_environment_variables),
        ("Download Script Config", test_download_script_without_hf),
        ("ComfyUI Integration", test_comfyui_integration),
        ("Argument Parsing", test_minimal_generation_args),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔧 Running: {test_name}")
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All CPU-only tests passed! The path configuration is working correctly.")
        print("\n📋 Next steps:")
        print("   1. Install minimal dependencies: pip install huggingface_hub python-dotenv")
        print("   2. Test model downloads: python3 scripts/download_models.py --check-only")
        print("   3. For full testing: Install torch and other ML dependencies")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)