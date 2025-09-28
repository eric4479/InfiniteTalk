# InfiniteTalk Workflow Guide

## 🎯 Quick Start Workflows

### 1. Single Person Image-to-Video

```bash
python generate_infinitetalk.py \
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \
    --wav2vec_dir weights/chinese-wav2vec2-base \
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \
    --input_json examples/single_example_image.json \
    --size infinitetalk-480 \
    --sample_steps 40 \
    --mode streaming \
    --motion_frame 9 \
    --save_file output/single_result
```

### 2. Multi-Person Animation

```bash
python generate_infinitetalk.py \
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \
    --wav2vec_dir weights/chinese-wav2vec2-base \
    --infinitetalk_dir weights/InfiniteTalk/multi/infinitetalk.safetensors \
    --input_json examples/multi_example_image.json \
    --size infinitetalk-480 \
    --sample_steps 40 \
    --mode streaming \
    --motion_frame 9 \
    --save_file output/multi_result
```

### 3. Video-to-Video Dubbing

```bash
python generate_infinitetalk.py \
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \
    --wav2vec_dir weights/chinese-wav2vec2-base \
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \
    --input_json examples/single_example_video.json \
    --size infinitetalk-480 \
    --sample_steps 40 \
    --mode streaming \
    --motion_frame 9 \
    --save_file output/dubbed_result
```

### 4. Fast Generation with LoRA (8 steps)

```bash
python generate_infinitetalk.py \
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \
    --wav2vec_dir weights/chinese-wav2vec2-base \
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \
    --lora_dir weights/loras/Wan2.1_I2V_14B_FusionX_LoRA.safetensors \
    --input_json examples/single_example_image.json \
    --lora_scale 1.0 \
    --size infinitetalk-480 \
    --sample_text_guide_scale 1.0 \
    --sample_audio_guide_scale 2.0 \
    --sample_steps 8 \
    --mode streaming \
    --motion_frame 9 \
    --save_file output/fast_result
```

### 5. Low VRAM Mode

```bash
python generate_infinitetalk.py \
    --ckpt_dir weights/Wan2.1-I2V-14B-480P \
    --wav2vec_dir weights/chinese-wav2vec2-base \
    --infinitetalk_dir weights/InfiniteTalk/single/infinitetalk.safetensors \
    --input_json examples/single_example_image.json \
    --size infinitetalk-480 \
    --sample_steps 40 \
    --num_persistent_param_in_dit 0 \
    --mode streaming \
    --motion_frame 9 \
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
