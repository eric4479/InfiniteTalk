#!/usr/bin/env python3
"""
Complete InfiniteTalk Setup and Download Script for Runpod/ComfyUI

This script downloads ALL required files for InfiniteTalk including:
- Model weights and configs
- Workflow templates and presets
- Example files and samples
- Quantization models (optional)
- LoRA models (optional)

Fixes common workflow errors by ensuring all required files are present.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from huggingface_hub import hf_hub_download, list_repo_files
import subprocess

# Add src to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from config_manager import ModelPathManager
    HAS_CONFIG_MANAGER = True
except ImportError:
    print("⚠️  Config manager not available - using default paths")
    HAS_CONFIG_MANAGER = False

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"📦 {title}")
    print('='*60)

def print_status(message: str, success: bool = True):
    """Print status message with icon"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")

def get_complete_file_configs() -> List[Dict]:
    """Get complete configuration for all required InfiniteTalk files"""
    
    configs = [
        {
            "name": "Base Wan Model",
            "repo_id": "Wan-AI/Wan2.1-I2V-14B-480P",
            "local_dir": "Wan2.1-I2V-14B-480P",
            "essential_files": [
                "config.json",
                "diffusion_pytorch_model.safetensors.index.json",
                "diffusion_pytorch_model-00001-of-00007.safetensors",
                "diffusion_pytorch_model-00002-of-00007.safetensors", 
                "diffusion_pytorch_model-00003-of-00007.safetensors",
                "diffusion_pytorch_model-00004-of-00007.safetensors",
                "diffusion_pytorch_model-00005-of-00007.safetensors",
                "diffusion_pytorch_model-00006-of-00007.safetensors",
                "diffusion_pytorch_model-00007-of-00007.safetensors",
            ],
            "size_estimate": "15GB",
            "required": True,
            "description": "Main video generation model"
        },
        {
            "name": "Chinese Wav2Vec2",
            "repo_id": "TencentGameMate/chinese-wav2vec2-base",
            "local_dir": "chinese-wav2vec2-base",
            "essential_files": [
                "config.json",
                "preprocessor_config.json",
                "pytorch_model.bin",
                "tokenizer.json",
                "vocab.json",
            ],
            "size_estimate": "500MB",
            "required": True,
            "description": "Audio encoder for Chinese speech"
        },
        {
            "name": "InfiniteTalk Weights",
            "repo_id": "MeiGen-AI/InfiniteTalk",
            "local_dir": "InfiniteTalk",
            "essential_files": [
                "single/infinitetalk.safetensors",
                "multi/infinitetalk.safetensors",
            ],
            "optional_files": [
                "quant_models/infinitetalk_single_fp8.safetensors",
                "quant_models/infinitetalk_multi_fp8.safetensors",
            ],
            "size_estimate": "200MB",
            "required": True,
            "description": "InfiniteTalk fine-tuned weights"
        },
        {
            "name": "Kokoro TTS",
            "repo_id": "hexgrad/Kokoro-82M",
            "local_dir": "Kokoro-82M",
            "essential_files": [
                "config.json",
                "pytorch_model.bin",
                "tokenizer.json",
            ],
            "size_estimate": "300MB",
            "required": False,
            "description": "Optional TTS model for speech synthesis"
        },
        {
            "name": "FusionX LoRA",
            "repo_id": "vrgamedevgirl84/Wan14BT2VFusioniX",
            "local_dir": "loras",
            "essential_files": [
                "FusionX_LoRa/Wan2.1_I2V_14B_FusionX_LoRA.safetensors",
            ],
            "size_estimate": "100MB",
            "required": False,
            "description": "FusionX LoRA for faster inference"
        },
        {
            "name": "LightX2V LoRA",
            "repo_id": "Kijai/WanVideo_comfy",
            "local_dir": "loras",
            "essential_files": [
                "Wan21_T2V_14B_lightx2v_cfg_step_distill_lora_rank32.safetensors",
            ],
            "size_estimate": "50MB",
            "required": False,
            "description": "LightX2V LoRA for 4-step inference"
        }
    ]
    
    return configs

def download_file_with_progress(repo_id: str, filename: str, local_dir: str) -> bool:
    """Download a single file with progress tracking"""
    try:
        print_info(f"Downloading {filename}...")
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        return True
    except Exception as e:
        print_status(f"Failed to download {filename}: {e}", success=False)
        return False

