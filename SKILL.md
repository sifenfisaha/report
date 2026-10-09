---
name: report
description: Turn a meeting recording (screen recording, Zoom/Meet/Teams export, voice memo; mp4, mkv, webm, mov, mp3, m4a, wav) into a transcript, screen notes and then the deliverable the user picks - a summary with decisions and action items, the list of changes someone asked for, a scope and hour estimate, a clean PDF or a shareable doc. Use this skill whenever the user points at a recording or a call and wants anything out of it ("what did the boss ask for", "extract the transcript", "write up the meeting", "make a report from this video", "what changes did they want"), even if they never say "report". Everything runs locally with ffmpeg and faster-whisper; the recording is never uploaded.
---

# Report: from a meeting recording to a deliverable

You get a recording; you give back what the person actually needs from it. The order is fixed for a reason: extract first (audio, transcript, screen frames), understand what was said, then ask what they want, then produce it. Asking before the extraction wastes their time because they cannot choose well without knowing what the recording holds; asking after lets them point at specifics ("the changes the boss listed at the start").

Everything runs on this machine. These are usually private company calls, so the recording, the audio and the transcript never go to an outside service.

Paths below are relative to this skill's folder (`~/.claude/skills/report`). Work files go in a `report/` folder next to the recording unless the user says otherwise. The Python environment and the speech models live in `~/.cache/report-skill/`, so nothing is downloaded twice.

## 1. Find the recording, set up

- The argument is the recording path. With no argument, look in the working directory (`find . -maxdepth 2 -iregex '.*\.\(mp4\|mkv\|webm\|mov\|mp3\|m4a\|wav\|ogg\)'`) and confirm which file if there are several.
- Run `bash scripts/setup.sh`. It creates the environment on first use (faster-whisper, numpy, Pillow, markdown), checks ffmpeg, and says whether Playwright is available for PDFs. It is idempotent and takes a second when already set up.

## 2. Extract

```
bash scripts/extract.sh <recording> [outdir]
```

This writes `media.json`, `audio16k.wav`, `audio-levels.txt` and, when the file has video, contact sheets in `sheets/`. Tell the user in one line how long the recording is and whether the audio has speech-level volume (a mean around -20 dB is normal; -60 dB means silence or the wrong track, and transcribing it would be a waste).

Start transcription in the background right away, because it is the slow step. On a 16-core CPU the `turbo` model does a 45-minute recording in about 8 minutes (short clips are dominated by the 20-second model load); the first use also downloads it (1.6 GB).

```
nohup ~/.cache/report-skill/venv/bin/python scripts/transcribe.py <outdir>/audio16k.wav <outdir> --model turbo --prompt "names and product terms" > <outdir>/transcribe.log 2>&1 &
```

- `turbo` (large-v3-turbo) is the default because accents and proper nouns come out far better than with `small`. If turbo is not cached yet and the network is slow, run `--model small` first for a usable transcript within minutes and turbo afterwards; the script caches each model.
- The `--prompt` is a vocabulary hint: names of people, products and tools from the screen notes or from the user. Without it whisper writes "Canada" for Calendly and turns product names into ordinary words.
- To stop a run use `pkill -f "[t]ranscribe.py"`. A plain `pkill -f transcribe` also matches the shell you typed it in and kills your own command.

## 3. Read the screen while the transcript runs

The contact sheets show one thumbnail per minute (`overview-*.jpg`) and one per 10 seconds (`detail-*.jpg`), each with its timestamp printed underneath. Read the overview first and look for anything shared on screen: a notes document being typed, slides, a dashboard, code, a chat window. In a requirements call the note-taker's list is often the best record of what was asked, in the client's own words, and it is invisible to the transcript.

For each stretch where a document is on screen, grab its latest state (the last thumbnail before the screen changes), because a document being typed is most complete at the end of the stretch:

```
bash scripts/frame.sh <recording> <seconds> <outdir>/frames/doc-<mmss>.png [W:H:X:Y] [scale]
```

Crop to the text area and upscale 2x so the text is legible, Read the image, and type what it says into `screen-notes.md` with the timestamp. Leave out personal content that happens to be on screen (private chats, notifications); it is not part of the meeting and the user did not ask for it.

## 4. Understand

When `transcribe.log` ends with `DONE`, read `transcript.txt` in full, not just the first screen. Then write `meeting-notes.md`:

- who was there (names from video tiles, the transcript or the user) and who is leading
- a timeline of topics with timestamps
- decisions, requests and changes asked for, action items with owner and date, open questions
- a short glossary of mis-hearings you corrected ("Canada" = Calendly) so the user can trust the rest

There is no speaker labelling. Attribute by content (who gives instructions, who asks) and, on video calls, by the highlighted active-speaker tile in a frame at that time. Write "the speaker" rather than guess a name when unsure; a wrong attribution in a report is worse than none.

## 5. Ask what they need

Now, with the facts in hand, give a three-line recap (length, who was there, the main topics) and ask with AskUserQuestion. Shape the options to what the recording holds; typical ones:

- summary with decisions and action items
- the list of changes or requests someone made, in bullet points
- scope and hour estimate for those changes
- a clean transcript
- a PDF or a shareable doc of one of the above
- something else (they type it)

## 6. Produce it

`references/outputs.md` has the structure for each deliverable; read the section you need before writing. Anything about scope or effort must be grounded in the actual codebase if it is on this machine (search for it); an estimate from the call alone is a guess, and say so if that is all you have.

- Markdown goes in the report folder next to the recording.
- A PDF: write markdown or HTML, then `~/.cache/report-skill/venv/bin/python scripts/build_pdf.py <in.md|in.html> <out.pdf> --title "..." --meta "Prepared by ..." --footer "..."`. Read `references/pdf-style.md` first; it is the difference between a document someone forwards and one that looks generated. Then open the PDF with Read and check every page before handing it over.
- A shareable doc: when a docs connector is available, follow its instructions.

Finish by listing the files you produced and saying in plain words what the deliverable contains.

## Gotchas

- faster-whisper's own audio loader breaks on recent PyAV versions, so `transcribe.py` loads the WAV with numpy. That is why `extract.sh` always produces 16 kHz mono PCM.
- Hugging Face's chunked downloader can crawl at 200 KB/s on a link that does 1 MB/s over plain HTTP; `fetch_model.sh` uses curl with resume instead.
- Whisper has no speaker labels and can loop on silence; voice activity detection is on in the script, and `condition_on_previous_text` is off so one garbled window does not poison the next.
- Keep every number consistent across the deliverable: if a figure appears in a table and in a chart, round it the same way in both.
