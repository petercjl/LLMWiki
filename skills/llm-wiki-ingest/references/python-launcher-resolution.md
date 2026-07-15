# Python Launcher Resolution

Resolve Python on the target computer. Never copy an author-machine path, guess
an installation directory, or assume one command name works on every platform.

## Mandatory Probe

A command is a valid Python launcher only when this probe exits with code `0`
and prints a real executable path and version:

```python
import sys; print(sys.executable); print(sys.version_info[:3])
```

Finding a command in `PATH` is not enough. On Windows, `python3.exe` or
`python.exe` may be a Microsoft Store application-execution alias rather than a
working interpreter. Reject any candidate whose probe fails or opens an install
prompt.

Resolve the launcher once, record both the executable and any prefix arguments,
and reuse that exact verified launcher for every bundled Python script in the
current ingest. Do not independently choose `python`, `python3`, or `py` again at
the validation step.

For final ingest validation on Windows, use the bundled
`scripts/run_ingest_validation.cmd`. It performs this discovery without relying
on PowerShell script execution policy. Do not change execution policy merely to
run validation.

## Windows PowerShell

Probe these command forms in order:

1. `python`
2. `py -3`
3. `python3`

For each form, discover it with `Get-Command -All` or `where.exe`, then actually
run the mandatory probe. `py -3` is a command plus a prefix argument; preserve
both parts when it succeeds.

If none succeeds, continue discovery without a whole-disk recursive search:

- ask an available `py` launcher for registered interpreters with `py -0p`;
- inspect Python executables returned from the current user and system `PATH`;
- inspect Python installation folders beneath environment-derived roots such as
  `LOCALAPPDATA`, `ProgramFiles`, and `ProgramFiles(x86)`;
- inspect registered Python/App Paths entries when available.

Run the mandatory probe against every discovered absolute executable before
selecting it. Do not add it to persistent `PATH`, change an execution policy,
enable or disable App Execution Aliases, or install another Python from this
ingest Skill.

## macOS And Linux

Use `command -v` or an equivalent shell lookup to enumerate `python3` and
`python`, then run the mandatory probe on each resolved executable. Also inspect
active version-manager shims already present in `PATH`. Reuse the first verified
interpreter; do not install or relink Python from this ingest Skill.

## Failure Rule

If exhaustive target-machine discovery finds no verified interpreter, record
the candidates and probe errors in `audit-handoff.md`, mark validation as
incomplete, and stop before a success claim. Ask the user to repair the Wiki
tool environment through the initialization workflow. Do not substitute a
manual file listing for the validator.