def download_model_files(config: Dict, base_model_dir: str, include_optional: bool = False) -> Tuple[int, int]:
    """Download files for a specific model configuration"""
    
    local_path = Path(base_model_dir) / config["local_dir"]
    local_path.mkdir(parents=True, exist_ok=True)
    
    files_to_download = config["essential_files"].copy()
    if include_optional and "optional_files" in config:
        files_to_download.extend(config["optional_files"])
    
    print_info(f"Downloading {len(files_to_download)} files to {local_path}")
    
    successful = 0
    total = len(files_to_download)
    
    for filename in files_to_download:
        if download_file_with_progress(config["repo_id"], filename, str(local_path)):
            successful += 1
        else:
            print_status(f"⚠️  Skipped {filename} (may not exist or permission issue)")
    
    return successful, total

def check_existing_files(config: Dict, base_model_dir: str) -> Tuple[int, int, List[str]]:
    """Check which files already exist"""
    
    local_path = Path(base_model_dir) / config["local_dir"]
    files_to_check = config["essential_files"]
    
    existing = []
    missing = []
    
    for filename in files_to_check:
        file_path = local_path / filename
        if file_path.exists():
            existing.append(filename)
        else:
            missing.append(filename)
    
    return len(existing), len(files_to_check), missing

def setup_templates_and_examples(base_dir: str = ".") -> bool:
    """Ensure example templates and workflow presets are available"""
    
    print_section("Template and Example Setup")
    
    examples_dir = Path(base_dir) / "examples"
    
    # Check if examples already exist
    required_examples = [
        "single_example_image.json",
        "multi_example_image.json", 
        "single_example_video.json"
    ]
    
    missing_examples = []
    for example in required_examples:
        if not (examples_dir / example).exists():
            missing_examples.append(example)
    
    if not missing_examples:
        print_status("All example templates found")
        return True
    
    print_info(f"Missing examples: {missing_examples}")
    
    # Create basic example templates if missing
    single_image_template = {
        "input_image": "path/to/your/image.jpg",
        "input_audio": "path/to/your/audio.wav",
        "output_path": "output/result.mp4"
    }
    
    multi_image_template = {
        "input_images": [
            "path/to/person1.jpg",
            "path/to/person2.jpg"
        ],
        "input_audio": "path/to/your/audio.wav",
        "output_path": "output/multi_result.mp4"
    }
    
    single_video_template = {
        "input_video": "path/to/your/video.mp4",
        "input_audio": "path/to/your/audio.wav",
        "output_path": "output/dubbed_result.mp4"
    }
    
    try:
        examples_dir.mkdir(exist_ok=True)
        
        if "single_example_image.json" in missing_examples:
            with open(examples_dir / "single_example_image.json", "w") as f:
                json.dump(single_image_template, f, indent=2)
            print_status("Created single_example_image.json template")
        
        if "multi_example_image.json" in missing_examples:
            with open(examples_dir / "multi_example_image.json", "w") as f:
                json.dump(multi_image_template, f, indent=2)
            print_status("Created multi_example_image.json template")
        
        if "single_example_video.json" in missing_examples:
            with open(examples_dir / "single_example_video.json", "w") as f:
                json.dump(single_video_template, f, indent=2)
            print_status("Created single_example_video.json template")
        
        # Create subdirectories
        (examples_dir / "single").mkdir(exist_ok=True)
        (examples_dir / "multi").mkdir(exist_ok=True)
        
        print_status("Template and example setup complete")
        return True
        
    except Exception as e:
        print_status(f"Failed to setup templates: {e}", success=False)
        return False

