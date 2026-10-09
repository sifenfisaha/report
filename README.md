# report

A [Claude Code](https://claude.com/claude-code) skill that turns a meeting recording into a transcript, screen notes and the deliverable you ask for: a summary with decisions and action items, the list of changes someone requested, a scope and hour estimate, a clean PDF or a shareable doc.

Everything runs on your machine. The recording, the audio and the transcript never leave it.

## What it does

Give it a recording and it works through four stages:

1. **Extract.** Probes the file, pulls out 16 kHz audio, measures the volume, and builds contact sheets of the video with a timestamp under every thumbnail (one per minute and one per ten seconds).
2. **Transcribe.** Runs [faster-whisper](https://github.com/SYSTRAN/faster-whisper) locally on the CPU, in the background, with a vocabulary hint so names and product terms come out right. A 45-minute call takes about 8 minutes on a 16-core machine with the default `turbo` model.
3. **Read the screen.** While the transcript runs, it scans the contact sheets for anything shared on screen (a notes document being typed, slides, a dashboard), grabs those frames at full resolution and writes down what they say. In a requirements call the note-taker's list is often the best record of what was asked, and it never appears in the transcript.
4. **Understand, then ask.** It reads the whole transcript, writes meeting notes (participants, timeline, decisions, requests, action items, open questions, corrected mis-hearings) and only then asks what you want out of it. Asking first would waste your time; you cannot choose well before you know what the recording holds.

Then it produces the deliverable: markdown next to the recording, a PDF in a restrained print style with a running footer and page numbers, or a doc through a connector if one is available. Estimates are grounded in your codebase when it is on the same machine.

## Requirements

| Tool | Needed for | Notes |
| --- | --- | --- |
| Claude Code | running the skill | any recent version |
| ffmpeg, ffprobe | audio extraction, frames | `sudo apt install ffmpeg`, `brew install ffmpeg`, `sudo pacman -S ffmpeg` |
| Python 3.10+ | transcription, contact sheets | [uv](https://docs.astral.sh/uv/) is used when present, plain `venv` otherwise |
| Node + Playwright | PDF output only | `npm i -g playwright && npx playwright install chromium` |
| poppler-utils | PDF page counts only | optional |

The first transcription downloads a speech model into `~/.cache/report-skill/models/` (1.6 GB for `turbo`, 480 MB for `small`). Nothing else is fetched after that.

## Install

```bash
git clone https://github.com/sifenfisaha/report.git
cd report && ./install.sh
```

The installer links the checkout into `~/.claude/skills/report` and creates the Python environment, so `git pull` later updates the installed skill in place. Start a new Claude Code session afterwards; the skill appears in the skill list. To install by hand, copy or symlink this folder to `~/.claude/skills/report` and run `scripts/setup.sh`.

## Use

In any project:

```
/report ~/Videos/calls/client-call.mp4
```

or just say what you want in plain words: "here's the recording of Monday's call, what did they ask us to change". The skill triggers on the recording, not on the word "report".

After extraction it asks what you need. Typical answers: a summary with action items, the list of requested changes, an hour estimate for them, a clean transcript, a PDF of any of those.

## What you get

Next to the recording, in a `report/` folder:

```
report/
├── media.json          probe of the file
├── audio16k.wav        mono 16 kHz audio used for transcription
├── audio-levels.txt    mean and peak volume
├── sheets/             overview.jpg, detail-1.jpg … (timestamped thumbnails)
├── frames/             full-resolution frames of anything shared on screen
├── transcript.txt      [mm:ss -> mm:ss] one line per segment
├── transcript.json     the same with exact times
├── screen-notes.md     what was on screen, with timestamps
├── meeting-notes.md    participants, timeline, decisions, requests, action items
└── <deliverable>.md / .pdf
```

## Models and privacy

Transcription uses CTranslate2 builds of Whisper from Hugging Face, fetched with plain `curl` (resumable, and several times faster than the Hub's chunked downloader on slow links). Available names: `tiny`, `base`, `small`, `medium`, `large-v3`, `turbo`, `distil-large-v3`, or any `org/repo` of a CTranslate2 model. `turbo` is the default: accents and proper nouns come out far better than with `small`, at about four to five times real time on a modern CPU. No GPU is needed.

There is no speaker diarization. Speakers are attributed from context and, on video calls, from the active-speaker highlight in the frames; the skill says "the speaker" rather than guess.

## PDF output

`scripts/build_pdf.py` converts markdown or HTML to an A4 PDF: one sans face, hairline rules, tables that keep their header on every page and never split a row, a footer with the document title and "Page X of Y". The rules it follows are in `references/pdf-style.md`; the skill checks every rendered page before handing the file over.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `REPORT_SKILL_HOME` | `~/.cache/report-skill` | environment and model cache |
| `PLAYWRIGHT_MODULE` | auto-detected | path to the `playwright` package if it is not on the module path |
| `CHROME_PATH` | auto-detected | browser to use when Playwright's own Chromium is missing |

## Scripts

All scripts can be run on their own, outside Claude Code.

| Script | Does |
| --- | --- |
| `scripts/setup.sh` | creates the environment, checks tools (idempotent) |
| `scripts/extract.sh <recording> [outdir]` | probe, audio, levels, contact sheets |
| `scripts/transcribe.py <wav> <outdir> [--model turbo] [--language en] [--prompt "…"]` | local transcription |
| `scripts/fetch_model.sh <name>` | downloads a model into the cache |
| `scripts/frame.sh <recording> <seconds> <out.png> [W:H:X:Y] [scale]` | one full-resolution frame, optionally cropped and upscaled |
| `scripts/build_pdf.py <in.md\|in.html> <out.pdf> [--title] [--meta] [--footer]` | PDF in the house style |
| `scripts/render_pdf.js <in.html> <out.pdf> [footer] [a4\|letter]` | the Playwright renderer behind it |

## Troubleshooting

- **Model download crawls.** `fetch_model.sh` already avoids the Hub's chunked downloader. If a mirror is faster for you, download the files by hand into `~/.cache/report-skill/models/<name>/` (`model.bin`, `config.json`, `tokenizer.json`, `vocabulary.*`).
- **`open() got an unexpected keyword argument 'metadata_errors'`.** That is faster-whisper's loader against a new PyAV; the skill never calls it because `transcribe.py` reads the WAV with numpy. If you see it, you ran faster-whisper on a file other than `audio16k.wav`.
- **PDF step says Playwright not found.** Install it globally or set `PLAYWRIGHT_MODULE` to its package directory. On a machine with Chrome but without Playwright's bundled Chromium, set `CHROME_PATH`.
- **Silent transcript.** Check `audio-levels.txt`; a mean near -60 dB means the recording has no usable speech track.

## Repository layout

```
SKILL.md            the skill: what Claude does, step by step
scripts/            the pipeline, usable on their own
assets/report.css   print stylesheet for PDFs
references/         deliverable templates and the PDF style rules
evals/evals.json    test prompts for the skill-creator benchmark loop
install.sh          links the checkout into ~/.claude/skills and runs setup
```

## License

MIT. See `LICENSE`.
