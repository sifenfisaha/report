#!/usr/bin/env python3
"""Local transcription with faster-whisper (CPU, int8).

usage: transcribe.py <audio16k.wav> <outdir> [--model turbo] [--language en]
                     [--prompt "names, products, tools"] [--threads N]

Writes <outdir>/transcript.txt ([mm:ss -> mm:ss] text per line) and
transcript.json. Progress goes to stdout; the last line is "DONE ...".
The WAV must be 16 kHz mono PCM (extract.sh makes it so); it is loaded with
numpy because faster-whisper's own loader breaks on recent PyAV releases.
"""
import argparse
import json
import os
import subprocess
import sys
import time
import wave

import numpy as np

HOME = os.environ.get("REPORT_SKILL_HOME", os.path.expanduser("~/.cache/report-skill"))
HERE = os.path.dirname(os.path.abspath(__file__))

ap = argparse.ArgumentParser()
ap.add_argument("wav")
ap.add_argument("outdir")
ap.add_argument("--model", default="turbo")
ap.add_argument("--language", default=None, help="ISO code; default auto-detect on the first 30 s")
ap.add_argument("--prompt", default=None, help="vocabulary hint: names, product terms, tools")
ap.add_argument("--threads", type=int, default=0)
ap.add_argument("--beam", type=int, default=5)
args = ap.parse_args()


def model_dir(name):
    if os.path.isdir(name) and os.path.exists(os.path.join(name, "model.bin")):
        return name
    d = os.path.join(HOME, "models", name.split("/")[-1])
    if not os.path.exists(os.path.join(d, "model.bin")):
        print(f"[{name}] not cached, downloading", flush=True)
        subprocess.run(["bash", os.path.join(HERE, "fetch_model.sh"), name], check=True)
    return d


def load_wav(path):
    with wave.open(path, "rb") as w:
        if w.getframerate() != 16000 or w.getnchannels() != 1 or w.getsampwidth() != 2:
            sys.exit("expected 16 kHz mono 16-bit PCM; run extract.sh first")
        data = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
    return data.astype(np.float32) / 32768.0


def stamp(s):
    s = int(s)
    return f"{s // 60:02d}:{s % 60:02d}"


from faster_whisper import WhisperModel  # noqa: E402  (import after the arg check so --help stays fast)

t0 = time.time()
tag = args.model.split("/")[-1]
print(f"[{tag}] loading model", flush=True)
model = WhisperModel(model_dir(args.model), device="cpu", compute_type="int8",
                     cpu_threads=args.threads or os.cpu_count() or 4)
audio = load_wav(args.wav)
print(f"[{tag}] transcribing {len(audio) / 16000 / 60:.1f} min of audio", flush=True)
segments, info = model.transcribe(
    audio, beam_size=args.beam, language=args.language, initial_prompt=args.prompt,
    vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500),
    condition_on_previous_text=False,
)
print(f"[{tag}] language={info.language} p={info.language_probability:.2f}", flush=True)

os.makedirs(args.outdir, exist_ok=True)
out = []
with open(os.path.join(args.outdir, "transcript.txt"), "w") as f:
    for s in segments:
        text = s.text.strip()
        f.write(f"[{stamp(s.start)} -> {stamp(s.end)}] {text}\n")
        f.flush()
        out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": text})
        if len(out) % 25 == 0:
            print(f"[{tag}] {len(out)} segments, at {s.end / 60:.1f} min, {time.time() - t0:.0f}s elapsed", flush=True)
with open(os.path.join(args.outdir, "transcript.json"), "w") as f:
    json.dump({"model": tag, "language": info.language, "segments": out}, f, indent=1)
print(f"DONE {len(out)} segments in {time.time() - t0:.0f}s -> {args.outdir}/transcript.txt", flush=True)
