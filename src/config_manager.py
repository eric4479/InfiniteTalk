"""
Configuration manager for handling model paths across different environments.

This module provides utilities for managing model paths when running InfiniteTalk
in different environments like local development, Runpod, GCP, or as ComfyUI nodes.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union


class ModelPathManager:
    """Manages model paths for different deployment environments"""
    
    def __init__(self, base_model_dir: Optional[str] = None, comfyui_model_dir: Optional[str] = None):
        """
        Initialize the model path manager.
        
        Args:
            base_model_dir: Base directory for all models (defaults to env var or ./weights)
            comfyui_model_dir: ComfyUI models directory (defaults to env var or auto-detect)
        """
        self.base_model_dir = base_model_dir or os.getenv('INFINITETALK_MODEL_DIR', './weights')
        self.comfyui_model_dir = comfyui_model_dir or os.getenv('COMFYUI_MODEL_DIR', None)
        
        # Auto-detect ComfyUI if not specified
        if self.comfyui_model_dir is None:
            self.comfyui_model_dir = self._detect_comfyui_models_dir()
        
        # Environment detection
        self.env_info = self._detect_environment()
        
        # Model path mappings
        self._model_paths = {
            'wan_base': 'Wan2.1-I2V-14B-480P',
            'wav2vec': 'chinese-wav2vec2-base', 
            'infinitetalk': 'InfiniteTalk/single',
            'kokoro': 'Kokoro-82M',
            'loras': 'loras',
            'vae': 'vae',
            'checkpoints': 'checkpoints',
            'audio_encoders': 'audio_encoders'
        }
        
    def _detect_environment(self) -> Dict[str, bool]:
        """Detect runtime environment and set appropriate defaults"""
        env_info = {
            'is_runpod': 'RUNPOD_POD_ID' in os.environ,
            'is_colab': 'COLAB_GPU' in os.environ,
            'is_gcp': 'GOOGLE_CLOUD_PROJECT' in os.environ or 'GCP_PROJECT' in os.environ,
            'is_local': not any([
                'RUNPOD_POD_ID' in os.environ,
                'COLAB_GPU' in os.environ,
                'GOOGLE_CLOUD_PROJECT' in os.environ,
                'GCP_PROJECT' in os.environ,
                'KUBERNETES_SERVICE_HOST' in os.environ
            ]),
            'has_comfyui': self.comfyui_model_dir is not None
        }
        
        # Set environment-specific defaults
        if env_info['is_runpod'] and not os.getenv('INFINITETALK_MODEL_DIR'):
            self.base_model_dir = '/workspace/models'
            
        return env_info
    
    def _detect_comfyui_models_dir(self) -> Optional[str]:
        """Try to detect ComfyUI installation and models directory"""
        possible_paths = [
            "/workspace/ComfyUI/models",
            "./ComfyUI/models", 
            "../ComfyUI/models",
            "../../ComfyUI/models",
            "/content/ComfyUI/models"  # For Colab
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
                
        return None
        
    def get_model_path(self, model_type: str, filename: Optional[str] = None) -> str:
        """
        Get model path based on environment and model type.
        
        Args:
            model_type: Type of model (wan_base, wav2vec, infinitetalk, etc.)
            filename: Optional filename to append to the path
            
        Returns:
            Full path to the model or model directory
        """
        
        # For ComfyUI integration with specific model types
        if self.comfyui_model_dir and model_type in ['checkpoints', 'loras', 'vae']:
            base_path = Path(self.comfyui_model_dir) / model_type
            return str(base_path / filename) if filename else str(base_path)
        
        # Standard model paths
        if model_type in self._model_paths:
            base_path = Path(self.base_model_dir) / self._model_paths[model_type]
            return str(base_path / filename) if filename else str(base_path)
        
        # Fallback for unknown types
        base_path = Path(self.base_model_dir) / model_type
        return str(base_path / filename) if filename else str(base_path)
    
    def ensure_model_directory(self, model_type: str) -> Path:
        """
        Ensure model directory exists and return Path object.
        
        Args:
            model_type: Type of model directory to create
            
        Returns:
            Path object for the model directory
        """
        path = Path(self.get_model_path(model_type))
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def get_all_model_paths(self) -> Dict[str, str]:
        """
        Get all configured model paths.
        
        Returns:
            Dictionary mapping model types to their paths
        """
        return {
            model_type: self.get_model_path(model_type) 
            for model_type in self._model_paths.keys()
        }
    
    def print_environment_info(self):
        """Print information about the detected environment and paths"""
        print("=== InfiniteTalk Model Path Configuration ===")
        print(f"Base model directory: {self.base_model_dir}")
        print(f"ComfyUI model directory: {self.comfyui_model_dir}")
        print()
        
        print("Environment detection:")
        for env_type, detected in self.env_info.items():
            status = "✓" if detected else "✗"
            print(f"  {status} {env_type}: {detected}")
        print()
        
        print("Model paths:")
        for model_type, path in self.get_all_model_paths().items():
            exists = "✓" if Path(path).exists() else "✗"
            print(f"  {exists} {model_type}: {path}")
        print()


# Global instance for backward compatibility
model_path_manager = ModelPathManager()


def get_model_path(model_type: str, filename: Optional[str] = None) -> str:
    """Convenience function to get model path using global manager"""
    return model_path_manager.get_model_path(model_type, filename)


def ensure_model_directory(model_type: str) -> Path:
    """Convenience function to ensure model directory using global manager"""
    return model_path_manager.ensure_model_directory(model_type)