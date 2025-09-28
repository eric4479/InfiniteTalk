#!/usr/bin/env python3
"""
Optimized model download script for InfiniteTalk.

This script downloads only the essential files for each model,
avoiding unnecessary large downloads while ensuring all required
files are present for proper operation.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# Add src to path to import config_manager
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    from huggingface_hub import hf_hub_download, snapshot_download
    HF_AVAILABLE = True
except ImportError:
    print("Warning: huggingface_hub not available. Please install it with:")
    print("pip install huggingface_hub")
    HF_AVAILABLE = False

from config_manager import ModelPathManager


def get_essential_files_config() -> List[Dict]:
    """Get optimized configuration with only essential files for each model"""
    return [
        {
            'repo_id': 'Wan-AI/Wan2.1-I2V-14B-480P',
            'model_type': 'wan_base',
            'description': 'Base Wan model (essential files only)',
            'required': True,
            'files': [
                'config.json',
                'diffusion_pytorch_model-00001-of-00007.safetensors',
                'diffusion_pytorch_model-00002-of-00007.safetensors', 
                'diffusion_pytorch_model-00003-of-00007.safetensors',
                'diffusion_pytorch_model-00004-of-00007.safetensors',
                'diffusion_pytorch_model-00005-of-00007.safetensors',
                'diffusion_pytorch_model-00006-of-00007.safetensors',
                'diffusion_pytorch_model-00007-of-00007.safetensors',
                'diffusion_pytorch_model.safetensors.index.json'
            ]
        },
        {
            'repo_id': 'TencentGameMate/chinese-wav2vec2-base', 
            'model_type': 'wav2vec',
            'description': 'Audio encoder (essential files only)',
            'required': True,
            'files': [
                'config.json',
                'pytorch_model.bin',
                'tokenizer.json',
                'preprocessor_config.json'
            ]
        },
        {
            'repo_id': 'MeiGen-AI/InfiniteTalk',
            'model_type': 'infinitetalk',
            'description': 'InfiniteTalk weights',
            'required': True,
            'files': ['single/infinitetalk.safetensors']
        },
        {
            'repo_id': 'hexgrad/Kokoro-82M',
            'model_type': 'kokoro',
            'description': 'TTS model (essential files only)',
            'required': False,  # Only needed if using TTS mode
            'files': [
                'config.json',
                'pytorch_model.bin',
                'tokenizer.json'
            ]
        }
    ]


def check_file_exists(repo_id: str, filename: str) -> bool:
    """Check if a file exists in the repository without downloading"""
    try:
        from huggingface_hub import repo_info
        info = repo_info(repo_id)
        return any(sibling.rfilename == filename for sibling in info.siblings)
    except:
        return True  # Assume it exists if we can't check


def download_essential_files(repo_id: str, local_dir: str, files: List[str]) -> Tuple[int, int]:
    """
    Download only essential files from a repository.
    
    Returns:
        Tuple of (successful_downloads, total_files)
    """
    if not HF_AVAILABLE:
        print(f"Cannot download {repo_id}: huggingface_hub not available")
        return 0, len(files)
    
    local_path = Path(local_dir)
    local_path.mkdir(parents=True, exist_ok=True)
    
    successful = 0
    total = len(files)
    
    print(f"  Downloading {total} essential files...")
    
    for file_path in files:
        try:
            target_path = local_path / file_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Skip if file already exists and is not empty
            if target_path.exists() and target_path.stat().st_size > 0:
                print(f"    ✓ {file_path} (already exists)")
                successful += 1
                continue
            
            # Download the file
            print(f"    📥 {file_path}...")
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=file_path,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            
            if Path(downloaded_path).exists():
                print(f"    ✓ {file_path}")
                successful += 1
            else:
                print(f"    ✗ {file_path} (download failed)")
                
        except Exception as e:
            print(f"    ✗ {file_path} (error: {e})")
    
    return successful, total


def get_file_size_estimate(model_config: Dict) -> str:
    """Estimate download size for a model"""
    estimates = {
        'wan_base': '~15GB (7 safetensors files)',
        'wav2vec': '~500MB (pytorch_model.bin)',
        'infinitetalk': '~100MB (safetensors)',
        'kokoro': '~300MB (pytorch_model.bin)'
    }
    return estimates.get(model_config['model_type'], 'Unknown size')


def download_optimized_models(
    path_manager: ModelPathManager, 
    force_download: bool = False,
    skip_optional: bool = False,
    show_estimates: bool = False
) -> Tuple[int, int]:
    """
    Download only essential model files.
    
    Returns:
        Tuple of (successful_downloads, total_downloads)
    """
    models = get_essential_files_config()
    
    if show_estimates:
        print("\n📊 Download size estimates:")
        total_estimate = 0
        for model in models:
            if skip_optional and not model['required']:
                continue
            size_est = get_file_size_estimate(model)
            print(f"   {model['description']}: {size_est}")
        print()
    
    successful_models = 0
    total_models = 0
    
    for model in models:
        model_type = model['model_type']
        
        # Skip optional models if requested
        if skip_optional and not model['required']:
            print(f"⏭️  Skipping optional model: {model['description']}")
            continue
        
        print(f"\n📥 {model['description']}...")
        local_dir = path_manager.get_model_path(model_type)
        
        # For infinitetalk, adjust the path
        if model_type == 'infinitetalk':
            local_dir = str(Path(local_dir).parent.parent)
        
        # Check if already downloaded (unless force)
        if not force_download:
            existing_files = 0
            for file_path in model['files']:
                full_path = Path(local_dir) / file_path
                if full_path.exists() and full_path.stat().st_size > 0:
                    existing_files += 1
            
            if existing_files == len(model['files']):
                print(f"  ✅ All files already exist")
                successful_models += 1
                total_models += 1
                continue
            elif existing_files > 0:
                print(f"  📋 {existing_files}/{len(model['files'])} files exist, downloading missing...")
        
        # Download essential files
        successful_files, total_files = download_essential_files(
            model['repo_id'], 
            local_dir, 
            model['files']
        )
        
        if successful_files == total_files:
            print(f"  ✅ {model['description']} complete ({successful_files}/{total_files} files)")
            successful_models += 1
        else:
            print(f"  ⚠️  {model['description']} partial ({successful_files}/{total_files} files)")
        
        total_models += 1
    
    return successful_models, total_models


def main():
    parser = argparse.ArgumentParser(
        description="Download essential InfiniteTalk model files (optimized)"
    )
    parser.add_argument(
        '--model-base-dir',
        type=str,
        default=None,
        help='Base directory for models'
    )
    parser.add_argument(
        '--comfyui-model-dir',
        type=str,
        default=None,
        help='ComfyUI models directory'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force download even if files exist'
    )
    parser.add_argument(
        '--skip-optional',
        action='store_true',
        help='Skip optional models (like TTS)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check which files exist'
    )
    parser.add_argument(
        '--estimate-size',
        action='store_true',
        help='Show download size estimates'
    )
    
    args = parser.parse_args()
    
    # Initialize path manager
    path_manager = ModelPathManager(
        base_model_dir=args.model_base_dir,
        comfyui_model_dir=args.comfyui_model_dir
    )
    
    print("🚀 InfiniteTalk Optimized Model Downloader")
    print("=" * 50)
    path_manager.print_environment_info()
    
    if args.estimate_size:
        models = get_essential_files_config()
        print("📊 DOWNLOAD SIZE ESTIMATES")
        print("-" * 30)
        for model in models:
            if args.skip_optional and not model['required']:
                continue
            size_est = get_file_size_estimate(model)
            status = "Required" if model['required'] else "Optional"
            print(f"   {model['description']}")
            print(f"     Size: {size_est}")
            print(f"     Files: {len(model['files'])} files")
            print(f"     Status: {status}")
            print()
        return
    
    if args.check_only:
        print("🔍 Checking existing files...")
        models = get_essential_files_config()
        
        for model in models:
            model_type = model['model_type']
            print(f"\n📋 {model['description']}:")
            
            local_dir = path_manager.get_model_path(model_type)
            if model_type == 'infinitetalk':
                local_dir = str(Path(local_dir).parent.parent)
            
            existing = 0
            for file_path in model['files']:
                full_path = Path(local_dir) / file_path
                if full_path.exists() and full_path.stat().st_size > 0:
                    print(f"     ✅ {file_path}")
                    existing += 1
                else:
                    print(f"     ❌ {file_path}")
            
            print(f"   Status: {existing}/{len(model['files'])} files present")
        return
    
    if not HF_AVAILABLE:
        print("❌ Error: huggingface_hub is required for downloading models.")
        print("Install it with: pip install huggingface_hub")
        sys.exit(1)
    
    print("📥 Starting optimized model downloads...")
    successful, total = download_optimized_models(
        path_manager, 
        force_download=args.force,
        skip_optional=args.skip_optional,
        show_estimates=args.estimate_size
    )
    
    print(f"\n🎯 DOWNLOAD SUMMARY")
    print("=" * 30)
    print(f"✅ Models completed: {successful}/{total}")
    
    if successful == total:
        print("🎉 All essential models downloaded successfully!")
        print("\n📋 Next steps:")
        print("   python3 generate_infinitetalk.py --print_paths --input_json examples/...")
        sys.exit(0)
    else:
        print(f"⚠️  {total - successful} models incomplete")
        print("   Run with --check-only to see missing files")
        sys.exit(1)


if __name__ == "__main__":
    main()