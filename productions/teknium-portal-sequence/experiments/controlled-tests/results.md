# Teknium H3 controlled tests

Source reference: [`assets/characters/teknium/source/teknium-character-sheet.jpeg`](../../../../assets/characters/teknium/source/teknium-character-sheet.jpeg)

## Identity contract

- Lean athletic adult male with an angular face.
- Spiky layered turbo-green hair.
- Crimson-red angular visor covering the eyes.
- Dark tactical-green high-collar jacket.
- Black strapped tactical cargo trousers, black combat boots and dark gloves.
- Restrained neon-green accents.
- Rectangular black-and-green Hermes console.
- Graphic-novel/anime visual medium.

## Test matrix

| Test | Keyframe intent | H3 action | Camera | Audio |
|---|---|---|---|---|
| Character proof | Neutral identity and costume | Breathing; subtle hair and fabric movement | Slow Push In | Room tone; no dialogue/music |
| Action proof | Console activation | One control press; one green pulse | Static | Console click and pulse; no dialogue/music |
| Advert proof | Campaign hero composition | Raise console; portal brightens once | Slow Pull Out | Portal resonance and one synth swell |

## Fixed generation parameters

- Image backend: OpenAI Codex `gpt-image-2-medium`, reference-conditioned.
- Video backend: local MiniMax H3 FL2VA INT8.
- Resolution: 832×480.
- Frames: 124 at 24 fps (5.167 seconds).
- Steps: 20.
- Sampler/scheduler: Euler / simple.
- CFG: 1.0.
- Video/audio sigma shift: 12 / 3.
- Seed: 20260830.
- Native H3 audio decoded through the standalone audio VAE.

## Files

- Reusable keyframes: [`assets/characters/teknium/variations`](../../../../assets/characters/teknium/variations/)
- Test clips: [`clips/`](./clips/)
- Exact prompts: [`prompts/`](./prompts/)

The three tests deliberately use one subject, one action and one camera setup each. This isolates identity, movement and audio behaviour before attempting multi-shot content.

## Results — 30 August 2026

All three renders completed and passed full video/audio decode checks. Each output is 832×480, 24 fps, 5.167 seconds, H.264 video with 32 kHz stereo AAC audio.

| Test | Render time | Visual verdict | Audio level | Finding |
|---|---:|---|---|---|
| Character proof | 525 s | CONDITIONAL | mean −50.0 dB; peak −39.0 dB | Identity and costume are highly stable, but the requested subtle motion and Push In are barely visible. Useful identity baseline, weak motion test. |
| Action proof | 440 s | PASS | mean −35.9 dB; peak −18.3 dB | Identity remains stable and the single green console pulse develops coherently without obvious anatomy drift. |
| Advert proof | 425 s | PASS | mean −14.1 dB; peak −2.8 dB | Portal brightening reads clearly, identity remains stable and right-side copy space survives. Audio is strong and should be normalised in post. |
| Ref2VA proof | 435 s | CONDITIONAL | mean −38.1 dB; peak −24.9 dB | The reference sheet retains green hair, red visor, dark tactical clothing and console, but detail and graphic-novel finish are substantially weaker than the Codex-keyframe FL2VA route; the requested button press becomes a broad hand gesture. Use Ref2VA for multi-reference identity guidance, not as the default final-quality shot route. |

All media files passed video/audio decode checks before inclusion.
