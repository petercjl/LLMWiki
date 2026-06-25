# Video Course Ingest Branch

Use this reference when the source is a local video/audio course and the user wants it in `$WIKI_ROOT`.

## Main Line

The main line is:

```text
inspect media -> install missing tools -> archive raw media -> extract audio -> ASR -> keyframes/OCR -> source/extraction notes -> ASR correction notes -> coverage -> formal pages -> index/log -> validation -> audit handoff
```

Do not skip good tooling merely because it is not already installed. If a high-quality local ASR or OCR tool is missing, install it when feasible, then continue on the main line. Avoid low-quality shortcuts that would shrink or distort the course.

## Tool Nodes

Prefer these tools on macOS:

- `ffprobe`: inspect codec, duration, resolution, audio stream, and file size.
- `ffmpeg`: extract 16 kHz mono WAV and keyframes.
- `whisper-cpp` on Apple Silicon when Python ASR packages are absent or unstable.
- `tesseract` with `chi_sim+eng` for keyframe OCR.
- ImageMagick only when keyframes need preprocessing for OCR.

Useful probes:

```bash
ffprobe -hide_banner -v error -show_entries format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate -of default=noprint_wrappers=1 "$video"
which ffmpeg ffprobe whisper-cli tesseract
tesseract --list-langs
```

If `whisper-cpp` is missing and Homebrew is available:

```bash
brew install whisper-cpp
mkdir -p "$HOME/.local/share/whisper.cpp/models"
curl -L --fail -o "$HOME/.local/share/whisper.cpp/models/ggml-large-v3-turbo.bin" \
  https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin
```

Use a better current model if available. Record the exact model path and version in extraction notes and log.

## Raw Layout

Use one stable slug for the whole course/batch:

```text
raw/videos/<source-slug>/
raw/transcripts/<source-slug>/
raw/assets/<source-slug>/<chapter-id>/keyframes/
_meta/extraction-notes/<source-slug>/
```

Temporary audio and intermediate ASR files may live under `_meta/working/<source-slug>/`, but do not commit or treat them as durable source unless they are intentionally promoted to `raw/`.

Preserve raw ASR output separately from corrected interpretation. Do not overwrite raw ASR after generating it.

## Media Inspection

Before extraction, inventory every media file:

- filename and inferred chapter title
- duration
- audio/video codecs
- resolution
- whether subtitles, slides, screen recording, or mostly talking head/cover are visible
- expected primary evidence: speech, slides, subtitles, screenshots, or mixed

For a batch, inspect all files before formal writing. Do not let the first file's visual density determine the whole batch.

## Extraction Commands

Audio:

```bash
ffmpeg -y -i "$video" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$work/chXX.wav"
```

Keyframes:

```bash
ffmpeg -y -i "$video" -vf "fps=1/15,scale=1280:-1" "$raw_assets/chXX/keyframes/frame_%03d.jpg"
```

Use `fps=1/10` or denser when slides change quickly, subtitles contain important text, or screen content carries knowledge not fully spoken. Use sparser sampling for static covers or talking-head videos.

OCR:

```bash
tesseract "$frame" "$work/ocr_frame_001" -l chi_sim+eng --psm 6
```

ASR:

```bash
whisper-cli -m "$model" -f "$work/chXX.wav" -l zh \
  --prompt "course-specific terms, platform names, metric names" \
  --carry-initial-prompt \
  -otxt -osrt -oj \
  -of "$work/chXX-whisper-large-v3-turbo-prompted"
```

Copy final raw ASR artifacts to `raw/transcripts/<source-slug>/`:

- `.raw.txt`
- `.raw.srt`
- `.raw.json`

## ASR/OCR Correction Rules

Raw ASR is evidence, not truth. For formal pages:

- Correct obvious ASR errors only when supported by file names, slide/OCR text, repeated context, or domain knowledge.
- Record corrections in `knowledge-unit-inventory.md`, `coverage-matrix.md`, or `omission-audit.md`.
- Keep unresolved terms as `待确认` instead of turning them into operational instructions.
- Do not silently rewrite raw transcript files.

Examples of acceptable correction records:

- `循环量` -> `询盘量`, when cover OCR and course context show the course is about inquiry volume.
- `万物首页` -> `旺铺首页`, when Alibaba International Station storefront context supports it.
- `学习局道` -> `学习渠道`, when it is an obvious ASR error.
- Ambiguous metric/tool words remain unresolved until verified in the current platform backend or original audio.

## Extraction Notes

For video courses, create or update:

```text
_meta/extraction-notes/<source-slug>/
├── source-profile.md
├── source-inventory.md
├── knowledge-unit-inventory.md
├── coverage-matrix.md
├── omission-audit.md
├── formal-page-plan.md
└── audit-handoff.md
```

For each chapter, add chapter-level files when useful:

```text
_meta/extraction-notes/<source-slug>/chXX/
├── segment-plan.md
├── coverage-matrix.md
└── omission-audit.md
```

Track both spoken units and visual units:

- spoken micro-segments
- visible slide title/outcome/diagram/table text
- subtitle-only anchors
- screenshots that carry operational meaning
- watermarks, decorative covers, and garbled OCR as raw-only when appropriate

## Formal Compilation

Formal pages should be domain knowledge, not video notes. A video-course package may have a source-summary index, but the durable pages should normally be:

- capability framework
- concept page
- operating playbook
- learning path
- case library entry
- Agent-use query page

Enrichment is encouraged after source coverage:

- reconstruct causal chains
- add decision tables
- turn examples into reusable rules
- add testing models and QA checklists
- connect with existing wiki pages

Mark platform-specific rules and backend terms as time-sensitive. If the course mentions platform tools or metrics, formal use should require current backend verification.

## Validation And Return To Main Line

Before finishing:

1. Confirm raw media exists.
2. Confirm raw ASR exists for every processed media file.
3. Confirm keyframes/OCR exist when screen content may carry knowledge.
4. Confirm every meaningful ASR/OCR unit has a coverage row or omission reason.
5. Run `validate_ingest_contract.py` where possible.
6. Run placeholder scan on formal outputs.
7. Remove `_meta/working/<source-slug>/` unless there is a deliberate reason to keep it.
8. Update relevant domain index, root `index.md`, and `log.md`.

If an ASR term is uncertain, do not block the whole ingest. Mark it unresolved, keep the raw evidence, formalize the surrounding method safely, and return to the main ingest workflow.
