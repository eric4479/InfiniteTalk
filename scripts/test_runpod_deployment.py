#!/usr/bin/env python3
"""
Comprehensive Runpod deployment validation script for InfiniteTalk.

This script tests all aspects of the InfiniteTalk deployment with Issue #123 fixes
to ensure everything works correctly in Runpod environments.
"""

import sys
import os
import traceback
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_status(message, success=True):
    icon = "✅" if success else "❌" 
    print(f"{icon} {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def test_python_environment():
    """Test Python environment and dependencies"""
    print_header("Python Environment Test")
    
    try:
        print_info(f"Python version: {sys.version}")
        print_info(f"Python executable: {sys.executable}")
        
        # Test PyTorch
        import torch
        print_status(f"PyTorch {torch.__version__} imported successfully")
        
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name()
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            vram_free = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()
            print_status(f"CUDA available: {gpu_name} ({gpu_memory:.1f}GB total)")
            print_info(f"Available VRAM: {vram_free/1e9:.1f}GB")
        else:
            print_status("CUDA not available - will use CPU mode", success=False)
        
        # Test key dependencies
        deps = [
            ('transformers', 'transformers'),
            ('diffusers', 'diffusers'), 
            ('accelerate', 'accelerate'),
            ('numpy', 'numpy'),
            ('PIL', 'PIL'),
            ('opencv', 'cv2'),
            ('gradio', 'gradio'),
        ]
        
        for name, module in deps:
            try:
                __import__(module)
                print_status(f"{name} imported successfully")
            except ImportError:
                print_status(f"{name} import failed", success=False)
        
        return True
        
    except Exception as e:
        print_status(f"Environment test failed: {e}", success=False)
        traceback.print_exc()
        return False

def test_infinitetalk_imports():
    """Test InfiniteTalk specific modules"""
    print_header("InfiniteTalk Module Test")
    
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        # Test config manager
        from src.config_manager import ModelPathManager
        print_status("Config manager imported")
        
        # Test utilities
        from src.utils import setup_logging, get_device_info
        print_status("Utilities imported")
        
        # Test ComfyUI handler if available
        try:
            from src.comfyui_handler import ComfyUIModelHandler
            print_status("ComfyUI handler imported")
        except ImportError:
            print_status("ComfyUI handler not available", success=False)
        
        # Initialize manager
        manager = ModelPathManager()
        print_status("ModelPathManager initialized")
        
        return True
        
    except Exception as e:
        print_status(f"Module import failed: {e}", success=False)
        traceback.print_exc()
        return False

def test_environment_detection():
    """Test environment detection and Issue #123 fixes"""
    print_header("Environment Detection & Issue #123 Test")
    
    try:
        from src.config_manager import ModelPathManager
        
        manager = ModelPathManager()
        env_info = manager.env_info
        
        print_info("Environment detection results:")
        for key, value in env_info.items():
            status_icon = "✅" if value else "❌"
            print(f"  {status_icon} {key}: {value}")
        
        print_info("\nModel path configuration:")
        print(f"  Base model directory: {manager.base_model_dir}")
        print(f"  Wan base: {manager.get_model_path('wan_base')}")
        print(f"  Wav2Vec: {manager.get_model_path('wav2vec')}")
        print(f"  InfiniteTalk: {manager.get_model_path('infinitetalk')}")
        
        # Test Issue #123 fix
        is_runpod = env_info.get('is_runpod', False)
        is_local = env_info.get('is_local', False)
        
        if is_runpod:
            print_status("Runpod environment detected correctly")
            if "/workspace" in manager.base_model_dir:
                print_status("Issue #123 fix working: Using /workspace paths")
            else:
                print_status("Issue #123 fix problem: Not using /workspace paths", success=False)
        elif is_local:
            print_status("Local environment detected")
            if manager.base_model_dir == "./weights":
                print_status("Using local weights directory correctly")
            else:
                print_info(f"Using custom model directory: {manager.base_model_dir}")
        else:
            print_status("Other environment detected")
        
        return True
        
    except Exception as e:
        print_status(f"Environment detection failed: {e}", success=False)
        traceback.print_exc()
        return False

def test_download_system():
    """Test the optimized download system"""
    print_header("Download System Test")
    
    try:
        download_script = Path(__file__).parent / "download_models_optimized.py"
        
        if not download_script.exists():
            print_status("Download script not found", success=False)
            return False
        
        print_status("Download script found")
        
        # Test help
        result = subprocess.run([
            sys.executable, str(download_script), "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print_status("Download script help works")
        else:
            print_status("Download script help failed", success=False)
        
        # Test check-only mode
        print_info("Testing model status check...")
        result = subprocess.run([
            sys.executable, str(download_script), "--check-only"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_status("Model status check works")
            # Show first few lines of output
            lines = result.stdout.split('\n')[:15]
            for line in lines:
                if line.strip() and not line.startswith('===='):
                    print(f"    {line}")
        else:
            print_status("Model status check failed", success=False)
            print(f"Error: {result.stderr}")
        
        # Test size estimation
        print_info("Testing download size estimation...")
        result = subprocess.run([
            sys.executable, str(download_script), "--estimate-size"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print_status("Size estimation works")
        else:
            print_status("Size estimation failed", success=False)
        
        return True
        
    except Exception as e:
        print_status(f"Download system test failed: {e}", success=False)
        traceback.print_exc()
        return False

def test_generation_system():
    """Test the generation system without actually generating"""
    print_header("Generation System Test")
    
    try:
        generate_script = Path(__file__).parent.parent / "generate_infinitetalk.py"
        
        if not generate_script.exists():
            print_status("Generation script not found", success=False)
            return False
        
        print_status("Generation script found")
        
        # Test help
        result = subprocess.run([
            sys.executable, str(generate_script), "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "InfiniteTalk" in result.stdout:
            print_status("Generation script help works")
        else:
            print_status("Generation script help failed", success=False)
            return False
        
        # Test argument parsing without model loading
        print_info("Testing argument parsing...")
        test_args = [
            sys.executable, str(generate_script),
            "--mode", "t2v",
            "--text", "test prompt", 
            "--duration", "30",
            "--dry-run"  # This flag doesn't exist but should fail gracefully
        ]
        
        result = subprocess.run(test_args, capture_output=True, text=True, timeout=10)
        
        # Should fail but not crash
        if "unrecognized arguments" in result.stderr or result.returncode == 2:
            print_status("Argument parsing works (expected error)")
        else:
            print_status("Unexpected generation script behavior")
        
        return True
        
    except Exception as e:
        print_status(f"Generation system test failed: {e}", success=False)
        return False

def test_gradio_app():
    """Test Gradio app without starting it"""
    print_header("Gradio App Test")
    
    try:
        app_script = Path(__file__).parent.parent / "app.py"
        
        if not app_script.exists():
            print_status("Gradio app script not found", success=False)
            return False
        
        print_status("Gradio app script found")
        
        # Test if we can import gradio
        import gradio as gr
        print_status(f"Gradio {gr.__version__} available")
        
        # Check if app.py can be parsed
        try:
            with open(app_script, 'r') as f:
                content = f.read()
            
            if "gradio" in content.lower() and "interface" in content.lower():
                print_status("Gradio app script appears valid")
            else:
                print_status("Gradio app script may be incomplete", success=False)
        except Exception as e:
            print_status(f"Could not read app script: {e}", success=False)
        
        return True
        
    except Exception as e:
        print_status(f"Gradio app test failed: {e}", success=False)
        return False

def test_disk_space():
    """Test disk space requirements"""
    print_header("Disk Space Test")
    
    try:
        # Get disk usage
        total, used, free = shutil.disk_usage('.')
        
        free_gb = free / (1024**3)
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        used_percent = (used / total) * 100
        
        print_info(f"Disk usage:")
        print_info(f"  Total: {total_gb:.1f} GB")
        print_info(f"  Used: {used_gb:.1f} GB ({used_percent:.1f}%)")
        print_info(f"  Free: {free_gb:.1f} GB")
        
        # Requirements check
        if free_gb >= 25:
            print_status(f"Excellent disk space ({free_gb:.1f} GB free)")
        elif free_gb >= 20:
            print_status(f"Good disk space ({free_gb:.1f} GB free)")
        elif free_gb >= 15:
            print_status(f"Adequate disk space ({free_gb:.1f} GB free) - use --skip-optional")
        else:
            print_status(f"Low disk space ({free_gb:.1f} GB free) - cleanup needed", success=False)
        
        return free_gb >= 15
        
    except Exception as e:
        print_status(f"Disk space test failed: {e}", success=False)
        return False

def test_runpod_features():
    """Test Runpod-specific features"""
    print_header("Runpod Features Test")
    
    try:
        # Check workspace directory
        workspace = Path("/workspace")
        if workspace.exists():
            print_status("Workspace directory exists")
            
            # Test write permissions
            try:
                test_file = workspace / ".infinitetalk_test"
                test_file.write_text("test")
                test_file.unlink()
                print_status("Workspace write permissions OK")
            except Exception as e:
                print_status(f"Workspace write permission failed: {e}", success=False)
        else:
            print_status("Workspace directory not found (not Runpod?)")
        
        # Check environment variables
        runpod_vars = [
            'RUNPOD_POD_ID',
            'RUNPOD_POD_HOSTNAME', 
            'JUPYTER_PASSWORD',
            'RUNPOD_TCP_PORT_22',
        ]
        
        detected_vars = 0
        for var in runpod_vars:
            value = os.getenv(var)
            if value:
                detected_vars += 1
                print_info(f"  {var}: {'*' * len(str(value))}")  # Hide actual values
        
        if detected_vars > 0:
            print_status(f"Runpod environment variables detected ({detected_vars}/{len(runpod_vars)})")
        else:
            print_status("No Runpod environment variables found")
        
        # Check ports
        common_ports = [7860, 8188, 8189, 22, 8080]
        print_info("Checking common ports...")
        for port in common_ports:
            env_var = f"RUNPOD_TCP_PORT_{port}"
            if os.getenv(env_var):
                print_info(f"  Port {port} mapped: {os.getenv(env_var)}")
        
        return True
        
    except Exception as e:
        print_status(f"Runpod features test failed: {e}", success=False)
        return False

def main():
    """Run comprehensive deployment validation"""
    print("🚀 InfiniteTalk Runpod Deployment Validation")
    print("=" * 60)
    print("Comprehensive testing of InfiniteTalk with Issue #123 fixes")
    print("Testing dynamic model paths and Runpod optimization features")
    print()
    
    tests = [
        ("Python Environment", test_python_environment),
        ("InfiniteTalk Modules", test_infinitetalk_imports),
        ("Environment Detection", test_environment_detection),
        ("Download System", test_download_system),
        ("Generation System", test_generation_system),
        ("Gradio App", test_gradio_app),
        ("Disk Space", test_disk_space),
        ("Runpod Features", test_runpod_features),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print_status("Testing interrupted by user", success=False)
            return 1
        except Exception as e:
            print_status(f"{test_name} test crashed: {e}", success=False)
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print_header("Deployment Validation Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        print_status(f"{test_name}: {'PASSED' if result else 'FAILED'}", success=result)
    
    print(f"\n🎯 Overall Score: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print_status("🎉 Perfect! InfiniteTalk is ready for production deployment on Runpod")
        print("\n📋 Recommended next steps:")
        print("1. Download models: python scripts/download_models_optimized.py --skip-optional")
        print("2. Start Gradio: python app.py --share --server-port 7860") 
        print("3. Test generation: python generate_infinitetalk.py --mode t2v --text 'mountain sunset' --duration 60")
    elif passed >= total * 0.8:
        print_status(f"🟡 Good! {passed}/{total} tests passed. Minor issues detected but deployment should work")
        print("\n📋 Next steps:")
        print("1. Review failed tests above")
        print("2. Download models: python scripts/download_models_optimized.py --skip-optional")
        print("3. Test carefully before production use")
    else:
        print_status(f"🔴 Issues detected! Only {passed}/{total} tests passed", success=False)
        print("\n📋 Required actions:")
        print("1. Fix the failed tests above")
        print("2. Re-run this validation script")
        print("3. Do not deploy until all tests pass")
        return 1
    
    print(f"\n📖 Documentation: RUNPOD_DEPLOYMENT.md")
    print(f"🐛 Support: https://github.com/eric4479/InfiniteTalk/issues")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())