def create_workflow_guide(base_dir: str = ".") -> bool:
    """Create a workflow guide for users"""
    
    guide_content = """# InfiniteTalk Workflow Guide

## 🎯 Quick Start Workflows

### 1. Single Person Image-to-Video

```bash
python generate_infinitetalk.py \\
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \\
    --wav2vec_dir weights/chinese-wav2vec2-base \\
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \\
    --input_json examples/single_example_image.json \\
    --size infinitetalk-480 \\
    --sample_steps 40 \\
    --mode streaming \\
    --motion_frame 9 \\
    --save_file output/single_result
```

### 2. Multi-Person Animation

```bash
python generate_infinitetalk.py \\
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \\
    --wav2vec_dir weights/chinese-wav2vec2-base \\
    --infinitetalk_dir weights/InfiniteTalk/multi/infinitetalk.safetensors \\
    --input_json examples/multi_example_image.json \\
    --size infinitetalk-480 \\
    --sample_steps 40 \\
    --mode streaming \\
    --motion_frame 9 \\
    --save_file output/multi_result
```

### 3. Video-to-Video Dubbing

```bash
python generate_infinitetalk.py \\
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \\
    --wav2vec_dir weights/chinese-wav2vec2-base \\
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \\
    --input_json examples/single_example_video.json \\
    --size infinitetalk-480 \\
    --sample_steps 40 \\
    --mode streaming \\
    --motion_frame 9 \\
    --save_file output/dubbed_result
```

### 4. Fast Generation with LoRA (8 steps)

```bash
python generate_infinitetalk.py \\
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \\
    --wav2vec_dir weights/chinese-wav2vec2-base \\
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \\
    --lora_dir weights/loras/Wan2.1_I2V_14B_FusionX_LoRA.safetensors \\
    --input_json examples/single_example_image.json \\
    --lora_scale 1.0 \\
    --size infinitetalk-480 \\
    --sample_text_guide_scale 1.0 \\
    --sample_audio_guide_scale 2.0 \\
    --sample_steps 8 \\
    --mode streaming \\
    --motion_frame 9 \\
    --save_file output/fast_result
```

### 5. Low VRAM Mode

```bash
python generate_infinitetalk.py \\
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \\
    --wav2vec_dir weights/chinese-wav2vec2-base \\
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \\
    --input_json examples/single_example_image.json \\
    --size infinitetalk-480 \\
    --sample_steps 40 \\
    --num_persistent_param_in_dit 0 \\
    --mode streaming \\
    --motion_frame 9 \\
    --save_file output/lowvram_result
```

## 🔧 Parameter Guide

- `--mode streaming`: For long video generation
- `--mode clip`: For short video chunks
- `--size infinitetalk-480`: 480p resolution
- `--size infinitetalk-720`: 720p resolution  
- `--sample_steps`: Quality vs speed (40=high quality, 8=fast with LoRA)
- `--motion_frame`: Motion amplitude (9=default)
- `--num_persistent_param_in_dit 0`: Low VRAM mode

## 🎨 Tips for Best Results

1. **Audio Quality**: Use clear audio files, preferably 16kHz sample rate
2. **Image Quality**: Use high-resolution portrait images (512x512 or higher)
3. **Lip Sync**: Increase `--sample_audio_guide_scale` (3-5) for better sync
4. **Speed**: Use LoRA models for faster generation
5. **Memory**: Use `--num_persistent_param_in_dit 0` if running out of VRAM

## 🚨 Common Issues

### "Missing infinitetalk.safetensors"
- Run: `python scripts/download_complete_infinitetalk.py`

### "CUDA out of memory"
- Add: `--num_persistent_param_in_dit 0`

### "Poor lip sync"
- Increase: `--sample_audio_guide_scale 4`

### "Workflow template not found"
- Check examples/ directory has .json files
- Run template setup if needed
"""
    
    try:
        guide_path = Path(base_dir) / "WORKFLOW_GUIDE.md"
        guide_path.write_text(guide_content)
        print_status("Created workflow guide: WORKFLOW_GUIDE.md")
        return True
    except Exception as e:
        print_status(f"Failed to create workflow guide: {e}", success=False)
        return False

