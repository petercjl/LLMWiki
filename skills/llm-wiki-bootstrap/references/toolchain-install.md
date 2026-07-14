# Toolchain Installation

Read this reference when bootstrap detects a missing tool or the user asks to prepare the machine for later ingestion.

## Profiles

**Core profile**

- Python 3 for deterministic Wiki scripts.
- Obsidian 1.12.7 or later. Its official CLI is bundled with the app.

**Media-ingestion profile**

- FFmpeg and ffprobe for probing, audio extraction, and frame sampling.
- A local Whisper-compatible ASR executable plus one explicitly selected model.
- Tesseract OCR with `chi_sim` and `eng` language data.
- ImageMagick only when OCR preprocessing or image conversion requires it.

Git is optional and is not part of either required profile. Office/PDF extractors are source-specific additions and should be installed only when an actual source needs them.

## Decision Rules

1. Inventory independent installations from PATH, user/system environment variables, install records, common system/user directories, and version-manager locations.
2. Record both native system architecture and current process architecture. On Windows ARM64, an x64 process does not make the system x64.
3. Reuse a compatible working installation. If multiple usable runtimes exist, report them and stop for user choice.
4. Select one compatible artifact and one trusted source before downloading. State version, architecture, URL, expected verification method, and whether PATH/profile changes are proposed.
5. Ask for confirmation. Download with the operating system's native client, not an Agent web-fetch tool.
6. Resolve a current checksum or signature from the same trusted release manifest. Pin the resolved version and checksum for that run, verify after download, and record both. Do not embed a release checksum permanently in this skill.
7. If a mirror index cannot be opened by an Agent browser, test the known mirror URL with the native client. A page-access failure is not a file-download failure.
8. Never silently fall back from a domestic or course-controlled mirror to GitHub. Stop and explain the missing artifact.
9. Use absolute executable paths for verification. Ask before making a persistent PATH or profile change.

## Obsidian

Preferred domestic download route:

- Mirror index: `https://obsidian.bijitongbu.site/`
- Signed download resolver: `https://obsidian-dl.notebooksyncer.com/sign?os=win` or `?os=mac`

Use the native client with the resolver's required request headers when needed. Confirm the returned platform artifact before downloading. If this route cannot provide a verified compatible file, stop and give the user the prepared manual course download link rather than switching sources silently.

After installation, start Obsidian and let the user open the new Wiki directory with **Open folder as vault**. Then test the bundled CLI:

- Windows: locate `Obsidian.com` beside `Obsidian.exe` and run `& "<path>\Obsidian.com" help`. After GUI registration and a new PowerShell window, also test `obsidian help`.
- macOS: run `"/Applications/Obsidian.app/Contents/MacOS/obsidian-cli" help`. After GUI registration, also test `/usr/local/bin/obsidian help` when present.
- Linux: test the installed package launcher with `obsidian help`.

Do not use `--help`. Do not call `Obsidian.exe help` on Windows. Do not edit `obsidian.json` to register a vault.

## Python

Inspect before installing. For official CPython installers in mainland China, use the Tsinghua mirror index:

- `https://mirrors.tuna.tsinghua.edu.cn/python/`

For later Python packages, use the Tsinghua PyPI index for that command only:

- `https://pypi.tuna.tsinghua.edu.cn/simple`

Do not permanently rewrite the user's global pip configuration unless asked.

## Windows Media Toolchain

Prefer the Tsinghua MSYS2 mirror when it has packages for the native architecture:

- Mirror root: `https://mirrors.tuna.tsinghua.edu.cn/msys2/`
- Windows x64 repository: `mingw64`
- Windows ARM64 repository: `clangarm64`

For Windows ARM64, the current native package names are:

- `mingw-w64-clang-aarch64-ffmpeg`
- `mingw-w64-clang-aarch64-whisper.cpp`
- `mingw-w64-clang-aarch64-tesseract-ocr`
- `mingw-w64-clang-aarch64-tesseract-data-chi_sim`
- `mingw-w64-clang-aarch64-tesseract-data-eng`
- `mingw-w64-clang-aarch64-imagemagick` when needed

For x64, resolve the corresponding `mingw-w64-x86_64-*` names from the mirror's current package database instead of assuming versions. Configure the selected MSYS2 environment to use the Tsinghua mirror before package installation.

The upstream whisper.cpp project currently publishes Windows x64 binaries but no Windows ARM64 release asset. Do not label an upstream x64 package as native ARM64. The Tsinghua MSYS2 `clangarm64` repository currently supplies a native `mingw-w64-clang-aarch64-whisper.cpp` package; prefer that package on Windows ARM64 and verify the resulting `whisper-cli` architecture and help output.

For the multilingual model, a domestic ModelScope mirror is available:

- Repository: `https://modelscope.cn/models/cjc1887415157/whisper.cpp`
- Small multilingual direct file: `https://modelscope.cn/models/cjc1887415157/whisper.cpp/resolve/master/ggml-small.bin`

The Small model is roughly 466 MB and is the default course balance for Chinese teaching videos. Before the real download, make a native HEAD request, record the current 64-character `X-Linked-Etag` supplied by ModelScope, then calculate SHA-256 after download and compare it with that recorded value. Also preserve the model repository's published model hash as secondary provenance. Do not permanently hard-code either value in the Skill because the repository can update.

If the native MSYS2 package later disappears or fails verification, use only one of these explicit fallback branches:

1. a course-controlled native ARM64 build with a published manifest and checksum;
2. a locally compiled native ARM64 build after the user approves the compiler toolchain;
3. a verified x64 build under Windows emulation, clearly reported as emulated, after a clean-machine test proves it works.

If neither executable nor model has a trusted compatible mirror, leave ASR missing and report that video/audio ingestion is not ready.

## macOS Media Toolchain

If Homebrew already exists, use Tsinghua's Homebrew API and bottle mirror as temporary environment variables for the installation command. Reference:

- `https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/`

Install only missing items: FFmpeg, whisper.cpp, Tesseract plus Chinese/English language data, and ImageMagick when needed. Do not persist mirror variables in shell profiles without permission. Resolve the ASR model from a course-controlled manifest and verify its checksum.

## Verification

Run and record:

- `python --version` or the selected Python executable.
- Obsidian app version and `<obsidian-cli> help` while Obsidian is running.
- `ffmpeg -version` and `ffprobe -version`.
- the selected ASR executable's help/version plus the model path and checksum.
- `tesseract --version` and `tesseract --list-langs`; require `chi_sim` and `eng`.
- `magick -version` only when ImageMagick was installed.

Write a short `TOOLS.md` in the Wiki root after a real installation, listing tool, version, architecture, executable path, source, and verification result. Do not include secrets or temporary signed URLs.
