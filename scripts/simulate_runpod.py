#!/usr/bin/env python3
"""
Runpod environment simulator for local testing.

This script simulates a Runpod environment locally to test 
the model path configuration before deploying to actual Runpod.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def simulate_runpod_environment():
    """Simulate Runpod environment with temporary directories"""
    
    print("🔧 Setting up Runpod simulation...")
    
    # Create temporary workspace
    temp_workspace = Path(tempfile.mkdtemp(prefix='runpod_sim_'))
    workspace_models = temp_workspace / 'workspace' / 'models'
    workspace_comfyui = temp_workspace / 'workspace' / 'ComfyUI' / 'models'
    
    # Create directory structure
    workspace_models.mkdir(parents=True, exist_ok=True)
    workspace_comfyui.mkdir(parents=True, exist_ok=True)
    
    # Set Runpod environment variables
    os.environ['RUNPOD_POD_ID'] = 'sim-test-pod-123'
    os.environ['INFINITETALK_MODEL_DIR'] = str(workspace_models)
    os.environ['COMFYUI_MODEL_DIR'] = str(workspace_comfyui)
    
    print(f"✅ Simulated Runpod workspace: {temp_workspace}")
    print(f"   Models directory: {workspace_models}")
    print(f"   ComfyUI directory: {workspace_comfyui}")
    
    return temp_workspace

def test_runpod_simulation():
    """Test the complete Runpod workflow"""
    
    print("🧪 RUNPOD SIMULATION TEST")
    print("=" * 50)
    
    temp_workspace = None
    
    try:
        # Set up simulated environment
        temp_workspace = simulate_runpod_environment()
        
        # Import and test after environment is set
        from config_manager import ModelPathManager
        from comfyui_handler import ComfyUIModelHandler
        
        print("\n1. Testing Environment Detection:")
        path_manager = ModelPathManager()
        path_manager.print_environment_info()
        
        # Verify Runpod detection
        assert path_manager.env_info['is_runpod'], "Failed to detect Runpod environment"
        assert not path_manager.env_info['is_local'], "Should not detect as local"
        print("✅ Environment detection working!")
        
        print("\n2. Testing Model Path Resolution:")
        model_paths = path_manager.get_all_model_paths()
        for model_type, path in model_paths.items():
            print(f"   {model_type}: {path}")
        
        # Verify paths point to workspace
        wan_path = path_manager.get_model_path('wan_base')
        assert '/workspace/models' in wan_path, f"Wan path should be in workspace: {wan_path}"
        print("✅ Model paths correctly resolved to workspace!")
        
        print("\n3. Testing Directory Creation:")
        created_dirs = []
        for model_type in ['wan_base', 'wav2vec', 'infinitetalk']:
            dir_path = path_manager.ensure_model_directory(model_type)
            created_dirs.append(str(dir_path))
            assert dir_path.exists(), f"Directory not created: {dir_path}"
            print(f"   ✅ Created: {dir_path}")
        
        print("\n4. Testing ComfyUI Integration:")
        comfyui_handler = ComfyUIModelHandler()
        node_config = comfyui_handler.get_comfyui_node_config()
        
        print("   ComfyUI node paths:")
        for key, path in node_config['model_paths'].items():
            print(f"     {key}: {path}")
        
        # Verify ComfyUI paths
        checkpoint_path = comfyui_handler.get_model_path('checkpoints')
        assert '/workspace/ComfyUI/models' in checkpoint_path, f"ComfyUI path incorrect: {checkpoint_path}"
        print("✅ ComfyUI integration working!")
        
        print("\n5. Testing Download Script Configuration:")
        sys.path.insert(0, str(Path(__file__).parent))
        import download_models
        
        models = download_models.get_models_to_download()
        existing = download_models.check_existing_models(path_manager)
        
        print(f"   Models configured: {len(models)}")
        print(f"   Existing models: {existing}")
        print("✅ Download script configuration working!")
        
        print("\n🎉 RUNPOD SIMULATION SUCCESSFUL!")
        print("=" * 50)
        print("All tests passed - the solution should work on actual Runpod!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ RUNPOD SIMULATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        if temp_workspace and temp_workspace.exists():
            shutil.rmtree(temp_workspace)
            print(f"\n🧹 Cleaned up temporary workspace: {temp_workspace}")
        
        # Restore environment
        for env_var in ['RUNPOD_POD_ID', 'INFINITETALK_MODEL_DIR', 'COMFYUI_MODEL_DIR']:
            os.environ.pop(env_var, None)

def main():
    """Run Runpod simulation test"""
    
    print("🚀 InfiniteTalk Runpod Environment Simulation")
    print("=" * 60)
    print("This test simulates a Runpod environment to verify")
    print("that the Issue #123 fix will work correctly on Runpod.")
    print()
    
    success = test_runpod_simulation()
    
    if success:
        print("\n📋 READY FOR RUNPOD TESTING!")
        print("=" * 40)
        print("1. Deploy to Runpod")
        print("2. Run: git checkout fix-model-download-paths")
        print("3. Run: ./scripts/setup_runpod.sh")
        print("4. Run: python3 scripts/download_models.py")
        print("5. Test inference as normal")
        print()
        print("The model path configuration should work automatically!")
    else:
        print("\n❌ ISSUES DETECTED")
        print("Please review the errors above before testing on Runpod.")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)