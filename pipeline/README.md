# NRCU generation pipeline

A small, backend-aware workflow rather than a framework.

```text
character profile + source sheet
→ storyboard
→ approved keyframes
→ H3 shot renders
→ edit
→ voice, music and effects
→ master
→ production folder
```

## Current routes

- **Keyframes:** Codex reference-conditioned image generation.
- **Final video:** MiniMax H3 FL2VA, with 20 steps for heavy action and six-step Turbo for simpler shots.
- **Preview video:** four-step FastH3 LoRA for animatics and low-motion inserts.
- **Reference guidance:** Ref2VA where multiple images, video or audio references are needed.
- **Continuity:** LongVideos for planning and state; important beats still use approved keyframes.
- **Audio:** native H3 effects, Kokoro/reference voices, MiniMax Music 3 and FFmpeg mastering.

Model weights and third-party repositories are intentionally excluded. See [`docs/production-tooling.md`](../docs/production-tooling.md) for sources and requirements.

## Reproducing the Teknium revision

With the required models available in a local ComfyUI instance:

```bash
COMFYUI_URL=http://127.0.0.1:8189 \
COMFYUI_INPUT_DIR=/path/to/ComfyUI/input \
python3 pipeline/examples/teknium/render_revision.py

python3 pipeline/examples/teknium/assemble_revision.py
```

The renderer stages repository keyframes into ComfyUI, downloads completed clips through the local API and writes them into the production directory. The assembler requires `ffmpeg` and `ffprobe`.
