#!/usr/bin/env python3
"""Render eight high-energy Teknium shots with a quality/speed hybrid H3 policy."""
import json
import os
import shutil
import sys
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[3]
BASE = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8189").rstrip("/")
COMFY_INPUT = Path(os.environ["COMFYUI_INPUT_DIR"])
KEYFRAME_DIR = REPO_ROOT / "assets/characters/teknium/variations"
FINAL_DIR = REPO_ROOT / "productions/teknium-portal-sequence/v2/clips"
FINAL_DIR.mkdir(parents=True, exist_ok=True)

SHOTS = [
    {"id":"01-entry","image":"shot-01-entry.png","steps":20,"turbo":False,"prompt":"[Shot 1] Preserve Teknium's exact green hair, red visor, dark tactical outfit, console and the dark teal command deck. Teknium sprints two powerful strides from the side doorway toward the dormant circular portal, console locked in his left hand and straps trailing behind. The camera performs a low Truck Right following his forward drive. Movement quality: sudden, strong, direct and bound. No one speaks.\n\noverall_soundscape:\nHard boot strikes, rushing fabric, fast breath and a rising electrical room tone. No dialogue.\n\nnon_diegetic_music:\nN/A"},
    {"id":"02-boot-stop","image":"shot-02-boot-stop.png","steps":6,"turbo":True,"prompt":"[Shot 1] Preserve the exact black combat boot, strapped trouser cuff, wet metal floor and distant circular portal. Teknium's boot skids sharply into a planted stop as a short spray of green sparks and grit travels backward across the floor. The camera remains Static at floor level. Movement quality: sudden, strong, direct and bound. No one speaks.\n\noverall_soundscape:\nA heavy boot scrape, brief sparks and one low metallic impact. No dialogue.\n\nnon_diegetic_music:\nN/A"},
    {"id":"03-console-swipe","image":"shot-03-console-swipe.png","steps":6,"turbo":True,"prompt":"[Shot 1] Preserve Teknium's exact rear silhouette, green hair, tactical jacket, gloves, rectangular console and the same dark command deck. His right gloved hand makes one fast deliberate sweep across the console and concentric green interface arcs ignite beneath his fingers. The camera performs a short Push In over his shoulder toward the console and dormant portal. Movement quality: sudden, light, direct and bound. No one speaks.\n\noverall_soundscape:\nOne tactile swipe, layered interface chimes and a strengthening console hum. No dialogue.\n\nnon_diegetic_music:\nN/A"},
    {"id":"04-visor-flash","image":"shot-04-visor-flash.png","steps":6,"turbo":True,"prompt":"[Shot 1] Preserve Teknium's exact angular face, turbo-green spiky hair, crimson visor and high tactical collar. The red visor flashes once from dark crimson to intense red while reflected green portal rings sweep across its surface and his hair lifts in the energy wind. The camera performs a rapid Push In at a slight Dutch angle. Movement quality: sudden, strong, direct and bound. No one speaks.\n\noverall_soundscape:\nA sharp electronic lock-on tone, rising wind and one low heartbeat-like impact. No dialogue.\n\nnon_diegetic_music:\nN/A"},
    {"id":"05-energy-pulse","image":"shot-05-energy-pulse.png","steps":20,"turbo":False,"prompt":"[Shot 1] Preserve Teknium's exact identity, tactical outfit, console, anatomy and the same command deck. Teknium drives the console forward and releases one concentrated green energy pulse that crosses the room and strikes the circular portal ring; hair, straps and dust snap backward from the force. The camera performs an Arc Shot to the right around his grounded stance. Movement quality: sudden, strong, direct and bound. No one speaks.\n\noverall_soundscape:\nA charging whine, forceful energy discharge, floor vibration and scattering grit. No dialogue.\n\nnon_diegetic_music:\nN/A"},
    {"id":"06-system-cascade","image":"shot-06-system-cascade.png","steps":6,"turbo":True,"prompt":"[Shot 1] Preserve the same industrial deck, Teknium's exact silhouette and the circular portal geometry. Green floor conduits, wall strips and ceiling lights activate in one rapid cascade travelling from the foreground toward the portal while steam and dust sweep through the space. Teknium remains braced at the centre. The camera performs a controlled Pull Out from the overhead three-quarter angle. Movement quality: sustained, strong, direct and free. No one speaks.\n\noverall_soundscape:\nSequential relay clicks, electrical surges, vented steam and a deepening structural hum. No dialogue.\n\nnon_diegetic_music:\nN/A"},
    {"id":"07-portal-open","image":"shot-07-portal-open.png","steps":20,"turbo":False,"prompt":"[Shot 1] Preserve Teknium's exact identity, clothing, console and circular portal. The circular portal tears open in one violent expansion behind him, concentric rings rotating as turbulent green depth forms; Teknium shields his visor and holds his ground while hair, straps, dust and fragments pull toward the opening. The camera performs a dramatic low Push In. Movement quality: sustained, strong, direct and bound. No one speaks.\n\noverall_soundscape:\nA deep dimensional rupture, accelerating wind, rotating machinery and debris rattling across metal. No dialogue.\n\nnon_diegetic_music:\nN/A"},
    {"id":"08-portal-leap","image":"shot-08-portal-leap.png","steps":20,"turbo":False,"prompt":"[Shot 1] Preserve Teknium's exact profile, green hair, red visor, tactical outfit, console and the fully open circular portal. Teknium launches forward in one committed leap and passes into the portal, leading foot and torso travelling cleanly through the threshold as straps and particles stream behind him. The camera performs a fast Truck Right matching his motion. Movement quality: sudden, strong, direct and free. No one speaks.\n\noverall_soundscape:\nOne explosive foot launch, rushing fabric, particle suction and a clean portal transit impact. No dialogue.\n\nnon_diegetic_music:\nN/A"},
]

