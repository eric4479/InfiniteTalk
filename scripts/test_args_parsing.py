#!/usr/bin/env python3
"""
Test the enhanced generate_infinitetalk.py argument parsing
without requiring torch and other ML dependencies.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config_manager import ModelPathManager

def test_args_parsing():
    """Test the argument parsing that was added to generate_infinitetalk.py"""
    
    # Simulate the enhanced argument parser from generate_infinitetalk.py
    parser = argparse.ArgumentParser(description="Test InfiniteTalk argument parsing")
    
    # Model path configuration arguments (from our enhancement)
    parser.add_argument(
        "--model_base_dir",
        type=str,
        default=os.getenv('INFINITETALK_MODEL_DIR', './weights'),
        help="Base directory for all models (overrides INFINITETALK_MODEL_DIR env var)"
    )
    parser.add_argument(
        "--comfyui_model_dir", 
        type=str,
        default=os.getenv('COMFYUI_MODEL_DIR', None),
        help="ComfyUI models directory (if running as ComfyUI node)"
    )
    parser.add_argument(
        "--print_paths",
        action="store_true",
        default=False,
        help="Print detected environment and model paths before generation"
    )
    
    # Original model path arguments (modified in our enhancement)
    parser.add_argument(
        "--ckpt_dir",
        type=str,
        default=None,
        help="The path to the Wan checkpoint directory (auto-detected if not specified)."
    )
    parser.add_argument(
        "--wav2vec_dir",
        type=str,
        default=None,
        help="The path to the wav2vec checkpoint directory (auto-detected if not specified)."
    )
    parser.add_argument(
        "--infinitetalk_dir",
        type=str,
        default=None,
        help="The path to the InfiniteTalk checkpoint directory (auto-detected if not specified)."
    )
    
    # Test different argument combinations
    test_cases = [
        # Default case
        [],
        # Custom model directory
        ["--model_base_dir", "test_workspace/models"],
        # With ComfyUI
        ["--model_base_dir", "test_workspace/models", "--comfyui_model_dir", "test_workspace/ComfyUI/models"],
        # With path printing
        ["--print_paths"],
        # Override specific paths
        ["--ckpt_dir", "custom/wan", "--wav2vec_dir", "custom/wav2vec"],
    ]
    
    for i, test_args in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {' '.join(test_args) if test_args else 'Default'} ===")
        
        # Parse arguments
        args = parser.parse_args(test_args)
        
        # Initialize model path manager (like the enhanced generate_infinitetalk.py)
        path_manager = ModelPathManager(
            base_model_dir=args.model_base_dir,
            comfyui_model_dir=args.comfyui_model_dir
        )
        
        # Set model path defaults if not provided (like our enhancement)
        if args.ckpt_dir is None:
            args.ckpt_dir = path_manager.get_model_path('wan_base')
        if args.wav2vec_dir is None:
            args.wav2vec_dir = path_manager.get_model_path('wav2vec') 
        if args.infinitetalk_dir is None:
            args.infinitetalk_dir = path_manager.get_model_path('infinitetalk', 'infinitetalk.safetensors')
        
        print(f"Final resolved paths:")
        print(f"  --ckpt_dir: {args.ckpt_dir}")
        print(f"  --wav2vec_dir: {args.wav2vec_dir}")
        print(f"  --infinitetalk_dir: {args.infinitetalk_dir}")
        
        if args.print_paths:
            print("\nEnvironment info (would be printed):")
            path_manager.print_environment_info()

def main():
    print("🧪 Testing Enhanced generate_infinitetalk.py Argument Parsing")
    print("=" * 60)
    
    test_args_parsing()
    
    print("\n" + "=" * 60)
    print("✅ Argument parsing test completed!")
    print("\n📋 The enhanced generate_infinitetalk.py would work like this:")
    print("   • Automatic model path detection")
    print("   • Environment-specific defaults")
    print("   • ComfyUI integration support")
    print("   • Backward compatibility with existing args")

if __name__ == '__main__':
    main()