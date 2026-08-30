#!/usr/bin/env python3
"""Assemble the energetic eight-shot Teknium revision with beat-synced cuts."""
import json
import subprocess
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[3]
ROOT=REPO_ROOT/'productions/teknium-portal-sequence/v2'
CLIPS=ROOT/'clips'
MUSIC=ROOT/'audio/score.flac'
VOICE=ROOT/'audio/narration.wav'
OUTPUT=ROOT/'final.mp4'

# Start offsets choose the useful action window; durations align cuts to measured score accents.
SHOTS=[
 ('shot-01-entry.mp4',0.00,5.00),
 ('shot-02-boot-stop.mp4',1.00,1.75),
 ('shot-03-console-swipe.mp4',0.30,4.75),
 ('shot-04-visor-flash.mp4',1.50,1.50),
 ('shot-05-energy-pulse.mp4',0.00,3.25),
 ('shot-06-system-cascade.mp4',0.50,3.75),
 ('shot-07-portal-open.mp4',0.50,3.25),
 ('shot-08-portal-leap.mp4',0.00,5.00),
]
for name,_,_ in SHOTS:
 if not (CLIPS/name).is_file(): raise FileNotFoundError(CLIPS/name)
for p in (MUSIC,VOICE):
 if not p.is_file(): raise FileNotFoundError(p)

cmd=['ffmpeg','-y','-v','error']
for name,_,_ in SHOTS: cmd += ['-i',str(CLIPS/name)]
cmd += ['-i',str(MUSIC),'-i',str(VOICE)]

filters=[]
for i,(_,start,duration) in enumerate(SHOTS):
 end=start+duration
 filters.append(f'[{i}:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,scale=1280:738:flags=lanczos,crop=1280:720,format=yuv420p[v{i}]')
 filters.append(f'[{i}:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,aresample=48000[a{i}]')
filters += [
 'color=c=white:s=1280x720:r=24:d=0.083,format=yuv420p[flashv]',
 'anullsrc=r=48000:cl=stereo:d=0.083[flasha]',
 '[v0][a0][v1][a1][v2][a2][v3][a3][flashv][flasha][v4][a4][v5][a5][v6][a6][v7][a7]concat=n=9:v=1:a=1[cutv][cuta]',
 '[cutv]tpad=stop_mode=clone:stop_duration=0.75[vout]',
 '[cuta]apad=pad_dur=0.75,atrim=0:29.083,volume=0.85[native]',
 '[8:a]aresample=48000,atrim=0:29.083,afade=t=in:st=0:d=0.4,afade=t=out:st=28.083:d=1.0,volume=0.24[music]',
 '[9:a]aresample=48000,volume=1.05,adelay=7750|7750,asplit=2[voice][sidechain]',
 '[music][sidechain]sidechaincompress=threshold=0.02:ratio=7:attack=15:release=250[ducked]',
 '[native][ducked][voice]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:LRA=11:TP=-1.0,aresample=48000[aout]',
]
cmd += ['-filter_complex',';'.join(filters),'-map','[vout]','-map','[aout]','-c:v','libx264','-preset','slow','-crf','18','-profile:v','high','-level','4.1','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(OUTPUT)]
subprocess.run(cmd,check=True)
subprocess.run(['ffmpeg','-v','error','-i',str(OUTPUT),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels','-of','json',str(OUTPUT)],text=True))
(ROOT/'revision-report.json').write_text(json.dumps({'output':str(OUTPUT.relative_to(REPO_ROOT)),'shots':SHOTS,'flash_seconds':0.083,'end_hold_seconds':0.75,'voice_start_seconds':7.75,'probe':probe},indent=2)+'\n')
print(json.dumps(probe,indent=2))
