#!/usr/bin/env python3
"""
Unified model download script for InfiniteTalk.

This script downloads all required models to appropriate directories
based on the current deployment environment (local, Runpod, GCP, ComfyUI).
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


def get_models_to_download() -> List[Dict]:
    """Get list of models to download with their configurations"""
    return [
        {
            'repo_id': 'Wan-AI/Wan2.1-I2V-14B-480P',
            'model_type': 'wan_base',
            'description': 'Base Wan model for image-to-video generation',
            'required': True,
            'files': None  # Download entire repo
        },
        {
            'repo_id': 'TencentGameMate/chinese-wav2vec2-base', 
            'model_type': 'wav2vec',
            'description': 'Audio encoder for speech processing',
            'required': True,
            'files': None  # Download entire repo
        },
        {
            'repo_id': 'MeiGen-AI/InfiniteTalk',
            'model_type': 'infinitetalk',
            'description': 'InfiniteTalk weights for talking head generation',
            'required': True,
            'files': ['single/infinitetalk.safetensors']  # Specific files only
        },
        {
            'repo_id': 'hexgrad/Kokoro-82M',
            'model_type': 'kokoro',
            'description': 'TTS model for text-to-speech synthesis',
            'required': False,  # Only needed if using TTS mode
            'files': None  # Download entire repo
        }
    ]


def download_model_repo(repo_id: str, local_dir: str, files: List[str] = None) -> bool:
    """
    Download a model repository or specific files.
    
    Args:
        repo_id: HuggingFace repository ID
        local_dir: Local directory to download to
        files: List of specific files to download (None for entire repo)
        
    Returns:
        True if successful, False otherwise
    """
    if not HF_AVAILABLE:
        print(f"Cannot download {repo_id}: huggingface_hub not available")
        return False
    
    try:
        local_path = Path(local_dir)
        local_path.mkdir(parents=True, exist_ok=True)
        
        if files is None:
            # Download entire repository
            print(f"  Downloading entire repository to {local_dir}...")
            snapshot_download(
                repo_id=repo_id,
                local_dir=local_dir,
                local_dir_use_symlinks=False,
                resume_download=True
            )
        else:
            # Download specific files
            print(f"  Downloading {len(files)} files to {local_dir}...")
            for file_path in files:
                target_path = local_path / file_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                hf_hub_download(
                    repo_id=repo_id,
                    filename=file_path,
                    local_dir=local_dir,
                    local_dir_use_symlinks=False,
                    resume_download=True
                )
        
        print(f"  ✓ Successfully downloaded {repo_id}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to download {repo_id}: {e}")
        return False


def check_existing_models(path_manager: ModelPathManager) -> Dict[str, bool]:
    """Check which models already exist"""
    models = get_models_to_download()
    existing = {}
    
    for model in models:
        model_path = path_manager.get_model_path(model['model_type'])
        
        if model['files'] is None:
            # Check if directory exists and has files
            existing[model['model_type']] = (
                Path(model_path).exists() and 
                any(Path(model_path).iterdir())
            )
        else:
            # Check if specific files exist
            all_files_exist = True
            for file_path in model['files']:
                full_path = Path(model_path).parent / file_path
                if not full_path.exists():
                    all_files_exist = False
                    break
            existing[model['model_type']] = all_files_exist
    
    return existing


def download_all_models(
    path_manager: ModelPathManager, 
    force_download: bool = False,
    skip_optional: bool = False
) -> Tuple[int, int]:
    """
    Download all required models.
    
    Args:
        path_manager: Model path manager instance
        force_download: Force download even if models exist
        skip_optional: Skip optional models
        
    Returns:
        Tuple of (successful_downloads, total_downloads)
    """
    models = get_models_to_download()
    existing = check_existing_models(path_manager)
    
    successful = 0
    total = 0
    
    for model in models:
        model_type = model['model_type']
        
        # Skip optional models if requested
        if skip_optional and not model['required']:
            print(f"Skipping optional model: {model['description']}")
            continue
        
        # Skip existing models unless force download
        if existing.get(model_type, False) and not force_download:
            print(f"✓ {model['description']} already exists at {path_manager.get_model_path(model_type)}")
            successful += 1
            total += 1
            continue
        
        print(f"Downloading {model['description']}...")
        local_dir = path_manager.get_model_path(model_type)
        
        # For infinitetalk, we need to adjust the path
        if model_type == 'infinitetalk':
            local_dir = str(Path(local_dir).parent.parent)  # Remove /single from path
        
        if download_model_repo(model['repo_id'], local_dir, model['files']):
            successful += 1
        
        total += 1
    
    return successful, total


def create_model_symlinks(path_manager: ModelPathManager):
    """Create symlinks for ComfyUI compatibility if needed"""
    if not path_manager.comfyui_model_dir:
        return
    
    print("Creating ComfyUI-compatible symlinks...")
    comfyui_base = Path(path_manager.comfyui_model_dir)
    
    # Link checkpoints
    checkpoints_dir = comfyui_base / 'checkpoints'
    checkpoints_dir.mkdir(exist_ok=True)
    
    wan_path = Path(path_manager.get_model_path('wan_base'))
    if wan_path.exists():
        symlink_path = checkpoints_dir / 'wan_base'
        if not symlink_path.exists():
            try:
                symlink_path.symlink_to(wan_path, target_is_directory=True)
                print(f"  ✓ Created symlink: {symlink_path} -> {wan_path}")
            except OSError as e:
                print(f"  ✗ Failed to create symlink: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Download InfiniteTalk models for different deployment environments"
    )
    parser.add_argument(
        '--model-base-dir',
        type=str,
        default=None,
        help='Base directory for models (overrides environment variables)'
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
        help='Force download even if models already exist'
    )
    parser.add_argument(
        '--skip-optional',
        action='store_true',
        help='Skip optional models (like TTS)'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check which models exist, do not download'
    )
    parser.add_argument(
        '--create-symlinks',
        action='store_true',
        help='Create ComfyUI-compatible symlinks'
    )
    
    args = parser.parse_args()
    
    # Initialize path manager
    path_manager = ModelPathManager(
        base_model_dir=args.model_base_dir,
        comfyui_model_dir=args.comfyui_model_dir
    )
    
    # Print environment information
    path_manager.print_environment_info()
    
    if args.check_only:
        print("Checking existing models...")
        existing = check_existing_models(path_manager)
        for model_type, exists in existing.items():
            status = "✓" if exists else "✗"
            path = path_manager.get_model_path(model_type)
            print(f"  {status} {model_type}: {path}")
        return
    
    if not HF_AVAILABLE:
        print("Error: huggingface_hub is required for downloading models.")
        print("Install it with: pip install huggingface_hub")
        sys.exit(1)
    
    print("Starting model downloads...")
    successful, total = download_all_models(
        path_manager, 
        force_download=args.force,
        skip_optional=args.skip_optional
    )
    
    if args.create_symlinks:
        create_model_symlinks(path_manager)
    
    print(f"\nDownload summary: {successful}/{total} models downloaded successfully")
    if successful == total:
        print("✓ All models downloaded successfully!")
        sys.exit(0)
    else:
        print(f"✗ {total - successful} models failed to download")
        sys.exit(1)


if __name__ == "__main__":
    main()