NEGATIVE = "identity drift, costume change, visor change, duplicate person, extra limbs, malformed hands, frozen pose, slideshow, subtitles, captions, readable text, blur"


def fetch(path):
    with urlopen(BASE + path, timeout=30) as response:
        return json.load(response)


def render(shot, index):
    source_image = KEYFRAME_DIR / shot["image"]
    if not source_image.is_file():
        raise FileNotFoundError(source_image)
    COMFY_INPUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_image, COMFY_INPUT / shot["image"])
    model_link = ["1", 0]
    workflow = {
        "1":{"class_type":"UNETLoader","inputs":{"unet_name":"diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors","weight_dtype":"default"}},
        "2":{"class_type":"CLIPLoader","inputs":{"clip_name":"text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors","type":"minimax"}},
        "3":{"class_type":"VAELoader","inputs":{"vae_name":"vae/minimax_h3_video_vae_fp16.safetensors"}},
        "4":{"class_type":"VAELoader","inputs":{"vae_name":"vae/minimax_h3_audio_vae_fp32.safetensors"}},
        "5":{"class_type":"LoadImage","inputs":{"image":shot["image"]}},
        "6":{"class_type":"CLIPTextEncode","inputs":{"text":NEGATIVE,"clip":["2",0]}},
        "7":{"class_type":"MiniMaxH3ImageToVideo","inputs":{"clip":["2",0],"vae":["3",0],"prompt":shot["prompt"],"width":832,"height":480,"length":124,"first_frame":["5",0]}},
    }
    if shot["turbo"]:
        workflow["15"]={"class_type":"LoraLoaderModelOnly","inputs":{"model":["1",0],"lora_name":"minimax_h3_turbo_v4_step600_ema_pruned_comfyui.safetensors","strength_model":1.0}}
        model_link=["15",0]
    workflow.update({
        "8":{"class_type":"MiniMaxH3SigmaShift","inputs":{"model":model_link,"shift_video":12.0,"shift_audio":3.0}},
        "9":{"class_type":"KSampler","inputs":{"model":["8",0],"seed":20260830+index,"steps":shot["steps"],"cfg":1.0,"sampler_name":"euler","scheduler":"simple","positive":["7",0],"negative":["6",0],"latent_image":["7",1],"denoise":1.0}},
        "10":{"class_type":"VAEDecode","inputs":{"samples":["9",0],"vae":["3",0]}},
        "11":{"class_type":"VAEDecodeAudio","inputs":{"samples":["9",0],"vae":["4",0]}},
        "12":{"class_type":"CreateVideo","inputs":{"images":["10",0],"audio":["11",0],"fps":24.0}},
        "13":{"class_type":"SaveVideo","inputs":{"video":["12",0],"filename_prefix":f"nrcu-v2/shot-{shot['id']}","format":"mp4","codec":"h264"}},
    })
    body=json.dumps({"prompt":workflow,"client_id":str(uuid.uuid4())}).encode()
    request=Request(BASE+"/prompt",data=body,headers={"Content-Type":"application/json"})
    try:
        with urlopen(request,timeout=30) as response: submission=json.load(response)
    except HTTPError as error:
        raise RuntimeError(error.read().decode("utf-8",errors="replace")) from error
    if submission.get("node_errors"): raise RuntimeError(json.dumps(submission["node_errors"],indent=2))
    pid=submission["prompt_id"]; print(f"SUBMITTED {shot['id']} steps={shot['steps']} turbo={shot['turbo']} {pid}",flush=True)
    started=time.time()
    for _ in range(600):
        time.sleep(5); history=fetch("/history/"+pid)
        if pid not in history: continue
        item=history[pid]
        if item.get("status",{}).get("status_str")=="error": raise RuntimeError(json.dumps(item.get("status"),indent=2))
        output=item.get("outputs",{}).get("13",{}); media=output.get("videos") or output.get("images") or []
        if media:
            result = media[0]
            destination = FINAL_DIR / f"shot-{shot['id']}.mp4"
            query = urlencode({
                "filename": result["filename"],
                "subfolder": result.get("subfolder", ""),
                "type": result.get("type", "output"),
            })
            with urlopen(BASE + "/view?" + query, timeout=120) as response:
                destination.write_bytes(response.read())
            print(f"COMPLETED {shot['id']} {destination} elapsed={time.time()-started:.0f}s",flush=True)
            return
        raise RuntimeError(f"{shot['id']} completed without video")
    raise TimeoutError(shot["id"])


def main():
    for i,shot in enumerate(SHOTS,1): render(shot,i)
    print(f"ALL_OK {len(SHOTS)}/{len(SHOTS)}",flush=True)

if __name__=="__main__":
    try: main()
    except Exception as error:
        print(f"FAILED {type(error).__name__}: {error}",file=sys.stderr,flush=True); raise
