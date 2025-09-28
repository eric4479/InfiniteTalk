"""
ComfyUI integration handler for InfiniteTalk.

This module provides utilities for integrating InfiniteTalk with ComfyUI,
including proper model path handling and node creation helpers.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union, List

from config_manager import ModelPathManager


class ComfyUIModelHandler:
    """Handle model paths and integration for ComfyUI custom nodes"""
    
    def __init__(self, comfyui_base_path: Optional[str] = None):
        """
        Initialize ComfyUI model handler.
        
        Args:
            comfyui_base_path: Path to ComfyUI models directory
        """
        self.comfyui_models = self._detect_comfyui_models(comfyui_base_path)
        self.path_manager = ModelPathManager(comfyui_model_dir=str(self.comfyui_models) if self.comfyui_models else None)
        
    def _detect_comfyui_models(self, provided_path: Optional[str]) -> Optional[Path]:
        """Try to detect ComfyUI models directory"""
        if provided_path and Path(provided_path).exists():
            return Path(provided_path)
        
        # Try environment variable
        env_path = os.getenv('COMFYUI_MODEL_DIR')
        if env_path and Path(env_path).exists():
            return Path(env_path)
        
        # Try common ComfyUI installation paths
        possible_paths = [
            "/workspace/ComfyUI/models",           # Runpod/Docker
            "./ComfyUI/models",                    # Local relative
            "../ComfyUI/models",                   # Custom nodes folder
            "../../ComfyUI/models",                # Nested custom nodes
            "/content/ComfyUI/models",             # Google Colab
            Path.home() / "ComfyUI" / "models",    # User home
        ]
        
        for path in possible_paths:
            path_obj = Path(path)
            if path_obj.exists() and path_obj.is_dir():
                return path_obj
                
        return None
    
    def get_model_path(self, model_type: str, filename: Optional[str] = None) -> str:
        """
        Get model path compatible with ComfyUI structure.
        
        Args:
            model_type: Type of model (checkpoints, loras, vae, etc.)
            filename: Optional filename to append
            
        Returns:
            Full path to model or model directory
        """
        if not self.comfyui_models:
            # Fallback to standard InfiniteTalk paths
            return self.path_manager.get_model_path(model_type, filename)
        
        # ComfyUI-specific model type mappings
        comfyui_mapping = {
            'wan_base': 'checkpoints',
            'infinitetalk': 'infinitetalk',
            'loras': 'loras',
            'vae': 'vae',
            'wav2vec': 'audio_encoders',
            'kokoro': 'audio_encoders',
            'checkpoints': 'checkpoints',
            'controlnet': 'controlnet',
            'embeddings': 'embeddings',
            'upscale_models': 'upscale_models'
        }
        
        # Map to ComfyUI structure
        comfyui_type = comfyui_mapping.get(model_type, model_type)
        model_dir = self.comfyui_models / comfyui_type
        
        # Ensure directory exists
        model_dir.mkdir(parents=True, exist_ok=True)
        
        if filename:
            return str(model_dir / filename)
        return str(model_dir)
    
    def create_node_paths(self) -> Dict[str, str]:
        """
        Create standard paths for ComfyUI node configuration.
        
        Returns:
            Dictionary of model paths for node inputs
        """
        return {
            'wan_checkpoint': self.get_model_path('checkpoints'),
            'infinitetalk_weights': self.get_model_path('infinitetalk', 'infinitetalk.safetensors'),
            'wav2vec_model': self.get_model_path('audio_encoders'),
            'lora_dir': self.get_model_path('loras'),
            'vae_dir': self.get_model_path('vae')
        }
    
    def validate_models(self) -> Dict[str, bool]:
        """
        Validate that required models exist.
        
        Returns:
            Dictionary mapping model types to existence status
        """
        required_models = {
            'wan_base': self.path_manager.get_model_path('wan_base'),
            'infinitetalk': self.path_manager.get_model_path('infinitetalk', 'infinitetalk.safetensors'),
            'wav2vec': self.path_manager.get_model_path('wav2vec')
        }
        
        validation = {}
        for model_type, path in required_models.items():
            validation[model_type] = Path(path).exists()
        
        return validation
    
    def setup_comfyui_symlinks(self) -> List[str]:
        """
        Create symlinks in ComfyUI models directory for InfiniteTalk models.
        
        Returns:
            List of created symlink descriptions
        """
        if not self.comfyui_models:
            return ["ComfyUI models directory not found, skipping symlinks"]
        
        created_links = []
        
        # Create symlinks for main models
        symlink_configs = [
            {
                'source': self.path_manager.get_model_path('wan_base'),
                'target': self.comfyui_models / 'checkpoints' / 'wan_base',
                'description': 'Wan base model'
            },
            {
                'source': self.path_manager.get_model_path('wav2vec'),
                'target': self.comfyui_models / 'audio_encoders' / 'wav2vec2',
                'description': 'Wav2Vec audio encoder'
            },
            {
                'source': self.path_manager.get_model_path('infinitetalk').replace('/infinitetalk.safetensors', ''),
                'target': self.comfyui_models / 'infinitetalk',
                'description': 'InfiniteTalk weights'
            }
        ]
        
        for config in symlink_configs:
            source_path = Path(config['source'])
            target_path = config['target']
            
            if not source_path.exists():
                created_links.append(f"⚠️  Source not found for {config['description']}: {source_path}")
                continue
            
            try:
                # Ensure parent directory exists
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Remove existing symlink or directory
                if target_path.exists() or target_path.is_symlink():
                    if target_path.is_symlink():
                        target_path.unlink()
                    # Don't remove actual directories automatically
                
                # Create symlink
                target_path.symlink_to(source_path, target_is_directory=source_path.is_dir())
                created_links.append(f"✓ Created symlink for {config['description']}: {target_path} -> {source_path}")
                
            except OSError as e:
                created_links.append(f"✗ Failed to create symlink for {config['description']}: {e}")
        
        return created_links
    
    def get_comfyui_node_config(self) -> Dict:
        """
        Generate configuration dictionary for ComfyUI nodes.
        
        Returns:
            Configuration dictionary with all necessary paths
        """
        return {
            "model_paths": self.create_node_paths(),
            "environment": self.path_manager.env_info,
            "comfyui_models_dir": str(self.comfyui_models) if self.comfyui_models else None,
            "base_model_dir": self.path_manager.base_model_dir,
            "models_valid": self.validate_models()
        }
    
    def print_comfyui_info(self):
        """Print ComfyUI integration information"""
        print("=== ComfyUI Integration Status ===")
        print(f"ComfyUI models directory: {self.comfyui_models or 'Not detected'}")
        print()
        
        if self.comfyui_models:
            print("Model paths for ComfyUI:")
            for model_type, path in self.create_node_paths().items():
                exists = "✓" if Path(path).exists() else "✗"
                print(f"  {exists} {model_type}: {path}")
        else:
            print("ComfyUI not detected - using standard InfiniteTalk paths")
        
        print()
        print("Model validation:")
        validation = self.validate_models()
        for model_type, valid in validation.items():
            status = "✓" if valid else "✗"
            print(f"  {status} {model_type}: {'Valid' if valid else 'Missing'}")
        print()


def create_comfyui_handler(comfyui_path: Optional[str] = None) -> ComfyUIModelHandler:
    """
    Factory function to create ComfyUI handler.
    
    Args:
        comfyui_path: Optional path to ComfyUI models directory
        
    Returns:
        Configured ComfyUIModelHandler instance
    """
    return ComfyUIModelHandler(comfyui_path)


def setup_comfyui_environment() -> Dict[str, str]:
    """
    Setup environment variables for ComfyUI integration.
    
    Returns:
        Dictionary of set environment variables
    """
    handler = create_comfyui_handler()
    
    env_vars = {}
    
    # Set model paths as environment variables
    if handler.comfyui_models:
        env_vars['COMFYUI_MODEL_DIR'] = str(handler.comfyui_models)
        os.environ['COMFYUI_MODEL_DIR'] = str(handler.comfyui_models)
    
    # Set InfiniteTalk model directory
    env_vars['INFINITETALK_MODEL_DIR'] = handler.path_manager.base_model_dir
    os.environ['INFINITETALK_MODEL_DIR'] = handler.path_manager.base_model_dir
    
    # Set specific model paths
    model_paths = handler.create_node_paths()
    for key, value in model_paths.items():
        env_var = f'INFINITETALK_{key.upper()}'
        env_vars[env_var] = value
        os.environ[env_var] = value
    
    return env_vars


# For backward compatibility and easy imports
comfyui_handler = None

def get_comfyui_handler() -> ComfyUIModelHandler:
    """Get global ComfyUI handler instance"""
    global comfyui_handler
    if comfyui_handler is None:
        comfyui_handler = create_comfyui_handler()
    return comfyui_handler