def main():
    """Main download and setup function"""
    
    parser = argparse.ArgumentParser(description="Complete InfiniteTalk Setup")
    parser.add_argument("--model-base-dir", default="./weights", help="Base directory for models")
    parser.add_argument("--comfyui-model-dir", help="ComfyUI models directory")
    parser.add_argument("--check-only", action="store_true", help="Only check which files exist")
    parser.add_argument("--estimate-size", action="store_true", help="Show download size estimates")
    parser.add_argument("--skip-optional", action="store_true", help="Skip optional models (TTS, LoRA)")
    parser.add_argument("--include-lora", action="store_true", help="Include LoRA models")
    parser.add_argument("--force", action="store_true", help="Force re-download existing files")
    parser.add_argument("--setup-templates", action="store_true", help="Setup workflow templates only")
    
    args = parser.parse_args()
    
    print("🚀 Complete InfiniteTalk Setup and Download")
    print("=" * 60)
    print("Downloads ALL required files including workflow templates")
    print()
    
    # Setup path manager if available
    if HAS_CONFIG_MANAGER:
        manager = ModelPathManager(comfyui_model_dir=args.comfyui_model_dir)
        base_model_dir = manager.base_model_dir
        print_info(f"Using model directory: {base_model_dir}")
        
        # Print environment info
        env_info = manager.env_info
        print_info("Environment detection:")
        for key, value in env_info.items():
            if value:
                print(f"  ✓ {key}")
    else:
        base_model_dir = args.model_base_dir
        print_info(f"Using model directory: {base_model_dir}")
    
    # Setup templates and examples
    if args.setup_templates:
        setup_templates_and_examples()
        create_workflow_guide()
        return
    
    # Get file configurations
    file_configs = get_complete_file_configs()
    
    if args.estimate_size:
        print_section("Download Size Estimates")
        total_essential = 0
        total_optional = 0
        
        for config in file_configs:
            size_str = config["size_estimate"].replace("GB", "").replace("MB", "")
            if "GB" in config["size_estimate"]:
                size_gb = float(size_str)
            else:
                size_gb = float(size_str) / 1000
                
            if config["required"]:
                total_essential += size_gb
                print_info(f"✅ {config['name']}: {config['size_estimate']} (required)")
            else:
                total_optional += size_gb
                print_info(f"🔸 {config['name']}: {config['size_estimate']} (optional)")
        
        print()
        print_info(f"Essential models: ~{total_essential:.1f} GB")
        print_info(f"Optional models: ~{total_optional:.1f} GB")
        print_info(f"Total (all): ~{total_essential + total_optional:.1f} GB")
        return
    
    if args.check_only:
        print_section("File Status Check")
        for config in file_configs:
            existing, total, missing = check_existing_files(config, base_model_dir)
            status = "✅" if existing == total else "❌"
            print_info(f"{status} {config['name']}: {existing}/{total} files present")
            if missing:
                print(f"    Missing: {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}")
        return
    
    # Setup templates first
    setup_templates_and_examples()
    create_workflow_guide()
    
    # Download models
    print_section("Downloading Models")
    
    total_successful = 0
    total_files = 0
    
    for config in file_configs:
        if not config["required"] and args.skip_optional:
            print_status(f"Skipping optional model: {config['name']}")
            continue
            
        if config["name"] in ["FusionX LoRA", "LightX2V LoRA"] and not args.include_lora:
            print_status(f"Skipping LoRA model: {config['name']} (use --include-lora to download)")
            continue
        
        print_section(f"Downloading {config['name']}")
        print_info(config["description"])
        
        # Check existing files first
        existing, total, missing = check_existing_files(config, base_model_dir)
        
        if existing == total and not args.force:
            print_status(f"All files already exist for {config['name']}")
            total_successful += existing
            total_files += total
            continue
        
        # Download files
        successful, total_config = download_model_files(
            config, 
            base_model_dir, 
            include_optional=not args.skip_optional
        )
        
        total_successful += successful
        total_files += total_config
        
        if successful == total_config:
            print_status(f"✅ {config['name']} download complete ({successful}/{total_config})")
        else:
            print_status(f"⚠️  {config['name']} partial download ({successful}/{total_config})", success=False)
    
    # Final summary
    print_section("Download Summary")
    print_info(f"Successfully downloaded: {total_successful}/{total_files} files")
    
    if total_successful == total_files:
        print_status("🎉 All downloads completed successfully!")
        print_info("InfiniteTalk is ready to use!")
        print()
        print_info("Next steps:")
        print_info("1. Test with: python scripts/test_runpod_deployment.py")
        print_info("2. Run generation: python generate_infinitetalk.py --help")
        print_info("3. Start Gradio: python app.py")
        print_info("4. See workflow examples: WORKFLOW_GUIDE.md")
    else:
        print_status(f"⚠️  Some downloads failed ({total_successful}/{total_files})", success=False)
        print_info("You may still be able to use InfiniteTalk with available files")
        print_info("Run with --check-only to see what's missing")

if __name__ == "__main__":
    main()