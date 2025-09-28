#!/usr/bin/env python3
"""
InfiniteTalk Model File Checker and Issue Reporter

This script checks what model files are missing and provides
specific guidance on what needs to be downloaded.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_manager import ModelPathManager


def get_required_files() -> Dict[str, Dict]:
    """Define exactly what files are required for each model"""
    return {
        'wan_base': {
            'description': 'Wan Base Model (14B parameters)',
            'repo_id': 'Wan-AI/Wan2.1-I2V-14B-480P',
            'critical_files': [
                'config.json',
                'diffusion_pytorch_model.safetensors.index.json'
            ],
            'model_files': [
                'diffusion_pytorch_model-00001-of-00007.safetensors',
                'diffusion_pytorch_model-00002-of-00007.safetensors', 
                'diffusion_pytorch_model-00003-of-00007.safetensors',
                'diffusion_pytorch_model-00004-of-00007.safetensors',
                'diffusion_pytorch_model-00005-of-00007.safetensors',
                'diffusion_pytorch_model-00006-of-00007.safetensors',
                'diffusion_pytorch_model-00007-of-00007.safetensors'
            ],
            'size_estimate': '~15GB'
        },
        'wav2vec': {
            'description': 'Chinese Wav2Vec2 Audio Encoder',
            'repo_id': 'TencentGameMate/chinese-wav2vec2-base',
            'critical_files': [
                'config.json',
                'preprocessor_config.json'
            ],
            'model_files': [
                'pytorch_model.bin'
            ],
            'optional_files': [
                'tokenizer.json'
            ],
            'size_estimate': '~500MB'
        },
        'infinitetalk': {
            'description': 'InfiniteTalk Talking Head Weights',
            'repo_id': 'MeiGen-AI/InfiniteTalk',
            'critical_files': [],
            'model_files': [
                'single/infinitetalk.safetensors'
            ],
            'size_estimate': '~100MB'
        },
        'kokoro': {
            'description': 'Kokoro TTS Model (Optional)',
            'repo_id': 'hexgrad/Kokoro-82M',
            'critical_files': [
                'config.json'
            ],
            'model_files': [
                'pytorch_model.bin'
            ],
            'optional_files': [
                'tokenizer.json'
            ],
            'size_estimate': '~300MB',
            'required': False
        }
    }


def check_model_files(path_manager: ModelPathManager) -> Dict[str, Dict]:
    """Check which model files are present and missing"""
    
    required_files = get_required_files()
    results = {}
    
    for model_type, config in required_files.items():
        model_path = Path(path_manager.get_model_path(model_type))
        
        # Special handling for infinitetalk path
        if model_type == 'infinitetalk':
            model_path = model_path.parent.parent
        
        result = {
            'path': str(model_path),
            'exists': model_path.exists(),
            'critical_missing': [],
            'model_missing': [],
            'optional_missing': [],
            'critical_present': [],
            'model_present': [],
            'optional_present': [],
            'total_size': 0
        }
        
        if model_path.exists():
            # Check critical files
            for file_name in config.get('critical_files', []):
                file_path = model_path / file_name
                if file_path.exists():
                    result['critical_present'].append(file_name)
                    result['total_size'] += file_path.stat().st_size
                else:
                    result['critical_missing'].append(file_name)
            
            # Check model files
            for file_name in config.get('model_files', []):
                file_path = model_path / file_name
                if file_path.exists():
                    result['model_present'].append(file_name)
                    result['total_size'] += file_path.stat().st_size
                else:
                    result['model_missing'].append(file_name)
            
            # Check optional files
            for file_name in config.get('optional_files', []):
                file_path = model_path / file_name
                if file_path.exists():
                    result['optional_present'].append(file_name)
                    result['total_size'] += file_path.stat().st_size
                else:
                    result['optional_missing'].append(file_name)
        else:
            # Directory doesn't exist - all files missing
            result['critical_missing'] = config.get('critical_files', [])
            result['model_missing'] = config.get('model_files', [])
            result['optional_missing'] = config.get('optional_files', [])
        
        results[model_type] = result
    
    return results


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def generate_download_commands(missing_files: Dict[str, Dict]) -> List[str]:
    """Generate specific download commands for missing files"""
    
    required_files = get_required_files()
    commands = []
    
    for model_type, result in missing_files.items():
        config = required_files[model_type]
        
        # Skip if no files missing
        total_missing = len(result['critical_missing']) + len(result['model_missing'])
        if total_missing == 0:
            continue
        
        # Skip optional models if not required
        if not config.get('required', True):
            continue
        
        repo_id = config['repo_id']
        model_path = result['path']
        
        commands.append(f"# {config['description']} - {config['size_estimate']}")
        commands.append(f"mkdir -p {model_path}")
        
        # Critical files
        for file_name in result['critical_missing']:
            commands.append(
                f"huggingface-cli download {repo_id} {file_name} --local-dir {model_path}"
            )
        
        # Model files
        for file_name in result['model_missing']:
            commands.append(
                f"huggingface-cli download {repo_id} {file_name} --local-dir {model_path}"
            )
        
        commands.append("")  # Empty line
    
    return commands


def print_detailed_report(path_manager: ModelPathManager, check_results: Dict[str, Dict]):
    """Print detailed report of model status"""
    
    required_files = get_required_files()
    
    print("🔍 DETAILED MODEL FILE ANALYSIS")
    print("=" * 60)
    
    total_missing_critical = 0
    total_missing_models = 0
    total_present_size = 0
    
    for model_type, result in check_results.items():
        config = required_files[model_type]
        
        print(f"\n📦 {config['description']}")
        print(f"   Repository: {config['repo_id']}")
        print(f"   Local path: {result['path']}")
        print(f"   Directory exists: {'✅' if result['exists'] else '❌'}")
        
        if result['total_size'] > 0:
            print(f"   Downloaded size: {format_file_size(result['total_size'])}")
            total_present_size += result['total_size']
        
        # Critical files status
        if config.get('critical_files'):
            print(f"   Critical files:")
            for file_name in config['critical_files']:
                if file_name in result['critical_present']:
                    print(f"     ✅ {file_name}")
                else:
                    print(f"     ❌ {file_name} - MISSING")
                    total_missing_critical += 1
        
        # Model files status
        if config.get('model_files'):
            print(f"   Model files:")
            for file_name in config['model_files']:
                if file_name in result['model_present']:
                    print(f"     ✅ {file_name}")
                else:
                    print(f"     ❌ {file_name} - MISSING")
                    total_missing_models += 1
        
        # Optional files status
        if config.get('optional_files'):
            print(f"   Optional files:")
            for file_name in config['optional_files']:
                if file_name in result['optional_present']:
                    print(f"     ✅ {file_name}")
                else:
                    print(f"     ⚠️  {file_name} - missing (optional)")
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    print(f"Total downloaded size: {format_file_size(total_present_size)}")
    print(f"Missing critical files: {total_missing_critical}")
    print(f"Missing model files: {total_missing_models}")
    
    if total_missing_critical > 0 or total_missing_models > 0:
        print(f"\n⚠️  ISSUES FOUND")
        print(f"   Critical files missing: {total_missing_critical}")
        print(f"   Model files missing: {total_missing_models}")
        print(f"   Status: ❌ InfiniteTalk will NOT work")
    else:
        print(f"\n✅ ALL REQUIRED FILES PRESENT")
        print(f"   Status: ✅ InfiniteTalk should work correctly")


def main():
    """Main function"""
    
    print("🔍 InfiniteTalk Model File Checker")
    print("=" * 50)
    
    # Initialize path manager
    path_manager = ModelPathManager()
    path_manager.print_environment_info()
    
    # Check model files
    check_results = check_model_files(path_manager)
    
    # Print detailed report
    print_detailed_report(path_manager, check_results)
    
    # Generate download commands if needed
    commands = generate_download_commands(check_results)
    
    if commands:
        print("\n📥 DOWNLOAD COMMANDS TO FIX ISSUES")
        print("=" * 50)
        print("Run these commands to download missing files:\n")
        
        print("# Install HuggingFace CLI if not already installed")
        print("pip install --upgrade huggingface_hub[cli]\n")
        
        for cmd in commands:
            print(cmd)
        
        print("\n# Alternative: Use the optimized downloader")
        print("python3 scripts/download_models_optimized.py")
    
    else:
        print("\n🎉 No missing files - ready for inference!")
    
    return len(commands) == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)