# Video Course Ingest Branch

Use this reference when the source is a local video/audio course and the user wants it in `$WIKI_ROOT`.

## Main Line

The main line is:

```text
resolve configured tools -> inspect media -> repair genuinely missing tools with approval -> archive raw media -> extract audio -> ASR -> keyframes/OCR -> source/extraction notes -> ASR correction notes -> coverage -> placement proposal and user confirmation -> formal pages -> index/log -> validation -> audit handoff
```

Do not skip good tooling merely because a short command is absent from `PATH`.
Resolve the bootstrap config, `$WIKI_ROOT/TOOLS.md`, and recorded absolute paths
first. If a high-quality local ASR or OCR tool is genuinely missing, explain
what is needed and ask before installing or replacing software, then continue
on the main line. Avoid low-quality shortcuts that would shrink or distort the
course.

## Tool Resolution On Every Platform

The bootstrap process may have installed the media tools in a Wiki-specific
directory instead of the global `PATH`. That is valid and preferred over
duplicate installation.

Resolve tools in this order:

1. current process variables `LLMWIKI_MEDIA_BIN` and `WHISPER_MODEL`
2. `~/.llmwiki/config.json`, read as data without executing a shell script
3. the verified absolute paths recorded in `$WIKI_ROOT/TOOLS.md`
4. the current `PATH`
5. platform-standard install locations

If the configured media directory exists, build absolute paths to `ffprobe`,
`ffmpeg`, `tesseract`, and the installed Whisper CLI (including `.exe` on
Windows) and execute those paths directly. Check that `WHISPER_MODEL` exists
before starting ASR. Record the resolved executable and model paths in
`source-profile.md` or extraction notes.

### Windows PowerShell

Read the bootstrap JSON config before probing tools. Do not dot-source
`config.ps1` and do not change execution policy:

```powershell
$configPath = Join-Path $env:USERPROFILE '.llmwiki\config.json'
$config = if (Test-Path -LiteralPath $configPath) {
  Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
} else {
  $null
}
$wikiRoot = if ($config) { [string]$config.WIKI_ROOT } else { Join-Path $env:USERPROFILE 'wiki' }
$mediaBin = if ($config) { [string]$config.LLMWIKI_MEDIA_BIN } else { '' }
$model = if ($config) { [string]$config.WHISPER_MODEL } else { '' }
$ffprobe = if ($mediaBin) { Join-Path $mediaBin 'ffprobe.exe' }
$ffmpeg = if ($mediaBin) { Join-Path $mediaBin 'ffmpeg.exe' }
$tesseract = if ($mediaBin) { Join-Path $mediaBin 'tesseract.exe' }
$whisper = if ($mediaBin) { Join-Path $mediaBin 'whisper-cli.exe' }
```

Set `$toolsFile = Join-Path $wikiRoot 'TOOLS.md'`; call the read tool or
`Get-Content` only after `Test-Path -LiteralPath $toolsFile` succeeds. An absent
file on an older Wiki is not an error. Test the resolved absolute paths with
`& $ffprobe -version`, `& $ffmpeg -version`,
`& $tesseract --version`, and `& $whisper --help`. If the recorded Whisper
executable uses another name, use the exact path in `TOOLS.md`. A failed
`Get-Command ffmpeg` is not evidence that the configured executable is missing.
Use PowerShell syntax throughout; do not translate the Bash examples below
literally.

Windows PowerShell can surface normal native stderr output from FFmpeg or
Whisper as `NativeCommandError`, especially when `$ErrorActionPreference` is
`Stop`. Do not use that preference around native media commands. Run the native
command, capture its log, and decide success only from `$LASTEXITCODE` plus the
expected output file. For example:

```powershell
$previousPreference = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
& $ffmpeg -y -i $video -vn -ac 1 -ar 16000 -c:a pcm_s16le $wav 2>&1 |
  Tee-Object -FilePath $ffmpegLog
$nativeExit = $LASTEXITCODE
$ErrorActionPreference = $previousPreference
if ($nativeExit -ne 0 -or -not (Test-Path -LiteralPath $wav)) {
  throw "FFmpeg failed with exit code $nativeExit; see $ffmpegLog"
}
```

### macOS/Linux

Load `~/.llmwiki/config.env` when it exists, then use the configured absolute
paths before global commands:

```bash
test -f "$HOME/.llmwiki/config.env" && source "$HOME/.llmwiki/config.env"
test -f "$WIKI_ROOT/TOOLS.md" && sed -n '1,220p' "$WIKI_ROOT/TOOLS.md"
```

The following probes and optional Homebrew example apply only after configured
paths have been checked.

## macOS Tool Nodes

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

If `whisper-cpp` is genuinely missing, the user approves installation, and
Homebrew is available:

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

When ingesting a later chapter into an existing course package, update these
package-level files instead of creating a second package. Add chapter-level
files under `chXX/` for segment and coverage detail, but keep
`source-profile.md`, `source-inventory.md`, `knowledge-unit-inventory.md`,
`coverage-matrix.md`, `omission-audit.md`, `formal-page-plan.md`, and
`audit-handoff.md` at the package root so validators and future audits can find
the whole course context.

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

Before creating or updating formal pages, follow the main Skill's mandatory
placement proposal. Show the user the recommended category/path and
merge/create/split plan, then wait for explicit confirmation. Raw preservation,
ASR/OCR, and extraction notes may be completed before this gate; formal domain
pages, query entries, and formal indexes may not.

Formal pages should be domain knowledge, not video notes. A video-course package may have a source-summary index, but the durable pages should normally be:

- capability framework
- concept page
- operating playbook
- learning path
- case library entry
- Agent-use query page

For an added chapter in an existing course package, decide whether to:

- create a new formal page when the chapter introduces a new durable capability,
  playbook, concept, or diagnostic template
- merge into an existing formal page when the chapter only reinforces or
  extends an existing theory
- update only the package index and coverage records when the chapter is a
  transition, intro, outro, or raw-only artifact

Record that disposition in the package `formal-page-plan.md` and chapter
coverage/omission files.

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
5. Run `validate_ingest_contract.py` where possible. For existing course
   packages with added chapters, pass the package-level notes directory, not
   only `_meta/extraction-notes/<source-slug>/chXX/`, because the required
   profile, inventory, formal plan, and audit handoff live at package root.
   The validator checks that every formalized/merged coverage row resolves to a
   real target page. It does not require internal source-unit IDs or transcript
   sentences to appear verbatim in learner-facing formal pages.
6. Run placeholder scan on formal outputs.
7. Remove `_meta/working/<source-slug>/` unless there is a deliberate reason to keep it.
8. Update relevant domain index, root `index.md`, and `log.md`.

If an ASR term is uncertain, do not block the whole ingest. Mark it unresolved, keep the raw evidence, formalize the surrounding method safely, and return to the main ingest workflow.
