#!/usr/bin/env python3
"""
Simple Runpod simulation test that doesn't require external dependencies.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_runpod_basics():
    """Test basic Runpod functionality without external dependencies"""
    
    print("🧪 BASIC RUNPOD SIMULATION TEST")
    print("=" * 50)
    
    temp_workspace = None
    
    try:
        # Create temporary workspace
        temp_workspace = Path(tempfile.mkdtemp(prefix='runpod_test_'))
        workspace_models = temp_workspace / 'workspace' / 'models'
        workspace_comfyui = temp_workspace / 'workspace' / 'ComfyUI' / 'models'
        
        workspace_models.mkdir(parents=True, exist_ok=True)
        workspace_comfyui.mkdir(parents=True, exist_ok=True)
        
        # Set Runpod environment
        os.environ['RUNPOD_POD_ID'] = 'test-pod-123'
        os.environ['INFINITETALK_MODEL_DIR'] = str(workspace_models)
        os.environ['COMFYUI_MODEL_DIR'] = str(workspace_comfyui)
        
        print(f"✅ Created test workspace: {temp_workspace}")
        
        # Test 1: Environment Detection
        print("\n1. Testing Environment Detection:")
        from config_manager import ModelPathManager
        
        path_manager = ModelPathManager()
        print(f"   Runpod detected: {path_manager.env_info['is_runpod']}")
        print(f"   Local detected: {path_manager.env_info['is_local']}")
        print(f"   ComfyUI detected: {path_manager.env_info['has_comfyui']}")
        
        assert path_manager.env_info['is_runpod'], "Should detect Runpod"
        assert not path_manager.env_info['is_local'], "Should not detect local"
        assert path_manager.env_info['has_comfyui'], "Should detect ComfyUI"
        print("✅ Environment detection working!")
        
        # Test 2: Model Paths
        print("\n2. Testing Model Paths:")
        wan_path = path_manager.get_model_path('wan_base')
        wav2vec_path = path_manager.get_model_path('wav2vec')
        lora_path = path_manager.get_model_path('loras')  # Should go to ComfyUI
        
        print(f"   Wan path: {wan_path}")
        print(f"   Wav2Vec path: {wav2vec_path}")
        print(f"   LoRA path: {lora_path}")
        
        assert '/workspace/models' in wan_path, f"Wan should be in workspace: {wan_path}"
        assert '/workspace/models' in wav2vec_path, f"Wav2Vec should be in workspace: {wav2vec_path}"
        assert '/workspace/ComfyUI/models' in lora_path, f"LoRA should be in ComfyUI: {lora_path}"
        print("✅ Model paths correctly configured!")
        
        # Test 3: Directory Creation
        print("\n3. Testing Directory Creation:")
        for model_type in ['wan_base', 'wav2vec', 'loras']:
            dir_path = path_manager.ensure_model_directory(model_type)
            assert dir_path.exists(), f"Directory not created: {dir_path}"
            print(f"   ✅ Created: {dir_path}")
        
        # Test 4: ComfyUI Integration
        print("\n4. Testing ComfyUI Integration:")
        from comfyui_handler import ComfyUIModelHandler
        
        handler = ComfyUIModelHandler()
        node_paths = handler.create_node_paths()
        
        print("   ComfyUI node paths:")
        for key, path in node_paths.items():
            print(f"     {key}: {path}")
            if 'comfyui' in key.lower() or key in ['lora_dir', 'vae_dir']:
                assert '/workspace/ComfyUI/models' in path, f"ComfyUI path incorrect: {path}"
        
        print("✅ ComfyUI integration working!")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("=" * 50)
        print("The Runpod configuration is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if temp_workspace and temp_workspace.exists():
            shutil.rmtree(temp_workspace)
        
        # Restore environment
        for var in ['RUNPOD_POD_ID', 'INFINITETALK_MODEL_DIR', 'COMFYUI_MODEL_DIR']:
            os.environ.pop(var, None)

def main():
    """Run basic Runpod test"""
    
    print("🚀 InfiniteTalk Runpod Configuration Test")
    print("=" * 50)
    print("Testing Issue #123 fix for Runpod deployment")
    print()
    
    success = test_runpod_basics()
    
    if success:
        print("\n📋 READY FOR RUNPOD!")
        print("=" * 30)
        print("🟢 Environment detection: Working")
        print("🟢 Model path configuration: Working")  
        print("🟢 ComfyUI integration: Working")
        print("🟢 Directory creation: Working")
        print()
        print("🚀 Deploy to Runpod and run:")
        print("   git checkout fix-model-download-paths")
        print("   ./scripts/setup_runpod.sh")
        print("   python3 scripts/download_models.py")
    else:
        print("\n❌ Issues found - review before Runpod testing")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)